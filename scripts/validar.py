"""Confere se nada se perdeu na conversão e se a casca pública está limpa.

Uso:  python scripts/validar.py [caminho/do/syllabus.pdf]
Sai com código 1 se alguma checagem FALHAR. Avisos não reprovam.

Checagens:
 1. Toda seção do sumário do PDF virou arquivo (casca e texto local).
 2. O número de objetivos extraídos bate com o PDF (listas dos capítulos e Apêndice B).
 3. A contagem de palavras do markdown fica próxima da do PDF (diferença em %).
 4. Todo frontmatter é YAML válido e tem os campos obrigatórios.
 5. A casca pública não contém trechos longos do texto do syllabus (proteção de direitos autorais).
 6. Os links internos dos .md apontam para arquivos que existem.
 7. O git ignora o PDF, build/ e syllabus-texto/.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

from comum import (
    DADOS,
    RAIZ,
    SYLLABUS,
    TEXTO,
    achar_pdf,
    caminho_relativo,
    carregar_bruto,
    texto_sem_marcas,
)

CAMPOS = {
    "capitulo": int,
    "secao": str,
    "titulo": str,
    "objetivos": list,
    "nivel_k": (str, type(None)),
    "keywords": list,
    "tempo_estudo_min": (int, type(None)),
    "pagina_original": int,
    "relacionados": list,
}
TOLERANCIA_PALAVRAS = 3.0   # % aceitável de diferença
NGRAMA = 12                 # palavras seguidas do syllabus que não podem aparecer na casca

resultados: list[tuple[str, str, str]] = []  # (status, checagem, detalhe)


def registrar(status: str, checagem: str, detalhe: str) -> None:
    resultados.append((status, checagem, detalhe))


def ler_frontmatter(arq: Path) -> tuple[dict | None, str]:
    t = arq.read_text(encoding="utf-8")
    if not t.startswith("---\n"):
        return None, "sem frontmatter"
    try:
        fim = t.index("\n---\n", 4)
        return yaml.safe_load(t[4:fim]), t[fim + 5:]
    except (ValueError, yaml.YAMLError) as e:
        return None, f"YAML inválido: {e}"


def palavras(texto: str) -> list[str]:
    return re.findall(r"[A-Za-zÀ-ÿ0-9]+(?:['’-][A-Za-zÀ-ÿ0-9]+)*", texto)


def palavras_conteudo(texto: str) -> list[str]:
    """Palavras com ao menos uma letra (ignora números de título e o marcador "o" de lista do PDF)
    e com hífen tratado como separador, para comparar PDF e markdown em pé de igualdade."""
    return [w for w in re.split(r"[^A-Za-zÀ-ÿ0-9']+", texto) if re.search(r"[A-Za-zÀ-ÿ]", w) and w != "o"]


def limpar_md(md: str) -> str:
    md = texto_sem_marcas(md)
    md = re.sub(r"^---\n.*?\n---\n", "", md, flags=re.S)        # frontmatter
    md = re.sub(r"^> .*$", "", md, flags=re.M)                   # aviso de direitos
    md = re.sub(r"^#+\s*\d+(?:\.\d+)*\.?\s*", "", md, flags=re.M)  # numeração dos títulos
    md = re.sub(r"^\|[-|\s]+\|$", "", md, flags=re.M)            # separador de tabela
    md = re.sub(r"[*_`#|>]|<br>|<sup>|</sup>", " ", md)
    md = re.sub(r"^\s*-\s", " ", md, flags=re.M)
    return md


# --------------------------------------------------------------------- checagens
def checar_secoes(sumario: list[dict]) -> None:
    capitulos = {e["numero"]: e for e in sumario if e["nivel"] == 1}
    faltando_casca, faltando_texto = [], []
    for e in sumario:
        cam = caminho_relativo(e, capitulos)
        if not (SYLLABUS / cam).exists():
            faltando_casca.append(e["numero"])
        if TEXTO.exists() and not (TEXTO / cam).exists():
            faltando_texto.append(e["numero"])
        # Seções 0.x estão dentro de 00-introducao.md: o título precisa aparecer lá.
        if e["numero"].startswith("0.") and TEXTO.exists():
            alvo = (TEXTO / cam).read_text(encoding="utf-8") if (TEXTO / cam).exists() else ""
            if not re.search(rf"^## {re.escape(e['numero'])}\. ", alvo, flags=re.M):
                faltando_texto.append(e["numero"])
    n = len(sumario)
    if faltando_casca or faltando_texto:
        registrar("FALHA", "1. Seções do sumário", f"sem casca: {faltando_casca}; sem texto: {faltando_texto}")
    else:
        registrar("OK", "1. Seções do sumário", f"{n} entradas do sumário (capítulos 0 a 6) → todas têm arquivo")
    if not TEXTO.exists():
        registrar("AVISO", "1. Seções do sumário", "syllabus-texto/ não existe; só a casca foi conferida")


def checar_objetivos(pdf: Path) -> None:
    import pymupdf

    doc = pymupdf.open(pdf)
    texto = [p.get_text() for p in doc]
    codigos_pdf = set(re.findall(r"FL-\d+\.\d+\.\d+", "\n".join(texto)))
    # Apêndice B: matriz de rastreabilidade (páginas em paisagem após "Appendix B").
    # Na matriz, cada objetivo é: "1.1.1" / enunciado (1+ linhas) / "K1".
    ini_b = next(i for i, t in enumerate(texto) if re.search(r"Appendix B", t) and i > 20)
    ini_c = next(i for i, t in enumerate(texto) if re.search(r"Appendix C", t) and i > ini_b)
    linhas_b = [l.strip() for t in texto[ini_b:ini_c] for l in t.splitlines()]
    k_apendice: dict[str, str] = {}
    for i, l in enumerate(linhas_b):
        if re.fullmatch(r"\d\.\d\.\d", l) and l != "4.0.1":
            k = next((x for x in linhas_b[i + 1:i + 5] if re.fullmatch(r"K[1-3]", x)), None)
            if k:
                k_apendice[f"FL-{l}"] = k
    codigos_b = set(k_apendice)

    dados = json.loads((DADOS / "objetivos.json").read_text(encoding="utf-8"))
    extraidos = {o["codigo"] for o in dados["objetivos"]}
    ks = {o["codigo"]: o["nivel_k"] for o in dados["objetivos"]}
    k_diverge = [c for c in extraidos if k_apendice.get(c) and k_apendice[c] != ks[c]]

    detalhe = (f"extraídos {len(extraidos)} · no PDF {len(codigos_pdf)} · no Apêndice B {len(codigos_b)}"
               f" · dados/objetivos.json total={dados['total']}")
    if extraidos == codigos_pdf == codigos_b and dados["total"] == len(extraidos) and not k_diverge:
        registrar("OK", "2. Objetivos de aprendizagem", detalhe + " · níveis K conferem com o Apêndice B")
    else:
        faltam = sorted(codigos_pdf - extraidos)
        sobram = sorted(extraidos - codigos_pdf)
        registrar("FALHA", "2. Objetivos de aprendizagem",
                  f"{detalhe} · faltam {faltam} · sobram {sobram} · K divergente {k_diverge}")
    # Todo objetivo aponta para um arquivo que existe.
    sem_arquivo = [o["codigo"] for o in dados["objetivos"] if not (RAIZ / o["arquivo"]).exists()]
    if sem_arquivo:
        registrar("FALHA", "2. Objetivos de aprendizagem", f"apontam para arquivo inexistente: {sem_arquivo}")


def checar_palavras(pdf: Path, sumario: list[dict], md: str) -> None:
    import pymupdf

    from converter import area_util

    doc = pymupdf.open(pdf)
    pag_ini = next(e["pagina"] for e in sumario if e["numero"] == "0")
    pag_fim = max(e["pagina"] for e in sumario if e["nivel"] == 1 and e["numero"] == "6")
    # Última página de conteúdo = página anterior a "7. References".
    for i in range(pag_fim, doc.page_count):
        if re.search(r"^\s*7\.\s*References", doc[i].get_text(), flags=re.M):
            pag_fim = i  # índice base 0 da página de References = página anterior em base 1
            break
    n_pdf = 0
    for i in range(pag_ini - 1, pag_fim):
        pag = doc[i]
        pag.set_cropbox(area_util(pag))
        n_pdf += len(palavras_conteudo(pag.get_text()))

    if TEXTO.exists():
        arquivos = sorted(p for p in TEXTO.rglob("*.md"))
        n_md = sum(len(palavras_conteudo(limpar_md(p.read_text(encoding="utf-8")))) for p in arquivos)
        origem = f"syllabus-texto/ ({len(arquivos)} arquivos)"
    else:
        ini = md.index("# 0. Introduction")
        fim = re.search(r"^#+ 7\. References", md, flags=re.M).start()
        n_md = len(palavras_conteudo(limpar_md(md[ini:fim])))
        origem = "build/bruto.md"
    dif = (n_md - n_pdf) / n_pdf * 100
    detalhe = f"PDF págs. {pag_ini}–{pag_fim}: {n_pdf} palavras · {origem}: {n_md} palavras · diferença {dif:+.2f}%"
    registrar("OK" if abs(dif) <= TOLERANCIA_PALAVRAS else "FALHA", "3. Contagem de palavras", detalhe)


def checar_frontmatter() -> None:
    problemas = []
    total = 0
    for pasta, tipo in ((SYLLABUS, "casca"), (TEXTO, "texto-integral")):
        if not pasta.exists():
            continue
        for arq in sorted(pasta.rglob("*.md")):
            total += 1
            fm, resto = ler_frontmatter(arq)
            rel = arq.relative_to(RAIZ).as_posix()
            if fm is None:
                problemas.append(f"{rel}: {resto}")
                continue
            for campo, tipo_esp in CAMPOS.items():
                if campo not in fm:
                    problemas.append(f"{rel}: falta '{campo}'")
                elif not isinstance(fm[campo], tipo_esp):
                    problemas.append(f"{rel}: '{campo}' com tipo {type(fm[campo]).__name__}")
            if fm.get("tipo") != tipo:
                problemas.append(f"{rel}: tipo '{fm.get('tipo')}' (esperado '{tipo}')")
            if fm.get("nivel_k") not in (None, "K1", "K2", "K3"):
                problemas.append(f"{rel}: nivel_k inválido")
            if any(not re.fullmatch(r"FL-\d+\.\d+\.\d+", o) for o in fm.get("objetivos", [])):
                problemas.append(f"{rel}: código de objetivo inválido")
    for g in sorted((RAIZ / "guias").glob("*.md")):
        total += 1
        fm, resto = ler_frontmatter(g)
        if fm is None or fm.get("tipo") != "guia" or "baseado_em" not in fm:
            problemas.append(f"{g.relative_to(RAIZ).as_posix()}: frontmatter de guia incompleto")
    if problemas:
        registrar("FALHA", "4. Frontmatter YAML", f"{len(problemas)} problema(s): " + "; ".join(problemas[:10]))
    else:
        registrar("OK", "4. Frontmatter YAML", f"{total} arquivos com YAML válido e campos obrigatórios")


def checar_casca_limpa() -> None:
    """Nenhuma sequência de NGRAMA palavras do texto do syllabus pode estar na casca, guias ou dados."""
    if not TEXTO.exists():
        registrar("AVISO", "5. Casca sem texto do syllabus", "syllabus-texto/ não existe; checagem pulada")
        return
    ngramas: set[tuple[str, ...]] = set()
    for arq in TEXTO.rglob("*.md"):
        _, corpo = ler_frontmatter(arq)
        # As listas de keywords são termos do glossário (dados de referência), não prosa:
        # ficam fora da comparação, assim como as listas de objetivos (código + nível).
        corpo = re.sub(r"#### Keywords\n+.*?(?=\n####|\Z)", "", corpo, flags=re.S)
        p = [w.lower() for w in palavras(limpar_md(corpo))]
        ngramas.update(tuple(p[i:i + NGRAMA]) for i in range(len(p) - NGRAMA + 1))
    publicos = list(SYLLABUS.rglob("*.md")) + list((RAIZ / "guias").glob("*.md")) + [
        RAIZ / "llms.txt", RAIZ / "CLAUDE.md", RAIZ / "README.md", *DADOS.glob("*.*")]
    vazamentos = []
    for arq in publicos:
        if not arq.exists():
            continue
        p = [w.lower() for w in palavras(arq.read_text(encoding="utf-8"))]
        for i in range(len(p) - NGRAMA + 1):
            if tuple(p[i:i + NGRAMA]) in ngramas:
                vazamentos.append(f"{arq.relative_to(RAIZ).as_posix()}: \"{' '.join(p[i:i + NGRAMA])}\"")
                break
    if vazamentos:
        registrar("FALHA", "5. Casca sem texto do syllabus", f"{len(vazamentos)} arquivo(s): " + "; ".join(vazamentos[:5]))
    else:
        registrar("OK", "5. Casca sem texto do syllabus",
                  f"{len(publicos)} arquivos públicos sem nenhuma sequência de {NGRAMA}+ palavras do syllabus")


def checar_links() -> None:
    quebrados = []
    arquivos = list(SYLLABUS.rglob("*.md")) + list((RAIZ / "guias").glob("*.md")) + [
        RAIZ / "README.md", RAIZ / "CLAUDE.md", RAIZ / "llms.txt", RAIZ / "AVISO-LEGAL.md"]
    n = 0
    for arq in arquivos:
        if not arq.exists():
            continue
        t = arq.read_text(encoding="utf-8")
        alvos = re.findall(r"\]\(([^)]+)\)", t) + re.findall(r"^\[[^\]]+\]:\s*(\S+)", t, flags=re.M)
        for alvo in alvos:
            if re.match(r"https?://|mailto:|#", alvo):
                continue
            n += 1
            caminho = (arq.parent / alvo.split("#")[0]).resolve()
            if not caminho.exists():
                quebrados.append(f"{arq.relative_to(RAIZ).as_posix()} → {alvo}")
    if quebrados:
        registrar("FALHA", "6. Links internos", f"{len(quebrados)} quebrado(s): " + "; ".join(quebrados[:8]))
    else:
        registrar("OK", "6. Links internos", f"{n} links internos, todos resolvem")


def checar_gitignore(pdf: Path) -> None:
    alvos = [pdf, RAIZ / "build" / "bruto.md", TEXTO / "00-introducao.md"]
    nao_ignorados = []
    for a in alvos:
        r = subprocess.run(["git", "check-ignore", "-q", str(a)], cwd=RAIZ)
        if r.returncode != 0:
            nao_ignorados.append(a.relative_to(RAIZ).as_posix() if a.is_relative_to(RAIZ) else str(a))
    rastreados = subprocess.run(["git", "ls-files", "fonte", "build", "syllabus-texto"],
                                cwd=RAIZ, capture_output=True, text=True).stdout.split()
    if nao_ignorados or rastreados:
        registrar("FALHA", "7. Git ignora conteúdo protegido",
                  f"não ignorados: {nao_ignorados}; já rastreados: {rastreados}")
    else:
        registrar("OK", "7. Git ignora conteúdo protegido", "fonte/*.pdf, build/ e syllabus-texto/ fora do git")


def main() -> int:
    pdf = achar_pdf(sys.argv[1] if len(sys.argv) > 1 else None)
    md, sumario = carregar_bruto()

    checar_secoes(sumario)
    checar_objetivos(pdf)
    checar_palavras(pdf, sumario, md)
    checar_frontmatter()
    checar_casca_limpa()
    checar_links()
    checar_gitignore(pdf)

    print("\nRELATÓRIO DE VALIDAÇÃO\n" + "=" * 70)
    for status, checagem, detalhe in resultados:
        print(f"[{status:^5}] {checagem}\n        {detalhe}")
    falhas = sum(1 for s, *_ in resultados if s == "FALHA")
    avisos = sum(1 for s, *_ in resultados if s == "AVISO")
    print("=" * 70)
    print(f"{len(resultados) - falhas - avisos} OK · {avisos} aviso(s) · {falhas} falha(s)")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
