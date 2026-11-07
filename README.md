# istqb-ai-ready

*Leia em português: [README.pt-BR.md](README.pt-BR.md)*

A QA knowledge base built on the **ISTQB® Certified Tester Foundation Level (CTFL) Syllabus v4.0.1**,
organised so that AI tools (Claude Code and others) can **read, search and cite** the syllabus section by
section. It serves as a good-practice guide for other testing projects.

> Independent project, not affiliated with ISTQB® or BSTQB. **This repository does not contain the syllabus
> text**: it contains the structure (sections, objectives, keywords, pages), our own summaries and scripts
> that generate the full text on your machine from the official PDF. See [LEGAL-NOTICE.md](LEGAL-NOTICE.md).

## What is here

```
istqb-ai-ready/
├── CLAUDE.md            rules for AI tools: how to query, cite, and what not to do
├── llms.txt             compact index of every file (llms.txt format)
├── LEGAL-NOTICE.md      attribution to ISTQB® and conditions of use
├── README.md            this file (English) · README.pt-BR.md (Portuguese)
├── syllabus/            SHELL: 1 file per section (86), with frontmatter + our summary + PDF page
├── syllabus-text/       FULL TEXT (same paths), generated locally, outside git
├── data/
│   ├── objectives.json  64 learning objectives (code, K-level, section, file)
│   ├── glossary.json    265 terms with sections and pages, plus the official glossary link
│   ├── keywords.json    102 keywords, by chapter
│   └── summaries.yaml   our summary of each section (source of the shells)
├── guides/              practical application, written by us (not the syllabus)
│   ├── black-box-techniques.md
│   ├── test-planning-checklist.md
│   └── test-plan-template.md
├── scripts/             PDF → markdown pipeline
└── source/              put the official PDF here (git-ignored)
```

Every section has a frontmatter like this:

```yaml
---
chapter: 4
section: "4.2.1"
title: "Equivalence Partitioning"
objectives: ["FL-4.2.1"]
k_level: "K3"
keywords: ["coverage", "coverage item", "equivalence partitioning", "test technique"]
study_time_min: null      # the syllabus only defines time per chapter
source_page: 39
related: ["4.2.2"]
source: "ISTQB CTFL v4.0.1"
type: "shell"
---
```

## How it was generated

| Script | What it does |
|---|---|
| `scripts/convert.py` | PDF → `build/raw.md` with pymupdf4llm. Crops each page's header and footer, normalises headings from the table of contents, fixes hyphenation and marks the source page (`<!-- page: N -->`). |
| `scripts/extract_metadata.py` | Objectives (chapter lists), keywords and index terms → `data/*.json`. |
| `scripts/split.py` | One file per section in `syllabus/` (shell) and `syllabus-text/` (local text), plus one `_index.md` per chapter and `llms.txt`. |
| `scripts/validate.py` | Checks sections × table of contents, objectives × PDF × Appendix B, word count (difference in %), frontmatter, links, absence of syllabus text in the shell, and `.gitignore`. |

## How to regenerate from the PDF

Requirements: Python 3.10+.

1. Download the official CTFL v4.0.1 PDF from <https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/> and save it in `source/`.
2. Create the environment and run the pipeline:

```bash
python -m venv .venv
```

```bash
.venv/Scripts/pip install -r requirements.txt      # Linux/macOS: .venv/bin/pip
```

```bash
.venv/Scripts/python scripts/convert.py && .venv/Scripts/python scripts/extract_metadata.py && .venv/Scripts/python scripts/split.py && .venv/Scripts/python scripts/validate.py
```

This creates `syllabus-text/`, which stays on your machine only. Use it for offline search and so the AI can
read the official text. **Do not commit or redistribute that folder.**

To change a summary, edit `data/summaries.yaml` and run `scripts/split.py` again. Do not edit `syllabus/` by hand.

## How to use it with Claude Code in another project

### 1. Add it as a submodule

In the testing project:

```bash
git submodule add https://github.com/DEVJS2005/istqb-ai-ready.git docs/istqb-ai-ready
```

Anyone cloning the project later should use `git clone --recurse-submodules`, or run
`git submodule update --init` after cloning. To update the base: `git submodule update --remote docs/istqb-ai-ready`.

### 2. Point the project's CLAUDE.md at the base

Add to the project's `CLAUDE.md` (Claude Code treats `@path` as a file import):

```markdown
## QA good-practice base (ISTQB CTFL)
@docs/istqb-ai-ready/CLAUDE.md

- When planning, designing or reviewing tests, check `docs/istqb-ai-ready/llms.txt` first.
- Cite the syllabus section used (e.g. "per syllabus 4.2.1").
```

### 3. (Optional) Generate the full text inside the submodule

Repeat the "How to regenerate" steps inside `docs/istqb-ai-ready/`. Without it, the AI works from the shells
and points to the PDF page when it needs the exact wording.

### 4. CI (GitHub Actions)

If a project workflow needs the base, check out with submodules:

```yaml
- uses: actions/checkout@v4
  with:
    submodules: true
```

## Attribution

Content derived from the **ISTQB® Certified Tester Foundation Level Syllabus v4.0.1**, © International Software
Testing Qualifications Board (ISTQB®). ISTQB® is a registered trademark of the International Software Testing
Qualifications Board. The authors and ISTQB® are the source and copyright owners of the syllabus. Official page:
<https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/>. In Brazil: BSTQB,
<https://bstqb.org.br>. Details and conditions of use in [LEGAL-NOTICE.md](LEGAL-NOTICE.md).

The scripts, summaries and guides in this repository are authored by its maintainers. Non-commercial use.
