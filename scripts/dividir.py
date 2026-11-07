"""build/bruto.md → um arquivo por seção numerada, em duas versões.

Uso:  python scripts/dividir.py
(rode antes: python scripts/converter.py)

syllabus/        CASCA pública (vai para o git): frontmatter, resumo nosso (dados/resumos.yaml),
                 página do PDF original, objetivos, relacionados e guias. Sem texto do syllabus.
syllabus-texto/  TEXTO INTEGRAL local (ignorado pelo git): mesmo frontmatter + texto da seção.

Os caminhos são iguais nas duas pastas: syllabus/X.md ↔ syllabus-texto/X.md.
"""
from __future__ import annotations

import json
import re
import shutil

import yaml

from comum import (
    DADOS,
    LINK_OFICIAL,
    SYLLABUS,
    TEXTO,
    VERSAO,
    caminho_relativo,
    carregar_bruto,
    segmentar,
    texto_sem_marcas,
)
from extrair_metadados import _ocorre, extrair_keywords, extrair_objetivos

# Guias práticos (pasta guias/) ligados a cada seção ou capítulo.
GUIAS = {
    "1.4": ["checklist-planejamento.md"],
    "4": ["tecnicas-caixa-preta.md"],
    "4.2": ["tecnicas-caixa-preta.md"],
    "5": ["checklist-planejamento.md", "template-plano-de-teste.md"],
    "5.1": ["checklist-planejamento.md", "template-plano-de-teste.md"],
    "5.2": ["checklist-planejamento.md", "template-plano-de-teste.md"],
}

AVISO_CASCA = (
    "> **Casca.** Este arquivo não contém o texto do syllabus. O resumo é nosso (não é texto do ISTQB).\n"
    "> Para o conteúdo exato, veja a seção e a página indicadas no PDF oficial ou o arquivo em `syllabus-texto/`."
)
AVISO_TEXTO = (
    f"> Texto do ISTQB® Certified Tester Foundation Level Syllabus v{VERSAO}, © ISTQB®.\n"
    "> Gerado localmente a partir do PDF oficial para uso pessoal. Não redistribua. Ver AVISO-LEGAL.md."
)


def _ordem(n: str) -> list[int]:
    return [int(x) for x in n.split(".")]


def guias_de(numero: str) -> list[str]:
    partes = numero.split(".")
    for i in range(len(partes), 0, -1):
        chave = ".".join(partes[:i])
        if chave in GUIAS:
            return GUIAS[chave]
    return []


def referencias(texto: str, numeros: set[str], proprio: str) -> list[str]:
    """Seções citadas no texto: "see section 2.2.3", "sections 4.2, 4.3", "chapter 2.2.1"."""
    achadas = set()
    for m in re.finditer(r"(?:sections?|chapters?)\s+((?:\d+(?:\.\d+)*(?:,\s*|\s+and\s+)?)+)", texto, flags=re.I):
        for n in re.findall(r"\d+(?:\.\d+)*", m.group(1)):
            n = n.rstrip(".")
            if n in numeros and n != proprio:
                achadas.add(n)
    return sorted(achadas, key=_ordem)


def montar(md: str, sumario: list[dict]) -> list[dict]:
    """Calcula o frontmatter e as relações de cada arquivo."""
    capitulos = {e["numero"]: e for e in sumario if e["nivel"] == 1}
    numeros = {e["numero"] for e in sumario}
    segmentos = segmentar(md, sumario)
    objetivos = extrair_objetivos(md, sumario)
    keywords = extrair_keywords(md)
    resumos = yaml.safe_load((DADOS / "resumos.yaml").read_text(encoding="utf-8"))

    itens = []
    for e in sumario:
        n = e["numero"]
        cap = n.split(".")[0]
        if cap == "0" and n != "0":
            continue  # a introdução inteira fica em 00-introducao.md
        seg = segmentos[n]
        texto = texto_sem_marcas(seg["texto"])
        if e["nivel"] == 1:
            objs = [o for o in objetivos if str(o["capitulo"]) == cap]
            kws = keywords.get(cap, [])
            # A introdução lista suas seções à parte ("Seções da introdução"), num arquivo só.
            filhos = [] if cap == "0" else [x for x in sumario if x["nivel"] == 2 and x["numero"].split(".")[0] == cap]
            relacionados: list[str] = []
        else:
            objs = [o for o in objetivos if o["secao"] == n]
            kws = [k for k in keywords.get(cap, []) if _ocorre(k, texto)]
            filhos = [x for x in sumario if x["numero"].startswith(n + ".") and x["nivel"] == e["nivel"] + 1]
            irmaos = [x["numero"] for x in sumario if x["nivel"] == e["nivel"]
                      and x["numero"].rsplit(".", 1)[0] == n.rsplit(".", 1)[0]]
            i = irmaos.index(n)
            vizinhos = irmaos[max(0, i - 1):i] + irmaos[i + 1:i + 2]
            relacionados = sorted(set(referencias(texto, numeros, n)) | set(vizinhos), key=_ordem)
        niveis = sorted({o["nivel_k"] for o in objs})
        r = resumos.get(n, {})
        itens.append(
            {
                "entrada": e,
                "caminho": caminho_relativo(e, capitulos),
                "texto": seg["texto"],
                "filhos": filhos,
                "objetivos": objs,
                "resumo": r,
                "frontmatter": {
                    "capitulo": int(cap),
                    "secao": n,
                    "titulo": e["titulo"],
                    "objetivos": [o["codigo"] for o in objs],
                    "nivel_k": niveis[-1] if niveis else None,
                    "keywords": kws,
                    # O syllabus só define tempo por capítulo; nas seções fica nulo.
                    "tempo_estudo_min": e["minutos"] if e["nivel"] == 1 else None,
                    "pagina_original": e["pagina"],
                    "relacionados": relacionados,
                    "fonte": f"ISTQB CTFL v{VERSAO}",
                },
            }
        )
    return itens


def _frontmatter(dados: dict, tipo: str) -> str:
    """Uma chave por linha; valores em JSON (que também é YAML válido).

    Assim "4.1" fica sempre entre aspas e nunca vira número decimal.
    """
    dados = {**dados, "tipo": tipo}
    linhas = [f"{chave}: {json.dumps(valor, ensure_ascii=False)}" for chave, valor in dados.items()]
    return "---\n" + "\n".join(linhas) + "\n---\n"


def _link(de: str, para: str) -> str:
    """Link relativo entre dois arquivos dentro de syllabus/."""
    origem = de.split("/")[:-1]
    destino = para.split("/")
    comum = 0
    while comum < len(origem) and comum < len(destino) - 1 and origem[comum] == destino[comum]:
        comum += 1
    return "/".join([".."] * (len(origem) - comum) + destino[comum:])


def gerar_casca(item: dict, por_numero: dict[str, dict]) -> str:
    fm, e, cam = item["frontmatter"], item["entrada"], item["caminho"]
    nivel = e["nivel"]
    titulo = f"{e['numero']}. {e['titulo']}" if e["numero"] != "0" else "0. Introduction"
    partes = [_frontmatter(fm, "casca"), f"# {titulo}\n", AVISO_CASCA + "\n"]

    resumo = item["resumo"].get("resumo") or item["resumo"].get("curto")
    if resumo:
        partes.append(f"## Resumo (nosso)\n\n{resumo.strip()}\n")

    if nivel == 1 and e["minutos"]:
        partes.append(f"**Tempo de estudo do capítulo (syllabus):** {e['minutos']} minutos.\n")

    if item["objetivos"]:
        linhas = []
        for o in item["objetivos"]:
            alvo = por_numero[o["secao"]]["caminho"]
            ref = f"[{o['secao']}]({_link(cam, alvo)})" if alvo != cam else o["secao"]
            linhas.append(f"- `{o['codigo']}` ({o['nivel_k']}): seção {ref}")
        partes.append(
            "## Objetivos de aprendizagem\n\n"
            "Código e nível K. O enunciado de cada objetivo está no syllabus oficial "
            "(ou em `syllabus-texto/_dados/objetivos-completos.json`, se gerado).\n\n" + "\n".join(linhas) + "\n"
        )

    if item["filhos"]:
        linhas = []
        for f in item["filhos"]:
            alvo = por_numero[f["numero"]]
            curto = alvo["resumo"].get("curto", "")
            linhas.append(f"- [{f['numero']} {f['titulo']}]({_link(cam, alvo['caminho'])}): {curto}")
        partes.append("## Seções\n\n" + "\n".join(linhas) + "\n")

    if e["numero"] == "0":
        linhas = []
        for n, r in item["resumo_intro"]:
            linhas.append(f"- **{n}**: {r}")
        partes.append("## Seções da introdução\n\n" + "\n".join(linhas) + "\n")

    if nivel == 1 and fm["keywords"]:
        partes.append("## Keywords do capítulo\n\n" + ", ".join(fm["keywords"]) + "\n")

    if fm["relacionados"]:
        linhas = []
        for n in fm["relacionados"]:
            alvo = por_numero.get(n)
            if alvo:
                linhas.append(f"- [{n} {alvo['entrada']['titulo']}]({_link(cam, alvo['caminho'])})")
        partes.append("## Relacionados\n\n" + "\n".join(linhas) + "\n")

    partes.append(
        "## Onde ler no original\n\n"
        f"- ISTQB® CTFL v{VERSAO}, seção **{e['numero']}**, página **{e['pagina']}** do PDF.\n"
        f"- PDF oficial: <{LINK_OFICIAL}>\n"
        f"- Texto local (se gerado com `scripts/`): `syllabus-texto/{cam}`\n"
    )

    guias = guias_de(e["numero"])
    if guias:
        prof = cam.count("/") + 1
        links = "\n".join(f"- [{g}]({'../' * prof}guias/{g})" for g in guias)
        partes.append("## Aplicação prática (nossa)\n\n" + links + "\n")

    return "\n".join(partes)


def gerar_texto(item: dict) -> str:
    return "\n".join([_frontmatter(item["frontmatter"], "texto-integral"), AVISO_TEXTO + "\n", item["texto"].strip() + "\n"])


def gerar_llms(itens: list[dict]) -> str:
    """Índice enxuto no padrão llms.txt (https://llmstxt.org)."""
    from comum import RAIZ

    linhas = [
        "# istqb-ai-ready",
        "",
        f"> Base de conhecimento de QA estruturada para IAs a partir do ISTQB® CTFL Syllabus v{VERSAO}.",
        "> Cada seção do syllabus tem um arquivo com frontmatter, resumo nosso e página do PDF original; o texto integral só existe localmente em syllabus-texto/.",
        "",
        "Leia primeiro CLAUDE.md (regras de uso). Cite sempre a seção usada, ex.: \"conforme syllabus 4.2.1\".",
        "Em syllabus/ estão as cascas (resumo nosso). Se existir syllabus-texto/<mesmo caminho>, ele tem o texto oficial da seção.",
        "",
        "## Regras e aviso",
        "",
        "- [CLAUDE.md](CLAUDE.md): como uma IA deve consultar e citar esta base",
        "- [AVISO-LEGAL.md](AVISO-LEGAL.md): atribuição ao ISTQB® e condições de uso",
        "- [README.md](README.md): o que é, como regenerar a partir do PDF, como usar em outros projetos",
        "",
        "## Guias práticos (interpretação nossa, não é syllabus)",
        "",
    ]
    for g in sorted((RAIZ / "guias").glob("*.md")):
        fm = yaml.safe_load(g.read_text(encoding="utf-8").split("---")[1])
        base = ", ".join(fm.get("baseado_em", []))
        linhas.append(f"- [guias/{g.name}](guias/{g.name}): {fm['titulo']} (baseado em {base})")
    linhas += [
        "",
        "## Dados",
        "",
        "- [dados/objetivos.json](dados/objetivos.json): os 64 objetivos de aprendizagem (código, nível K, seção, arquivo)",
        "- [dados/keywords.json](dados/keywords.json): keywords de cada capítulo",
        "- [dados/glossario.json](dados/glossario.json): termos do syllabus com seções e páginas; definição no glossário oficial do ISTQB",
        "- [dados/resumos.yaml](dados/resumos.yaml): resumos nossos de cada seção (fonte das cascas)",
        "",
        "## Syllabus (cascas)",
        "",
    ]
    for it in itens:
        e = it["entrada"]
        curto = it["resumo"].get("curto", "")
        k = f" [{it['frontmatter']['nivel_k']}]" if it["frontmatter"]["nivel_k"] and e["nivel"] > 1 else ""
        recuo = "  " if e["nivel"] == 3 else ""
        if e["nivel"] == 1:
            if linhas[-1] != "":
                linhas.append("")
            titulo = "Introdução" if e["numero"] == "0" else f"Capítulo {e['numero']}: {e['titulo']}"
            linhas.append(f"### {titulo}")
            linhas.append("")
        linhas.append(f"{recuo}- [{e['numero']} {e['titulo']}](syllabus/{it['caminho']}){k}: {curto}")
    linhas += [
        "",
        "## Optional",
        "",
        f"- [Syllabus oficial (PDF)]({LINK_OFICIAL}): fonte primária, use quando precisar do texto exato e não houver syllabus-texto/",
        "- [Glossário oficial ISTQB](https://glossary.istqb.org/): definições dos termos",
        "- [scripts/](scripts/): pipeline PDF → markdown (converter, dividir, extrair_metadados, validar)",
        "",
    ]
    return "\n".join(linhas)


def main() -> None:
    md, sumario = carregar_bruto()
    itens = montar(md, sumario)
    por_numero: dict[str, dict] = {}
    for it in itens:
        por_numero[it["entrada"]["numero"]] = it
    # Seções 0.x apontam para o arquivo único da introdução.
    resumos = yaml.safe_load((DADOS / "resumos.yaml").read_text(encoding="utf-8"))
    intro = por_numero["0"]
    intro["resumo_intro"] = [
        (f"{e['numero']} {e['titulo']}", resumos.get(e["numero"], {}).get("curto", ""))
        for e in sumario if e["numero"].startswith("0.")
    ]
    for e in sumario:
        if e["numero"].startswith("0."):
            por_numero[e["numero"]] = intro

    for pasta in (SYLLABUS, TEXTO):
        if pasta.exists():
            for filho in pasta.iterdir():
                if filho.name != "_dados":
                    shutil.rmtree(filho) if filho.is_dir() else filho.unlink()
        pasta.mkdir(exist_ok=True)

    for it in itens:
        for pasta, conteudo in ((SYLLABUS, gerar_casca(it, por_numero)), (TEXTO, gerar_texto(it))):
            destino = pasta / it["caminho"]
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(conteudo, encoding="utf-8")

    from comum import RAIZ

    (RAIZ / "llms.txt").write_text(gerar_llms(itens), encoding="utf-8")
    print(f"OK: {len(itens)} arquivos em syllabus/ (casca) e syllabus-texto/ (texto local)")
    print("OK: llms.txt")


if __name__ == "__main__":
    main()
