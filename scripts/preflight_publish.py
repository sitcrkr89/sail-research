#!/usr/bin/env python3
"""Pre-publish quality gate for the delegated Sail Research publish pipeline.

Runs the existing site-wide publication contract (scripts/validate_site.py)
plus per-report editorial gates on the draft files passed as arguments.
Exit 0 only when every check passes; a failing report must NOT be pushed.

Owner authorization: Sail-Holdings docs/AUTHORIZATIONS.md AUTH-2026-07-27-03.
"""

from __future__ import annotations

import html
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]

# Hype / overclaim language that must never appear in a published report body.
# Tuned to avoid false positives on quoted source material markers.
FORBIDDEN_LANGUAGE = [
    "game-changer",
    "game changer",
    "revolutionary",
    "guaranteed",
    "guarantee returns",
    "breakthrough that changes everything",
    "disruptive innovation will",
    "can't miss",
    "cannot miss",
    "once-in-a-lifetime",
    "skyrocket",
    "to the moon",
    "massive upside",
    "sure thing",
]

REPORT_NAME = re.compile(r"^20\d{6}-[a-z0-9]+(?:-[a-z0-9]+)*\.html$")
PRIMARY_ID = re.compile(r'data-publication-id="(SR-2026-\d{4})"')


def source_chain_hosts(sources_html: str) -> set[str]:
    hosts: set[str] = set()
    for href in re.findall(r'href="(https?://[^"]+)"', sources_html):
        hostname = urlparse(html.unescape(href)).hostname
        if hostname:
            hosts.add(hostname.lower().removeprefix("www."))
    return hosts


def primary_source_chains(sources_html: str) -> set[str]:
    chains: set[str] = set()
    for attributes in re.findall(r"<li([^>]*)>", sources_html):
        if not re.search(r'data-source-class="primary"', attributes):
            continue
        match = re.search(r'data-source-chain="([^"]+)"', attributes)
        if match:
            chains.add(match.group(1))
    return chains


def registry_entry(path: Path) -> dict | None:
    data = json.loads((ROOT / "ops" / "publications.json").read_text(encoding="utf-8"))
    rel = str(path.relative_to(ROOT))
    return next((item for item in data["publications"] if item["path"] == rel), None)


def check_report(path: Path) -> list[str]:
    errors: list[str] = []
    rel = path.relative_to(ROOT) if path.is_absolute() else path
    if path.parent.name != "reports":
        errors.append(f"{rel}: report must live under reports/")
    if not REPORT_NAME.match(path.name):
        errors.append(f"{rel}: filename must be YYYYMMDD-<slug>.html")
    source = path.read_text(encoding="utf-8")

    if "FILL:" in source or "<!-- FILL" in source:
        errors.append(f"{rel}: unfilled template marker remains")
    ids = PRIMARY_ID.findall(source)
    entry = registry_entry(path)
    if entry is None:
        errors.append(f"{rel}: report is not registered in ops/publications.json")
    if len(ids) != 1:
        errors.append(f"{rel}: expected exactly one primary data-publication-id, found {ids or 'none'}")
    elif entry is not None and ids[0] != entry["id"]:
        errors.append(f"{rel}: primary id {ids[0]} does not match registry id {entry['id']}")

    if entry is not None and entry["publication_status"] in {"archived", "superseded"}:
        status = entry["publication_status"]
        if f'data-publication-status="{status}"' not in source:
            errors.append(f"{rel}: body status does not match registry")
        if status == "superseded":
            if 'name="robots" content="noindex,follow"' not in source:
                errors.append(f"{rel}: superseded report must be noindex,follow")
            if f'data-superseded-by="{entry["superseded_by"]}"' not in source:
                errors.append(f"{rel}: superseded report lacks replacement notice")
        return errors
    if 'class="chip grade"' not in source:
        errors.append(f"{rel}: missing evidence-grade chip")
    if 'class="box caveat"' not in source:
        errors.append(f"{rel}: missing evidence caveat box")
    sources_match = re.search(r"<h2>Sources.*?</h2>\s*<ul>(.*?)</ul>", source, re.S)
    if not sources_match:
        errors.append(f"{rel}: missing Sources box")
        source_items: list[str] = []
        source_hosts: set[str] = set()
        source_chains: set[str] = set()
    else:
        source_items = re.findall(r"<li(?:\s[^>]*)?>", sources_match.group(1))
        source_hosts = source_chain_hosts(sources_match.group(1))
        source_chains = primary_source_chains(sources_match.group(1))
        if not source_items:
            errors.append(f"{rel}: Sources box lists no sources")

    body_lower = source.lower()
    for phrase in FORBIDDEN_LANGUAGE:
        if phrase in body_lower:
            errors.append(f"{rel}: forbidden language: {phrase!r}")

    grade_attr = re.search(r'class="chip grade"[^>]*data-evidence-strength="([^"]+)"', source)
    if entry is not None and (not grade_attr or grade_attr.group(1) != entry["evidence_strength"]):
        errors.append(f"{rel}: evidence-strength metadata does not match registry")
    if entry is not None and entry["evidence_strength"] == "A":
        # Evidence A requires a marked statement plus distinct primary publisher hosts.
        if len(source_items) < 2:
            errors.append(f"{rel}: Evidence A requires at least 2 sources, found {len(source_items)}")
        if len(source_hosts) < 2:
            errors.append(f"{rel}: Evidence A requires at least two distinct primary-source hosts")
        if len(source_chains) < 2:
            errors.append(f"{rel}: Evidence A requires at least two structured primary-source chains")
        statement = re.search(
            r'<p[^>]*data-independence-statement="[^"]+"[^>]*>(.*?)</p>', source, re.S
        )
        statement_text = (
            html.unescape(re.sub(r"<[^>]+>", "", statement.group(1))).lower()
            if statement else ""
        )
        if "independent" not in statement_text:
            errors.append(f"{rel}: Evidence A requires a marked independence statement")
    return errors


def main() -> int:
    argv = sys.argv[1:]
    run_site = "--no-site" not in argv
    args = [Path(a) for a in argv if a != "--no-site"]
    if not args:
        print("usage: preflight_publish.py [--no-site] <report.html> [more reports...]", file=sys.stderr)
        return 2
    errors: list[str] = []
    for arg in args:
        path = arg if arg.is_absolute() else ROOT / arg
        if not path.exists():
            errors.append(f"{arg}: file not found")
            continue
        errors.extend(check_report(path))

    analytical = []
    for arg in args:
        path = arg if arg.is_absolute() else ROOT / arg
        if path.exists():
            entry = registry_entry(path)
            if entry and entry.get("analysis_tier") == "analyst_brief":
                analytical.append(str(path.relative_to(ROOT)))
    if analytical:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "preflight_analysis.py"), *analytical],
            capture_output=True,
            text=True,
        )
        sys.stdout.write(result.stdout)
        if result.returncode != 0:
            errors.append("preflight_analysis.py failed (see output above)")

    if run_site:
        for script, flag in (
            ("render_publication_surfaces.py", "--check"),
            ("sync_report_metadata.py", "--check"),
        ):
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / script), flag],
                capture_output=True,
                text=True,
            )
            sys.stdout.write(result.stdout)
            if result.returncode != 0:
                errors.append(f"{script} failed (see output above)")
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_site.py")],
            capture_output=True,
            text=True,
        )
        sys.stdout.write(result.stdout)
        if result.returncode != 0:
            errors.append("validate_site.py failed (see output above)")

    if errors:
        print("PREFLIGHT: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PREFLIGHT: PASS ({len(args)} report(s) gated)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
