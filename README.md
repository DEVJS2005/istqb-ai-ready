# istqb-ai-ready

Base de conhecimento de QA construída sobre o **ISTQB® Certified Tester Foundation Level (CTFL)
Syllabus v4.0.1**, organizada para que IAs (Claude Code e outras) consigam **ler, buscar e citar**
o syllabus seção por seção. Serve de guia de boas práticas para outros projetos de teste.

> Projeto independente, sem vínculo com o ISTQB® ou o BSTQB. **Este repositório não contém o texto
> do syllabus**: contém a estrutura (seções, objetivos, keywords, páginas), resumos nossos e scripts
> que geram o texto integral na sua máquina a partir do PDF oficial. Veja [AVISO-LEGAL.md](AVISO-LEGAL.md).

## O que tem aqui

```
istqb-ai-ready/
├── CLAUDE.md            regras para IAs: como consultar, citar e o que não fazer
├── llms.txt             índice enxuto de todos os arquivos (padrão llms.txt)
├── AVISO-LEGAL.md       atribuição ao ISTQB® e condições de uso
├── syllabus/            CASCA: 1 arquivo por seção (86), com frontmatter + resumo nosso + página do PDF
├── syllabus-texto/      TEXTO INTEGRAL (mesmos caminhos), gerado localmente, fora do git
├── dados/
│   ├── objetivos.json   64 objetivos de aprendizagem (código, nível K, seção, arquivo)
│   ├── glossario.json   265 termos com seções e páginas, mais o link do glossário oficial
│   ├── keywords.json    102 keywords, por capítulo
│   └── resumos.yaml     nossos resumos de cada seção (fonte das cascas)
├── guias/               aplicação prática, escrita por nós (não é syllabus)
│   ├── checklist-planejamento.md
│   ├── tecnicas-caixa-preta.md
│   └── template-plano-de-teste.md
├── scripts/             pipeline PDF → markdown
└── fonte/               coloque aqui o PDF oficial (ignorado pelo git)
```

Cada seção tem um frontmatter como este:

```yaml
---
capitulo: 4
secao: "4.2.1"
titulo: "Equivalence Partitioning"
objetivos: ["FL-4.2.1"]
nivel_k: "K3"
keywords: ["coverage", "coverage item", "equivalence partitioning", "test technique"]
tempo_estudo_min: null      # o syllabus só define tempo por capítulo
pagina_original: 39
relacionados: ["4.2.2"]
fonte: "ISTQB CTFL v4.0.1"
tipo: "casca"
---
```

O texto do syllabus fica em inglês, que é o idioma do PDF usado. Resumos, guias e regras estão em português.

## Como foi gerado

| Script | Faz |
|---|---|
| `scripts/converter.py` | PDF → `build/bruto.md` com pymupdf4llm. Recorta cabeçalho e rodapé de cada página, normaliza os títulos pelo sumário, corrige hifenização e marca a página de origem (`<!-- pagina: N -->`). |
| `scripts/extrair_metadados.py` | Objetivos (listas dos capítulos), keywords e termos do índice → `dados/*.json`. |
| `scripts/dividir.py` | Um arquivo por seção em `syllabus/` (casca) e `syllabus-texto/` (texto local), mais `_index.md` por capítulo e `llms.txt`. |
| `scripts/validar.py` | Confere seções × sumário, objetivos × PDF × Apêndice B, palavras (diferença em %), frontmatter, links, ausência de texto do syllabus na casca e `.gitignore`. |

Última validação (PDF v4.0.1): 97/97 entradas do sumário, 64/64 objetivos (níveis K conferem com o
Apêndice B), palavras −0,01%, 175 frontmatters válidos, 0 trechos do syllabus na casca, links ok.

## Como regenerar a partir do PDF

Requisitos: Python 3.10+.

1. Baixe o PDF oficial do CTFL v4.0.1 em <https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/> e salve em `fonte/`.
2. Crie o ambiente e rode o pipeline:

```bash
python -m venv .venv
```

```bash
.venv/Scripts/pip install -r requirements.txt      # Linux/macOS: .venv/bin/pip
```

```bash
.venv/Scripts/python scripts/converter.py && .venv/Scripts/python scripts/extrair_metadados.py && .venv/Scripts/python scripts/dividir.py && .venv/Scripts/python scripts/validar.py
```

Isso cria `syllabus-texto/`, que fica só na sua máquina. Use para busca offline e para a IA ler o
texto oficial. **Não commite nem redistribua essa pasta.**

Para mudar um resumo, edite `dados/resumos.yaml` e rode de novo `scripts/dividir.py`. Não edite
`syllabus/` à mão.

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

### 3. (Opcional) Gerar o texto integral dentro do submodule

Repita os passos de "Como regenerar" dentro de `docs/istqb-ai-ready/`. Sem isso, a IA trabalha
com as cascas e indica a página do PDF quando precisar do texto exato.

### 4. CI (GitHub Actions)

Se o workflow do projeto precisar da base, faça o checkout com submodules:

```yaml
- uses: actions/checkout@v4
  with:
    submodules: true
```

Enquanto este repositório for privado, o checkout do submodule no CI precisa de um token com
acesso a ele (`token:` no `actions/checkout`).

## Atribuição

Conteúdo derivado do **ISTQB® Certified Tester Foundation Level Syllabus v4.0.1**, © International
Software Testing Qualifications Board (ISTQB®). ISTQB® é marca registrada do International Software
Testing Qualifications Board. Os autores e o ISTQB® são a fonte e os titulares do copyright do
syllabus. Página oficial: <https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/>.
No Brasil: BSTQB, <https://bstqb.org.br>. Detalhes e condições de uso em [AVISO-LEGAL.md](AVISO-LEGAL.md).

Os scripts, resumos e guias deste repositório são de autoria dos mantenedores. Uso não comercial.
