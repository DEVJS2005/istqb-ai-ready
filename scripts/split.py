"""build/raw.md → one file per numbered section, in two versions, plus llms.txt.

Usage:  python scripts/split.py
(run first: python scripts/convert.py)

syllabus/        public SHELL (committed): frontmatter, our summary (data/summaries.yaml),
                 original PDF page, objectives, related sections and guides. No syllabus text.
syllabus-text/   local FULL TEXT (git-ignored): same frontmatter + the section's text.

Paths are identical in both folders: syllabus/X.md ↔ syllabus-text/X.md.
"""
from __future__ import annotations

import json
import re
import shutil

import yaml

from common import (
    DATA,
    FULLTEXT,
    OFFICIAL_LINK,
    ROOT,
    SYLLABUS,
    VERSION,
    load_raw,
    relative_path,
    segment,
    strip_page_marks,
)
from extract_metadata import extract_keywords, extract_objectives, occurs

# Practical guides (guides/) linked from each section or chapter.
GUIDES = {
    "1.4": ["test-planning-checklist.md"],
    "4": ["black-box-techniques.md"],
    "4.2": ["black-box-techniques.md"],
    "5": ["test-planning-checklist.md", "test-plan-template.md"],
    "5.1": ["test-planning-checklist.md", "test-plan-template.md"],
    "5.2": ["test-planning-checklist.md", "test-plan-template.md"],
}

SHELL_NOTICE = (
    "> **Shell.** This file does not contain the syllabus text. The summary is ours (not ISTQB text).\n"
    "> For the exact content, see the section and page given below in the official PDF, or the file in `syllabus-text/`."
)
FULLTEXT_NOTICE = (
    f"> Text of the ISTQB® Certified Tester Foundation Level Syllabus v{VERSION}, © ISTQB®.\n"
    "> Generated locally from the official PDF for personal use. Do not redistribute. See LEGAL-NOTICE.md."
)


def _order(n: str) -> list[int]:
    return [int(x) for x in n.split(".")]


def guides_for(number: str) -> list[str]:
    parts = number.split(".")
    for i in range(len(parts), 0, -1):
        key = ".".join(parts[:i])
        if key in GUIDES:
            return GUIDES[key]
    return []


def references(text: str, numbers: set[str], own: str) -> list[str]:
    """Sections cited in the text: "see section 2.2.3", "sections 4.2, 4.3", "chapter 2.2.1"."""
    found = set()
    for m in re.finditer(r"(?:sections?|chapters?)\s+((?:\d+(?:\.\d+)*(?:,\s*|\s+and\s+)?)+)", text, flags=re.I):
        for n in re.findall(r"\d+(?:\.\d+)*", m.group(1)):
            n = n.rstrip(".")
            if n in numbers and n != own:
                found.add(n)
    return sorted(found, key=_order)


def build_items(md: str, toc: list[dict]) -> list[dict]:
    """Compute the frontmatter and relations of every file."""
    chapters = {e["number"]: e for e in toc if e["level"] == 1}
    numbers = {e["number"] for e in toc}
    segments = segment(md, toc)
    objectives = extract_objectives(md, toc)
    keywords = extract_keywords(md)
    summaries = yaml.safe_load((DATA / "summaries.yaml").read_text(encoding="utf-8"))

    items = []
    for e in toc:
        n = e["number"]
        chapter = n.split(".")[0]
        if chapter == "0" and n != "0":
            continue  # the whole introduction goes into 00-introduction.md
        seg = segments[n]
        text = strip_page_marks(seg["text"])
        if e["level"] == 1:
            objs = [o for o in objectives if str(o["chapter"]) == chapter]
            kws = keywords.get(chapter, [])
            # The introduction lists its sections separately, in a single file.
            children = [] if chapter == "0" else [x for x in toc if x["level"] == 2 and x["number"].split(".")[0] == chapter]
            related: list[str] = []
        else:
            objs = [o for o in objectives if o["section"] == n]
            kws = [k for k in keywords.get(chapter, []) if occurs(k, text)]
            children = [x for x in toc if x["number"].startswith(n + ".") and x["level"] == e["level"] + 1]
            siblings = [x["number"] for x in toc if x["level"] == e["level"]
                        and x["number"].rsplit(".", 1)[0] == n.rsplit(".", 1)[0]]
            i = siblings.index(n)
            neighbours = siblings[max(0, i - 1):i] + siblings[i + 1:i + 2]
            related = sorted(set(references(text, numbers, n)) | set(neighbours), key=_order)
        levels = sorted({o["k_level"] for o in objs})
        items.append(
            {
                "entry": e,
                "path": relative_path(e, chapters),
                "text": seg["text"],
                "children": children,
                "objectives": objs,
                "summary": summaries.get(n, {}),
                "frontmatter": {
                    "chapter": int(chapter),
                    "section": n,
                    "title": e["title"],
                    "objectives": [o["code"] for o in objs],
                    "k_level": levels[-1] if levels else None,
                    "keywords": kws,
                    # The syllabus only defines study time per chapter; sections get null.
                    "study_time_min": e["minutes"] if e["level"] == 1 else None,
                    "source_page": e["page"],
                    "related": related,
                    "source": f"ISTQB CTFL v{VERSION}",
                },
            }
        )
    return items


def _frontmatter(data: dict, kind: str) -> str:
    """One key per line; values as JSON (which is also valid YAML).

    This way "4.1" is always quoted and never becomes a decimal number.
    """
    data = {**data, "type": kind}
    lines = [f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in data.items()]
    return "---\n" + "\n".join(lines) + "\n---\n"


def _link(src: str, dst: str) -> str:
    """Relative link between two files inside syllabus/."""
    origin = src.split("/")[:-1]
    target = dst.split("/")
    same = 0
    while same < len(origin) and same < len(target) - 1 and origin[same] == target[same]:
        same += 1
    return "/".join([".."] * (len(origin) - same) + target[same:])


def build_shell(item: dict, by_number: dict[str, dict]) -> str:
    fm, e, path = item["frontmatter"], item["entry"], item["path"]
    level = e["level"]
    parts = [_frontmatter(fm, "shell"), f"# {e['number']}. {e['title']}\n", SHELL_NOTICE + "\n"]

    summary = item["summary"].get("summary") or item["summary"].get("short")
    if summary:
        parts.append(f"## Summary (ours)\n\n{summary.strip()}\n")

    if level == 1 and e["minutes"]:
        parts.append(f"**Chapter study time (syllabus):** {e['minutes']} minutes.\n")

    if item["objectives"]:
        lines = []
        for o in item["objectives"]:
            target = by_number[o["section"]]["path"]
            ref = f"[{o['section']}]({_link(path, target)})" if target != path else o["section"]
            lines.append(f"- `{o['code']}` ({o['k_level']}): section {ref}")
        parts.append(
            "## Learning objectives\n\n"
            "Code and K-level. The wording of each objective is in the official syllabus "
            "(or in `syllabus-text/_data/objectives-full.json`, if generated).\n\n" + "\n".join(lines) + "\n"
        )

    if item["children"]:
        lines = []
        for c in item["children"]:
            target = by_number[c["number"]]
            short = target["summary"].get("short", "")
            lines.append(f"- [{c['number']} {c['title']}]({_link(path, target['path'])}): {short}")
        parts.append("## Sections\n\n" + "\n".join(lines) + "\n")

    if e["number"] == "0":
        lines = [f"- **{n}**: {s}" for n, s in item["intro_sections"]]
        parts.append("## Introduction sections\n\n" + "\n".join(lines) + "\n")

    if level == 1 and fm["keywords"]:
        parts.append("## Chapter keywords\n\n" + ", ".join(fm["keywords"]) + "\n")

    if fm["related"]:
        lines = []
        for n in fm["related"]:
            target = by_number.get(n)
            if target:
                lines.append(f"- [{n} {target['entry']['title']}]({_link(path, target['path'])})")
        parts.append("## Related\n\n" + "\n".join(lines) + "\n")

    parts.append(
        "## Where to read the original\n\n"
        f"- ISTQB® CTFL v{VERSION}, section **{e['number']}**, page **{e['page']}** of the PDF.\n"
        f"- Official PDF: <{OFFICIAL_LINK}>\n"
        f"- Local text (if generated with `scripts/`): `syllabus-text/{path}`\n"
    )

    guides = guides_for(e["number"])
    if guides:
        depth = path.count("/") + 1
        links = "\n".join(f"- [{g}]({'../' * depth}guides/{g})" for g in guides)
        parts.append("## Practical application (ours)\n\n" + links + "\n")

    return "\n".join(parts)


def build_fulltext(item: dict) -> str:
    return "\n".join([_frontmatter(item["frontmatter"], "full-text"), FULLTEXT_NOTICE + "\n", item["text"].strip() + "\n"])


def build_llms(items: list[dict]) -> str:
    """Compact index in the llms.txt format (https://llmstxt.org)."""
    lines = [
        "# istqb-ai-ready",
        "",
        f"> QA knowledge base structured for AI tools, built from the ISTQB® CTFL Syllabus v{VERSION}.",
        "> Each syllabus section has a file with frontmatter, our own summary and the original PDF page; the full text exists only locally in syllabus-text/.",
        "",
        "Read CLAUDE.md first (usage rules). Always cite the section used, e.g. \"per syllabus 4.2.1\".",
        "syllabus/ holds the shells (our summaries). If syllabus-text/<same path> exists, it has the official text of the section.",
        "",
        "## Rules and notice",
        "",
        "- [CLAUDE.md](CLAUDE.md): how an AI should query and cite this base",
        "- [LEGAL-NOTICE.md](LEGAL-NOTICE.md): attribution to ISTQB® and conditions of use",
        "- [README.md](README.md): what this is, how to regenerate it from the PDF, how to use it in other projects (Portuguese: README.pt-BR.md)",
        "",
        "## Practical guides (our interpretation, not the syllabus)",
        "",
    ]
    for g in sorted((ROOT / "guides").glob("*.md")):
        fm = yaml.safe_load(g.read_text(encoding="utf-8").split("---")[1])
        based = ", ".join(fm.get("based_on", []))
        lines.append(f"- [guides/{g.name}](guides/{g.name}): {fm['title']} (based on {based})")
    lines += [
        "",
        "## Data",
        "",
        "- [data/objectives.json](data/objectives.json): the 64 learning objectives (code, K-level, section, file)",
        "- [data/keywords.json](data/keywords.json): keywords of each chapter",
        "- [data/glossary.json](data/glossary.json): syllabus terms with sections and pages; definitions are in the official ISTQB glossary",
        "- [data/summaries.yaml](data/summaries.yaml): our summary of each section (source of the shells)",
        "",
        "## Syllabus (shells)",
        "",
    ]
    for it in items:
        e = it["entry"]
        short = it["summary"].get("short", "")
        k = f" [{it['frontmatter']['k_level']}]" if it["frontmatter"]["k_level"] and e["level"] > 1 else ""
        indent = "  " if e["level"] == 3 else ""
        if e["level"] == 1:
            if lines[-1] != "":
                lines.append("")
            heading = "Introduction" if e["number"] == "0" else f"Chapter {e['number']}: {e['title']}"
            lines += [f"### {heading}", ""]
        lines.append(f"{indent}- [{e['number']} {e['title']}](syllabus/{it['path']}){k}: {short}")
    lines += [
        "",
        "## Optional",
        "",
        f"- [Official syllabus (PDF)]({OFFICIAL_LINK}): primary source, use it when you need the exact text and there is no syllabus-text/",
        "- [Official ISTQB glossary](https://glossary.istqb.org/): definitions of the terms",
        "- [scripts/](scripts/): PDF → markdown pipeline (convert, extract_metadata, split, validate)",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    md, toc = load_raw()
    items = build_items(md, toc)
    by_number = {it["entry"]["number"]: it for it in items}
    # Sections 0.x point to the single introduction file.
    summaries = yaml.safe_load((DATA / "summaries.yaml").read_text(encoding="utf-8"))
    intro = by_number["0"]
    intro["intro_sections"] = [
        (f"{e['number']} {e['title']}", summaries.get(e["number"], {}).get("short", ""))
        for e in toc if e["number"].startswith("0.")
    ]
    for e in toc:
        if e["number"].startswith("0."):
            by_number[e["number"]] = intro

    for folder in (SYLLABUS, FULLTEXT):
        if folder.exists():
            for child in folder.iterdir():
                if child.name != "_data":
                    shutil.rmtree(child) if child.is_dir() else child.unlink()
        folder.mkdir(exist_ok=True)

    for it in items:
        for folder, content in ((SYLLABUS, build_shell(it, by_number)), (FULLTEXT, build_fulltext(it))):
            dest = folder / it["path"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")

    (ROOT / "llms.txt").write_text(build_llms(items), encoding="utf-8")
    print(f"OK: {len(items)} files in syllabus/ (shell) and syllabus-text/ (local text)")
    print("OK: llms.txt")


if __name__ == "__main__":
    main()
