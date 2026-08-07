#!/usr/bin/env python3
"""Dependency-free publication-contract checks for the Sail Research site."""

from __future__ import annotations

import html
import json
import re
import struct
import sys

from collections import Counter
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "ops" / "publications.json"
TAXONOMY_PATH = ROOT / "ops" / "editorial_taxonomy.json"
BASE_URL = "https://sitcrkr89.github.io/sail-research/"
SOCIAL_IMAGE_URL = BASE_URL + "assets/social-card.png"
CANONICAL_SAMPLER_ALGORITHM = (
    "        var passed = 0;\n"
    "        var answers = [];\n"
    "        for (var i = 0; i < data.gates.length; i += 1) {\n"
    "          answers.push(document.getElementById('gate-answer-' + i).value);\n"
    "        }\n"
    "        for (var j = 0; j < answers.length; j += 1) {\n"
    "          if (answers[j] !== 'yes') break;\n"
    "          passed += 1;\n"
    "        }\n"
    "        var stance = passed > 0 ? data.gates[passed - 1].stance_if_passed : 'MONITOR';\n"
)

CORE_URLS = {
    Path("index.html"): BASE_URL,
    Path("product.html"): BASE_URL + "product.html",
    Path("for.html"): BASE_URL + "for.html",
    Path("about.html"): BASE_URL + "about.html",
    Path("governance.html"): BASE_URL + "governance.html",
    Path("corrections.html"): BASE_URL + "corrections.html",
    Path("scope.html"): BASE_URL + "scope.html",
    Path("digest.html"): BASE_URL + "digest.html",
    Path("research/index.html"): BASE_URL + "research/",
    Path("research/methodology.html"): BASE_URL + "research/methodology.html",
    Path("research/qualification-sampler.html"): BASE_URL + "research/qualification-sampler.html",
}


class PageParser(HTMLParser):
    VOID = {
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, dict[str, str | None]]] = []
        self.structure_errors = 0
        self.h1 = 0
        self.main = 0
        self.title_count = 0
        self.lang: str | None = None
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.canonicals: list[str] = []
        self.metas: dict[str, list[str]] = {}
        self.link_rels: list[tuple[str, str]] = []
        self.body_attrs: dict[str, str | None] = {}
        self.publication_ids: list[str] = []
        self.evidence_strengths: list[str] = []
        self.evidence_definitions: list[tuple[str, str]] = []
        self.claim_state_definitions: list[tuple[str, str]] = []
        self.archive_notices: list[str] = []
        self.publication_cards: list[tuple[str, str, str]] = []
        self.featured_ids: list[str] = []
        self.latest_ids: list[str] = []
        self.correction_edges: list[tuple[str, str]] = []
        self.superseded_by: list[str] = []
        self.corrects: list[str] = []
        self.table_count = 0
        self.unwrapped_tables = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if tag == "html":
            self.lang = data.get("lang")
        elif tag == "title":
            self.title_count += 1
        elif tag == "h1":
            self.h1 += 1
        elif tag == "main":
            self.main += 1
        elif tag == "body":
            self.body_attrs = data
        elif tag == "a" and data.get("href"):
            self.hrefs.append(data["href"] or "")
            if data.get("class") and "pub" in (data.get("class") or "").split():
                if data.get("data-publication-id"):
                    self.publication_cards.append(
                        (
                            data["data-publication-id"] or "",
                            data.get("data-publication-status") or "",
                            data.get("data-analysis-tier") or "",
                        )
                    )
            if data.get("data-featured-id"):
                self.featured_ids.append(data["data-featured-id"] or "")
        elif tag == "link":
            rel = data.get("rel") or ""
            href = data.get("href") or ""
            self.link_rels.append((rel, href))
            if "canonical" in rel.split():
                self.canonicals.append(href)
        elif tag == "meta":
            key = data.get("name") or data.get("property")
            if key:
                self.metas.setdefault(key, []).append(data.get("content") or "")
        elif tag == "table":
            self.table_count += 1
            wrapped = any(
                "table-scroll" in ((entry.get("class") or "").split())
                for _, entry in self.stack
            )
            if not wrapped:
                self.unwrapped_tables += 1

        if data.get("id"):
            self.ids.append(data["id"] or "")
        if data.get("data-publication-id"):
            self.publication_ids.append(data["data-publication-id"] or "")
        if data.get("data-evidence-strength"):
            self.evidence_strengths.append(data["data-evidence-strength"] or "")
            if data.get("data-definition"):
                self.evidence_definitions.append(
                    (data["data-evidence-strength"] or "", data["data-definition"] or "")
                )
        if data.get("data-claim-state"):
            self.claim_state_definitions.append(
                (data["data-claim-state"] or "", data.get("data-definition") or "")
            )
        if data.get("data-archive-notice"):
            self.archive_notices.append(data["data-archive-notice"] or "")
        if data.get("data-latest-id"):
            self.latest_ids.append(data["data-latest-id"] or "")
        if data.get("data-featured-id") and tag != "a":
            self.featured_ids.append(data["data-featured-id"] or "")
        if data.get("data-correction-for") and data.get("data-corrected-by"):
            self.correction_edges.append(
                (data["data-correction-for"] or "", data["data-corrected-by"] or "")
            )
        if data.get("data-superseded-by"):
            self.superseded_by.append(data["data-superseded-by"] or "")
        if data.get("data-corrects"):
            self.corrects.append(data["data-corrects"] or "")

        if tag not in self.VOID:
            self.stack.append((tag, data))

    def handle_endtag(self, tag: str) -> None:
        if tag in self.VOID:
            return
        if not self.stack or self.stack[-1][0] != tag:
            self.structure_errors += 1
            return
        self.stack.pop()


def parse_page(path: Path) -> tuple[str, PageParser]:
    source = path.read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(source)
    return source, parser


def local_target(page: Path, href: str) -> tuple[Path, str] | None:
    parsed = urlparse(href)
    if parsed.scheme or href.startswith("//") or parsed.path.startswith("/"):
        return None
    path = unquote(parsed.path)
    target = page if not path else (page.parent / path).resolve()
    if target.is_dir():
        target /= "index.html"
    return target, unquote(parsed.fragment)


def expected_report_files() -> set[Path]:
    files = set((ROOT / "reports").glob("20*.html"))
    files.update((ROOT / "reports" / "full").glob("20*.html"))
    return {path.resolve() for path in files}


def source_chain_hosts(source: str) -> set[str]:
    sources = re.search(r"<h2>Sources.*?</h2>\s*<ul>(.*?)</ul>", source, re.S)
    if not sources:
        return set()
    hosts: set[str] = set()
    for href in re.findall(r'href="(https?://[^"]+)"', sources.group(1)):
        hostname = urlparse(html.unescape(href)).hostname
        if hostname:
            hosts.add(hostname.lower().removeprefix("www."))
    return hosts


def primary_source_chains(source: str) -> set[str]:
    sources = re.search(r"<h2>Sources.*?</h2>\s*<ul>(.*?)</ul>", source, re.S)
    if not sources:
        return set()
    chains: set[str] = set()
    for attributes in re.findall(r"<li([^>]*)>", sources.group(1)):
        if not re.search(r'data-source-class="primary"', attributes):
            continue
        match = re.search(r'data-source-chain="([^"]+)"', attributes)
        if match:
            chains.add(match.group(1))
    return chains


def grade_definition_rows(source: str) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    pattern = re.compile(
        r'<div class="g-item"[^>]*data-evidence-strength="([^"]+)"'
        r'[^>]*data-definition="([^"]+)"[^>]*>.*?<div class="d">(.*?)</div>',
        re.S,
    )
    for strength, definition, visible in pattern.findall(source):
        visible_text = html.unescape(re.sub(r"<[^>]+>", "", visible)).strip()
        rows.append((html.unescape(strength), html.unescape(definition), visible_text))
    return rows


def validate_registry(registry: dict, taxonomy: dict, errors: list[str]) -> dict[str, dict]:
    required = {
        "id", "path", "canonical_url", "title", "description", "published_at",
        "modified_at", "sector", "artifact_type", "evidence_strength",
        "methodology_version", "publication_status", "analysis_tier", "library_visible", "indexable",
    }
    if registry.get("schema_version") != "2.0":
        errors.append("ops/publications.json: schema_version must be 2.0")
    if registry.get("taxonomy_version") != taxonomy.get("schema_version"):
        errors.append("ops/publications.json: taxonomy_version does not match editorial taxonomy")
    if registry.get("base_url") != BASE_URL:
        errors.append("ops/publications.json: unexpected base_url")

    items = registry.get("publications", [])
    by_id: dict[str, dict] = {}
    seen_paths: set[str] = set()
    seen_urls: set[str] = set()
    registered_paths: set[Path] = set()
    allowed_strengths = set(taxonomy.get("evidence_strength", {}))
    allowed_statuses = set(taxonomy.get("publication_status", {}))
    allowed_artifacts = set(taxonomy.get("artifact_type", {}))
    allowed_tiers = set(taxonomy.get("analysis_tier", {}))
    compatibility = taxonomy.get("tier_compatibility", {})
    for index, item in enumerate(items):
        missing = required - set(item)
        if missing:
            errors.append(f"ops/publications.json: item {index} missing {sorted(missing)}")
            continue
        item_id = item["id"]
        if not re.fullmatch(r"SR-2026-\d{4}(?:-F)?", item_id):
            errors.append(f"ops/publications.json: invalid publication id {item_id!r}")
        if item_id in by_id:
            errors.append(f"ops/publications.json: duplicate id {item_id}")
        by_id[item_id] = item
        if item["path"] in seen_paths:
            errors.append(f"ops/publications.json: duplicate path {item['path']}")
        seen_paths.add(item["path"])
        raw_path = Path(item["path"])
        allowed_shape = (
            (len(raw_path.parts) == 2 and raw_path.parts[0] == "reports")
            or (len(raw_path.parts) == 3 and raw_path.parts[:2] == ("reports", "full"))
        )
        resolved_path = (ROOT / raw_path).resolve()
        reports_root = (ROOT / "reports").resolve()
        if raw_path.is_absolute() or ".." in raw_path.parts or not allowed_shape or reports_root not in resolved_path.parents:
            errors.append(f"{item_id}: unsafe report path {item['path']!r}")
        else:
            registered_paths.add(resolved_path)
        if item["canonical_url"] in seen_urls:
            errors.append(f"ops/publications.json: duplicate canonical {item['canonical_url']}")
        seen_urls.add(item["canonical_url"])
        if item["canonical_url"] != BASE_URL + item["path"]:
            errors.append(f"{item_id}: canonical_url does not match path")
        try:
            published = date.fromisoformat(item["published_at"])
            modified = date.fromisoformat(item["modified_at"])
            if published > modified:
                errors.append(f"{item_id}: published_at is after modified_at")
        except ValueError:
            errors.append(f"{item_id}: invalid ISO publication date")
        if item["publication_status"] not in allowed_statuses:
            errors.append(f"{item_id}: invalid publication_status {item['publication_status']!r}")
        if item["artifact_type"] not in allowed_artifacts:
            errors.append(f"{item_id}: invalid artifact_type {item['artifact_type']!r}")
        if item["analysis_tier"] not in allowed_tiers:
            errors.append(f"{item_id}: invalid analysis_tier {item['analysis_tier']!r}")
        elif item["analysis_tier"] not in compatibility.get(item["artifact_type"], []):
            errors.append(f"{item_id}: incompatible artifact_type and analysis_tier")
        if item["analysis_tier"] == "analyst_brief" and item.get("decision_stance") not in taxonomy.get("decision_stance", {}):
            errors.append(f"{item_id}: analyst brief requires a valid decision_stance")
        quality = item.get("analytical_quality")
        if quality and quality.get("review_status") not in {"owner_review_required", "approved"}:
            errors.append(f"{item_id}: invalid analytical review status")
        if quality and quality.get("review_status") != "approved" and (
            item["library_visible"] or item["indexable"]
        ):
            errors.append(f"{item_id}: owner review hold cannot be library-visible or indexable")
        if quality and quality.get("review_status") == "owner_review_required" and item["publication_status"] != "review_hold":
            errors.append(f"{item_id}: owner_review_required requires review_hold")
        if item["publication_status"] == "review_hold" and (
            not quality or quality.get("review_status") != "owner_review_required"
        ):
            errors.append(f"{item_id}: review_hold requires owner_review_required")
        strength = item["evidence_strength"]
        if strength is not None and strength not in allowed_strengths:
            errors.append(f"{item_id}: invalid evidence_strength {strength!r}")
        if item["publication_status"] == "superseded":
            if strength is not None:
                errors.append(f"{item_id}: superseded publication must withdraw its grade")
            if item["library_visible"] or item["indexable"] or item.get("featured_rank"):
                errors.append(f"{item_id}: superseded publication cannot be listed, indexed, or featured")
            for key in ("superseded_by", "correction_date", "correction_reason", "conclusion_impact"):
                if not item.get(key):
                    errors.append(f"{item_id}: superseded publication missing {key}")
        if item["publication_status"] == "archived":
            if not item.get("archived_at"):
                errors.append(f"{item_id}: archived publication missing archived_at")
            elif item["archived_at"] != item["modified_at"]:
                errors.append(f"{item_id}: archived_at must match the archive notice modification date")
            if item["methodology_version"] == taxonomy.get("schema_version"):
                errors.append(f"{item_id}: archived publication cannot claim the current methodology version")

    actual = expected_report_files()
    registered = registered_paths
    for path in sorted(actual - registered):
        errors.append(f"ops/publications.json: unregistered report {path.relative_to(ROOT)}")
    for path in sorted(registered - actual):
        errors.append(f"ops/publications.json: registered report missing on disk: {path.relative_to(ROOT)}")

    for item in items:
        replacement = item.get("superseded_by")
        if not replacement:
            continue
        if replacement == item["id"] or replacement not in by_id:
            errors.append(f"{item['id']}: invalid superseded_by relation")
            continue
        if by_id[replacement].get("corrects") != item["id"]:
            errors.append(f"{item['id']}: replacement {replacement} lacks reciprocal corrects edge")
    for item in items:
        original = item.get("corrects")
        if original and (original not in by_id or by_id[original].get("superseded_by") != item["id"]):
            errors.append(f"{item['id']}: corrects edge is not reciprocal")
    for start in by_id:
        seen: set[str] = set()
        current = start
        while current in by_id and by_id[current].get("superseded_by"):
            if current in seen:
                errors.append(f"ops/publications.json: correction cycle includes {current}")
                break
            seen.add(current)
            current = by_id[current]["superseded_by"]
    return by_id


def validate_common_page(
    path: Path,
    expected_url: str,
    source: str,
    parser: PageParser,
    errors: list[str],
    cache: dict[Path, tuple[str, PageParser]],
) -> None:
    rel = path.relative_to(ROOT)
    if parser.lang != "en":
        errors.append(f"{rel}: html lang must be en")
    if parser.title_count != 1:
        errors.append(f"{rel}: expected exactly one title, found {parser.title_count}")
    if parser.h1 != 1:
        errors.append(f"{rel}: expected exactly one h1, found {parser.h1}")
    if parser.main != 1:
        errors.append(f"{rel}: expected exactly one main, found {parser.main}")
    if parser.structure_errors or parser.stack:
        errors.append(f"{rel}: unbalanced HTML structure detected")
    duplicates = sorted(key for key, count in Counter(parser.ids).items() if count > 1)
    if duplicates:
        errors.append(f"{rel}: duplicate id attributes: {duplicates}")
    if len(parser.canonicals) != 1 or parser.canonicals[0] != expected_url:
        errors.append(f"{rel}: canonical must equal {expected_url}")
    for key in (
        "description", "og:title", "og:description", "og:url", "og:image",
        "og:image:type", "og:image:width", "og:image:height", "og:image:alt",
        "twitter:card", "twitter:image", "twitter:image:alt", "viewport",
    ):
        values = parser.metas.get(key, [])
        if len(values) != 1 or not values[0]:
            errors.append(f"{rel}: expected one non-empty {key} metadata value")
    if parser.metas.get("og:url") != [expected_url]:
        errors.append(f"{rel}: og:url must equal canonical URL")
    if parser.metas.get("og:image") != [SOCIAL_IMAGE_URL]:
        errors.append(f"{rel}: og:image must use the canonical PNG social card")
    if parser.metas.get("twitter:image") != [SOCIAL_IMAGE_URL]:
        errors.append(f"{rel}: twitter:image must use the canonical PNG social card")
    if parser.metas.get("og:image:type") != ["image/png"]:
        errors.append(f"{rel}: og:image:type must be image/png")
    if parser.metas.get("og:image:width") != ["1200"] or parser.metas.get("og:image:height") != ["630"]:
        errors.append(f"{rel}: social-card dimensions must be declared as 1200x630")
    if not any("icon" in rel_value.split() and href for rel_value, href in parser.link_rels):
        errors.append(f"{rel}: missing favicon link")
    if re.search(r"(?<!&)mdash;", source):
        errors.append(f"{rel}: literal mdash artifact detected")

    for href in parser.hrefs:
        target_data = local_target(path, href)
        if target_data is None:
            continue
        target, fragment = target_data
        if target != ROOT and ROOT not in target.parents:
            errors.append(f"{rel}: local link escapes repository: {href}")
            continue
        if not target.exists():
            errors.append(f"{rel}: broken local link: {href}")
            continue
        if fragment:
            if target not in cache:
                cache[target] = parse_page(target)
            if fragment not in cache[target][1].ids:
                errors.append(f"{rel}: broken local fragment: {href}")


def validate_report(path: Path, item: dict, source: str, parser: PageParser, errors: list[str]) -> None:
    rel = path.relative_to(ROOT)
    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", source, re.S)
    title_match = re.search(r"<title>(.*?)</title>", source, re.S)
    h1_text = html.unescape(re.sub(r"<[^>]+>", "", h1_match.group(1))).strip() if h1_match else ""
    title_text = html.unescape(title_match.group(1)).strip() if title_match else ""
    if h1_text != item["title"]:
        errors.append(f"{rel}: visible headline does not match registry title")
    expected_title = f"{item['title']} — Sail Research {item['id']}"
    if title_text != expected_title:
        errors.append(f"{rel}: document title does not match registry title")
    if parser.body_attrs.get("data-publication-status") != item["publication_status"]:
        errors.append(f"{rel}: body publication status does not match registry")
    if parser.body_attrs.get("data-methodology-version") != item["methodology_version"]:
        errors.append(f"{rel}: body methodology version does not match registry")
    if parser.body_attrs.get("data-analysis-tier") != item["analysis_tier"]:
        errors.append(f"{rel}: body analysis tier does not match registry")
    if parser.body_attrs.get("data-decision-stance", "") != item.get("decision_stance", ""):
        errors.append(f"{rel}: body decision stance does not match registry")
    if parser.publication_ids != [item["id"]]:
        errors.append(f"{rel}: expected one primary data-publication-id {item['id']}")
    strength = item["evidence_strength"]
    if strength is None:
        if parser.evidence_strengths:
            errors.append(f"{rel}: withdrawn grade must not expose evidence-strength metadata")
    elif parser.evidence_strengths != [strength]:
        errors.append(f"{rel}: evidence-strength chip does not match registry")
    if not any(href.endswith("research/index.html") for href in parser.hrefs):
        errors.append(f"{rel}: missing report-library return link")
    if parser.unwrapped_tables:
        errors.append(f"{rel}: {parser.unwrapped_tables} table(s) lack accessible scroll wrappers")
    if source.count('class="table-scroll"') != parser.table_count:
        errors.append(f"{rel}: every table must have exactly one table-scroll wrapper")

    if item["publication_status"] == "archived":
        if parser.archive_notices != [item["methodology_version"]]:
            errors.append(f"{rel}: archived report lacks a visible legacy/not-regraded notice")
        archive_copy = source.lower()
        if "archived" not in archive_copy or "not regraded" not in archive_copy:
            errors.append(f"{rel}: archived report status is not explicit in visible copy")
        if f"Legacy {strength} — not regraded" not in source:
            errors.append(f"{rel}: archived grade chip must be explicitly labeled legacy/not regraded")
    elif parser.archive_notices:
        errors.append(f"{rel}: non-archived report exposes an archive notice")

    if item["publication_status"] in {"active", "corrected"} and strength == "A":
        statement = re.search(
            r'<p[^>]*data-independence-statement="[^"]+"[^>]*>(.*?)</p>',
            source,
            re.S,
        )
        if not statement or "independent" not in html.unescape(
            re.sub(r"<[^>]+>", "", statement.group(1))
        ).lower():
            errors.append(f"{rel}: Evidence A requires a marked independence statement")
        hosts = source_chain_hosts(source)
        if len(hosts) < 2:
            errors.append(f"{rel}: Evidence A requires at least two distinct primary-source hosts")
        if len(primary_source_chains(source)) < 2:
            errors.append(f"{rel}: Evidence A requires at least two structured primary-source chains")

    jsonld_blocks = re.findall(
        r'<script type="application/ld\+json">\s*(.*?)\s*</script>', source, re.S
    )
    if len(jsonld_blocks) != 1:
        errors.append(f"{rel}: expected exactly one Article JSON-LD block")
    else:
        try:
            data = json.loads(html.unescape(jsonld_blocks[0]))
        except json.JSONDecodeError:
            errors.append(f"{rel}: malformed Article JSON-LD")
        else:
            expected = {
                "@type": "Article",
                "headline": item["title"],
                "datePublished": item["published_at"],
                "dateModified": item["modified_at"],
                "mainEntityOfPage": item["canonical_url"],
            }
            for key, value in expected.items():
                if data.get(key) != value:
                    errors.append(f"{rel}: JSON-LD {key} does not match registry")
            for role in ("author", "publisher"):
                if data.get(role) != {"@type": "Organization", "name": "Sail Research"}:
                    errors.append(f"{rel}: JSON-LD {role} must identify Sail Research as an organization")

    if item["publication_status"] == "superseded":
        if parser.metas.get("robots") != ["noindex,follow"]:
            errors.append(f"{rel}: superseded report must be noindex,follow")
        if parser.superseded_by != [item["superseded_by"]]:
            errors.append(f"{rel}: missing visible superseded-by notice")
        replacement = item["superseded_by"]
        replacement_path = next(
            candidate["path"] for candidate in json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))["publications"]
            if candidate["id"] == replacement
        )
        expected_href = str(Path(replacement_path).relative_to(Path(item["path"]).parent))
        if expected_href not in parser.hrefs:
            errors.append(f"{rel}: superseded notice does not link to replacement")
        if "Superseded" not in source or "do not cite" not in source.lower():
            errors.append(f"{rel}: superseded state is not prominent in visible copy")
    if item["publication_status"] == "corrected":
        expected_original = item.get("corrects")
        if not expected_original or parser.corrects != [expected_original]:
            errors.append(f"{rel}: corrected report lacks reciprocal visible notice")


def validate_surfaces(
    registry: dict,
    taxonomy: dict,
    errors: list[str],
) -> None:
    visible = sorted(
        (item for item in registry["publications"] if item["library_visible"]),
        key=lambda item: (item["published_at"], item["id"]),
        reverse=True,
    )
    expected_cards = [(item["id"], item["publication_status"], item["analysis_tier"]) for item in visible]
    library_source, library_parser = parse_page(ROOT / "research" / "index.html")
    if library_parser.publication_cards != expected_cards:
        errors.append("research/index.html: publication order/status does not match registry projection")
    count_match = re.search(r'id="count"[^>]*>Showing (\d+) entr(?:y|ies)', library_source)
    if not count_match or int(count_match.group(1)) != len(visible):
        errors.append("research/index.html: visible count does not match registry")
    if re.search(r"SR-2026-0008(?!-F)", " ".join(item[0] for item in library_parser.publication_cards)):
        errors.append("research/index.html: superseded SR-2026-0008 remains listed")

    latest = max(visible, key=lambda item: (item["published_at"], item["id"]))
    if library_parser.latest_ids != [latest["id"]]:
        errors.append("research/index.html: latest publication marker does not match visible registry projection")
    homepage_source, homepage_parser = parse_page(ROOT / "index.html")
    if homepage_parser.latest_ids != [latest["id"], latest["id"]]:
        errors.append("index.html: latest publication markers do not match registry")
    expected_featured = [
        item["id"] for item in sorted(
            (entry for entry in registry["publications"] if entry.get("featured_rank")),
            key=lambda entry: entry["featured_rank"],
        )
    ]
    if homepage_parser.featured_ids != expected_featured:
        errors.append("index.html: featured publications do not match registry")
    expected_claim_states = list(taxonomy["claim_state"].items())
    if homepage_parser.claim_state_definitions != expected_claim_states:
        errors.append("index.html: claim-state demo does not exactly match canonical taxonomy")

    corrections_parser = parse_page(ROOT / "corrections.html")[1]
    expected_edges = {
        (item["id"], item["superseded_by"])
        for item in registry["publications"] if item.get("superseded_by")
    }
    if set(corrections_parser.correction_edges) != expected_edges:
        errors.append("corrections.html: ledger edges do not match registry")

    sitemap_source = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    if len(sitemap_source) > 1_000_000:
        errors.append("sitemap.xml: exceeds bounded parser limit")
        return
    if (
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' not in sitemap_source
        or not sitemap_source.rstrip().endswith("</urlset>")
    ):
        errors.append("sitemap.xml: invalid sitemap envelope")
        return
    records = re.findall(
        r"<url><loc>([^<]+)</loc><lastmod>([^<]+)</lastmod><priority>[^<]+</priority></url>",
        sitemap_source,
    )
    if sitemap_source.count("<url>") != len(records) or sitemap_source.count("</url>") != len(records):
        errors.append("sitemap.xml: invalid URL record structure")
        return
    locations = [loc for loc, _ in records]
    expected_locations = set(CORE_URLS.values()) | {
        item["canonical_url"] for item in registry["publications"] if item["indexable"]
    }
    if set(locations) != expected_locations or len(locations) != len(expected_locations):
        errors.append("sitemap.xml: URL set does not match core pages plus indexable registry reports")
    record_map = dict(records)
    for item in registry["publications"]:
        if item["indexable"] and record_map.get(item["canonical_url"]) != item["modified_at"]:
            errors.append(f"sitemap.xml: lastmod mismatch for {item['id']}")
    for loc in locations:
        parsed = urlparse(loc)
        if parsed.scheme != "https" or parsed.netloc != "sitcrkr89.github.io":
            errors.append(f"sitemap.xml: non-HTTPS or foreign URL {loc}")

    expected_grade_rows = [
        (strength, definition, definition)
        for strength, definition in taxonomy["evidence_strength"].items()
    ]
    methodology_source = (ROOT / "research" / "methodology.html").read_text(encoding="utf-8")
    library_source = (ROOT / "research" / "index.html").read_text(encoding="utf-8")
    if grade_definition_rows(methodology_source) != expected_grade_rows:
        errors.append("research/methodology.html: evidence-grade definitions do not exactly match taxonomy")
    if grade_definition_rows(library_source) != expected_grade_rows:
        errors.append("research/index.html: evidence-grade definitions do not exactly match taxonomy")
    if 'data-taxonomy-version="2.0"' not in methodology_source:
        errors.append("research/methodology.html: missing taxonomy version marker")

    sampler_source = (ROOT / "research" / "qualification-sampler.html").read_text(encoding="utf-8")
    methodology_path = ROOT / "ops" / "methodology_hbm_qualification.json"
    data_matches = re.findall(
        r'<script id="methodology-data" type="application/json">(.*?)</script>',
        sampler_source,
        re.DOTALL,
    )
    if len(data_matches) != 1:
        errors.append("research/qualification-sampler.html: expected exactly one methodology data block")
    else:
        try:
            canonical = json.loads(methodology_path.read_text(encoding="utf-8"))
            embedded = json.loads(data_matches[0])
            if embedded.get("gates") != canonical["gates"]:
                errors.append("research/qualification-sampler.html: embedded gates do not match canonical methodology")
            if embedded.get("transfer_rules") != canonical["transfer_rules"]:
                errors.append("research/qualification-sampler.html: embedded transfer rules do not match canonical methodology")
            if embedded.get("questions") != canonical["questions"]:
                errors.append("research/qualification-sampler.html: embedded questions do not match canonical methodology")
        except (KeyError, json.JSONDecodeError) as exc:
            errors.append(f"research/qualification-sampler.html: methodology data block unreadable: {exc}")
    algorithm_matches = re.findall(
        r"// SAMPLER-ALGORITHM:BEGIN\n(.*?)// SAMPLER-ALGORITHM:END",
        sampler_source,
        re.DOTALL,
    )
    if len(algorithm_matches) != 1 or algorithm_matches[0] != CANONICAL_SAMPLER_ALGORITHM:
        errors.append("research/qualification-sampler.html: pinned sampler algorithm was modified or duplicated")

    assessments_path = ROOT / "ops" / "methodology_assessments.json"
    methodology_path2 = ROOT / "ops" / "methodology_hbm_qualification.json"
    try:
        assessments = json.loads(assessments_path.read_text(encoding="utf-8"))
        methodology = json.loads(methodology_path2.read_text(encoding="utf-8"))
        items = assessments.get("assessments", [])
        if len(items) < 2:
            errors.append("ops/methodology_assessments.json: reproducibility requires at least two vendor assessments")
        if len({item.get("vendor") for item in items}) < 2:
            errors.append("ops/methodology_assessments.json: assessments must cover at least two distinct vendors")
        for item in items:
            item_id = item.get("assessment_id", "<unknown>")
            if item.get("methodology_id") != methodology["methodology_id"] or item.get("methodology_version") != methodology["version"]:
                errors.append(f"{item_id}: methodology reference does not match canonical ladder")
            if item.get("method_modified"):
                errors.append(f"{item_id}: method modification breaks the replication claim")
            gate_answers = item.get("gate_answers", [])
            expected_gates = [gate["id"] for gate in methodology["gates"]]
            if [entry.get("gate") for entry in gate_answers] != expected_gates:
                errors.append(f"{item_id}: gate answers do not cover the full ladder in order")
                continue
            for entry in gate_answers:
                if entry.get("answer") not in {"yes", "no", "unknown"}:
                    errors.append(f"{item_id} {entry.get('gate')}: invalid gate answer")
                if entry.get("answer") == "yes" and not entry.get("source_ref"):
                    errors.append(f"{item_id} {entry.get('gate')}: yes answer requires a source reference")
            passed = 0
            for entry in gate_answers:
                if entry.get("answer") != "yes":
                    break
                passed += 1
            expected_stance = methodology["gates"][passed - 1]["stance_if_passed"] if passed else "MONITOR"
            if item.get("stance") != expected_stance:
                errors.append(f"{item_id}: declared stance is not recomputable from gate answers")
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        errors.append(f"ops/methodology_assessments.json: unreadable replication record: {exc}")


def main() -> int:
    errors: list[str] = []
    try:
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        taxonomy = json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"SITE QA: FAIL\n- registry/taxonomy load failed: {exc}")
        return 1

    by_id = validate_registry(registry, taxonomy, errors)
    social_card = ROOT / "assets" / "social-card.png"
    try:
        social_bytes = social_card.read_bytes()
        if social_bytes[:8] != b"\x89PNG\r\n\x1a\n" or len(social_bytes) < 24:
            errors.append("assets/social-card.png: invalid PNG file")
        elif struct.unpack(">II", social_bytes[16:24]) != (1200, 630):
            errors.append("assets/social-card.png: expected exact 1200x630 dimensions")
    except OSError as exc:
        errors.append(f"assets/social-card.png: cannot read social card: {exc}")
    cache: dict[Path, tuple[str, PageParser]] = {}
    all_paths = [ROOT / rel for rel in CORE_URLS]
    all_paths.extend(sorted(expected_report_files()))
    for path in all_paths:
        if not path.exists():
            errors.append(f"{path.relative_to(ROOT)}: public page missing")
            continue
        source, parser = parse_page(path)
        cache[path.resolve()] = (source, parser)
        rel = path.relative_to(ROOT)
        if rel in CORE_URLS:
            expected_url = CORE_URLS[rel]
        else:
            primary_ids = parser.publication_ids
            item = by_id.get(primary_ids[0]) if len(primary_ids) == 1 else None
            expected_url = item["canonical_url"] if item else BASE_URL + str(rel)
        validate_common_page(path, expected_url, source, parser, errors, cache)
        if rel not in CORE_URLS:
            if len(parser.publication_ids) != 1 or parser.publication_ids[0] not in by_id:
                errors.append(f"{rel}: cannot resolve registry publication id")
            else:
                validate_report(path, by_id[parser.publication_ids[0]], source, parser, errors)

    validate_surfaces(registry, taxonomy, errors)

    public_copy_paths = [ROOT / rel for rel in CORE_URLS]
    public_copy_paths.extend(sorted(expected_report_files()))
    public_copy = "\n".join(path.read_text(encoding="utf-8") for path in public_copy_paths if path.exists())
    for stale_claim in (
        "Human-reviewed grades",
        "Human release gate",
        "never release without human review",
        "No pipeline publishes alone",
        "before human approval",
    ):
        if stale_claim.lower() in public_copy.lower():
            errors.append(f"public governance copy: stale review claim {stale_claim!r}")

    site_css = (ROOT / "assets" / "site.css").read_text(encoding="utf-8")
    if '.nav a:not(.nav-cta):not(.nav-keep) { display: none; }' in site_css:
        errors.append("assets/site.css: mobile navigation still hides primary destinations")
    homepage_css = (ROOT / "index.html").read_text(encoding="utf-8")
    if ".hero .btn-solid { background: var(--bg-elevated);" in homepage_css:
        errors.append("index.html: low-contrast hero primary button regression")
    methodology_css = (ROOT / "research" / "methodology.html").read_text(encoding="utf-8")
    if "color:#fff; background:var(--ink)" in methodology_css:
        errors.append("research/methodology.html: low-contrast step or grade badge regression")
    for form_page in ("scope.html", "digest.html"):
        source = (ROOT / form_page).read_text(encoding="utf-8")
        if 'action="mailto:sail.research.info@gmail.com" method="post" enctype="text/plain"' not in source:
            errors.append(f"{form_page}: missing truthful mail-draft fallback")
        if "not submission" not in source.lower() and "not submitted" not in source.lower():
            errors.append(f"{form_page}: does not explain that a draft is not submission")
    if 'action="digest.html" method="get"' in (ROOT / "index.html").read_text(encoding="utf-8"):
        errors.append("index.html: email address must not be copied into a GET query")
    if '../../assets/report.css' not in (ROOT / "reports" / "_TEMPLATE_FULL.html").read_text(encoding="utf-8"):
        errors.append("reports/_TEMPLATE_FULL.html: stylesheet path is wrong for reports/full/")

    if errors:
        print("SITE QA: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        f"SITE QA: PASS ({len(CORE_URLS)} core pages, "
        f"{len(registry['publications'])} registered reports, "
        f"{sum(1 for item in registry['publications'] if item['library_visible'])} library entries)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
