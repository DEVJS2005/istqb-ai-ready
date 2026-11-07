# CLAUDE.md: como uma IA deve usar esta base

Este repositório é uma base de conhecimento de QA construída sobre o **ISTQB® Certified Tester
Foundation Level (CTFL) Syllabus v4.0.1**. Serve de guia de boas práticas para planejar, projetar,
revisar e relatar testes em outros projetos. Estas regras valem para o Claude Code e para qualquer
outra IA que leia a base.

> **Usado como submodule?** Todos os caminhos abaixo são relativos à pasta desta base
> (ex.: `docs/istqb-ai-ready/llms.txt` no projeto que a incluiu).

## Mapa rápido

| Pasta / arquivo | O que é | Origem |
|---|---|---|
| `llms.txt` | Índice de tudo, com uma linha por arquivo | gerado |
| `syllabus/` | **Casca**: um arquivo por seção, com frontmatter, resumo **nosso**, objetivos, relacionados e página do PDF | gerado + nosso |
| `syllabus-texto/` | **Texto integral** de cada seção (mesmos caminhos de `syllabus/`). Só existe na máquina de quem gerou a partir do PDF. **Não está no git.** | ISTQB |
| `dados/objetivos.json` | 64 objetivos de aprendizagem (código, K, seção, arquivo) | gerado |
| `dados/glossario.json` | Termos do syllabus, com seções e páginas onde aparecem. As definições ficam no glossário oficial | gerado |
| `dados/keywords.json` | Keywords de cada capítulo | gerado |
| `guias/` | Aplicação prática: checklists, templates, exemplos | **nosso** (interpretação) |

## Regras

1. **Consulte primeiro o `llms.txt`** ao planejar ou revisar testes. Escolha as seções relevantes
   e leia **só** essas. Não carregue a base inteira.
   - Para achar uma seção por objetivo: `dados/objetivos.json`.
   - Para achar uma seção por termo: `dados/glossario.json` (campo `secoes`).
   - Para seguir um assunto: o campo `relacionados` do frontmatter.

2. **Prefira o texto oficial quando existir.** Para cada `syllabus/<caminho>.md`, verifique se existe
   `syllabus-texto/<caminho>.md`:
   - **Existe:** use-o como fonte do conteúdo. Ele é o texto do syllabus.
   - **Não existe:** use o resumo da casca e avise que é um resumo. Se precisar do texto exato:
     - com acesso à web, consulte o PDF oficial (link em `AVISO-LEGAL.md`) e vá direto à página
       em `pagina_original`;
     - sem acesso à web, diga ao usuário a seção e a página para ele ler, ou sugira gerar o texto
       local (`python scripts/converter.py && python scripts/dividir.py`, ver `README.md`).

3. **Sempre cite a seção usada**, no formato: _"conforme syllabus 4.2.1"_ ou
   _"(ISTQB CTFL v4.0.1, 4.2.1)"_. Ao citar um objetivo, use o código: _"FL-4.2.1 (K3)"_.

4. **Use a terminologia do glossário; não invente termos.** Os termos estão em `dados/glossario.json`
   e nas `keywords` do frontmatter, e a definição oficial está em <https://glossary.istqb.org/>. Em
   português, use o termo consagrado e mostre o original na primeira menção, ex.: "particionamento de
   equivalência (equivalence partitioning)". Não crie nomes novos para técnicas, níveis, tipos ou papéis.

5. **Diferencie o que é syllabus do que é interpretação nossa.**
   - `syllabus-texto/` = texto do ISTQB.
   - `syllabus/` = estrutura do ISTQB + **resumo nosso** (marcado como "Resumo (nosso)").
   - `guias/` = **interpretação nossa**. Ao usar um guia, deixe isso claro: _"segundo o guia
     interno tecnicas-caixa-preta.md (baseado no syllabus 4.2.2)"_.

6. **Se a base não cobre o assunto, diga isso** em vez de inventar. Exemplos fora do escopo do CTFL:
   teste de performance em profundidade, segurança avançada, ferramentas específicas (Cypress,
   Playwright, JMeter…), métricas de mercado. Responda: _"O syllabus CTFL não cobre isso; o mais
   próximo é a seção X"_. Se for responder com conhecimento geral, marque como tal.

7. **Não reproduza o syllabus em bloco** em respostas, commits ou arquivos de outros projetos.
   Cite a seção e parafraseie. Trechos curtos com citação da fonte são aceitáveis; cópias extensas,
   não (ver `AVISO-LEGAL.md`).

## Fluxos comuns

- **Planejar testes de uma feature:** `guias/checklist-planejamento.md` → seções 5.1.x, 5.2.x
  → `guias/template-plano-de-teste.md`.
- **Projetar casos de teste:** `syllabus/04-test-analysis-and-design/_index.md` → técnica
  (4.2.1 a 4.2.4, 4.4.x) → `guias/tecnicas-caixa-preta.md`.
- **Revisar um artefato (story, requisito, plano):** 3.2.2 a 3.2.5, 4.5.1 e 4.5.2.
- **Relatar defeito ou status:** 5.5, 5.3.2 e 5.3.3.
- **Discutir estratégia de automação:** 5.1.6, 5.1.7, 6.2 e 2.1.4.

## Frontmatter de cada seção

```yaml
capitulo: 4                       # número do capítulo
secao: "4.2.1"                    # sempre string
titulo: "Equivalence Partitioning"  # título original (inglês)
objetivos: ["FL-4.2.1"]           # códigos de objetivo desta seção
nivel_k: "K3"                     # maior nível K entre os objetivos (null se não houver)
keywords: [...]                   # keywords do capítulo presentes nesta seção
tempo_estudo_min: null            # o syllabus só define tempo por capítulo (_index.md)
pagina_original: 39               # página do PDF v4.0.1
relacionados: ["4.2.2"]           # seções citadas no texto e seções vizinhas
fonte: "ISTQB CTFL v4.0.1"
tipo: "casca"                     # "casca" em syllabus/, "texto-integral" em syllabus-texto/
```

## Manutenção (para quem edita este repositório)

- Não edite `syllabus/`, `dados/*.json` nem `llms.txt` à mão: são gerados. Para mudar um resumo,
  edite `dados/resumos.yaml` e rode `python scripts/dividir.py`.
- Antes de commitar, rode `python scripts/validar.py`.
- Nunca commite `fonte/*.pdf`, `build/` ou `syllabus-texto/`.
