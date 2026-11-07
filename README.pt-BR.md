# istqb-ai-ready: syllabus ISTQB CTFL para IAs e engenharia de QA

[![License: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![Content: CC BY-NC 4.0](https://img.shields.io/badge/content-CC%20BY--NC%204.0-lightgrey.svg)](LICENSE-CONTENT.md)
[![ISTQB CTFL v4.0.1](https://img.shields.io/badge/ISTQB%20CTFL-v4.0.1-0a7bbb.svg)](https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/)
[![llms.txt](https://img.shields.io/badge/llms.txt-ready-green.svg)](llms.txt)

*Read in English: [README.md](README.md)*

**Base de conhecimento de engenharia de QA** e **padrão de boas práticas de teste de software** construída
sobre o **ISTQB® Certified Tester Foundation Level (CTFL) Syllabus v4.0.1**, organizada para que agentes de
IA (Claude Code, Cursor, Copilot e qualquer ferramenta que leia `llms.txt`) consigam **ler, buscar e citar**
o syllabus seção por seção. Conecte como git submodule em qualquer projeto de testes e o seu assistente de IA
passa a planejar, projetar e revisar testes seguindo o padrão ISTQB, citando a seção usada.

## Para quem é

- **Analistas e engenheiros de QA** que querem um padrão comum e citável para modelagem e planejamento de testes.
- **Times que usam agentes de IA** na automação de testes (Playwright, Cypress, Selenium, Jest, pytest…) e querem
  que o agente siga práticas reconhecidas em vez de improvisar.
- **Quem estuda para a certificação ISTQB CTFL (BSTQB)** e quer um mapa estruturado do syllabus, dos 64 objetivos
  de aprendizagem e dos níveis K.

## O que cobre

| Tema de engenharia de QA | Onde |
|---|---|
| Técnicas de teste caixa-preta: particionamento de equivalência, análise de valor limite, tabela de decisão, transição de estados | [4.2](syllabus/04-test-analysis-and-design/4.2-black-box-test-techniques.md) · [guia](guides/black-box-techniques.md) |
| Teste caixa-branca: cobertura de instrução e de ramo | [4.3](syllabus/04-test-analysis-and-design/4.3-white-box-test-techniques.md) |
| Técnicas baseadas em experiência: suposição de erro, teste exploratório, checklist | [4.4](syllabus/04-test-analysis-and-design/4.4-experience-based-test-techniques.md) |
| Critérios de aceite, user stories, ATDD/BDD/TDD | [4.5](syllabus/04-test-analysis-and-design/4.5-collaboration-based-test-approaches.md) · [2.1.3](syllabus/02-testing-throughout-the-software-development-lifecycle/2.1.3-testing-as-a-driver-for-software-development.md) |
| Estratégia e plano de teste, critérios de entrada e saída, estimativa | [5.1](syllabus/05-managing-the-test-activities/5.1-test-planning.md) · [checklist](guides/test-planning-checklist.md) · [template](guides/test-plan-template.md) |
| Teste baseado em risco, riscos de produto e de projeto | [5.2](syllabus/05-managing-the-test-activities/5.2-risk-management.md) |
| Pirâmide de teste e quadrantes de teste | [5.1.6](syllabus/05-managing-the-test-activities/5.1.6-test-pyramid.md) · [5.1.7](syllabus/05-managing-the-test-activities/5.1.7-testing-quadrants.md) |
| Níveis e tipos de teste, teste de regressão e de confirmação | [2.2](syllabus/02-testing-throughout-the-software-development-lifecycle/2.2-test-levels-and-test-types.md) |
| Shift left, DevOps e testes em CI/CD | [2.1.4](syllabus/02-testing-throughout-the-software-development-lifecycle/2.1.4-devops-and-testing.md) · [2.1.5](syllabus/02-testing-throughout-the-software-development-lifecycle/2.1.5-shift-left.md) |
| Teste estático e revisões | [3](syllabus/03-static-testing/_index.md) |
| Relatório de defeito, relatórios de teste, métricas | [5.5](syllabus/05-managing-the-test-activities/5.5-defect-management.md) · [5.3](syllabus/05-managing-the-test-activities/5.3-test-monitoring-test-control-and-test-completion.md) |
| Benefícios e riscos da automação, ferramentas de teste | [6](syllabus/06-test-tools/_index.md) |

> Projeto independente, sem vínculo com o ISTQB® ou o BSTQB. **Este repositório não contém o texto
> do syllabus**: contém a estrutura (seções, objetivos, keywords, páginas), resumos nossos e scripts
> que geram o texto integral na sua máquina a partir do PDF oficial. Veja [LEGAL-NOTICE.md](LEGAL-NOTICE.md).

O repositório está em inglês (pastas, campos, resumos, guias e regras para IA). Este arquivo é a versão
em português do README. O texto do syllabus também é em inglês, que é o idioma do PDF usado.

## O que tem aqui

```
istqb-ai-ready/
├── CLAUDE.md            regras para IAs: como consultar, citar e o que não fazer
├── llms.txt             índice enxuto de todos os arquivos (padrão llms.txt)
├── LEGAL-NOTICE.md      atribuição ao ISTQB® e condições de uso
├── LICENSE              MIT (código) · LICENSE-CONTENT.md: CC BY-NC 4.0 (nosso conteúdo) · CITATION.cff
├── README.md            versão em inglês · README.pt-BR.md (este arquivo)
├── syllabus/            CASCA (shell): 1 arquivo por seção (86), com frontmatter + resumo nosso + página do PDF
├── syllabus-text/       TEXTO INTEGRAL (mesmos caminhos), gerado localmente, fora do git
├── data/
│   ├── objectives.json  64 objetivos de aprendizagem (código, nível K, seção, arquivo)
│   ├── glossary.json    265 termos com seções e páginas, mais o link do glossário oficial
│   ├── keywords.json    102 keywords, por capítulo
│   └── summaries.yaml   nossos resumos de cada seção (fonte das cascas)
├── guides/              aplicação prática, escrita por nós (não é syllabus)
│   ├── black-box-techniques.md       técnicas caixa-preta na prática
│   ├── test-planning-checklist.md    checklist de planejamento de teste
│   └── test-plan-template.md         template de plano de teste
├── scripts/             pipeline PDF → markdown
└── source/              coloque aqui o PDF oficial (ignorado pelo git)
```

Cada seção tem um frontmatter como este:

```yaml
---
chapter: 4
section: "4.2.1"
title: "Equivalence Partitioning"
objectives: ["FL-4.2.1"]
k_level: "K3"
keywords: ["coverage", "coverage item", "equivalence partitioning", "test technique"]
study_time_min: null      # o syllabus só define tempo por capítulo
source_page: 39
related: ["4.2.2"]
source: "ISTQB CTFL v4.0.1"
type: "shell"
---
```

## Como foi gerado

| Script | Faz |
|---|---|
| `scripts/convert.py` | PDF → `build/raw.md` com pymupdf4llm. Recorta cabeçalho e rodapé de cada página, normaliza os títulos pelo sumário, corrige hifenização e marca a página de origem (`<!-- page: N -->`). |
| `scripts/extract_metadata.py` | Objetivos (listas dos capítulos), keywords e termos do índice → `data/*.json`. |
| `scripts/split.py` | Um arquivo por seção em `syllabus/` (casca) e `syllabus-text/` (texto local), mais `_index.md` por capítulo e `llms.txt`. |
| `scripts/validate.py` | Confere seções × sumário, objetivos × PDF × Apêndice B, palavras (diferença em %), frontmatter, links, ausência de texto do syllabus na casca e `.gitignore`. |

## Como regenerar a partir do PDF

Requisitos: Python 3.10+.

1. Baixe o PDF oficial do CTFL v4.0.1 em <https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/> e salve em `source/`.
2. Crie o ambiente e rode o pipeline:

```bash
python -m venv .venv
```

```bash
.venv/Scripts/pip install -r requirements.txt      # Linux/macOS: .venv/bin/pip
```

```bash
.venv/Scripts/python scripts/convert.py && .venv/Scripts/python scripts/extract_metadata.py && .venv/Scripts/python scripts/split.py && .venv/Scripts/python scripts/validate.py
```

Isso cria `syllabus-text/`, que fica só na sua máquina. Use para busca offline e para a IA ler o texto
oficial. **Não commite nem redistribua essa pasta.**

Para mudar um resumo, edite `data/summaries.yaml` e rode de novo `scripts/split.py`. Não edite `syllabus/` à mão.

## Como usar com Claude Code em outro projeto

### 1. Adicionar como submodule

No projeto de testes:

```bash
git submodule add https://github.com/DEVJS2005/istqb-ai-ready.git docs/istqb-ai-ready
```

Quem clonar o projeto depois deve usar `git clone --recurse-submodules`, ou rodar
`git submodule update --init` depois do clone. Para atualizar a base: `git submodule update --remote docs/istqb-ai-ready`.

### 2. Apontar o CLAUDE.md do projeto para a base

Adicione ao `CLAUDE.md` do projeto (o Claude Code entende `@caminho` como importação de arquivo):

```markdown
## Base de boas práticas de QA (ISTQB CTFL)
@docs/istqb-ai-ready/CLAUDE.md

- Ao planejar, projetar ou revisar testes, consulte primeiro `docs/istqb-ai-ready/llms.txt`.
- Cite a seção do syllabus usada (ex.: "conforme syllabus 4.2.1").
```

As regras importadas estão em inglês, mas valem para respostas em qualquer idioma. Em português, a IA deve
usar o termo consagrado e mostrar o original na primeira menção, ex.: "particionamento de equivalência
(equivalence partitioning)".

### 3. (Opcional) Gerar o texto integral dentro do submodule

Repita os passos de "Como regenerar" dentro de `docs/istqb-ai-ready/`. Sem isso, a IA trabalha com as cascas
e indica a página do PDF quando precisar do texto exato.

### 4. CI (GitHub Actions)

Se o workflow do projeto precisar da base, faça o checkout com submodules:

```yaml
- uses: actions/checkout@v4
  with:
    submodules: true
```

## Atribuição

Conteúdo derivado do **ISTQB® Certified Tester Foundation Level Syllabus v4.0.1**, © International Software
Testing Qualifications Board (ISTQB®). ISTQB® é marca registrada do International Software Testing Qualifications
Board. Os autores e o ISTQB® são a fonte e os titulares do copyright do syllabus. Página oficial:
<https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/>. No Brasil: BSTQB,
<https://bstqb.org.br>, que publica a tradução oficial em português. Detalhes e condições de uso em
[LEGAL-NOTICE.md](LEGAL-NOTICE.md).

## Licença

- Código (`scripts/`): [MIT](LICENSE).
- Nosso conteúdo escrito (guias, resumos, regras para IA): [CC BY-NC 4.0](LICENSE-CONTENT.md).
- O syllabus ISTQB®, sua estrutura, objetivos e terminologia: © ISTQB®, fora de ambas as licenças
  ([LEGAL-NOTICE.md](LEGAL-NOTICE.md)).

Se esta base for útil, cite-a pelo arquivo [CITATION.cff](CITATION.cff) (botão "Cite this repository" no GitHub).
