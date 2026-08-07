#!/usr/bin/env python3
"""Deterministic, tier-specific analytical contract for Sail publications."""

from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_SECTIONS = {
    "decision-object",
    "evidence-boundary",
    "decision-implications",
    "watch-conditions",
}
REQUIRED_EXHIBITS = {"mechanism", "scenario"}
FORMULAIC_HEADINGS = {"what the official record establishes"}


class ContractParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.records: list[dict] = []
        self.body: dict[str, str] = {}
        self.headings: list[str] = []
        self.heading_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"h1", "h2", "h3"}:
            self.heading_depth += 1
        data = {key: value or "" for key, value in attrs}
        if tag == "body":
            self.body = data
        kinds: list[str] = []
        if data.get("id") in REQUIRED_SECTIONS:
            kinds.append("section")
        for attr, kind in (
            ("data-analytical-exhibit", "exhibit"),
            ("data-watch-condition", "watch"),
            ("data-claim-row", "claim"),
            ("data-absence-claim", "absence"),
        ):
            if attr in data:
                kinds.append(kind)
        if data.get("data-source-class") == "secondary":
            kinds.append("secondary")
        for kind in kinds:
            self.records.append({
                "kind": kind,
                "tag": tag,
                "attrs": data,
                "depth": len(self.stack),
                "open": True,
                "text": [],
            })
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
            self.stack.append(tag)

    def handle_data(self, data: str) -> None:
        if self.stack and self.stack[-1] in {"script", "style"}:
            return
        for record in self.records:
            heading_only = (
                record["kind"] in {"section", "exhibit"}
                and self.heading_depth > 0
            )
            if record["open"] and not heading_only:
                record["text"].append(data)
        if self.heading_depth > 0:
            self.headings.append(data)

    def handle_endtag(self, tag: str) -> None:
        if not self.stack:
            return
        closing_depth = len(self.stack) - 1
        for record in self.records:
            if record["open"] and record["tag"] == tag and record["depth"] == closing_depth:
                record["open"] = False
        self.stack.pop()
        if tag in {"h1", "h2", "h3"}:
            self.heading_depth -= 1


def visible_text(record: dict) -> str:
    return " ".join("".join(record["text"]).split())


def registry_entry(path: Path) -> tuple[dict, dict, str]:
    registry = json.loads((ROOT / "ops/publications.json").read_text(encoding="utf-8"))
    taxonomy = json.loads((ROOT / "ops/editorial_taxonomy.json").read_text(encoding="utf-8"))
    relative = str(path.relative_to(ROOT))
    matches = [item for item in registry["publications"] if item["path"] == relative]
    if len(matches) != 1:
        raise ValueError("report must map to exactly one registry entry")
    return matches[0], taxonomy, relative


def check_report(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        entry, taxonomy, relative = registry_entry(path)
    except (KeyError, ValueError, json.JSONDecodeError) as exc:
        return [f"{path}: {exc}"], warnings
    if entry.get("analysis_tier") != "analyst_brief":
        return [f"{relative}: analysis gate requires analysis_tier analyst_brief"], warnings
    publication_status = entry.get("publication_status")
    if publication_status not in taxonomy.get("publication_status", {}):
        return [f"{relative}: invalid publication status"], warnings
    review_status = entry.get("analytical_quality", {}).get("review_status")
    if review_status not in {"owner_review_required", "approved"}:
        errors.append(f"{relative}: invalid analytical review status")
    if review_status != "approved" and (entry.get("library_visible") or entry.get("indexable")):
        errors.append(f"{relative}: owner review hold cannot be library-visible or indexable")
    if review_status == "owner_review_required" and publication_status != "review_hold":
        errors.append(f"{relative}: owner_review_required requires review_hold")
    if publication_status == "review_hold" and review_status != "owner_review_required":
        errors.append(f"{relative}: review_hold requires owner_review_required")
    if publication_status not in {"active", "corrected", "review_hold"}:
        return errors, warnings

    parser = ContractParser()
    parser.feed(path.read_text(encoding="utf-8"))
    if parser.body.get("data-analysis-tier") != entry["analysis_tier"]:
        errors.append(f"{relative}: body analysis tier does not match registry")
    stance = entry.get("decision_stance")
    if stance not in taxonomy.get("decision_stance", {}):
        errors.append(f"{relative}: invalid or missing decision stance")
    if parser.body.get("data-decision-stance") != stance:
        errors.append(f"{relative}: body decision stance does not match registry")
    sections = [record for record in parser.records if record["kind"] == "section"]
    for section_id in sorted(REQUIRED_SECTIONS):
        matches = [record for record in sections if record["attrs"].get("id") == section_id]
        if len(matches) != 1:
            errors.append(f"{relative}: missing {section_id} section")
        elif not visible_text(matches[0]):
            errors.append(f"{relative}: {section_id} section is empty")

    exhibits = {
        record["attrs"].get("data-analytical-exhibit")
        for record in parser.records
        if record["kind"] == "exhibit" and visible_text(record)
    }
    for exhibit in sorted(REQUIRED_EXHIBITS - exhibits):
        errors.append(f"{relative}: missing analytical exhibit: {exhibit}")

    watches = [record for record in parser.records if record["kind"] == "watch"]
    if not watches or any(
        not record["attrs"].get("data-trigger")
        or not record["attrs"].get("data-decision-impact")
        or not visible_text(record)
        for record in watches
    ):
        errors.append(f"{relative}: watch conditions require visible trigger and decision impact")

    allowed_claim_states = set(taxonomy.get("claim_state", {}))
    claims = [record for record in parser.records if record["kind"] == "claim"]
    if not claims:
        errors.append(f"{relative}: missing structured claim/evidence rows")
    for record in claims:
        attrs = record["attrs"]
        state = attrs.get("data-claim-state")
        if state not in allowed_claim_states:
            errors.append(f"{relative}: invalid claim state in analytical evidence row")
        if not attrs.get("data-source-ref") and state != "open_gap":
            errors.append(f"{relative}: analytical evidence row lacks source reference")
        if not visible_text(record):
            errors.append(f"{relative}: empty analytical evidence row")

    for record in (r for r in parser.records if r["kind"] == "absence"):
        if not record["attrs"].get("data-corpus-boundary") or not visible_text(record):
            errors.append(f"{relative}: absence claim requires a visible corpus-boundary statement")
    for record in (r for r in parser.records if r["kind"] == "secondary"):
        attrs = record["attrs"]
        if attrs.get("data-claim-scope") == "underlying-event" and attrs.get("data-claim-state") == "verified":
            errors.append(f"{relative}: secondary source cannot verify an underlying-event claim")

    headings = {" ".join(text.split()).lower() for text in parser.headings}
    if headings & FORMULAIC_HEADINGS:
        warnings.append(f"formulaic heading — {relative}")
    return errors, warnings


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: preflight_analysis.py <analyst-brief.html> [more reports...]", file=sys.stderr)
        return 2
    errors: list[str] = []
    warnings: list[str] = []
    for raw in sys.argv[1:]:
        path = Path(raw)
        path = path if path.is_absolute() else ROOT / path
        if not path.exists():
            errors.append(f"{raw}: file not found")
            continue
        report_errors, report_warnings = check_report(path)
        errors.extend(report_errors)
        warnings.extend(report_warnings)
    for warning in warnings:
        print(f"EDITORIAL WARNING: {warning}")
    if errors:
        print("ANALYSIS PREFLIGHT: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"ANALYSIS PREFLIGHT: PASS ({len(sys.argv) - 1} analyst brief(s) gated)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
