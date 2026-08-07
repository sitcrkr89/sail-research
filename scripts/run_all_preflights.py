#!/usr/bin/env python3
"""Run status-aware editorial preflight against every registered publication."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(script: str, paths: list[str]) -> int:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script), *paths],
        cwd=ROOT,
        text=True,
    )
    return result.returncode


def main() -> int:
    registry = json.loads((ROOT / "ops" / "publications.json").read_text(encoding="utf-8"))
    taxonomy = json.loads((ROOT / "ops" / "editorial_taxonomy.json").read_text(encoding="utf-8"))
    allowed_artifacts = set(taxonomy.get("artifact_type", {}))
    allowed_tiers = set(taxonomy.get("analysis_tier", {}))
    for item in registry.get("publications", []):
        path = Path(item["path"])
        allowed_shape = (
            (len(path.parts) == 2 and path.parts[0] == "reports")
            or (len(path.parts) == 3 and path.parts[:2] == ("reports", "full"))
        )
        if path.is_absolute() or ".." in path.parts or not allowed_shape:
            print(f"ALL PREFLIGHTS: FAIL — unsafe registry path {item['path']!r}")
            return 1
        if item.get("artifact_type") not in allowed_artifacts or item.get("analysis_tier") not in allowed_tiers:
            print(f"ALL PREFLIGHTS: FAIL — unknown publication routing for {item.get('id')}")
            return 1
    briefs = [item["path"] for item in registry["publications"] if item["artifact_type"] == "brief"]
    full = [item["path"] for item in registry["publications"] if item["artifact_type"] == "full_report"]
    analytical = [item["path"] for item in registry["publications"] if item["analysis_tier"] == "analyst_brief"]
    if len(briefs) + len(full) != len(registry["publications"]):
        print("ALL PREFLIGHTS: FAIL — every publication must route to exactly one editorial gate")
        return 1
    failures = 0
    failures += run("preflight_publish.py", ["--no-site", *briefs]) != 0
    failures += run("preflight_full.py", ["--no-site", *full]) != 0
    failures += run("render_publication_surfaces.py", ["--check"]) != 0
    failures += run("sync_report_metadata.py", ["--check"]) != 0
    failures += run("validate_site.py", []) != 0
    if failures:
        print(f"ALL PREFLIGHTS: FAIL ({failures} gate group(s) failed)")
        return 1
    print(f"ALL PREFLIGHTS: PASS ({len(briefs)} briefs, {len(full)} full reports, {len(analytical)} analyst briefs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
