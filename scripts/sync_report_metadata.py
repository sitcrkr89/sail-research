#!/usr/bin/env python3
"""Synchronize report metadata and machine-readable status from the registry."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "ops" / "publications.json"
START = "<!-- PUBLICATION-METADATA:START -->"
END = "<!-- PUBLICATION-METADATA:END -->"
STATUS_START = "<!-- PUBLICATION-STATUS-NOTICE:START -->"
STATUS_END = "<!-- PUBLICATION-STATUS-NOTICE:END -->"


def safe_report_path(raw_path: str) -> Path:
    relative = Path(raw_path)
    allowed_shape = (
        (len(relative.parts) == 2 and relative.parts[0] == "reports")
        or (len(relative.parts) == 3 and relative.parts[:2] == ("reports", "full"))
    )
    if relative.is_absolute() or ".." in relative.parts or not allowed_shape:
        raise ValueError(f"unsafe report path in registry: {raw_path!r}")
    candidate = (ROOT / relative).resolve()
    reports_root = (ROOT / "reports").resolve()
    if reports_root not in candidate.parents:
        raise ValueError(f"report path escapes reports/: {raw_path!r}")
    return candidate


def metadata_block(item: dict) -> str:
    depth = len(Path(item["path"]).parts) - 1
    favicon = "../" * depth + "assets/mark.svg"
    headline = html.escape(item["title"], quote=True)
    description = html.escape(item["description"], quote=True)
    status = item["publication_status"]
    title_prefix = "Superseded — " if status == "superseded" else ""
    structured = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": item["title"],
        "datePublished": item["published_at"],
        "dateModified": item["modified_at"],
        "author": {"@type": "Organization", "name": "Sail Research"},
        "publisher": {"@type": "Organization", "name": "Sail Research"},
        "mainEntityOfPage": item["canonical_url"],
    }
    return "\n".join(
        [
            START,
            f'<link rel="canonical" href="{item["canonical_url"]}">',
            '<meta property="og:type" content="article">',
            '<meta property="og:site_name" content="Sail Research">',
            f'<meta property="og:title" content="{title_prefix}{headline} — Sail Research {item["id"]}">',
            f'<meta property="og:description" content="{description}">',
            f'<meta property="og:url" content="{item["canonical_url"]}">',
            '<meta property="og:image" content="https://sitcrkr89.github.io/sail-research/assets/social-card.png">',
            '<meta property="og:image:type" content="image/png">',
            '<meta property="og:image:width" content="1200">',
            '<meta property="og:image:height" content="630">',
            '<meta property="og:image:alt" content="Sail Research — Evidence at the claim boundary">',
            f'<meta property="article:published_time" content="{item["published_at"]}">',
            f'<meta property="article:modified_time" content="{item["modified_at"]}">',
            '<meta name="twitter:card" content="summary_large_image">',
            '<meta name="twitter:image" content="https://sitcrkr89.github.io/sail-research/assets/social-card.png">',
            '<meta name="twitter:image:alt" content="Sail Research — Evidence at the claim boundary">',
            f'<link rel="icon" href="{favicon}" type="image/svg+xml">',
            '<script type="application/ld+json">',
            json.dumps(structured, ensure_ascii=False, separators=(",", ":")),
            "</script>",
            END,
        ]
    ) + "\n"


def archive_notice(item: dict) -> str:
    methodology = html.escape(item["methodology_version"], quote=True)
    return "\n".join(
        [
            STATUS_START,
            f'<aside class="archive-notice wrap" data-archive-notice="{methodology}" aria-label="Archive status">',
            '  <p class="notice-label">Archived · legacy grade · not regraded</p>',
            '  <p>This report is retained for provenance. Its displayed grade is historical and has not been regraded under Standards v2.0.</p>',
            '</aside>',
            STATUS_END,
        ]
    ) + "\n"


def strip_legacy_metadata(source: str) -> str:
    source = re.sub(
        rf"{re.escape(START)}.*?{re.escape(END)}\s*",
        "",
        source,
        flags=re.S,
    )
    source = re.sub(r'^<link rel="canonical"[^>]*>\s*$', "", source, flags=re.M)
    source = re.sub(r'<meta property="(?:og:|article:)[^"]+"[^>]*>\s*', "", source)
    source = re.sub(r'^<meta name="twitter:(?:card|image|image:alt)"[^>]*>\s*$', "", source, flags=re.M)
    source = re.sub(r'^<link rel="icon"[^>]*>\s*$', "", source, flags=re.M)
    source = re.sub(
        r'<script type="application/ld\+json">\s*\{.*?\}\s*</script>\s*',
        "",
        source,
        flags=re.S,
    )
    source = re.sub(
        rf"{re.escape(STATUS_START)}.*?{re.escape(STATUS_END)}\s*",
        "",
        source,
        flags=re.S,
    )
    return source


def expected_source(item: dict, source: str) -> str:
    source = strip_legacy_metadata(source)
    document_title = f"{item['title']} — Sail Research {item['id']}"
    source, title_count = re.subn(
        r"<title>.*?</title>",
        f"<title>{html.escape(document_title)}</title>",
        source,
        count=1,
        flags=re.S,
    )
    if title_count != 1:
        raise ValueError(f"{item['path']}: expected one title element")
    source, count = re.subn(
        r'(<meta name="description"[^>]*>\s*)',
        lambda match: match.group(1) + metadata_block(item),
        source,
        count=1,
    )
    if count != 1:
        raise ValueError(f"{item['path']}: expected one description meta tag")
    source, count = re.subn(
        r'<body(?:\s+data-publication-status="[^"]+")?(?:\s+data-methodology-version="[^"]+")?>',
        f'<body data-publication-status="{item["publication_status"]}" data-methodology-version="{item["methodology_version"]}">',
        source,
        count=1,
    )
    if count != 1:
        raise ValueError(f"{item['path']}: expected a simple body start tag")
    if item["publication_status"] == "archived":
        source, count = re.subn(
            r"(</nav>\s*)",
            lambda match: match.group(1) + archive_notice(item) + "\n",
            source,
            count=1,
        )
        if count != 1:
            raise ValueError(f"{item['path']}: expected one navigation block for archive notice")
    source, count = re.subn(
        r'<div class="r-id"(?: data-publication-id="[^"]+")?>',
        f'<div class="r-id" data-publication-id="{item["id"]}">',
        source,
        count=1,
    )
    if count != 1:
        raise ValueError(f"{item['path']}: expected one report id element")
    strength = item["evidence_strength"]
    if strength is not None:
        source, count = re.subn(
            r'<span class="chip grade"(?: data-evidence-strength="[^"]+")?>',
            f'<span class="chip grade" data-evidence-strength="{strength}">',
            source,
            count=1,
        )
        if count != 1:
            raise ValueError(f"{item['path']}: expected one evidence grade chip")
    return source


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    stale: list[tuple[Path, str]] = []
    try:
        for item in registry["publications"]:
            path = safe_report_path(item["path"])
            source = path.read_text(encoding="utf-8")
            expected = expected_source(item, source)
            if source != expected:
                stale.append((path, expected))
    except (KeyError, ValueError) as exc:
        print(f"REPORT METADATA: FAIL — {exc}")
        return 1

    if args.check:
        if stale:
            print("REPORT METADATA: FAIL — stale report metadata")
            for path, _ in stale:
                print(f"- {path.relative_to(ROOT)}")
            return 1
        print(f"REPORT METADATA: PASS ({len(registry['publications'])} reports current)")
        return 0

    for path, expected in stale:
        path.write_text(expected, encoding="utf-8")
        print(f"updated {path.relative_to(ROOT)}")
    print(f"REPORT METADATA: PASS ({len(stale)} reports updated)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
