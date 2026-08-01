#!/usr/bin/env python3
"""Render bounded public surfaces from the canonical publication registry.

Use ``--write`` only while editing. CI and publication preflight use ``--check``
so a stale surface fails closed instead of being silently rewritten.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "ops" / "publications.json"
TAXONOMY = ROOT / "ops" / "editorial_taxonomy.json"

CORE_SITEMAP = [
    ("", "1.0"),
    ("product.html", "0.9"),
    ("for.html", "0.8"),
    ("about.html", "0.8"),
    ("governance.html", "0.8"),
    ("corrections.html", "0.9"),
    ("scope.html", "0.9"),
    ("digest.html", "0.7"),
    ("research/", "0.9"),
    ("research/methodology.html", "0.8"),
]


def load_registry() -> dict:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    ids: set[str] = set()
    paths: set[str] = set()
    for item in registry.get("publications", []):
        raw_path = Path(item["path"])
        allowed_shape = (
            (len(raw_path.parts) == 2 and raw_path.parts[0] == "reports")
            or (len(raw_path.parts) == 3 and raw_path.parts[:2] == ("reports", "full"))
        )
        if raw_path.is_absolute() or ".." in raw_path.parts or not allowed_shape:
            raise ValueError(f"unsafe report path in registry: {item['path']!r}")
        if item["id"] in ids or item["path"] in paths:
            raise ValueError("publication IDs and paths must be unique")
        if item["canonical_url"] != registry.get("base_url", "") + item["path"]:
            raise ValueError(f"canonical/path mismatch for {item['id']}")
        ids.add(item["id"])
        paths.add(item["path"])
    return registry


def load_taxonomy() -> dict:
    taxonomy = json.loads(TAXONOMY.read_text(encoding="utf-8"))
    if taxonomy.get("schema_version") != "2.0":
        raise ValueError("editorial taxonomy schema_version must be 2.0")
    if set(taxonomy.get("evidence_strength", {})) != {"A", "B+", "B", "C"}:
        raise ValueError("editorial taxonomy must define A/B+/B/C evidence strengths")
    return taxonomy


def visible_publications(registry: dict) -> list[dict]:
    rows = [item for item in registry["publications"] if item["library_visible"]]
    return sorted(rows, key=lambda item: (item["published_at"], item["id"]), reverse=True)


def report_href(item: dict, *, from_research: bool = False) -> str:
    prefix = "../" if from_research else ""
    return prefix + item["path"]


def short_date(value: str) -> str:
    parsed = date.fromisoformat(value)
    return parsed.strftime("%d %b")


def long_date(value: str) -> str:
    parsed = date.fromisoformat(value)
    return f"{parsed.day} {parsed.strftime('%B %Y')}"


def sector_label(item: dict) -> str:
    return {
        "semiconductors": "Semiconductors",
        "biopharma": "Biopharma",
        "power": "Power",
        "archive": "Archive",
    }[item["sector"]]


def render_library(registry: dict) -> str:
    blocks: list[str] = []
    for item in visible_publications(registry):
        badges: list[str] = []
        if item["artifact_type"] == "full_report":
            badges.append('<span class="full">Full Report</span>')
        if item["publication_status"] == "corrected":
            badges.append('<span class="status corrected">Corrected</span>')
        if item["publication_status"] == "archived":
            grade = f"Legacy {item['evidence_strength']} · not regraded"
        else:
            grade = f"Evidence {item['evidence_strength']}"
        badges.append(
            f'<span class="grade" data-evidence-strength="{html.escape(str(item["evidence_strength"]))}">{html.escape(grade)}</span>'
        )
        search = " ".join(
            [item["id"], item["title"], item["description"], item["sector"]]
        ).lower()
        blocks.append(
            f'''        <a class="pub" href="{html.escape(report_href(item, from_research=True))}" data-publication-id="{html.escape(item['id'])}" data-publication-status="{html.escape(item['publication_status'])}" data-sector="{html.escape(item['sector'])}" data-s="{html.escape(search)}">
          <div class="date"><time datetime="{item['published_at']}">{short_date(item['published_at'])}</time></div>
          <div class="body">
            <div class="running">
              <span class="num">{html.escape(item['id'])}</span>
              <span class="domain">{sector_label(item)}</span>
              {' '.join(badges)}
            </div>
            <h3>{html.escape(item['title'])}</h3>
            <p class="deck">{html.escape(item['description'])}</p>
          </div>
          <span class="go">Read</span>
        </a>'''
        )
    return '      <div class="pub-list" id="list">\n' + "\n".join(blocks) + "\n      </div>"


def render_grade_definitions(taxonomy: dict, *, indent: str = "        ") -> str:
    labels = {
        "A": ("g-badge", "Independent primary chains"),
        "B+": ("g-badge bp", "Strong, bounded record"),
        "B": ("g-badge b", "Attributable, limited"),
        "C": ("g-badge c", "Exploratory"),
    }
    rows: list[str] = []
    for strength, definition in taxonomy["evidence_strength"].items():
        badge_class, label = labels[strength]
        escaped_definition = html.escape(definition, quote=True)
        rows.append(
            f'{indent}<div class="g-item" data-evidence-strength="{html.escape(strength)}" '
            f'data-definition="{escaped_definition}"><div class="{badge_class}">{html.escape(strength)}</div>'
            f'<div><div class="t">{html.escape(label)}</div><div class="d">{html.escape(definition)}</div></div></div>'
        )
    return "\n".join(rows)


def render_featured(registry: dict) -> str:
    items = sorted(
        (item for item in registry["publications"] if item.get("featured_rank")),
        key=lambda item: item["featured_rank"],
    )
    if len(items) != 3:
        raise ValueError("exactly three featured publications are required")
    main, *side = items
    main_markup = f'''        <a class="card feature-main" href="{html.escape(report_href(main))}" data-featured-id="{main['id']}">
          <div class="feature-visual" aria-hidden="true">
            <span class="badge">{sector_label(main)} · Evidence {html.escape(main['evidence_strength'])}</span>
          </div>
          <div class="feature-body">
            <div class="tags">
              <span class="tag tag-brass">Latest full report</span>
              <span class="tag">{sector_label(main)}</span>
              <span class="tag">{short_date(main['published_at'])} 2026</span>
            </div>
            <h3>{html.escape(main['title'])}</h3>
            <p>{html.escape(main['description'])}</p>
            <div class="feature-meta">
              <span>{main['id']}</span>
              <span class="read">Read the report →</span>
            </div>
          </div>
        </a>'''
    side_markup: list[str] = []
    for item in side:
        labels = []
        if item["publication_status"] == "corrected":
            labels.append('<span class="tag tag-brass">Corrected</span>')
        labels.append(f'<span class="tag">Evidence {html.escape(item["evidence_strength"])}</span>')
        labels.append(f'<span class="tag">{sector_label(item)}</span>')
        side_markup.append(
            f'''          <a class="card" href="{html.escape(report_href(item))}" data-featured-id="{item['id']}">
            <div class="tags">{' '.join(labels)}</div>
            <h3>{html.escape(item['title'])}</h3>
            <p>{html.escape(item['description'])}</p>
            <span class="read">Read →</span>
          </a>'''
        )
    return f'''      <div class="feature-layout">
{main_markup}
        <div class="feature-side">
{chr(10).join(side_markup)}
        </div>
      </div>'''


def render_corrections(registry: dict) -> str:
    by_id = {item["id"]: item for item in registry["publications"]}
    entries: list[str] = []
    for original in registry["publications"]:
        replacement_id = original.get("superseded_by")
        if not replacement_id:
            continue
        replacement = by_id[replacement_id]
        entries.append(
            f'''      <article class="correction-entry" data-correction-for="{original['id']}" data-corrected-by="{replacement_id}">
        <div class="correction-meta"><time datetime="{original['correction_date']}">{long_date(original['correction_date'])}</time> · Material correction</div>
        <h2>{original['id']} → {replacement_id}</h2>
        <p><strong>What was wrong:</strong> {html.escape(original['correction_reason'])}</p>
        <p><strong>Effect on the conclusion:</strong> {html.escape(original['conclusion_impact'])}</p>
        <div class="actions">
          <a class="btn btn-solid" href="{html.escape(report_href(replacement))}">Read the corrected report</a>
          <a class="btn" href="{html.escape(report_href(original))}">View the superseded record</a>
        </div>
      </article>'''
        )
    return "\n".join(entries) or "      <p>No material corrections recorded.</p>"


def render_sitemap_publications(registry: dict) -> str:
    rows = []
    for item in registry["publications"]:
        if not item["indexable"]:
            continue
        priority = "0.9" if item["publication_status"] in {"active", "corrected"} else "0.5"
        rows.append(
            f"  <url><loc>{html.escape(item['canonical_url'])}</loc><lastmod>{item['modified_at']}</lastmod><priority>{priority}</priority></url>"
        )
    return "\n".join(rows)


def replace_block(source: str, marker: str, rendered: str) -> str:
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError(f"expected exactly one {marker} marker pair")
    before, remainder = source.split(start, 1)
    _, after = remainder.split(end, 1)
    return f"{before}{start}\n{rendered}\n{end}{after}"


def expected_surfaces(registry: dict, taxonomy: dict) -> dict[Path, str]:
    latest = max(
        (item for item in registry["publications"] if item["publication_status"] in {"active", "corrected"}),
        key=lambda item: (item["published_at"], item["id"]),
    )
    homepage_path = ROOT / "index.html"
    homepage = homepage_path.read_text(encoding="utf-8")
    homepage = replace_block(
        homepage,
        "LATEST-UTILITY",
        f'    <span data-latest-id="{latest["id"]}">Latest publication <strong><time datetime="{latest["published_at"]}">{long_date(latest["published_at"])}</time></strong> · Quality-gated release</span>',
    )
    homepage = replace_block(
        homepage,
        "LATEST-SNAPSHOT",
        f'              <dd data-latest-id="{latest["id"]}">{latest["id"]} · {short_date(latest["published_at"])}</dd>',
    )
    homepage = replace_block(homepage, "FEATURED-PUBLICATIONS", render_featured(registry))

    library_path = ROOT / "research" / "index.html"
    library = library_path.read_text(encoding="utf-8")
    visible = visible_publications(registry)
    library = replace_block(library, "PUBLICATION-COUNT", f'        <div class="iss">Table of contents · {len(visible)} entries</div>')
    library = replace_block(library, "PUBLICATION-LIST", render_library(registry))
    library = replace_block(library, "PUBLICATION-COUNT-NOTE", f'      <p class="count-note" id="count">Showing {len(visible)} entries</p>')
    library = replace_block(library, "EVIDENCE-GRADE-DEFINITIONS", render_grade_definitions(taxonomy))

    methodology_path = ROOT / "research" / "methodology.html"
    methodology = methodology_path.read_text(encoding="utf-8")
    methodology = replace_block(
        methodology,
        "EVIDENCE-GRADE-DEFINITIONS",
        render_grade_definitions(taxonomy, indent="          "),
    )

    corrections_path = ROOT / "corrections.html"
    corrections = corrections_path.read_text(encoding="utf-8")
    corrections = replace_block(corrections, "CORRECTION-LEDGER", render_corrections(registry))

    sitemap_path = ROOT / "sitemap.xml"
    sitemap = sitemap_path.read_text(encoding="utf-8")
    sitemap = replace_block(sitemap, "PUBLICATION-URLS", render_sitemap_publications(registry))

    return {
        homepage_path: homepage,
        library_path: library,
        methodology_path: methodology,
        corrections_path: corrections,
        sitemap_path: sitemap,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write rendered blocks")
    mode.add_argument("--check", action="store_true", help="fail if rendered blocks are stale")
    args = parser.parse_args()

    try:
        surfaces = expected_surfaces(load_registry(), load_taxonomy())
    except (KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"SURFACE RENDER: FAIL — {exc}")
        return 1

    stale = [path for path, expected in surfaces.items() if path.read_text(encoding="utf-8") != expected]
    if args.check:
        if stale:
            print("SURFACE RENDER: FAIL — stale generated blocks")
            for path in stale:
                print(f"- {path.relative_to(ROOT)}")
            return 1
        print(f"SURFACE RENDER: PASS ({len(surfaces)} surfaces current)")
        return 0

    for path, expected in surfaces.items():
        if path in stale:
            path.write_text(expected, encoding="utf-8")
            print(f"updated {path.relative_to(ROOT)}")
    print(f"SURFACE RENDER: PASS ({len(stale)} surfaces updated)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
