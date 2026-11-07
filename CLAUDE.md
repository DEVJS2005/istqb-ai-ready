# CLAUDE.md: how an AI should use this base

This repository is a QA knowledge base built on the **ISTQB® Certified Tester Foundation Level (CTFL)
Syllabus v4.0.1**. It serves as a good-practice guide for planning, designing, reviewing and reporting
tests in other projects. These rules apply to Claude Code and to any other AI that reads the base.

> **Used as a submodule?** All paths below are relative to this base's folder
> (e.g. `docs/istqb-ai-ready/llms.txt` in the project that includes it).

## Quick map

| Folder / file | What it is | Origin |
|---|---|---|
| `llms.txt` | Index of everything, one line per file | generated |
| `syllabus/` | **Shell**: one file per section, with frontmatter, **our** summary, objectives, related sections and PDF page | generated + ours |
| `syllabus-text/` | **Full text** of each section (same paths as `syllabus/`). Exists only on the machine of whoever generated it from the PDF. **Not in git.** | ISTQB |
| `data/objectives.json` | 64 learning objectives (code, K-level, section, file) | generated |
| `data/glossary.json` | Syllabus terms with the sections and pages where they appear. Definitions live in the official glossary | generated |
| `data/keywords.json` | Keywords of each chapter | generated |
| `guides/` | Practical application: checklists, templates, examples | **ours** (interpretation) |

## Rules

1. **Check `llms.txt` first** when planning or reviewing tests. Pick the relevant sections and read
   **only** those. Do not load the whole base.
   - To find a section by objective: `data/objectives.json`.
   - To find a section by term: `data/glossary.json` (field `sections`).
   - To follow a topic: the `related` field in the frontmatter.

2. **Prefer the official text when it exists.** For each `syllabus/<path>.md`, check whether
   `syllabus-text/<path>.md` exists:
   - **It exists:** use it as the source of the content. It is the syllabus text.
   - **It does not:** use the shell's summary and say it is a summary. If you need the exact wording:
     - with web access, read the official PDF (link in `LEGAL-NOTICE.md`) and go straight to the
       page in `source_page`;
     - without web access, tell the user which section and page to read, or suggest generating the
       local text (`python scripts/convert.py && python scripts/split.py`, see `README.md`).

3. **Always cite the section used**, in the form _"per syllabus 4.2.1"_ or
   _"(ISTQB CTFL v4.0.1, 4.2.1)"_. When citing an objective, use its code: _"FL-4.2.1 (K3)"_.

4. **Use the glossary terminology; do not invent terms.** Terms are in `data/glossary.json` and in the
   frontmatter `keywords`; the official definitions are at <https://glossary.istqb.org/>. When answering
   in another language, use the established translation and show the original term on first mention,
   e.g. "particionamento de equivalência (equivalence partitioning)". Do not make up new names for
   techniques, levels, types or roles.

5. **Keep the syllabus apart from our interpretation.**
   - `syllabus-text/` = ISTQB text.
   - `syllabus/` = ISTQB structure + **our summary** (marked "Summary (ours)").
   - `guides/` = **our interpretation**. When you use a guide, say so: _"according to the internal guide
     black-box-techniques.md (based on syllabus 4.2.2)"_.

6. **If the base does not cover the topic, say so** instead of making things up. Out of CTFL scope, for
   example: in-depth performance testing, advanced security, specific tools (Cypress, Playwright, JMeter…),
   market metrics. Answer: _"The CTFL syllabus does not cover this; the closest is section X"_. If you answer
   from general knowledge, label it as such.

7. **Do not reproduce the syllabus in bulk** in answers, commits or files of other projects. Cite the
   section and paraphrase. Short excerpts with the source cited are fine; long copies are not
   (see `LEGAL-NOTICE.md`).

## Common flows

- **Plan testing for a feature:** `guides/test-planning-checklist.md` → sections 5.1.x, 5.2.x
  → `guides/test-plan-template.md`.
- **Design test cases:** `syllabus/04-test-analysis-and-design/_index.md` → technique
  (4.2.1 to 4.2.4, 4.4.x) → `guides/black-box-techniques.md`.
- **Review an artifact (story, requirement, plan):** 3.2.2 to 3.2.5, 4.5.1 and 4.5.2.
- **Report a defect or status:** 5.5, 5.3.2 and 5.3.3.
- **Discuss automation strategy:** 5.1.6, 5.1.7, 6.2 and 2.1.4.

## Frontmatter of each section

```yaml
chapter: 4                          # chapter number
section: "4.2.1"                    # always a string
title: "Equivalence Partitioning"   # original title
objectives: ["FL-4.2.1"]            # objective codes for this section
k_level: "K3"                       # highest K-level among the objectives (null if none)
keywords: [...]                     # chapter keywords present in this section
study_time_min: null                # the syllabus only defines time per chapter (_index.md)
source_page: 39                     # page in the v4.0.1 PDF
related: ["4.2.2"]                  # sections cited in the text and neighbouring sections
source: "ISTQB CTFL v4.0.1"
type: "shell"                       # "shell" in syllabus/, "full-text" in syllabus-text/
```

## Maintenance (for people editing this repository)

- Do not edit `syllabus/`, `data/*.json` or `llms.txt` by hand: they are generated. To change a summary,
  edit `data/summaries.yaml` and run `python scripts/split.py`.
- Run `python scripts/validate.py` before committing.
- Never commit `source/*.pdf`, `build/` or `syllabus-text/`.
- Keep `README.md` (English) and `README.pt-BR.md` (Portuguese) in sync.
