"""PDF do syllabus → build/bruto.md (markdown limpo, com marcadores de página).

Uso:  python scripts/converter.py [caminho/do/syllabus.pdf]

- Remove cabeçalhos e rodapés repetidos e números de página.
- Insere <!-- pagina: N --> no início de cada página, para rastrear a origem.
- Normaliza os títulos numerados (1. / 1.1. / 1.1.1.) para #, ##, ###.
- Junta palavras com hifenização quebrada no fim de linha.
- Mantém tabelas e listas no formato markdown gerado pelo pymupdf4llm.
"""
from __future__ import annotations

import json
import re
import sys

import pymupdf
import pymupdf4llm

from comum import BRUTO, BUILD, achar_pdf, ler_sumario



def area_util(pag: "pymupdf.Page") -> "pymupdf.Rect":
    """Retângulo da página sem o cabeçalho e o rodapé repetidos.

    Cabeçalho: bloco "Certified Tester / Foundation Level" (+24pt de folga com linhas vazias).
    Rodapé: bloco "v4.0.1 / Page X of 78 / data".
    """
    r = pag.mediabox
    topo, base = r.y0, r.y1
    for x0, y0, x1, y1, txt, *_ in pag.get_text("blocks"):
        if txt.strip().startswith("Certified Tester") and y0 < r.y1 * 0.2:
            topo = max(topo, y1 + 24)
        if re.search(r"Page \d+ of \d+", txt) and y0 > r.y1 * 0.7:
            base = min(base, y0 - 2)
    return pymupdf.Rect(r.x0, topo, r.x1, base)

# Linhas de cabeçalho/rodapé que se repetem em todas as páginas.
LIXO = [
    re.compile(r"^\**Certified Tester\s*Foundation Level\**$"),
    re.compile(r"^\**Certified Tester\**$"),
    re.compile(r"^\**Foundation Level\**$"),
    re.compile(r"^\**Page \d+ of \d+\**$"),
    re.compile(r"^\**v4\.0\.1\**$"),
    re.compile(r"^\**2024-09-15\**$"),
    re.compile(r"^\**©\s*International Software Testing Qualifications Board\**$"),
]


def limpar_pagina(texto: str) -> str:
    linhas = []
    for linha in texto.splitlines():
        s = linha.strip()
        if any(p.match(s) for p in LIXO):
            continue
        linhas.append(linha.rstrip())
    return "\n".join(linhas).strip()


def normalizar_titulos(md: str, sumario: list[dict]) -> str:
    """Garante que cada entrada do sumário vire um título markdown com o nível certo."""
    por_numero = {e["numero"]: e for e in sumario}
    saida = []
    em_objetivos = False  # dentro de "Learning Objectives for Chapter N" (até a próxima página)
    for linha in md.splitlines():
        s = re.sub(r"\*\*|__", "", linha).strip()
        s = re.sub(r"^#+\s*", "", s)
        if s.startswith("<!-- pagina:"):
            em_objetivos = False
        elif s.startswith("Learning Objectives for Chapter"):
            em_objetivos = True
        m = re.match(r"^(\d+(?:\.\d+)*)\.?\s+(.+?)\s*$", s)
        if em_objetivos and m:
            # Subtítulo da lista de objetivos: não é o início da seção.
            saida.append(f"##### {s}")
            continue
        if m and m.group(1) in por_numero:
            e = por_numero[m.group(1)]
            titulo_pdf = re.sub(r"\s+[–-]\s+\d+\s+minutes$", "", m.group(2)).strip()
            if _parecido(titulo_pdf, e["titulo"]):
                saida.append(f"{'#' * e['nivel']} {e['numero']}. {s[len(m.group(1)):].lstrip('. ').strip()}")
                continue
        # Títulos que não são seções numeradas (ex.: "Keywords") descem para ####.
        if linha.startswith("#"):
            saida.append("#### " + re.sub(r"^#+\s*", "", re.sub(r"\*\*", "", linha)).strip())
            continue
        saida.append(linha)
    return "\n".join(saida)


def _parecido(a: str, b: str) -> bool:
    norm = lambda x: re.sub(r"[^a-z0-9]", "", x.lower())
    return norm(a) == norm(b) or norm(a).startswith(norm(b)) or norm(b).startswith(norm(a))


def restaurar_hifens(md: str) -> str:
    """Devolve o hífen a compostos que a extração juntou na quebra de linha.

    Ex.: "riskbased" vira "risk-based" quando "risk-based" aparece em outro ponto do texto.
    """
    mapa = {h.replace("-", "").lower(): h for h in re.findall(r"\b[A-Za-z]+-[A-Za-z]+\b", md)}

    def trocar(m: re.Match) -> str:
        palavra = m.group(0)
        alvo = mapa.get(palavra.lower())
        if not alvo:
            return palavra
        # Mantém a caixa da primeira letra da palavra encontrada; o resto vem da forma original.
        return (alvo[0].upper() if palavra[0].isupper() else alvo[0].lower()) + alvo[1:]

    return re.sub(r"\b[A-Za-z]{6,}\b", trocar, md)


def corrigir_artefatos(md: str) -> str:
    md = re.sub(r"(\w) ~~(\w+)~~ (\w)", r"\1\2\3", md)       # "work ~~f~~ lows" -> "workflows"
    md = re.sub(r"^(\s*)- • ", r"\1- ", md, flags=re.M)        # marcador de lista duplicado
    md = re.sub(r"\*\* ([.,;:])", r"**\1", md)                 # "**Termo** ." -> "**Termo**."
    md = md.replace("<sup>®</sup>", "®")
    return md


def corrigir_hifenizacao(md: str) -> str:
    # "infor-\nmation" -> "information" (só quando a próxima linha começa em minúscula).
    md = re.sub(r"(\w)-\n(?=[a-z])", r"\1", md)
    # Espaços duplicados e espaços antes de pontuação deixados pela extração.
    md = re.sub(r"[ \t]+\n", "\n", md)
    md = re.sub(r"(?<=\S) {2,}(?=\S)", " ", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md


def main() -> None:
    pdf = achar_pdf(sys.argv[1] if len(sys.argv) > 1 else None)
    BUILD.mkdir(exist_ok=True)
    print(f"Convertendo {pdf.name} ...")
    sumario = ler_sumario(pdf)
    # Recorta a área útil de cada página, tirando cabeçalho e rodapé
    # (versão, "Page X of 78", data, copyright).
    doc = pymupdf.open(pdf)
    for pag in doc:
        pag.set_cropbox(area_util(pag))
    paginas = pymupdf4llm.to_markdown(doc, page_chunks=True, show_progress=False)

    partes = []
    for i, ch in enumerate(paginas, start=1):
        partes.append(f"<!-- pagina: {i} -->\n\n{limpar_pagina(ch['text'])}")
    md = "\n\n".join(partes) + "\n"
    md = normalizar_titulos(md, sumario)
    md = corrigir_hifenizacao(md)
    md = corrigir_artefatos(md)
    md = restaurar_hifens(md)

    BRUTO.write_text(md, encoding="utf-8")
    (BUILD / "sumario.json").write_text(json.dumps(sumario, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: {BRUTO.relative_to(BRUTO.parent.parent)} ({len(md.split())} palavras, {len(paginas)} páginas)")
    print(f"OK: build/sumario.json ({len(sumario)} entradas)")


if __name__ == "__main__":
    main()
