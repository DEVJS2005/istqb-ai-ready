"""Check that nothing was lost in the conversion and that the public shell is clean.

Usage:  python scripts/validate.py [path/to/syllabus.pdf]
Exits with code 1 if any check FAILS. Warnings do not fail.

Checks:
 1. Every table-of-contents section became a file (shell and local text).
 2. The number of extracted objectives matches the PDF (chapter lists and Appendix B).
 3. The markdown word count is close to the PDF's (difference in %).
 4. Every frontmatter is valid YAML and has the required fields.
 5. The public shell contains no long passages of syllabus text (copyright guard).
 6. Internal links in .md files point to files that exist.
 7. git ignores the PDF, build/ and syllabus-text/.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

from common import DATA, FULLTEXT, ROOT, SYLLABUS, find_pdf, load_raw, relative_path, strip_page_marks

FIELDS = {
    "chapter": int,
    "section": str,
    "title": str,
    "objectives": list,
    "k_level": (str, type(None)),
    "keywords": list,
    "study_time_min": (int, type(None)),
    "source_page": int,
    "related": list,
}
WORD_TOLERANCE = 3.0   # acceptable difference, in %
NGRAM = 12             # consecutive syllabus words that must not appear in public files

results: list[tuple[str, str, str]] = []  # (status, check, detail)


def record(status: str, check: str, detail: str) -> None:
    results.append((status, check, detail))


def read_frontmatter(path: Path) -> tuple[dict | None, str]:
    t = path.read_text(encoding="utf-8")
    if not t.startswith("---\n"):
        return None, "no frontmatter"
    try:
        end = t.index("\n---\n", 4)
        return yaml.safe_load(t[4:end]), t[end + 5:]
    except (ValueError, yaml.YAMLError) as e:
        return None, f"invalid YAML: {e}"


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-zÀ-ÿ0-9]+(?:['’-][A-Za-zÀ-ÿ0-9]+)*", text)


def content_words(text: str) -> list[str]:
    """Words with at least one letter (ignores heading numbers and the PDF's "o" list bullet),
    with hyphens treated as separators, so the PDF and the markdown are compared fairly."""
    return [w for w in re.split(r"[^A-Za-zÀ-ÿ0-9']+", text) if re.search(r"[A-Za-zÀ-ÿ]", w) and w != "o"]


def clean_md(md: str) -> str:
    md = strip_page_marks(md)
    md = re.sub(r"^---\n.*?\n---\n", "", md, flags=re.S)          # frontmatter
    md = re.sub(r"^> .*$", "", md, flags=re.M)                     # copyright notice
    md = re.sub(r"^#+\s*\d+(?:\.\d+)*\.?\s*", "", md, flags=re.M)  # heading numbers
    md = re.sub(r"^\|[-|\s]+\|$", "", md, flags=re.M)              # table separator
    md = re.sub(r"[*_`#|>]|<br>|<sup>|</sup>", " ", md)
    md = re.sub(r"^\s*-\s", " ", md, flags=re.M)
    return md


# --------------------------------------------------------------------- checks
def check_sections(toc: list[dict]) -> None:
    chapters = {e["number"]: e for e in toc if e["level"] == 1}
    no_shell, no_text = [], []
    for e in toc:
        path = relative_path(e, chapters)
        if not (SYLLABUS / path).exists():
            no_shell.append(e["number"])
        if FULLTEXT.exists() and not (FULLTEXT / path).exists():
            no_text.append(e["number"])
        # Sections 0.x live inside 00-introduction.md: their heading must be there.
        if e["number"].startswith("0.") and FULLTEXT.exists():
            target = (FULLTEXT / path).read_text(encoding="utf-8") if (FULLTEXT / path).exists() else ""
            if not re.search(rf"^## {re.escape(e['number'])}\. ", target, flags=re.M):
                no_text.append(e["number"])
    if no_shell or no_text:
        record("FAIL", "1. Table-of-contents sections", f"no shell: {no_shell}; no text: {no_text}")
    else:
        record("OK", "1. Table-of-contents sections", f"{len(toc)} entries (chapters 0 to 6) → all have a file")
    if not FULLTEXT.exists():
        record("WARN", "1. Table-of-contents sections", "syllabus-text/ does not exist; only the shell was checked")


def check_objectives(pdf: Path) -> None:
    import pymupdf

    doc = pymupdf.open(pdf)
    text = [p.get_text() for p in doc]
    pdf_codes = set(re.findall(r"FL-\d+\.\d+\.\d+", "\n".join(text)))
    # Appendix B matrix: each objective is "1.1.1" / wording (1+ lines) / "K1".
    start_b = next(i for i, t in enumerate(text) if re.search(r"Appendix B", t) and i > 20)
    start_c = next(i for i, t in enumerate(text) if re.search(r"Appendix C", t) and i > start_b)
    lines_b = [l.strip() for t in text[start_b:start_c] for l in t.splitlines()]
    k_appendix: dict[str, str] = {}
    for i, l in enumerate(lines_b):
        if re.fullmatch(r"\d\.\d\.\d", l) and l != "4.0.1":
            k = next((x for x in lines_b[i + 1:i + 5] if re.fullmatch(r"K[1-3]", x)), None)
            if k:
                k_appendix[f"FL-{l}"] = k
    codes_b = set(k_appendix)

    data = json.loads((DATA / "objectives.json").read_text(encoding="utf-8"))
    extracted = {o["code"] for o in data["objectives"]}
    ks = {o["code"]: o["k_level"] for o in data["objectives"]}
    k_mismatch = [c for c in extracted if k_appendix.get(c) and k_appendix[c] != ks[c]]

    detail = (f"extracted {len(extracted)} · in the PDF {len(pdf_codes)} · in Appendix B {len(codes_b)}"
              f" · data/objectives.json total={data['total']}")
    if extracted == pdf_codes == codes_b and data["total"] == len(extracted) and not k_mismatch:
        record("OK", "2. Learning objectives", detail + " · K-levels match Appendix B")
    else:
        record("FAIL", "2. Learning objectives",
               f"{detail} · missing {sorted(pdf_codes - extracted)} · extra {sorted(extracted - pdf_codes)}"
               f" · K mismatch {k_mismatch}")
    missing_file = [o["code"] for o in data["objectives"] if not (ROOT / o["file"]).exists()]
    if missing_file:
        record("FAIL", "2. Learning objectives", f"point to a missing file: {missing_file}")


def check_words(pdf: Path, toc: list[dict], md: str) -> None:
    import pymupdf

    from convert import content_area

    doc = pymupdf.open(pdf)
    first = next(e["page"] for e in toc if e["number"] == "0")
    last = next(e["page"] for e in toc if e["number"] == "6")
    # Last content page = the page before "7. References".
    for i in range(last, doc.page_count):
        if re.search(r"^\s*7\.\s*References", doc[i].get_text(), flags=re.M):
            last = i  # 0-based index of the References page = previous page, 1-based
            break
    n_pdf = 0
    for i in range(first - 1, last):
        page = doc[i]
        page.set_cropbox(content_area(page))
        n_pdf += len(content_words(page.get_text()))

    if FULLTEXT.exists():
        files = sorted(FULLTEXT.rglob("*.md"))
        n_md = sum(len(content_words(clean_md(p.read_text(encoding="utf-8")))) for p in files)
        origin = f"syllabus-text/ ({len(files)} files)"
    else:
        start = md.index("# 0. Introduction")
        end = re.search(r"^#+ 7\. References", md, flags=re.M).start()
        n_md = len(content_words(clean_md(md[start:end])))
        origin = "build/raw.md"
    diff = (n_md - n_pdf) / n_pdf * 100
    detail = f"PDF pages {first}–{last}: {n_pdf} words · {origin}: {n_md} words · difference {diff:+.2f}%"
    record("OK" if abs(diff) <= WORD_TOLERANCE else "FAIL", "3. Word count", detail)


def check_frontmatter() -> None:
    problems = []
    total = 0
    for folder, kind in ((SYLLABUS, "shell"), (FULLTEXT, "full-text")):
        if not folder.exists():
            continue
        for path in sorted(folder.rglob("*.md")):
            total += 1
            fm, rest = read_frontmatter(path)
            rel = path.relative_to(ROOT).as_posix()
            if fm is None:
                problems.append(f"{rel}: {rest}")
                continue
            for field, expected in FIELDS.items():
                if field not in fm:
                    problems.append(f"{rel}: missing '{field}'")
                elif not isinstance(fm[field], expected):
                    problems.append(f"{rel}: '{field}' has type {type(fm[field]).__name__}")
            if fm.get("type") != kind:
                problems.append(f"{rel}: type '{fm.get('type')}' (expected '{kind}')")
            if fm.get("k_level") not in (None, "K1", "K2", "K3"):
                problems.append(f"{rel}: invalid k_level")
            if any(not re.fullmatch(r"FL-\d+\.\d+\.\d+", o) for o in fm.get("objectives", [])):
                problems.append(f"{rel}: invalid objective code")
    for g in sorted((ROOT / "guides").glob("*.md")):
        total += 1
        fm, _ = read_frontmatter(g)
        if fm is None or fm.get("type") != "guide" or "based_on" not in fm:
            problems.append(f"{g.relative_to(ROOT).as_posix()}: incomplete guide frontmatter")
    if problems:
        record("FAIL", "4. YAML frontmatter", f"{len(problems)} problem(s): " + "; ".join(problems[:10]))
    else:
        record("OK", "4. YAML frontmatter", f"{total} files with valid YAML and required fields")


def check_shell_clean() -> None:
    """No run of NGRAM words from the syllabus text may appear in the shell, guides or data."""
    if not FULLTEXT.exists():
        record("WARN", "5. Shell free of syllabus text", "syllabus-text/ does not exist; check skipped")
        return
    ngrams: set[tuple[str, ...]] = set()
    for path in FULLTEXT.rglob("*.md"):
        _, body = read_frontmatter(path)
        # Keyword lists are glossary terms (reference data), not prose: they are left out of the
        # comparison, as are objective lists (code + level).
        body = re.sub(r"#### Keywords\n+.*?(?=\n####|\Z)", "", body, flags=re.S)
        w = [x.lower() for x in words(clean_md(body))]
        ngrams.update(tuple(w[i:i + NGRAM]) for i in range(len(w) - NGRAM + 1))
    public = list(SYLLABUS.rglob("*.md")) + list((ROOT / "guides").glob("*.md")) + [
        ROOT / "llms.txt", ROOT / "CLAUDE.md", ROOT / "README.md", ROOT / "README.pt-BR.md", *DATA.glob("*.*")]
    leaks = []
    for path in public:
        if not path.exists():
            continue
        w = [x.lower() for x in words(path.read_text(encoding="utf-8"))]
        for i in range(len(w) - NGRAM + 1):
            if tuple(w[i:i + NGRAM]) in ngrams:
                leaks.append(f"{path.relative_to(ROOT).as_posix()}: \"{' '.join(w[i:i + NGRAM])}\"")
                break
    if leaks:
        record("FAIL", "5. Shell free of syllabus text", f"{len(leaks)} file(s): " + "; ".join(leaks[:5]))
    else:
        record("OK", "5. Shell free of syllabus text",
               f"{len(public)} public files with no run of {NGRAM}+ words from the syllabus")


def check_links() -> None:
    broken = []
    files = list(SYLLABUS.rglob("*.md")) + list((ROOT / "guides").glob("*.md")) + [
        ROOT / "README.md", ROOT / "README.pt-BR.md", ROOT / "CLAUDE.md", ROOT / "llms.txt", ROOT / "LEGAL-NOTICE.md"]
    n = 0
    for path in files:
        if not path.exists():
            continue
        t = path.read_text(encoding="utf-8")
        targets = re.findall(r"\]\(([^)]+)\)", t) + re.findall(r"^\[[^\]]+\]:\s*(\S+)", t, flags=re.M)
        for target in targets:
            if re.match(r"https?://|mailto:|#", target):
                continue
            n += 1
            if not (path.parent / target.split("#")[0]).resolve().exists():
                broken.append(f"{path.relative_to(ROOT).as_posix()} → {target}")
    if broken:
        record("FAIL", "6. Internal links", f"{len(broken)} broken: " + "; ".join(broken[:8]))
    else:
        record("OK", "6. Internal links", f"{n} internal links, all resolve")


def check_gitignore(pdf: Path) -> None:
    targets = [pdf, ROOT / "build" / "raw.md", FULLTEXT / "00-introduction.md"]
    not_ignored = []
    for t in targets:
        if subprocess.run(["git", "check-ignore", "-q", str(t)], cwd=ROOT).returncode != 0:
            not_ignored.append(t.relative_to(ROOT).as_posix() if t.is_relative_to(ROOT) else str(t))
    tracked = subprocess.run(["git", "ls-files", "source", "build", "syllabus-text"],
                             cwd=ROOT, capture_output=True, text=True).stdout.split()
    if not_ignored or tracked:
        record("FAIL", "7. git ignores protected content", f"not ignored: {not_ignored}; already tracked: {tracked}")
    else:
        record("OK", "7. git ignores protected content", "source/*.pdf, build/ and syllabus-text/ are outside git")


def main() -> int:
    pdf = find_pdf(sys.argv[1] if len(sys.argv) > 1 else None)
    md, toc = load_raw()

    check_sections(toc)
    check_objectives(pdf)
    check_words(pdf, toc, md)
    check_frontmatter()
    check_shell_clean()
    check_links()
    check_gitignore(pdf)

    print("\nVALIDATION REPORT\n" + "=" * 70)
    for status, check, detail in results:
        print(f"[{status:^4}] {check}\n       {detail}")
    fails = sum(1 for s, *_ in results if s == "FAIL")
    warns = sum(1 for s, *_ in results if s == "WARN")
    print("=" * 70)
    print(f"{len(results) - fails - warns} OK · {warns} warning(s) · {fails} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
