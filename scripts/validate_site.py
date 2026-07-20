#!/usr/bin/env python3
"""Dependency-free publication checks for the Sail Research static site."""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PAGES = [ROOT / "index.html", ROOT / "research/index.html", ROOT / "research/methodology.html"]
PUBLIC_PAGES += sorted((ROOT / "reports").glob("2026*.html"))
LEGACY_METADATA_EXEMPT = {Path("research/methodology.html")}


class PageParser(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.h1 = 0
        self.h2_depth = 0
        self.empty_h2 = 0
        self.hrefs: list[str] = []
        self.canonical = False
        self.description = False
        self.og_title = False
        self.in_h2 = False
        self.h2_text: list[str] = []
        self.stack: list[str] = []
        self.structure_errors = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if tag not in self.VOID:
            self.stack.append(tag)
        if tag == "h1":
            self.h1 += 1
        elif tag == "h2":
            if self.in_h2:
                self.h2_depth += 1
            self.in_h2 = True
            self.h2_text = []
        elif tag == "a" and data.get("href"):
            self.hrefs.append(data["href"] or "")
        elif tag == "link" and data.get("rel") == "canonical":
            self.canonical = bool(data.get("href"))
        elif tag == "meta" and data.get("name") == "description":
            self.description = bool(data.get("content"))
        elif tag == "meta" and data.get("property") == "og:title":
            self.og_title = bool(data.get("content"))

    def handle_data(self, data: str) -> None:
        if self.in_h2:
            self.h2_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "h2" and self.in_h2:
            if not "".join(self.h2_text).strip():
                self.empty_h2 += 1
            self.in_h2 = False
        if tag in self.VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.structure_errors += 1
            return
        self.stack.pop()


def local_target(page: Path, href: str) -> Path | None:
    parsed = urlparse(href)
    if parsed.scheme or href.startswith(("#", "//", "mailto:", "tel:")):
        return None
    path = unquote(parsed.path)
    if not path:
        return page
    target = (page.parent / path).resolve()
    if target.is_dir():
        target /= "index.html"
    return target


def main() -> int:
    errors: list[str] = []
    for page in PUBLIC_PAGES:
        source = page.read_text(encoding="utf-8")
        parser = PageParser()
        parser.feed(source)
        rel = page.relative_to(ROOT)

        if parser.h1 != 1:
            errors.append(f"{rel}: expected exactly one h1, found {parser.h1}")
        if not parser.description:
            errors.append(f"{rel}: missing meta description")
        if rel not in LEGACY_METADATA_EXEMPT:
            if not parser.canonical:
                errors.append(f"{rel}: missing canonical URL")
            if not parser.og_title:
                errors.append(f"{rel}: missing Open Graph title")
        if parser.h2_depth:
            errors.append(f"{rel}: nested h2 detected")
        if parser.empty_h2:
            errors.append(f"{rel}: empty h2 detected")
        if parser.structure_errors or parser.stack:
            errors.append(f"{rel}: unbalanced HTML structure detected")
        if re.search(r"(?<!&)mdash;", source):
            errors.append(f"{rel}: literal mdash artifact detected")

        for href in parser.hrefs:
            target = local_target(page, href)
            if target is not None and ROOT not in target.parents and target != ROOT:
                errors.append(f"{rel}: local link escapes repository: {href}")
            elif target is not None and not target.exists():
                errors.append(f"{rel}: broken local link: {href}")

        if page.parent.name == "reports" and "../research/index.html" not in parser.hrefs:
            errors.append(f"{rel}: missing valid report-library return link")

    library = (ROOT / "research/index.html").read_text(encoding="utf-8")
    card_count = len(re.findall(r'<a class="r-card"', library))
    count_match = re.search(r'id="count"[^>]*>Showing (\d+) reports?', library)
    declared_count = int(count_match.group(1)) if count_match else -1
    if card_count != declared_count:
        errors.append(f"research/index.html: {card_count} cards but declared count is {declared_count}")

    if errors:
        print("SITE QA: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"SITE QA: PASS ({len(PUBLIC_PAGES)} pages, {card_count} report cards)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
