from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = Path("reports/20260805-sk-hynix-hbm4e-sample-shipment.html")


class AnalysisQualityContractTests(unittest.TestCase):
    def fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory(prefix="sail-analysis-contract-")
        root = Path(temp.name)
        (root / "scripts").mkdir()
        (root / "ops").mkdir()
        (root / "reports").mkdir()
        for relative in (
            Path("scripts/preflight_analysis.py"),
            Path("ops/publications.json"),
            Path("ops/editorial_taxonomy.json"),
            REPORT,
        ):
            source = ROOT / relative
            self.assertTrue(source.exists(), f"required analysis-contract artifact missing: {relative}")
            shutil.copy2(source, root / relative)
        return temp, root

    def run_gate(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(root / "scripts" / "preflight_analysis.py"), str(REPORT)],
            cwd=root,
            capture_output=True,
            text=True,
        )

    def mutate_report_and_fail(self, old: str, new: str, expected: str) -> None:
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        path = root / REPORT
        source = path.read_text(encoding="utf-8")
        self.assertIn(old, source, "mutation anchor missing from Golden Analyst Brief")
        path.write_text(source.replace(old, new, 1), encoding="utf-8")
        result = self.run_gate(root)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(expected, result.stdout)

    def mutate_report(self, old: str, new: str) -> subprocess.CompletedProcess[str]:
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        path = root / REPORT
        source = path.read_text(encoding="utf-8")
        self.assertIn(old, source, "mutation anchor missing from Golden Analyst Brief")
        path.write_text(source.replace(old, new, 1), encoding="utf-8")
        return self.run_gate(root)

    def test_taxonomy_defines_analysis_tiers_and_decision_stances(self) -> None:
        taxonomy = json.loads((ROOT / "ops" / "editorial_taxonomy.json").read_text(encoding="utf-8"))
        self.assertEqual(
            set(taxonomy["analysis_tier"]),
            {"legacy_brief", "signal_note", "analyst_brief", "full_report"},
        )
        self.assertEqual(
            set(taxonomy["decision_stance"]),
            {"MONITOR", "VALIDATE", "PILOT", "QUALIFY", "ALLOCATE", "HEDGE", "AVOID"},
        )

    def test_latest_hbm_is_registered_as_flagship_analyst_brief(self) -> None:
        registry = json.loads((ROOT / "ops" / "publications.json").read_text(encoding="utf-8"))
        entry = next(item for item in registry["publications"] if item["id"] == "SR-2026-0011")
        self.assertEqual(entry["analysis_tier"], "analyst_brief")
        self.assertEqual(entry["decision_stance"], "VALIDATE")
        self.assertEqual(entry["publication_status"], "review_hold")
        quality = entry["analytical_quality"]
        self.assertEqual(quality["gate_basis"], "binary_contract")
        self.assertEqual(quality["review_status"], "owner_review_required")
        self.assertFalse(entry["library_visible"])
        self.assertFalse(entry["indexable"])

    def test_analysis_gate_accepts_golden_brief(self) -> None:
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        result = self.run_gate(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ANALYSIS PREFLIGHT: PASS", result.stdout)

    def test_missing_decision_object_fails_closed(self) -> None:
        self.mutate_report_and_fail('id="decision-object"', 'id="decision-object-missing"', "missing decision-object section")

    def test_heading_only_decision_object_fails_closed(self) -> None:
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        path = root / REPORT
        source = path.read_text(encoding="utf-8")
        mutated, count = re.subn(
            r'<section id="decision-object"><h2>.*?</h2>.*?</section>',
            r'<section id="decision-object"><h2><span>Decision object</span></h2></section>',
            source,
            count=1,
            flags=re.S,
        )
        self.assertEqual(count, 1, "decision-object mutation anchor missing")
        path.write_text(mutated, encoding="utf-8")
        result = self.run_gate(root)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("decision-object section is empty", result.stdout)

    def test_heading_only_analytical_exhibit_fails_closed(self) -> None:
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        path = root / REPORT
        source = path.read_text(encoding="utf-8")
        mutated, count = re.subn(
            r'(<section data-analytical-exhibit="scenario"><h2>.*?</h2>).*?</section>',
            r"\1</section>",
            source,
            count=1,
            flags=re.S,
        )
        self.assertEqual(count, 1, "analytical-exhibit mutation anchor missing")
        path.write_text(mutated, encoding="utf-8")
        result = self.run_gate(root)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("missing analytical exhibit: scenario", result.stdout)

    def test_owner_review_hold_cannot_be_public(self) -> None:
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        registry_path = root / "ops" / "publications.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        entry = next(item for item in registry["publications"] if item["id"] == "SR-2026-0011")
        entry["library_visible"] = True
        registry_path.write_text(json.dumps(registry), encoding="utf-8")
        result = self.run_gate(root)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("owner review hold cannot be library-visible or indexable", result.stdout)

    def test_archived_owner_review_hold_cannot_bypass_public_gate(self) -> None:
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        registry_path = root / "ops" / "publications.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        entry = next(item for item in registry["publications"] if item["id"] == "SR-2026-0011")
        entry["publication_status"] = "archived"
        entry["indexable"] = True
        registry_path.write_text(json.dumps(registry), encoding="utf-8")
        result = self.run_gate(root)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("owner review hold cannot be library-visible or indexable", result.stdout)

    def test_unknown_publication_status_fails_analysis_gate(self) -> None:
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        registry_path = root / "ops" / "publications.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        entry = next(item for item in registry["publications"] if item["id"] == "SR-2026-0011")
        entry["publication_status"] = "unknown_status"
        registry_path.write_text(json.dumps(registry), encoding="utf-8")
        result = self.run_gate(root)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("invalid publication status", result.stdout)

    def test_analyst_brief_requires_two_analytical_exhibits(self) -> None:
        self.mutate_report_and_fail(
            'data-analytical-exhibit="scenario"',
            'data-nonanalytical-exhibit="scenario"',
            "missing analytical exhibit: scenario",
        )

    def test_unbounded_absence_claim_fails_closed(self) -> None:
        self.mutate_report_and_fail(
            'data-corpus-boundary="reviewed-source-set"',
            'data-corpus-boundary-removed="reviewed-source-set"',
            "absence claim requires a visible corpus-boundary statement",
        )

    def test_secondary_source_cannot_verify_underlying_event(self) -> None:
        self.mutate_report_and_fail(
            'data-source-class="secondary" data-claim-state="attributed" data-claim-scope="underlying-event"',
            'data-source-class="secondary" data-claim-state="verified" data-claim-scope="underlying-event"',
            "secondary source cannot verify an underlying-event claim",
        )

    def test_formulaic_heading_is_warning_not_hard_failure(self) -> None:
        result = self.mutate_report(
            "<h2>What changed</h2>",
            "<h2>What the official record establishes</h2>",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("EDITORIAL WARNING: formulaic heading", result.stdout)

    def test_signal_and_analyst_templates_are_distinct(self) -> None:
        signal = ROOT / "reports" / "_TEMPLATE_SIGNAL.html"
        analyst = ROOT / "reports" / "_TEMPLATE_ANALYST_BRIEF.html"
        self.assertTrue(signal.exists())
        self.assertTrue(analyst.exists())
        self.assertIn('data-analysis-tier="signal_note"', signal.read_text(encoding="utf-8"))
        self.assertIn('data-analysis-tier="analyst_brief"', analyst.read_text(encoding="utf-8"))

    def test_grouped_preflight_runs_global_site_checks_once(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "run_all_preflights.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.count("SITE QA: PASS"), 1, result.stdout)
        self.assertEqual(result.stdout.count("SURFACE RENDER: PASS"), 1, result.stdout)
        self.assertEqual(result.stdout.count("REPORT METADATA: PASS"), 1, result.stdout)


if __name__ == "__main__":
    unittest.main()
