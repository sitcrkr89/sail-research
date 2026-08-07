from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SiteContractTests(unittest.TestCase):
    def run_validator(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(root / "scripts" / "validate_site.py")],
            cwd=root,
            capture_output=True,
            text=True,
        )

    def fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        for name in (
            "index.html", "product.html", "for.html", "about.html", "governance.html",
            "corrections.html", "scope.html", "digest.html", "sitemap.xml",
        ):
            shutil.copy2(ROOT / name, root / name)
        for directory in ("assets", "reports", "research", "scripts"):
            shutil.copytree(ROOT / directory, root / directory)
        (root / "ops").mkdir()
        shutil.copy2(ROOT / "ops" / "publications.json", root / "ops" / "publications.json")
        shutil.copy2(ROOT / "ops" / "editorial_taxonomy.json", root / "ops" / "editorial_taxonomy.json")
        shutil.copy2(ROOT / "ops" / "methodology_hbm_qualification.json", root / "ops" / "methodology_hbm_qualification.json")
        shutil.copy2(ROOT / "ops" / "methodology_assessments.json", root / "ops" / "methodology_assessments.json")
        return temp, root

    def mutate_and_fail(self, relative: str, old: str, new: str, expected: str) -> None:
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        path = root / relative
        source = path.read_text(encoding="utf-8")
        self.assertIn(old, source, f"test mutation anchor missing in {relative}")
        path.write_text(source.replace(old, new, 1), encoding="utf-8")
        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(expected, result.stdout)

    def test_current_site_passes(self) -> None:
        result = self.run_validator(ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_supersession_notice_fails(self) -> None:
        self.mutate_and_fail(
            "reports/20260727-wuxiui-patent-no-bleed-perfusion.html",
            ' data-superseded-by="SR-2026-0008-F"',
            "",
            "missing visible superseded-by notice",
        )

    def test_missing_reciprocal_edge_fails(self) -> None:
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        path = root / "ops" / "publications.json"
        registry = json.loads(path.read_text(encoding="utf-8"))
        replacement = next(item for item in registry["publications"] if item["id"] == "SR-2026-0008-F")
        replacement.pop("corrects")
        path.write_text(json.dumps(registry), encoding="utf-8")
        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("lacks reciprocal corrects edge", result.stdout)

    def test_invalid_grade_fails(self) -> None:
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        path = root / "ops" / "publications.json"
        registry = json.loads(path.read_text(encoding="utf-8"))
        registry["publications"][4]["evidence_strength"] = "A+"
        path.write_text(json.dumps(registry), encoding="utf-8")
        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid evidence_strength", result.stdout)

    def test_unknown_artifact_type_fails_closed(self) -> None:
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        path = root / "ops" / "publications.json"
        registry = json.loads(path.read_text(encoding="utf-8"))
        registry["publications"][-1]["artifact_type"] = "other"
        path.write_text(json.dumps(registry), encoding="utf-8")
        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid artifact_type", result.stdout)

    def test_unknown_analysis_tier_fails_closed(self) -> None:
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        path = root / "ops" / "publications.json"
        registry = json.loads(path.read_text(encoding="utf-8"))
        registry["publications"][-1]["analysis_tier"] = "other"
        path.write_text(json.dumps(registry), encoding="utf-8")
        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid analysis_tier", result.stdout)

    def test_registry_path_escape_fails_closed(self) -> None:
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        path = root / "ops" / "publications.json"
        registry = json.loads(path.read_text(encoding="utf-8"))
        registry["publications"][0]["path"] = "../outside.html"
        path.write_text(json.dumps(registry), encoding="utf-8")
        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsafe report path", result.stdout)

    def test_owner_review_hold_public_flags_fail_site_validation(self) -> None:
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        path = root / "ops" / "publications.json"
        registry = json.loads(path.read_text(encoding="utf-8"))
        entry = next(item for item in registry["publications"] if item["id"] == "SR-2026-0011")
        entry["library_visible"] = True
        entry["indexable"] = True
        path.write_text(json.dumps(registry), encoding="utf-8")
        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("owner review hold cannot be library-visible or indexable", result.stdout)

    def test_renderer_does_not_expose_unapproved_review_hold(self) -> None:
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        path = root / "ops" / "publications.json"
        registry = json.loads(path.read_text(encoding="utf-8"))
        entry = next(item for item in registry["publications"] if item["id"] == "SR-2026-0011")
        entry["library_visible"] = True
        entry["indexable"] = True
        entry["featured_rank"] = 4
        path.write_text(json.dumps(registry), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(root / "scripts" / "render_publication_surfaces.py"), "--check"],
            cwd=root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("SR-2026-0011", (root / "research" / "index.html").read_text(encoding="utf-8"))
        self.assertNotIn("20260805-sk-hynix", (root / "sitemap.xml").read_text(encoding="utf-8"))

    def test_review_hold_requires_exact_owner_review_status(self) -> None:
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        path = root / "ops" / "publications.json"
        registry = json.loads(path.read_text(encoding="utf-8"))
        entry = next(item for item in registry["publications"] if item["id"] == "SR-2026-0011")
        entry["analytical_quality"]["review_status"] = "approved"
        path.write_text(json.dumps(registry), encoding="utf-8")
        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("review_hold requires owner_review_required", result.stdout)

    def test_stale_homepage_latest_fails(self) -> None:
        registry = json.loads((ROOT / "ops" / "publications.json").read_text(encoding="utf-8"))
        visible = [item for item in registry["publications"] if item["library_visible"]]
        latest = max(visible, key=lambda item: (item["published_at"], item["id"]))
        self.mutate_and_fail(
            "index.html",
            f'data-latest-id="{latest["id"]}"',
            'data-latest-id="SR-2026-0009"',
            "latest publication markers do not match registry",
        )

    def test_missing_full_report_in_sitemap_fails(self) -> None:
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        path = root / "sitemap.xml"
        source = path.read_text(encoding="utf-8")
        line = next(line for line in source.splitlines() if "20260731-hbm4e-16h-qualification-race-full" in line)
        path.write_text(source.replace(line + "\n", "", 1), encoding="utf-8")
        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("URL set does not match", result.stdout)

    def test_wrong_canonical_fails(self) -> None:
        self.mutate_and_fail(
            "reports/20260729-agc-yokohama-gmp-readiness.html",
            "https://sitcrkr89.github.io/sail-research/reports/20260729-agc-yokohama-gmp-readiness.html",
            "https://sitcrkr89.github.io/sail-research/reports/wrong.html",
            "canonical must equal",
        )

    def test_malformed_jsonld_fails(self) -> None:
        self.mutate_and_fail(
            "reports/full/20260731-hbm4e-16h-qualification-race-full.html",
            '{"@context":"https://schema.org"',
            '{BROKEN',
            "malformed Article JSON-LD",
        )

    def test_unwrapped_table_fails(self) -> None:
        self.mutate_and_fail(
            "reports/full/20260731-hbm4e-16h-qualification-race-full.html",
            '<div class="table-scroll" role="region" aria-label="Scrollable report data table" tabindex="0"><table',
            "<table",
            "lack accessible scroll wrappers",
        )

    def test_mobile_hidden_navigation_regression_fails(self) -> None:
        self.mutate_and_fail(
            "assets/site.css",
            "@media (max-width: 720px) {",
            "@media (max-width: 720px) {\n  .nav a:not(.nav-cta):not(.nav-keep) { display: none; }",
            "mobile navigation still hides",
        )

    def test_low_contrast_hero_regression_fails(self) -> None:
        self.mutate_and_fail(
            "index.html",
            ".hero .btn-solid { background: #fff;",
            ".hero .btn-solid { background: var(--bg-elevated);",
            "low-contrast hero primary button regression",
        )

    def test_claim_state_enum_drift_fails(self) -> None:
        self.mutate_and_fail(
            "index.html",
            'data-claim-state="open_gap"',
            'data-claim-state="gap"',
            "claim-state demo does not exactly match canonical taxonomy",
        )

    def test_visible_grade_definition_drift_fails(self) -> None:
        self.mutate_and_fail(
            "research/methodology.html",
            '<div class="d">Every load-bearing conclusion is supported by at least two independent primary-source chains.</div>',
            '<div class="d">Any two sources are sufficient.</div>',
            "evidence-grade definitions do not exactly match taxonomy",
        )

    def test_archived_report_without_visible_notice_fails(self) -> None:
        self.mutate_and_fail(
            "reports/20260705-macbook-local-ai.html",
            ' data-archive-notice="legacy-2026-07"',
            "",
            "archived report lacks a visible legacy/not-regraded notice",
        )

    def test_evidence_a_without_marked_independence_statement_fails(self) -> None:
        self.mutate_and_fail(
            "reports/20260708-hbm-tech-tracking.html",
            ' data-independence-statement="cross-publisher"',
            "",
            "Evidence A requires a marked independence statement",
        )

    def test_svg_social_preview_regression_fails(self) -> None:
        self.mutate_and_fail(
            "about.html",
            "https://sitcrkr89.github.io/sail-research/assets/social-card.png",
            "https://sitcrkr89.github.io/sail-research/assets/social-card.svg",
            "og:image must use the canonical PNG social card",
        )

    def test_sampler_gate_contract_drift_fails(self) -> None:
        self.mutate_and_fail(
            "research/qualification-sampler.html",
            '"name": "Production execution"',
            '"name": "Production executions"',
            "embedded gates do not match",
        )

    def test_sampler_algorithm_modification_fails(self) -> None:
        self.mutate_and_fail(
            "research/qualification-sampler.html",
            "if (answers[j] !== 'yes') break;",
            "if (answers[j] !== 'no') break;",
            "pinned sampler algorithm was modified or duplicated",
        )

    def test_methodology_assessment_stance_is_recomputable(self) -> None:
        assessments = json.loads((ROOT / "ops" / "methodology_assessments.json").read_text(encoding="utf-8"))
        methodology = json.loads((ROOT / "ops" / "methodology_hbm_qualification.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(assessments["assessments"]), 2, "reproducibility requires at least two vendors")
        vendors = set()
        for item in assessments["assessments"]:
            self.assertEqual(item["methodology_id"], methodology["methodology_id"])
            self.assertEqual(item["methodology_version"], methodology["version"])
            self.assertFalse(item["method_modified"], "method modification breaks the replication claim")
            answers = [entry["answer"] for entry in item["gate_answers"]]
            self.assertEqual(len(answers), len(methodology["gates"]))
            self.assertEqual([entry["gate"] for entry in item["gate_answers"]], [gate["id"] for gate in methodology["gates"]])
            for entry, gate in zip(item["gate_answers"], methodology["gates"]):
                self.assertIn(entry["answer"], {"yes", "no", "unknown"})
                if entry["answer"] == "yes":
                    self.assertTrue(entry.get("source_ref"), f"{item['assessment_id']} {gate['id']}: yes answer requires a source reference")
            passed = 0
            for answer in answers:
                if answer != "yes":
                    break
                passed += 1
            expected = methodology["gates"][passed - 1]["stance_if_passed"] if passed else "MONITOR"
            self.assertEqual(item["stance"], expected, f"{item['assessment_id']}: declared stance not recomputable from gate answers")
            vendors.add(item["vendor"])
        self.assertGreaterEqual(len(vendors), 2)

    def test_methodology_assessment_stance_tampering_fails(self) -> None:
        self.mutate_and_fail(
            "ops/methodology_assessments.json",
            '"stance": "VALIDATE"',
            '"stance": "ALLOCATE"',
            "declared stance is not recomputable",
        )

    def test_methodology_assessment_unsourced_yes_fails(self) -> None:
        self.mutate_and_fail(
            "ops/methodology_assessments.json",
            '"gate": "G1", "answer": "yes", "basis": "dated sample-shipment disclosure at announcement scope", "source_ref": "SRC-SEC-HBM4E"',
            '"gate": "G1", "answer": "yes", "basis": "dated sample-shipment disclosure at announcement scope", "source_ref": ""',
            "yes answer requires a source reference",
        )

    def test_sampler_contract_and_paid_boundary(self) -> None:
        source = (ROOT / "research" / "qualification-sampler.html").read_text(encoding="utf-8")
        canonical = json.loads((ROOT / "ops" / "methodology_hbm_qualification.json").read_text(encoding="utf-8"))
        embedded = json.loads(source.split('id="methodology-data" type="application/json">')[1].split("</script>")[0])
        self.assertEqual(embedded["gates"], canonical["gates"])
        self.assertEqual(embedded["transfer_rules"], canonical["transfer_rules"])
        self.assertIn("preliminary stance", source.lower())
        self.assertNotIn("evidence audit trail", source.split('id="sampler-result"')[1].split('id="sampler-paid-cta"')[0])

    def test_archived_registry_entry_requires_archive_date(self) -> None:
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        path = root / "ops" / "publications.json"
        registry = json.loads(path.read_text(encoding="utf-8"))
        registry["publications"][0].pop("archived_at")
        path.write_text(json.dumps(registry), encoding="utf-8")
        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("archived publication missing archived_at", result.stdout)

    def test_unverified_human_approval_claim_fails(self) -> None:
        self.mutate_and_fail(
            "reports/20260713-hbm4-vendor-confirmed.html",
            "before release.",
            "before human approval.",
            "stale review claim 'before human approval'",
        )

    def test_evidence_a_requires_distinct_structured_source_chains(self) -> None:
        temp, root = self.fixture()
        self.addCleanup(temp.cleanup)
        path = root / "reports" / "20260713-hbm4-vendor-confirmed.html"
        source = path.read_text(encoding="utf-8")
        source = source.replace('data-source-chain="sk-hynix"', 'data-source-chain="samsung"')
        source = source.replace('data-source-chain="micron"', 'data-source-chain="samsung"')
        path.write_text(source, encoding="utf-8")
        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("at least two structured primary-source chains", result.stdout)


if __name__ == "__main__":
    unittest.main()
