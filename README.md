# istqb-ai-ready: ISTQB CTFL syllabus for AI agents and QA engineering

[![License: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![Content: CC BY-NC 4.0](https://img.shields.io/badge/content-CC%20BY--NC%204.0-lightgrey.svg)](LICENSE-CONTENT.md)
[![ISTQB CTFL v4.0.1](https://img.shields.io/badge/ISTQB%20CTFL-v4.0.1-0a7bbb.svg)](https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/)
[![llms.txt](https://img.shields.io/badge/llms.txt-ready-green.svg)](llms.txt)
[![Validation](https://img.shields.io/badge/validation-7%2F7%20checks-brightgreen.svg)](scripts/validate.py)

*Leia em português: [README.pt-BR.md](README.pt-BR.md)*

A **QA engineering knowledge base** and **software testing best-practices standard** built on the
**ISTQB® Certified Tester Foundation Level (CTFL) Syllabus v4.0.1**, structured so that AI coding agents
(Claude Code, Cursor, Copilot and any tool that reads `llms.txt`) can **read, search and cite** the syllabus
section by section. Plug it into any testing project as a git submodule and your AI assistant plans, designs
and reviews tests following the ISTQB standard, citing the section it used.

## Who is this for

- **QA engineers and test analysts** who want a shared, citable standard for test design and test planning.
- **Teams using AI coding agents** for test automation (Playwright, Cypress, Selenium, Jest, pytest…) who want
  the agent to follow recognised testing practices instead of improvising.
- **People studying for the ISTQB CTFL exam** who want a structured map of the syllabus, its 64 learning
  objectives and K-levels.

## What it covers

| QA engineering topic | Where |
|---|---|
| Test design techniques: equivalence partitioning, boundary value analysis, decision tables, state transition testing | [4.2](syllabus/04-test-analysis-and-design/4.2-black-box-test-techniques.md) · [guide](guides/black-box-techniques.md) |
| White-box testing: statement and branch coverage | [4.3](syllabus/04-test-analysis-and-design/4.3-white-box-test-techniques.md) |
| Experience-based testing: error guessing, exploratory, checklist-based | [4.4](syllabus/04-test-analysis-and-design/4.4-experience-based-test-techniques.md) |
| Acceptance criteria, user stories, ATDD/BDD/TDD | [4.5](syllabus/04-test-analysis-and-design/4.5-collaboration-based-test-approaches.md) · [2.1.3](syllabus/02-testing-throughout-the-software-development-lifecycle/2.1.3-testing-as-a-driver-for-software-development.md) |
| Test strategy, test plan, entry/exit criteria, estimation | [5.1](syllabus/05-managing-the-test-activities/5.1-test-planning.md) · [checklist](guides/test-planning-checklist.md) · [template](guides/test-plan-template.md) |
| Risk-based testing, product and project risk | [5.2](syllabus/05-managing-the-test-activities/5.2-risk-management.md) |
| Test pyramid and testing quadrants | [5.1.6](syllabus/05-managing-the-test-activities/5.1.6-test-pyramid.md) · [5.1.7](syllabus/05-managing-the-test-activities/5.1.7-testing-quadrants.md) |
| Test levels, test types, regression and confirmation testing | [2.2](syllabus/02-testing-throughout-the-software-development-lifecycle/2.2-test-levels-and-test-types.md) |
| Shift left, DevOps and CI/CD testing | [2.1.4](syllabus/02-testing-throughout-the-software-development-lifecycle/2.1.4-devops-and-testing.md) · [2.1.5](syllabus/02-testing-throughout-the-software-development-lifecycle/2.1.5-shift-left.md) |
| Static testing and reviews | [3](syllabus/03-static-testing/_index.md) |
| Defect reports, test reports, metrics | [5.5](syllabus/05-managing-the-test-activities/5.5-defect-management.md) · [5.3](syllabus/05-managing-the-test-activities/5.3-test-monitoring-test-control-and-test-completion.md) |
| Test automation benefits and risks, test tools | [6](syllabus/06-test-tools/_index.md) |

> Independent project, not affiliated with ISTQB® or BSTQB. **This repository does not contain the syllabus
> text**: it contains the structure (sections, objectives, keywords, pages), our own summaries and scripts
> that generate the full text on your machine from the official PDF. See [LEGAL-NOTICE.md](LEGAL-NOTICE.md).

## What is here

```
istqb-ai-ready/
├── CLAUDE.md            rules for AI tools: how to query, cite, and what not to do
├── llms.txt             compact index of every file (llms.txt format)
├── LEGAL-NOTICE.md      attribution to ISTQB® and conditions of use
├── LICENSE              MIT (code) · LICENSE-CONTENT.md: CC BY-NC 4.0 (our content) · CITATION.cff
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

## License

- Code (`scripts/`): [MIT](LICENSE).
- Our written content (guides, summaries, AI rules): [CC BY-NC 4.0](LICENSE-CONTENT.md).
- The ISTQB® syllabus, its structure, objectives and terminology: © ISTQB®, not covered by either license
  ([LEGAL-NOTICE.md](LEGAL-NOTICE.md)).

If this base is useful to you, cite it with the [CITATION.cff](CITATION.cff) file ("Cite this repository" on GitHub).
