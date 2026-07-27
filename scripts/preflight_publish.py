#!/usr/bin/env python3
"""Pre-publish quality gate for the delegated Sail Research publish pipeline.

Runs the existing site-wide publication contract (scripts/validate_site.py)
plus per-report editorial gates on the draft files passed as arguments.
Exit 0 only when every check passes; a failing report must NOT be pushed.

Owner authorization: Sail-Holdings docs/AUTHORIZATIONS.md AUTH-2026-07-27-03.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

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
SR_ID = re.compile(r"SR-2026-\d{4}")


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
    ids = set(SR_ID.findall(source))
    if len(ids) != 1:
        errors.append(f"{rel}: expected exactly one distinct SR-2026-NNNN id, found {sorted(ids) or 'none'}")
    else:
        sr_id = next(iter(ids))
        for other in sorted((ROOT / "reports").glob("2026*.html")):
            if other != path and sr_id in other.read_text(encoding="utf-8"):
                errors.append(f"{rel}: {sr_id} already used by {other.name}")
    if 'class="chip grade"' not in source:
        errors.append(f"{rel}: missing evidence-grade chip")
    if 'class="box caveat"' not in source:
        errors.append(f"{rel}: missing evidence caveat box")
    sources_match = re.search(r"<h2>Sources.*?</h2>\s*<ul>(.*?)</ul>", source, re.S)
    if not sources_match:
        errors.append(f"{rel}: missing Sources box")
        source_items: list[str] = []
    else:
        source_items = re.findall(r"<li>", sources_match.group(1))
        if not source_items:
            errors.append(f"{rel}: Sources box lists no sources")

    body_lower = source.lower()
    for phrase in FORBIDDEN_LANGUAGE:
        if phrase in body_lower:
            errors.append(f"{rel}: forbidden language: {phrase!r}")

    grade_match = re.search(r'class="chip grade"[^>]*>([^<]*)<', source)
    grade_text = grade_match.group(1) if grade_match else ""
    if re.search(r"\bA\b", grade_text):
        # Evidence A requires at least two sources and an explicit independence claim.
        if len(source_items) < 2:
            errors.append(f"{rel}: Evidence A requires at least 2 sources, found {len(source_items)}")
        if "independent" not in body_lower:
            errors.append(f"{rel}: Evidence A requires an explicit independent-source statement")
    return errors


def main() -> int:
    args = [Path(a) for a in sys.argv[1:]]
    if not args:
        print("usage: preflight_publish.py <report.html> [more reports...]", file=sys.stderr)
        return 2
    errors: list[str] = []
    for arg in args:
        path = arg if arg.is_absolute() else ROOT / arg
        if not path.exists():
            errors.append(f"{arg}: file not found")
            continue
        errors.extend(check_report(path))

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
