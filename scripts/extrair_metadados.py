"""Extrai metadados do syllabus: objetivos de aprendizagem, keywords e termos do índice.

Uso:  python scripts/extrair_metadados.py [caminho/do/syllabus.pdf]
(rode antes: python scripts/converter.py)

Gera (vão para o git, sem texto do syllabus):
  dados/objetivos.json   código, nível K, seção e arquivos de cada objetivo
  dados/keywords.json    keywords de cada capítulo
  dados/glossario.json   termos (keywords + índice) com seções/páginas e link do glossário oficial

Gera (local, ignorado pelo git, pois contém frases do syllabus):
  syllabus-texto/_dados/objetivos-completos.json   inclui o texto de cada objetivo
"""
from __future__ import annotations

import json
import re
import sys

from comum import (
    DADOS,
    LINK_GLOSSARIO,
    LINK_OFICIAL,
    TEXTO,
    VERSAO,
    achar_pdf,
    caminho_relativo,
    carregar_bruto,
    segmentar,
    texto_sem_marcas,
)

RE_OBJETIVO = re.compile(r"(FL-(\d+)\.(\d+)\.(\d+))\s+\((K[1-3])\)\s+(.+?)\s*$")


def extrair_objetivos(md: str, sumario: list[dict]) -> list[dict]:
    """Lê as listas "Learning Objectives for Chapter N" do início de cada capítulo."""
    numeros = {e["numero"] for e in sumario}
    capitulos = {e["numero"]: e for e in sumario if e["nivel"] == 1}
    titulos = {e["numero"]: e["titulo"] for e in sumario}
    objetivos = []
    vistos = set()
    em_lista = False
    for linha in md.splitlines():
        s = re.sub(r"^[-#\s]+", "", linha).strip()
        if s.startswith("Learning Objectives for Chapter"):
            em_lista = True
            continue
        if linha.startswith("<!-- pagina:"):
            em_lista = False
            continue
        if not em_lista:
            continue
        m = RE_OBJETIVO.match(s)
        if not m or m.group(1) in vistos:
            continue
        codigo, c, s1, s2, k, texto = m.groups()
        vistos.add(codigo)
        # FL-a.b.c corresponde à seção a.b.c; se ela não existir, à seção a.b.
        secao = f"{c}.{s1}.{s2}" if f"{c}.{s1}.{s2}" in numeros else f"{c}.{s1}"
        entrada = next(e for e in sumario if e["numero"] == secao)
        objetivos.append(
            {
                "codigo": codigo,
                "nivel_k": k,
                "capitulo": int(c),
                "secao": secao,
                "titulo_secao": titulos[secao],
                "arquivo": "syllabus/" + caminho_relativo(entrada, capitulos),
                "arquivo_texto": "syllabus-texto/" + caminho_relativo(entrada, capitulos),
                "texto": texto,
            }
        )
    return objetivos


def extrair_keywords(md: str) -> dict[str, list[str]]:
    """Lê o bloco "Keywords" logo abaixo do título de cada capítulo."""
    resultado: dict[str, list[str]] = {}
    for m in re.finditer(r"^# (\d+)\. [^\n]*\n+#### Keywords\n+((?:(?!####).)+)", md, flags=re.M | re.S):
        termos = [t.strip() for t in m.group(2).replace("\n", " ").split(",") if t.strip()]
        resultado[m.group(1)] = termos
    return resultado


def extrair_indice(pdf) -> list[dict]:
    """Lê o Índice (cap. 11) do texto cru do PDF, que já vem uma entrada por linha."""
    import pymupdf

    doc = pymupdf.open(pdf)
    inicio = next(i for i in range(doc.page_count - 1, 0, -1) if "11. Index" in doc[i].get_text())
    linhas = []
    for i in range(inicio, doc.page_count):
        txt = doc[i].get_text()
        if i == inicio:
            txt = txt.split("11. Index", 1)[1]
        else:
            txt = txt.split("Qualifications Board", 1)[-1]
        linhas += [l.strip() for l in txt.splitlines() if l.strip()]

    entradas: list[str] = []
    for l in linhas:
        if re.fullmatch(r"[\d,\s]+", l) and entradas:
            entradas[-1] += " " + l   # continuação da lista de páginas
        else:
            entradas.append(l)

    termos = []
    for e in entradas:
        e = e.strip().rstrip(",")
        ver = re.match(r"(.+?),\s*See\s+(.+)$", e)
        if ver:
            termos.append({"termo": ver.group(1).strip(), "ver": ver.group(2).strip(), "paginas": []})
            continue
        m = re.match(r"(.+?),\s*([\d,\s]+)$", e)
        if m:
            pags = [int(p) for p in re.findall(r"\d+", m.group(2))]
            termos.append({"termo": m.group(1).strip(), "paginas": pags})
    return termos


def _ocorre(termo: str, texto: str) -> bool:
    base = re.sub(r"\s*\(.*?\)$", "", termo)  # "author (reviews)" -> "author"
    # Hífen e espaço são intercambiáveis ("V model" = "V-model", "shift-left" = "shift left").
    padrao = r"[\s-]".join(re.escape(p) for p in re.split(r"[\s-]+", base))
    return re.search(rf"(?<![\w-]){padrao}(s|es)?(?![\w-])", texto, flags=re.I) is not None


def _ordem(n: str) -> list[int]:
    return [int(x) for x in n.split(".")]


def secoes_por_pagina(termo: str, paginas: list[int], segmentos: dict[str, dict]) -> tuple[list[str], bool]:
    """Seções que cobrem as páginas do índice e cujo texto contém o termo.

    Se o termo não aparecer literalmente (grafia diferente no índice), devolve as seções
    daquela página e marca o resultado como aproximado.
    """
    candidatas = [n for n, s in segmentos.items() if "." in n and set(paginas) & set(s["paginas"])]
    achadas = [n for n in candidatas if _ocorre(termo, texto_sem_marcas(segmentos[n]["texto"]))]
    if achadas:
        return sorted(achadas, key=_ordem), False
    return sorted(candidatas, key=_ordem), True


def montar_glossario(keywords: dict[str, list[str]], indice: list[dict], segmentos: dict[str, dict]) -> list[dict]:
    por_termo: dict[str, dict] = {}
    for item in indice:
        chave = item["termo"].lower()
        secoes, aprox = secoes_por_pagina(item["termo"], item["paginas"], segmentos) if item["paginas"] else ([], False)
        por_termo[chave] = {
            "termo": item["termo"],
            "keyword_dos_capitulos": [],
            "paginas_indice": item["paginas"],
            "secoes": secoes,
        }
        if aprox:
            por_termo[chave]["secoes_aproximadas"] = True
        if "ver" in item:
            por_termo[chave]["ver"] = item["ver"]
    for cap, termos in keywords.items():
        for t in termos:
            chave = t.lower()
            if chave not in por_termo:
                secoes = [n for n, s in segmentos.items() if n.split(".")[0] == cap and n != cap
                          and _ocorre(t, texto_sem_marcas(s["texto"]))]
                por_termo[chave] = {"termo": t, "keyword_dos_capitulos": [], "paginas_indice": [], "secoes": secoes}
            por_termo[chave]["keyword_dos_capitulos"].append(int(cap))
    lista = sorted(por_termo.values(), key=lambda x: x["termo"].lower())
    for item in lista:
        item["definicao"] = None
        item["glossario_oficial"] = LINK_GLOSSARIO
    return lista


def main() -> None:
    pdf = achar_pdf(sys.argv[1] if len(sys.argv) > 1 else None)
    md, sumario = carregar_bruto()
    segmentos = segmentar(md, sumario)

    objetivos = extrair_objetivos(md, sumario)
    keywords = extrair_keywords(md)
    indice = extrair_indice(pdf)
    glossario = montar_glossario(keywords, indice, segmentos)

    DADOS.mkdir(exist_ok=True)
    cabecalho = {
        "fonte": f"ISTQB Certified Tester Foundation Level Syllabus v{VERSAO}",
        "link_oficial": LINK_OFICIAL,
        "aviso": "Metadados de referência. O texto do syllabus não é reproduzido; consulte o PDF oficial.",
    }
    publicos = [{k: v for k, v in o.items() if k != "texto"} for o in objetivos]
    (DADOS / "objetivos.json").write_text(
        json.dumps({**cabecalho, "total": len(publicos), "objetivos": publicos}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (DADOS / "keywords.json").write_text(
        json.dumps(
            {**cabecalho, "por_capitulo": {c: {"total": len(t), "keywords": t} for c, t in keywords.items()}},
            ensure_ascii=False, indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    (DADOS / "glossario.json").write_text(
        json.dumps(
            {
                **cabecalho,
                "observacao": (
                    "O syllabus não traz definições próprias: alinha seus termos ao glossário oficial do ISTQB. "
                    "Aqui ficam só os termos (keywords dos capítulos e entradas do índice), onde aparecem "
                    "e o link para a definição oficial."
                ),
                "glossario_oficial": LINK_GLOSSARIO,
                "total": len(glossario),
                "termos": glossario,
            },
            ensure_ascii=False, indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    (TEXTO / "_dados").mkdir(parents=True, exist_ok=True)
    (TEXTO / "_dados" / "objetivos-completos.json").write_text(
        json.dumps({**cabecalho, "total": len(objetivos), "objetivos": objetivos}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"OK: dados/objetivos.json ({len(objetivos)} objetivos)")
    print(f"OK: dados/keywords.json ({sum(len(t) for t in keywords.values())} keywords em {len(keywords)} capítulos)")
    print(f"OK: dados/glossario.json ({len(glossario)} termos)")
    print("OK: syllabus-texto/_dados/objetivos-completos.json (local)")


if __name__ == "__main__":
    main()
