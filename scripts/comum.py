"""Funções compartilhadas pelos scripts: caminhos, leitura do sumário do PDF e slugs."""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FONTE = RAIZ / "fonte"
BUILD = RAIZ / "build"
SYLLABUS = RAIZ / "syllabus"          # casca pública (vai para o git)
TEXTO = RAIZ / "syllabus-texto"       # texto integral local (ignorado pelo git)
DADOS = RAIZ / "dados"
BRUTO = BUILD / "bruto.md"

VERSAO = "4.0.1"
LINK_OFICIAL = "https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/"
LINK_GLOSSARIO = "https://glossary.istqb.org/"

# Páginas do sumário (Table of Contents) no PDF v4.0.1, base 1.
PAGINAS_SUMARIO = range(4, 8)


def achar_pdf(caminho: str | None = None) -> Path:
    """Retorna o PDF informado ou o único PDF em fonte/."""
    if caminho:
        p = Path(caminho)
        if not p.exists():
            sys.exit(f"PDF não encontrado: {p}")
        return p
    pdfs = sorted(FONTE.glob("*.pdf"))
    if not pdfs:
        sys.exit(
            "Nenhum PDF em fonte/. Baixe o syllabus oficial em\n"
            f"  {LINK_OFICIAL}\n"
            "e salve o arquivo em fonte/."
        )
    if len(pdfs) > 1:
        sys.exit(f"Mais de um PDF em fonte/: {[p.name for p in pdfs]}. Informe qual usar.")
    return pdfs[0]


def slug(texto: str) -> str:
    texto = re.sub(r"['’]", "", texto)  # "Tester's" -> "testers"
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    texto = re.sub(r"[^a-zA-Z0-9]+", "-", texto.lower()).strip("-")
    return texto


def ler_sumario(pdf: Path) -> list[dict]:
    """Lê o sumário do PDF e devolve [{numero, titulo, pagina, nivel, minutos}].

    Só inclui os capítulos 0 a 6 (conteúdo). Referências, apêndices e índice ficam de fora.
    """
    import pymupdf

    doc = pymupdf.open(pdf)
    texto = "\n".join(doc[i - 1].get_text() for i in PAGINAS_SUMARIO)
    linhas = [l.strip() for l in texto.splitlines()]
    entradas: list[dict] = []
    i = 0
    while i < len(linhas):
        m = re.fullmatch(r"(\d+(?:\.\d+)*)\.", linhas[i])
        if m and i + 1 < len(linhas):
            m2 = re.fullmatch(r"(.+?)\s*\.{2,}\s*(\d+)", linhas[i + 1])
            if m2:
                numero = m.group(1)
                titulo = m2.group(1).strip()
                minutos = None
                mm = re.search(r"\s+[–-]\s+(\d+)\s+minutes$", titulo)
                if mm:
                    minutos = int(mm.group(1))
                    titulo = titulo[: mm.start()].strip()
                entradas.append(
                    {
                        "numero": numero,
                        "titulo": titulo,
                        "pagina": int(m2.group(2)),
                        "nivel": numero.count(".") + 1,
                        "minutos": minutos,
                    }
                )
                i += 2
                continue
        i += 1
    return [e for e in entradas if int(e["numero"].split(".")[0]) <= 6]


def carregar_bruto() -> tuple[str, list[dict]]:
    """Lê build/bruto.md e build/sumario.json (gerados por converter.py)."""
    import json

    if not BRUTO.exists():
        sys.exit("build/bruto.md não existe. Rode antes: python scripts/converter.py")
    sumario = json.loads((BUILD / "sumario.json").read_text(encoding="utf-8"))
    return BRUTO.read_text(encoding="utf-8"), sumario


def segmentar(md: str, sumario: list[dict]) -> dict[str, dict]:
    """Divide o markdown bruto por seção do sumário.

    Retorna {numero: {texto, pagina_inicio, paginas}}. O texto de uma seção vai do seu título
    até o próximo título numerado (de qualquer nível), então uma seção-pai contém só a sua introdução.
    O capítulo 0 inteiro fica na entrada "0". O último trecho termina em "7. References".
    """
    numeros = {e["numero"] for e in sumario}
    linhas = md.splitlines()
    pagina = 0
    marcas: list[tuple[int, str, int]] = []  # (linha, numero, pagina)
    fim = len(linhas)
    for i, linha in enumerate(linhas):
        mp = re.match(r"<!-- pagina: (\d+) -->", linha)
        if mp:
            pagina = int(mp.group(1))
            continue
        mt = re.match(r"^(#{1,3}) (\d+(?:\.\d+)*)\. ", linha)
        if mt and mt.group(2) in numeros:
            marcas.append((i, mt.group(2), pagina))
        if re.match(r"^#+ 7\. References", linha):
            fim = i
            break

    secoes: dict[str, dict] = {}
    for k, (ini, numero, pag) in enumerate(marcas):
        prox = marcas[k + 1][0] if k + 1 < len(marcas) else fim
        if numero.startswith("0.") or numero == "0":
            continue
        trecho = "\n".join(linhas[ini:prox]).strip()
        secoes[numero] = {"texto": trecho, "pagina_inicio": pag, "paginas": _paginas(trecho, pag)}

    # Capítulo 0 (introdução) num trecho só.
    ini0 = next(i for i, n, _ in marcas if n == "0")
    fim0 = next(i for i, n, _ in marcas if n == "1")
    trecho0 = "\n".join(linhas[ini0:fim0]).strip()
    pag0 = next(p for _, n, p in marcas if n == "0")
    secoes["0"] = {"texto": trecho0, "pagina_inicio": pag0, "paginas": _paginas(trecho0, pag0)}
    return secoes


def _paginas(trecho: str, inicio: int) -> list[int]:
    pags = [inicio] + [int(p) for p in re.findall(r"<!-- pagina: (\d+) -->", trecho)]
    return sorted(set(pags))


def texto_sem_marcas(trecho: str) -> str:
    return re.sub(r"<!-- pagina: \d+ -->\n*", "", trecho)


def pasta_capitulo(cap: dict) -> str:
    return f"{int(cap['numero']):02d}-{slug(cap['titulo'])}"


def nome_arquivo(sec: dict) -> str:
    return f"{sec['numero']}-{slug(sec['titulo'])}.md"


def caminho_relativo(sec: dict, capitulos: dict[str, dict]) -> str:
    """Caminho da seção relativo à pasta syllabus/ (ou syllabus-texto/)."""
    cap_num = sec["numero"].split(".")[0]
    if cap_num == "0":
        # A introdução (0.1 a 0.11) fica num arquivo só.
        return "00-introducao.md"
    if sec["nivel"] == 1:
        return f"{pasta_capitulo(capitulos[cap_num])}/_index.md"
    return f"{pasta_capitulo(capitulos[cap_num])}/{nome_arquivo(sec)}"
