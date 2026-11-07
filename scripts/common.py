"""Shared helpers for the scripts: paths, reading the PDF table of contents, slugs and segmentation."""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "source"
BUILD = ROOT / "build"
SYLLABUS = ROOT / "syllabus"          # public shell (committed)
FULLTEXT = ROOT / "syllabus-text"     # local full text (git-ignored)
DATA = ROOT / "data"
RAW = BUILD / "raw.md"
TOC_JSON = BUILD / "toc.json"

VERSION = "4.0.1"
OFFICIAL_LINK = "https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/"
GLOSSARY_LINK = "https://glossary.istqb.org/"

# Table of Contents pages in the v4.0.1 PDF (1-based).
TOC_PAGES = range(4, 8)


def find_pdf(path: str | None = None) -> Path:
    """Return the given PDF, or the only PDF in source/."""
    if path:
        p = Path(path)
        if not p.exists():
            sys.exit(f"PDF not found: {p}")
        return p
    pdfs = sorted(SOURCE.glob("*.pdf"))
    if not pdfs:
        sys.exit(
            "No PDF in source/. Download the official syllabus from\n"
            f"  {OFFICIAL_LINK}\n"
            "and save it in source/."
        )
    if len(pdfs) > 1:
        sys.exit(f"More than one PDF in source/: {[p.name for p in pdfs]}. Pass the one to use.")
    return pdfs[0]


def slug(text: str) -> str:
    text = re.sub(r"['’]", "", text)  # "Tester's" -> "testers"
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")


def read_toc(pdf: Path) -> list[dict]:
    """Read the PDF table of contents into [{number, title, page, level, minutes}].

    Only chapters 0 to 6 (content). References, appendices and index are left out.
    """
    import pymupdf

    doc = pymupdf.open(pdf)
    text = "\n".join(doc[i - 1].get_text() for i in TOC_PAGES)
    lines = [l.strip() for l in text.splitlines()]
    entries: list[dict] = []
    i = 0
    while i < len(lines):
        m = re.fullmatch(r"(\d+(?:\.\d+)*)\.", lines[i])
        if m and i + 1 < len(lines):
            m2 = re.fullmatch(r"(.+?)\s*\.{2,}\s*(\d+)", lines[i + 1])
            if m2:
                number = m.group(1)
                title = m2.group(1).strip()
                minutes = None
                mm = re.search(r"\s+[–-]\s+(\d+)\s+minutes$", title)
                if mm:
                    minutes = int(mm.group(1))
                    title = title[: mm.start()].strip()
                entries.append(
                    {
                        "number": number,
                        "title": title,
                        "page": int(m2.group(2)),
                        "level": number.count(".") + 1,
                        "minutes": minutes,
                    }
                )
                i += 2
                continue
        i += 1
    return [e for e in entries if int(e["number"].split(".")[0]) <= 6]


def load_raw() -> tuple[str, list[dict]]:
    """Read build/raw.md and build/toc.json (produced by convert.py)."""
    if not RAW.exists():
        sys.exit("build/raw.md does not exist. Run first: python scripts/convert.py")
    toc = json.loads(TOC_JSON.read_text(encoding="utf-8"))
    return RAW.read_text(encoding="utf-8"), toc


def segment(md: str, toc: list[dict]) -> dict[str, dict]:
    """Split the raw markdown by table-of-contents section.

    Returns {number: {text, start_page, pages}}. A section's text runs from its heading to the next
    numbered heading of any level, so a parent section holds only its own introduction.
    All of chapter 0 is kept under "0". The last piece ends at "7. References".
    """
    numbers = {e["number"] for e in toc}
    lines = md.splitlines()
    page = 0
    marks: list[tuple[int, str, int]] = []  # (line, number, page)
    end = len(lines)
    for i, line in enumerate(lines):
        mp = re.match(r"<!-- page: (\d+) -->", line)
        if mp:
            page = int(mp.group(1))
            continue
        mt = re.match(r"^(#{1,3}) (\d+(?:\.\d+)*)\. ", line)
        if mt and mt.group(2) in numbers:
            marks.append((i, mt.group(2), page))
        if re.match(r"^#+ 7\. References", line):
            end = i
            break

    sections: dict[str, dict] = {}
    for k, (start, number, pg) in enumerate(marks):
        nxt = marks[k + 1][0] if k + 1 < len(marks) else end
        if number == "0" or number.startswith("0."):
            continue
        piece = "\n".join(lines[start:nxt]).strip()
        sections[number] = {"text": piece, "start_page": pg, "pages": _pages(piece, pg)}

    # Chapter 0 (introduction) as a single piece.
    start0 = next(i for i, n, _ in marks if n == "0")
    end0 = next(i for i, n, _ in marks if n == "1")
    piece0 = "\n".join(lines[start0:end0]).strip()
    page0 = next(p for _, n, p in marks if n == "0")
    sections["0"] = {"text": piece0, "start_page": page0, "pages": _pages(piece0, page0)}
    return sections


def _pages(piece: str, start: int) -> list[int]:
    return sorted({start, *(int(p) for p in re.findall(r"<!-- page: (\d+) -->", piece))})


def strip_page_marks(piece: str) -> str:
    return re.sub(r"<!-- page: \d+ -->\n*", "", piece)


def chapter_dir(chapter: dict) -> str:
    return f"{int(chapter['number']):02d}-{slug(chapter['title'])}"


def file_name(section: dict) -> str:
    return f"{section['number']}-{slug(section['title'])}.md"


def relative_path(section: dict, chapters: dict[str, dict]) -> str:
    """Path of a section relative to syllabus/ (or syllabus-text/)."""
    chapter = section["number"].split(".")[0]
    if chapter == "0":
        # The introduction (0.1 to 0.11) lives in a single file.
        return "00-introduction.md"
    if section["level"] == 1:
        return f"{chapter_dir(chapters[chapter])}/_index.md"
    return f"{chapter_dir(chapters[chapter])}/{file_name(section)}"
