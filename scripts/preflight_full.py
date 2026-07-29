#!/usr/bin/env python3
"""Pre-publish quality gate for Sail Research FULL reports (SR-2026-NNNN-F).

Deep-report contract per Sail-Holdings
docs/superpowers/specs/2026-07-29-wuxiui-deep-report-design.md: required deep
sections, evidence matrix, original analysis, retrieval-dated sources, dated
verification status, update history. Also runs scripts/validate_site.py
unless --no-site. Exit 0 only when every check passes; a failing report must
NOT be pushed.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

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

REPORT_NAME = re.compile(r"^20\d{6}-[a-z0-9]+(?:-[a-z0-9]+)*-full\.html$")
SR_ID = re.compile(r"SR-2026-\d{4}-F")
RETRIEVED = re.compile(r"Retrieved 20\d{2}-\d{2}-\d{2}")

REQUIRED_MARKERS = {
    'class="chip grade"': "evidence-grade chip",
    'class="box caveat"': "evidence caveat box",
    'id="evidence-matrix"': "evidence matrix",
    'id="original-analysis"': "original-analysis section",
    'id="benchmark"': "benchmark comparison section",
    'id="what-breaks"': "what-breaks-this-thesis section",
    'id="verification-status"': "dated verification-status block",
    'id="methodology"': "methodology & reproducibility section",
    'id="update-history"': "update-history block",
}


def check_report(path: Path) -> list[str]:
    errors: list[str] = []
    rel = path.relative_to(ROOT) if path.is_absolute() else path
    if path.parent.name != "full" or path.parent.parent.name != "reports":
        errors.append(f"{rel}: full report must live under reports/full/")
    if not REPORT_NAME.match(path.name):
        errors.append(f"{rel}: filename must be YYYYMMDD-<slug>-full.html")
    source = path.read_text(encoding="utf-8")

    if "FILL:" in source or "<!-- FILL" in source:
        errors.append(f"{rel}: unfilled template marker remains")

    ids = set(SR_ID.findall(source))
    if len(ids) != 1:
        errors.append(f"{rel}: expected exactly one distinct SR-2026-NNNN-F id, found {sorted(ids) or 'none'}")
    else:
        sr_id = next(iter(ids))
        for other in sorted((ROOT / "reports" / "full").glob("2026*.html")):
            if other != path and sr_id in other.read_text(encoding="utf-8"):
                errors.append(f"{rel}: {sr_id} already used by {other.name}")

    for marker, label in REQUIRED_MARKERS.items():
        if marker not in source:
            errors.append(f"{rel}: missing {label}")

    matrix = re.search(r'<table[^>]*id="evidence-matrix"[^>]*>(.*?)</table>', source, re.S)
    if matrix is None:
        errors.append(f"{rel}: evidence matrix must be a <table> carrying id=\"evidence-matrix\"")
    elif matrix.group(1).count("<tr") - 1 < 2:
        errors.append(f"{rel}: evidence matrix must list at least 2 claim rows")

    sources_match = re.search(r"<h2>Sources.*?</h2>\s*<ul>(.*?)</ul>", source, re.S)
    if not sources_match:
        errors.append(f"{rel}: missing Sources box")
        source_items: list[str] = []
    else:
        source_items = re.findall(r"<li>", sources_match.group(1))
        if not source_items:
            errors.append(f"{rel}: Sources box lists no sources")
    if not RETRIEVED.search(source):
        errors.append(f"{rel}: sources must carry retrieval dates (Retrieved YYYY-MM-DD)")

    body_lower = source.lower()
    for phrase in FORBIDDEN_LANGUAGE:
        if phrase in body_lower:
            errors.append(f"{rel}: forbidden language: {phrase!r}")

    grade_match = re.search(r'class="chip grade"[^>]*>([^<]*)<', source)
    grade_text = grade_match.group(1) if grade_match else ""
    if re.search(r"\bA\b", grade_text):
        if len(source_items) < 2:
            errors.append(f"{rel}: Evidence A requires at least 2 sources, found {len(source_items)}")
        if "independent" not in body_lower:
            errors.append(f"{rel}: Evidence A requires an explicit independent-source statement")
    return errors


def main() -> int:
    argv = sys.argv[1:]
    run_site = "--no-site" not in argv
    args = [Path(a) for a in argv if a != "--no-site"]
    if not args:
        print("usage: preflight_full.py [--no-site] <report.html> [more reports...]", file=sys.stderr)
        return 2
    errors: list[str] = []
    for arg in args:
        path = arg if arg.is_absolute() else ROOT / arg
        if not path.exists():
            errors.append(f"{arg}: file not found")
            continue
        errors.extend(check_report(path))

    if run_site:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_site.py")],
            capture_output=True,
            text=True,
        )
        sys.stdout.write(result.stdout)
        if result.returncode != 0:
            errors.append("validate_site.py failed (see output above)")

    if errors:
        print("PREFLIGHT-FULL: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PREFLIGHT-FULL: PASS ({len(args)} report(s) gated)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
