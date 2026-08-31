#!/usr/bin/env python3
"""Verify that docs/EULA.md still says exactly what eula.html says.

The EULA is a legal document with one canonical form: eula.html in this
repository, published at prismtabs.com/eula. The plugin repository keeps a
mirror at docs/EULA.md so the licence text travels with the code. A silent
drift between the two is worse than having only one of them, so this check
compares the prose word for word and fails loudly when they diverge.

Only the prose is compared. Formatting is irrelevant, and page furniture that
was never part of the Agreement (the navigation, the table of contents, and
anything marked `data-site-only`) is excluded, as are HTML comments in the
mirror.

Usage:
    tools/check-eula-sync.py [--mirror PATH] [--page PATH]

The mirror defaults to ../prismtabs/docs/EULA.md, or to $PRISMTABS_EULA when
that is set.
"""

from __future__ import annotations

import argparse
import difflib
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MIRROR = REPO_ROOT.parent / "prismtabs" / "docs" / "EULA.md"
DEFAULT_PAGE = REPO_ROOT / "eula.html"

# Elements whose text is page furniture rather than part of the Agreement.
SKIPPED_TAGS = {"script", "style", "svg", "head"}


class AgreementTextExtractor(HTMLParser):
    """Collects the visible text of the page's `.docs-content` element.

    Subtrees marked `data-site-only` are skipped: they carry commentary the
    site adds around the Agreement, not the Agreement itself.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._depth = 0            # nesting depth inside .docs-content
        self._skip_until: int | None = None
        self._skipped_tags = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)

        if tag in SKIPPED_TAGS:
            self._skipped_tags += 1
            return

        if self._depth == 0:
            classes = (attrs_dict.get("class") or "").split()
            if "docs-content" in classes:
                self._depth = 1
            return

        self._depth += 1
        if self._skip_until is None and "data-site-only" in attrs_dict:
            self._skip_until = self._depth

    def handle_endtag(self, tag: str) -> None:
        if tag in SKIPPED_TAGS:
            self._skipped_tags = max(0, self._skipped_tags - 1)
            return

        if self._depth == 0:
            return

        if self._skip_until is not None and self._depth == self._skip_until:
            self._skip_until = None
        self._depth -= 1

    def handle_data(self, data: str) -> None:
        if self._depth > 0 and self._skip_until is None and self._skipped_tags == 0:
            self.parts.append(data)

    def text(self) -> str:
        if not self.parts:
            raise ValueError("no .docs-content element found in the page")
        return " ".join(self.parts)


def markdown_text(source: str) -> str:
    """Strip the markdown formatting, leaving the prose."""
    text = source
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)      # HTML comments
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)   # headings
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)  # list bullets
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text, flags=re.DOTALL)  # bold
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)                # links
    text = text.replace("`", "")
    return text


def words(text: str) -> list[str]:
    """Reduce prose to a comparable sequence of words.

    Case and trailing punctuation are ignored so that a full stop moving
    inside or outside an emphasis span does not register as a difference.
    """
    tokens = re.findall(r"[^\s]+", text)
    normalised = []
    for token in tokens:
        token = token.strip(".,;:").lower()
        if token:
            normalised.append(token)
    return normalised


def sentences(text: str) -> list[str]:
    """Split prose into sentences, for a readable diff."""
    collapsed = re.sub(r"\s+", " ", text).strip()
    return [s.strip() for s in re.split(r"(?<=[.;:])\s+", collapsed) if s.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that docs/EULA.md matches the canonical eula.html."
    )
    parser.add_argument(
        "--mirror",
        type=Path,
        default=Path(os.environ.get("PRISMTABS_EULA", DEFAULT_MIRROR)),
        help="path to the docs/EULA.md mirror (default: %(default)s)",
    )
    parser.add_argument(
        "--page",
        type=Path,
        default=DEFAULT_PAGE,
        help="path to the canonical eula.html (default: %(default)s)",
    )
    args = parser.parse_args()

    if not args.mirror.is_file():
        print(
            f"error: EULA mirror not found at {args.mirror}\n"
            "       Pass --mirror, or set PRISMTABS_EULA, to point at the\n"
            "       docs/EULA.md in your checkout of the plugin repository.",
            file=sys.stderr,
        )
        return 2

    if not args.page.is_file():
        print(f"error: canonical page not found at {args.page}", file=sys.stderr)
        return 2

    extractor = AgreementTextExtractor()
    extractor.feed(args.page.read_text(encoding="utf-8"))

    try:
        page_text = extractor.text()
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    mirror_text = markdown_text(args.mirror.read_text(encoding="utf-8"))

    if words(page_text) == words(mirror_text):
        print(f"EULA in sync: {args.mirror.name} matches {args.page}")
        return 0

    print(
        f"error: {args.mirror.name} has drifted from {args.page.name}.\n"
        "       The mirror must say exactly what the canonical Agreement says.\n",
        file=sys.stderr,
    )
    diff = difflib.unified_diff(
        sentences(page_text),
        sentences(mirror_text),
        fromfile=str(args.page),
        tofile=str(args.mirror),
        lineterm="",
        n=1,
    )
    for line in diff:
        print(line, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
