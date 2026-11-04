r"""Reproduz o hands-on do Encontro 5 em replay, sem API ao vivo.

Na raiz, com .venv: python -X utf8 encontro-05/experimento_equipe.py
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
from datetime import datetime, timezone
from pathlib import Path

os.environ.update(PROVEDOR="anthropic", ANTHROPIC_API_KEY="", API_KEY="",
                  AURORA_REPLAY_MODO="usar", MPLBACKEND="Agg")
os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / "resultados" / "matplotlib"))

import avaliacao as av

PASTA = Path(__file__).resolve().parent
# Metas propostas antes do placar: não recalibrar para aprovar uma versão.
SLOS = {"acerto": 0.90, "custo_por_acerto": 0.002,
        "p95_segundos": 10.0, "bateu_limite": 0.02}


def golden_equipe():
    return [
        av.caso_da_equipe("B03", "responder", ["fin-viagens-e-reembolso"],
                         ["10 dias corridos", "dez dias corridos"], ["10 dias úteis", "30 dias"]),
        av.caso_da_equipe("B08", "responder", ["ti-vpn-codigos-de-erro"],
                         ["Certificado Aurora"], ["Modo TCP 443"]),
        av.caso_da_equipe("B12", "responder", ["beneficios-plano-odontologico"],
                         ["R$ 22", "22,00", "vinte e dois reais"], ["R$ 30", "30%"]),
        av.caso_da_equipe("B13", "escalar"),
        av.caso_da_equipe("B16", "responder", ["beneficios-auxilio-creche"],
                         ["R$ 600", "600,00", "seiscentos reais"], ["R$ 500", "500,00"]),
        av.caso_da_equipe("B18", "nao_sei"),
        av.caso_da_equipe("B20", "responder", ["rh-codigo-de-conduta"],
                         ["R$ 200", "200,00", "duzentos reais"],
                         ["limite de R$ 350", "limite é de R$ 350", "limite anual de R$ 350"]),
        av.caso_da_equipe("B22", "escalar"),
    ]


def main():
    av.preparar("usar")
    assert not av.modelo.tem_credencial()
    grupo = golden_equipe()
    assert av.conferir_gabarito(grupo) and len(grupo) == 8
    saida = PASTA / "evidencias"
    saida.mkdir(exist_ok=True)
    (PASTA / "golden-equipe.json").write_text(json.dumps(grupo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    producao = av.rodar("v1", av.carregar_banco())
    av.julgar(producao, "evidencia")
    suite = av.carregar_golden() + grupo
    rodadas = [av.rodar(v, suite) for v in ("v1", "v2", "v3")]
    for rodada in rodadas:
        av.julgar(rodada, "evidencia")
    v1, v2, v3 = rodadas
    ruido = av.teste_aa(v1)
    comparacoes = {"pr42": av.comparar(v1, v2), "barato": av.comparar(v1, v3),
                   "grupo_pr42": av.comparar(av.recorte(v1, casos=grupo), av.recorte(v2, casos=grupo)),
                   "turma_pr42": av.comparar(av.recorte(v1, casos=av.carregar_golden()), av.recorte(v2, casos=av.carregar_golden()))}
    gate = av.checar_slos(SLOS, *rodadas)
    diagnostico = io.StringIO()
    with contextlib.redirect_stdout(diagnostico):
        av.resumo_banco(producao)
        av.suspeitos(*(av.recorte(r, casos=grupo) for r in rodadas))
        for r in rodadas:
            av.variacoes(r, "B13")
            av.variacoes(r, "B22")
        av.mostrar_trace(v2, "B13", 0)
        spans = av.cascata(v2, "B13", 0, grafico=True)
    import matplotlib.pyplot as plt
    plt.savefig(saida / "cascata-v2-B13-a0.png", dpi=160, bbox_inches="tight")
    plt.close("all")
    (saida / "diagnostico.txt").write_text(diagnostico.getvalue(), encoding="utf-8")
    for nome, texto in (("placar.md", av.tabela_markdown(*rodadas)),
                         ("gabarito.md", av.gabarito_markdown(grupo)),
                         ("gate.md", av.slos_markdown(SLOS, *rodadas))):
        (saida / nome).write_text(texto + "\n", encoding="utf-8")
    arquivos = [PASTA / "avaliacao.py", PASTA / "golden-aurora.json", PASTA / "banco-producao.json",
                PASTA / "golden-equipe.json", *sorted((PASTA / "dados").glob("*")),
                PASTA.parent / "encontro-04" / "multiagente.py", PASTA.parent / "encontro-04" / "busca.py",
                *sorted((PASTA.parent / "encontro-03" / "corpus").glob("*.md")),
                *sorted((PASTA.parent / "comum").glob("*.py")),
                PASTA.parent / "encontro-01" / "politica_de_resposta.py",
                PASTA.parent / "encontro-02" / "camada.py", PASTA.parent / "encontro-02" / "agente.py"]
    hashes = {str(p.relative_to(PASTA.parent)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in arquivos if p.is_file()}
    evidencia = {"executado_em": datetime.now(timezone.utc).isoformat(), "sha256_fontes": hashes,
                 "cabecalhos": {nome: av._cabecalho(p) for nome, p in av.GRAVACOES.items()},
                 "producao": producao, "rodadas": rodadas, "ruido_aa": ruido,
                 "comparacoes": comparacoes, "slos": SLOS, "gate": gate,
                 "metricas": {r["versao"]: {"acerto": av.acerto(r), "slis": av.slis(r)} for r in rodadas},
                 "cascata": {"caso": "B13", "versao": "v2", "amostra": 0, "spans": spans}}
    (saida / "experimentos.json").write_text(json.dumps(evidencia, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(av.tabela_markdown(*rodadas))
    print("Evidências salvas em", saida)


if __name__ == "__main__":
    main()
