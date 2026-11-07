"""Extract syllabus metadata: learning objectives, keywords and index terms.

Usage:  python scripts/extract_metadata.py [path/to/syllabus.pdf]
(run first: python scripts/convert.py)

Writes (committed, no syllabus text):
  data/objectives.json   code, K-level, section and files for each learning objective
  data/keywords.json     keywords of each chapter
  data/glossary.json     terms (keywords + index) with sections/pages and the official glossary link

Writes (local, git-ignored, because it contains syllabus sentences):
  syllabus-text/_data/objectives-full.json   includes the wording of each objective
"""
from __future__ import annotations

import json
import re
import sys

from common import (
    DATA,
    FULLTEXT,
    GLOSSARY_LINK,
    OFFICIAL_LINK,
    VERSION,
    find_pdf,
    load_raw,
    relative_path,
    segment,
    strip_page_marks,
)

RE_OBJECTIVE = re.compile(r"(FL-(\d+)\.(\d+)\.(\d+))\s+\((K[1-3])\)\s+(.+?)\s*$")


def extract_objectives(md: str, toc: list[dict]) -> list[dict]:
    """Read the "Learning Objectives for Chapter N" lists at the start of each chapter."""
    numbers = {e["number"] for e in toc}
    chapters = {e["number"]: e for e in toc if e["level"] == 1}
    titles = {e["number"]: e["title"] for e in toc}
    objectives = []
    seen = set()
    in_list = False
    for line in md.splitlines():
        s = re.sub(r"^[-#\s]+", "", line).strip()
        if s.startswith("Learning Objectives for Chapter"):
            in_list = True
            continue
        if line.startswith("<!-- page:"):
            in_list = False
            continue
        if not in_list:
            continue
        m = RE_OBJECTIVE.match(s)
        if not m or m.group(1) in seen:
            continue
        code, c, s1, s2, k, text = m.groups()
        seen.add(code)
        # FL-a.b.c maps to section a.b.c; if that section does not exist, to section a.b.
        section = f"{c}.{s1}.{s2}" if f"{c}.{s1}.{s2}" in numbers else f"{c}.{s1}"
        entry = next(e for e in toc if e["number"] == section)
        objectives.append(
            {
                "code": code,
                "k_level": k,
                "chapter": int(c),
                "section": section,
                "section_title": titles[section],
                "file": "syllabus/" + relative_path(entry, chapters),
                "full_text_file": "syllabus-text/" + relative_path(entry, chapters),
                "text": text,
            }
        )
    return objectives


def extract_keywords(md: str) -> dict[str, list[str]]:
    """Read the "Keywords" block right below each chapter heading."""
    result: dict[str, list[str]] = {}
    for m in re.finditer(r"^# (\d+)\. [^\n]*\n+#### Keywords\n+((?:(?!####).)+)", md, flags=re.M | re.S):
        terms = [t.strip() for t in m.group(2).replace("\n", " ").split(",") if t.strip()]
        result[m.group(1)] = terms
    return result


def extract_index(pdf) -> list[dict]:
    """Read the Index (chapter 11) from the raw PDF text, which comes one entry per line."""
    import pymupdf

    doc = pymupdf.open(pdf)
    start = next(i for i in range(doc.page_count - 1, 0, -1) if "11. Index" in doc[i].get_text())
    lines = []
    for i in range(start, doc.page_count):
        txt = doc[i].get_text()
        txt = txt.split("11. Index", 1)[1] if i == start else txt.split("Qualifications Board", 1)[-1]
        lines += [l.strip() for l in txt.splitlines() if l.strip()]

    entries: list[str] = []
    for l in lines:
        if re.fullmatch(r"[\d,\s]+", l) and entries:
            entries[-1] += " " + l   # continuation of the page list
        else:
            entries.append(l)

    terms = []
    for e in entries:
        e = e.strip().rstrip(",")
        see = re.match(r"(.+?),\s*See\s+(.+)$", e)
        if see:
            terms.append({"term": see.group(1).strip(), "see": see.group(2).strip(), "pages": []})
            continue
        m = re.match(r"(.+?),\s*([\d,\s]+)$", e)
        if m:
            terms.append({"term": m.group(1).strip(), "pages": [int(p) for p in re.findall(r"\d+", m.group(2))]})
    return terms


def occurs(term: str, text: str) -> bool:
    base = re.sub(r"\s*\(.*?\)$", "", term)  # "author (reviews)" -> "author"
    # Hyphen and space are interchangeable ("V model" = "V-model", "shift-left" = "shift left").
    pattern = r"[\s-]".join(re.escape(p) for p in re.split(r"[\s-]+", base))
    return re.search(rf"(?<![\w-]){pattern}(s|es)?(?![\w-])", text, flags=re.I) is not None


def _order(n: str) -> list[int]:
    return [int(x) for x in n.split(".")]


def sections_for_pages(term: str, pages: list[int], segments: dict[str, dict]) -> tuple[list[str], bool]:
    """Sections that cover the index pages and whose text contains the term.

    If the term does not appear literally (different spelling in the index), return the sections
    on that page and flag the result as approximate.
    """
    candidates = [n for n, s in segments.items() if "." in n and set(pages) & set(s["pages"])]
    found = [n for n in candidates if occurs(term, strip_page_marks(segments[n]["text"]))]
    if found:
        return sorted(found, key=_order), False
    return sorted(candidates, key=_order), True


def build_glossary(keywords: dict[str, list[str]], index: list[dict], segments: dict[str, dict]) -> list[dict]:
    by_term: dict[str, dict] = {}
    for item in index:
        key = item["term"].lower()
        sections, approx = sections_for_pages(item["term"], item["pages"], segments) if item["pages"] else ([], False)
        by_term[key] = {
            "term": item["term"],
            "keyword_in_chapters": [],
            "index_pages": item["pages"],
            "sections": sections,
        }
        if approx:
            by_term[key]["approximate_sections"] = True
        if "see" in item:
            by_term[key]["see"] = item["see"]
    for chapter, terms in keywords.items():
        for t in terms:
            key = t.lower()
            if key not in by_term:
                sections = [n for n, s in segments.items() if n.split(".")[0] == chapter and n != chapter
                            and occurs(t, strip_page_marks(s["text"]))]
                by_term[key] = {"term": t, "keyword_in_chapters": [], "index_pages": [], "sections": sections}
            by_term[key]["keyword_in_chapters"].append(int(chapter))
    items = sorted(by_term.values(), key=lambda x: x["term"].lower())
    for item in items:
        item["definition"] = None
        item["official_glossary"] = GLOSSARY_LINK
    return items


def _write(path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    pdf = find_pdf(sys.argv[1] if len(sys.argv) > 1 else None)
    md, toc = load_raw()
    segments = segment(md, toc)

    objectives = extract_objectives(md, toc)
    keywords = extract_keywords(md)
    index = extract_index(pdf)
    glossary = build_glossary(keywords, index, segments)

    DATA.mkdir(exist_ok=True)
    header = {
        "source": f"ISTQB Certified Tester Foundation Level Syllabus v{VERSION}",
        "official_link": OFFICIAL_LINK,
        "notice": "Reference metadata. The syllabus text is not reproduced; see the official PDF.",
    }
    public = [{k: v for k, v in o.items() if k != "text"} for o in objectives]
    _write(DATA / "objectives.json", {**header, "total": len(public), "objectives": public})
    _write(DATA / "keywords.json",
           {**header, "by_chapter": {c: {"total": len(t), "keywords": t} for c, t in keywords.items()}})
    _write(DATA / "glossary.json", {
        **header,
        "note": ("The syllabus has no definitions of its own: it aligns its terms with the official ISTQB "
                 "glossary. This file lists only the terms (chapter keywords and index entries), where they "
                 "appear, and the link to the official definition."),
        "official_glossary": GLOSSARY_LINK,
        "total": len(glossary),
        "terms": glossary,
    })

    (FULLTEXT / "_data").mkdir(parents=True, exist_ok=True)
    _write(FULLTEXT / "_data" / "objectives-full.json", {**header, "total": len(objectives), "objectives": objectives})

    print(f"OK: data/objectives.json ({len(objectives)} objectives)")
    print(f"OK: data/keywords.json ({sum(len(t) for t in keywords.values())} keywords in {len(keywords)} chapters)")
    print(f"OK: data/glossary.json ({len(glossary)} terms)")
    print("OK: syllabus-text/_data/objectives-full.json (local)")


if __name__ == "__main__":
    main()
