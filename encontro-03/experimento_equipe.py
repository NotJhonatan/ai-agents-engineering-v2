r"""Reproduz os quatro passos do hands-on, sem alterar o avaliador do professor.

Na raiz: .\.venv\Scripts\python.exe -X utf8 encontro-03/experimento_equipe.py
O cache do modelo fica em resultados/ (ignorado pelo Git).
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
from datetime import datetime, timezone
from pathlib import Path

PASTA = Path(__file__).resolve().parent
os.environ.setdefault("HF_HOME", str(PASTA / "resultados" / "huggingface"))
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

import rag_aurora as r


def main():
    docs, casos = r.carregar_corpus(), r.carregar_casos()
    print(f"Preparando embeddings: {len(docs)} páginas, {len(casos)} casos", flush=True)
    emb = r.Embeddings()
    configuracoes = [
        ("base: tamanho 400 · vetor", dict(estrategia="tamanho", busca="vetor")),
        ("estrutura · vetor", dict(estrategia="estrutura", busca="vetor")),
        ("estrutura · BM25", dict(estrategia="estrutura", busca="bm25")),
        ("estrutura · híbrida", dict(estrategia="estrutura", busca="hibrida")),
        ("estrutura · híbrida · vigente", dict(estrategia="estrutura", busca="hibrida", so_vigente=True)),
        ("estrutura · híbrida · vigente · oficial", dict(estrategia="estrutura", busca="hibrida", so_vigente=True, so_oficial=True)),
    ]
    experimentos, detalhes = [], []
    for nome, parametros in configuracoes:
        print(f"Avaliando {nome}", flush=True)
        buscador = r.montar_buscador(docs, emb, **parametros)
        linhas = r.avaliar(buscador, casos, k=3)
        r.registrar(experimentos, nome, linhas)
        consultas = []
        for caso in casos:
            resultados = buscador(caso["pergunta"], 3)
            consultas.append({"caso": caso["id"], "pergunta": caso["pergunta"],
                              "resultados": [{"metadados": c.metadata, "texto": c.page_content,
                                              "pontuacao": s} for c, s in resultados]})
        detalhes.append({"nome": nome, "parametros": parametros, "k": 3,
                         "chunks": len(buscador.chunks), "avaliacao": linhas,
                         "falhas": r.falhas(linhas), "consultas": consultas})
        r.placar(linhas, nome)
    saida = PASTA / "evidencias"
    saida.mkdir(exist_ok=True)
    versoes = {p: importlib.metadata.version(p) for p in (
        "sentence-transformers", "transformers", "torch", "chromadb",
        "langchain-core", "langchain-text-splitters", "rank-bm25")}
    hashes = {str(p.relative_to(PASTA)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in [PASTA / "rag_aurora.py", PASTA / "casos.json", *sorted(r.CORPUS.glob("*.md"))]}
    evidencia = {"executado_em": datetime.now(timezone.utc).isoformat(),
                 "modelo": emb.nome, "versoes": versoes, "sha256_fontes": hashes,
                 "paginas": len(docs), "casos": len(casos), "configuracoes": detalhes}
    (saida / "experimentos.json").write_text(json.dumps(evidencia, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tabela = r.tabela_markdown(experimentos)
    (saida / "placar.md").write_text(tabela + "\n", encoding="utf-8")
    print(tabela, flush=True)
    print("Evidências salvas em", saida, flush=True)


if __name__ == "__main__":
    main()
