"""Syllabus PDF → build/raw.md (clean markdown with page markers).

Usage:  python scripts/convert.py [path/to/syllabus.pdf]

- Crops the repeated page header and footer (version, "Page X of 78", date, copyright).
- Inserts <!-- page: N --> at the start of each page, to track where text came from.
- Normalizes numbered headings (1. / 1.1. / 1.1.1.) to #, ##, ### using the table of contents.
- Fixes broken end-of-line hyphenation and small extraction artifacts.
- Keeps tables and lists in the markdown form produced by pymupdf4llm.
"""
from __future__ import annotations

import json
import re
import sys

import pymupdf
import pymupdf4llm

from common import BUILD, RAW, TOC_JSON, find_pdf, read_toc


def content_area(page: "pymupdf.Page") -> "pymupdf.Rect":
    """Page rectangle without the repeated header and footer.

    Header: the "Certified Tester / Foundation Level" block (+24pt for the empty lines below it).
    Footer: the "v4.0.1 / Page X of 78 / date" block.
    """
    r = page.mediabox
    top, bottom = r.y0, r.y1
    for x0, y0, x1, y1, txt, *_ in page.get_text("blocks"):
        if txt.strip().startswith("Certified Tester") and y0 < r.y1 * 0.2:
            top = max(top, y1 + 24)
        if re.search(r"Page \d+ of \d+", txt) and y0 > r.y1 * 0.7:
            bottom = min(bottom, y0 - 2)
    return pymupdf.Rect(r.x0, top, r.x1, bottom)


def normalize_headings(md: str, toc: list[dict]) -> str:
    """Make every table-of-contents entry a markdown heading at the right level."""
    by_number = {e["number"]: e for e in toc}
    out = []
    in_objectives = False  # inside "Learning Objectives for Chapter N" (until the next page)
    for line in md.splitlines():
        s = re.sub(r"\*\*|__", "", line).strip()
        s = re.sub(r"^#+\s*", "", s)
        if s.startswith("<!-- page:"):
            in_objectives = False
        elif s.startswith("Learning Objectives for Chapter"):
            in_objectives = True
        m = re.match(r"^(\d+(?:\.\d+)*)\.?\s+(.+?)\s*$", s)
        if in_objectives and m:
            # Sub-heading of the objectives list, not the start of the section.
            out.append(f"##### {s}")
            continue
        if m and m.group(1) in by_number:
            e = by_number[m.group(1)]
            pdf_title = re.sub(r"\s+[–-]\s+\d+\s+minutes$", "", m.group(2)).strip()
            if _similar(pdf_title, e["title"]):
                out.append(f"{'#' * e['level']} {e['number']}. {s[len(m.group(1)):].lstrip('. ').strip()}")
                continue
        # Headings that are not numbered sections (e.g. "Keywords") go down to ####.
        if line.startswith("#"):
            out.append("#### " + re.sub(r"^#+\s*", "", re.sub(r"\*\*", "", line)).strip())
            continue
        out.append(line)
    return "\n".join(out)


def _similar(a: str, b: str) -> bool:
    norm = lambda x: re.sub(r"[^a-z0-9]", "", x.lower())
    return norm(a) == norm(b) or norm(a).startswith(norm(b)) or norm(b).startswith(norm(a))


def restore_hyphens(md: str) -> str:
    """Put back the hyphen in compounds that extraction joined at a line break.

    E.g. "riskbased" becomes "risk-based" when "risk-based" appears elsewhere in the text.
    """
    known = {h.replace("-", "").lower(): h for h in re.findall(r"\b[A-Za-z]+-[A-Za-z]+\b", md)}

    def swap(m: re.Match) -> str:
        word = m.group(0)
        target = known.get(word.lower())
        if not target:
            return word
        # Keep the case of the found word's first letter; the rest comes from the original form.
        return (target[0].upper() if word[0].isupper() else target[0].lower()) + target[1:]

    return re.sub(r"\b[A-Za-z]{6,}\b", swap, md)


def fix_artifacts(md: str) -> str:
    md = re.sub(r"(\w) ~~(\w+)~~ (\w)", r"\1\2\3", md)       # "work ~~f~~ lows" -> "workflows"
    md = re.sub(r"^(\s*)- • ", r"\1- ", md, flags=re.M)        # duplicated list marker
    md = re.sub(r"\*\* ([.,;:])", r"**\1", md)                 # "**Term** ." -> "**Term**."
    md = md.replace("<sup>®</sup>", "®")
    return md


def fix_hyphenation(md: str) -> str:
    # "infor-\nmation" -> "information" (only when the next line starts in lowercase).
    md = re.sub(r"(\w)-\n(?=[a-z])", r"\1", md)
    md = re.sub(r"[ \t]+\n", "\n", md)
    md = re.sub(r"(?<=\S) {2,}(?=\S)", " ", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md


def main() -> None:
    pdf = find_pdf(sys.argv[1] if len(sys.argv) > 1 else None)
    BUILD.mkdir(exist_ok=True)
    print(f"Converting {pdf.name} ...")
    toc = read_toc(pdf)

    doc = pymupdf.open(pdf)
    for page in doc:
        page.set_cropbox(content_area(page))
    pages = pymupdf4llm.to_markdown(doc, page_chunks=True, show_progress=False)

    parts = []
    for i, chunk in enumerate(pages, start=1):
        parts.append(f"<!-- page: {i} -->\n\n{chunk['text'].strip()}")
    md = "\n\n".join(parts) + "\n"
    md = normalize_headings(md, toc)
    md = fix_hyphenation(md)
    md = fix_artifacts(md)
    md = restore_hyphens(md)

    RAW.write_text(md, encoding="utf-8")
    TOC_JSON.write_text(json.dumps(toc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: build/raw.md ({len(md.split())} words, {len(pages)} pages)")
    print(f"OK: build/toc.json ({len(toc)} entries)")


if __name__ == "__main__":
    main()
