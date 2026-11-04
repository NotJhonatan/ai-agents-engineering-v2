r"""Hands-on do Encontro 4 em replay, sem chamadas ao vivo.

Na raiz: .\.venv\Scripts\python.exe -X utf8 encontro-04/experimento_equipe.py
Preserva dados, arquiteturas, contratos e avaliador publicados pelo professor.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
from datetime import datetime, timezone
from pathlib import Path

# Apenas neste processo: uma chamada ausente deve parar, nunca usar a API.
os.environ.update(PROVEDOR="anthropic", ANTHROPIC_API_KEY="", API_KEY="",
                  AURORA_REPLAY_MODO="usar")

import multiagente as ma

PASTA = Path(__file__).resolve().parent


def main():
    ma.preparar("usar")
    assert not ma.modelo.tem_credencial()
    casos = ma.carregar_casos()
    arquiteturas = [
        ma.monolito(),
        ma.roteador_especialistas("llm", 3),
        ma.roteador_especialistas("regra", 3),
        ma.roteador_especialistas("llm", 4),
        ma.roteador_especialistas("llm", 3, "resumo_do_roteador"),
        ma.roteador_especialistas("llm", 3, se_incerto="agente_unico"),
        ma.supervisor(3),
    ]
    experimentos = []
    for arquitetura in arquiteturas:
        print("Avaliando:", arquitetura.nome, flush=True)
        rodada = ma.rodar(arquitetura, casos, mostrar=False)
        ma.registrar(experimentos, rodada)
        print(ma.resumo(rodada), flush=True)
    estado = ma.modelo.estado_replay()
    assert estado["faltando"] == estado["gravadas"] == 0
    assert estado["reproduzidas"] == sum(l["chamadas_modelo"] for e in experimentos for l in e["linhas"])
    arquivos = [PASTA / "multiagente.py", PASTA / "busca.py", PASTA / "casos.json",
                *sorted((PASTA / "dados").glob("*")),
                PASTA.parent / "comum" / "modelo.py", PASTA.parent / "comum" / "medidor.py",
                PASTA.parent / "comum" / "avaliar.py",
                PASTA.parent / "encontro-01" / "politica_de_resposta.py",
                PASTA.parent / "encontro-02" / "agente.py",
                PASTA.parent / "encontro-02" / "camada.py"]
    hashes = {str(p.relative_to(PASTA.parent)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in arquivos if p.is_file()}
    saida = PASTA / "evidencias"
    saida.mkdir(exist_ok=True)
    evidencia = {"executado_em": datetime.now(timezone.utc).isoformat(),
                 "replay": estado, "precos_por_milhao": {
                     "entrada": ma.medidor.PRECO_ENTRADA, "saida": ma.medidor.PRECO_SAIDA},
                 "sha256_fontes": hashes, "rodadas": experimentos}
    (saida / "experimentos.json").write_text(json.dumps(evidencia, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tabela = ma.tabela_markdown(experimentos)
    (saida / "placar.md").write_text(tabela + "\n", encoding="utf-8")
    tabela_nota = ma.tabela_markdown([experimentos[i] for i in (0, 1, 2, 6)])
    (saida / "placar-nota.md").write_text(tabela_nota + "\n", encoding="utf-8")
    # Inclui ganhos, regressões e os casos de coordenação discutidos na nota.
    trace = io.StringIO()
    with contextlib.redirect_stdout(trace):
        for rodada in experimentos:
            for caso_id in ("R1", "C2", "R2", "E1", "S1", "S2", "P1", "X1"):
                ma.mostrar_trace(rodada, caso_id)
                print()
    (saida / "traces.txt").write_text(trace.getvalue(), encoding="utf-8")
    print(tabela, flush=True)
    print("Replay conferido:", estado, flush=True)


if __name__ == "__main__":
    main()
