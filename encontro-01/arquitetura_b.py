"""Arquitetura B — workflow determinístico.   (COMPLETE OS TODOs 1 e 2)

O fluxo está escrito no código. O modelo só faz duas tarefas pequenas:
classificar a pergunta e redigir a resposta.

    pergunta ──► classificar ──► tema?
                                   ├── "elegibilidade" ──► escalar (sem chamar o modelo)
                                   └── "rh" | "ti" | "beneficios"
                                          ──► buscar(tema, pergunta) ──► [ modelo + 3 documentos ] ──► resposta

Quem decide o próximo passo é o CÓDIGO, não o modelo.
"""
from comum import modelo
from comum.resultado import Resultado
from ferramentas import buscar, formatar
from politica_de_resposta import FORMATO_JSON, REGRAS

CATEGORIAS = ("rh", "ti", "beneficios", "elegibilidade")


# --------------------------------------------------------------------------
# TODO 1 — o classificador
#
# Escreva o prompt de sistema que faz o modelo responder com UMA das
# CATEGORIAS acima, e nada mais. Dicas:
#   - diga o que entra em cada categoria (ex.: "ti: notebook, senha, VPN...");
#   - "elegibilidade" é quando a pessoa pergunta se ELA tem direito a algo;
#   - peça a resposta em minúsculas, sem pontuação.
# --------------------------------------------------------------------------
PROMPT_CLASSIFICADOR = """
Classifique a pergunta de um colaborador da Aurora Tecnologia.
Responda com exatamente uma destas palavras, em minúsculas e sem pontuação:
rh, ti, beneficios, elegibilidade

Use elegibilidade quando a pessoa perguntar se ELA tem direito a um
benefício. Essa regra tem prioridade sobre as demais.

Nos outros casos:
- rh: férias, licenças, jornada, banco de horas e regras de trabalho remoto.
- ti: notebook, equipamentos, senha, VPN e problemas de acesso a sistemas.
- beneficios: plano de saúde, vale-refeição, auxílio-creche e regras gerais
  dos benefícios.

Classifique pelo assunto que precisa ser resolvido, mesmo que a pergunta
mencione também outro assunto. Não explique a classificação.
"""


def classificar(pergunta: str) -> str:
    resposta = modelo.chamar([modelo.mensagem_do_usuario(pergunta)],
                             sistema=PROMPT_CLASSIFICADOR, max_tokens=10)
    categoria = resposta.texto.strip().lower()

    if categoria in CATEGORIAS:
        return categoria

    return "elegibilidade"


def resolver(pergunta: str) -> Resultado:
    categoria = classificar(pergunta)

    # ----------------------------------------------------------------------
    # TODO 2 — o roteamento
    #
    # a) Se a categoria for "elegibilidade", devolva direto:
    #        Resultado("escalar", [], "texto explicando que o RH vai analisar")
    #    (repare: esse caminho nem chama o modelo)
    #
    # b) Senão, busque os documentos do tema:   docs = buscar(categoria, pergunta)
    #    Se não vier nenhum documento, devolva Resultado("nao_sei", [], "...").
    #
    # c) Monte o prompt de sistema com REGRAS, FORMATO_JSON e os documentos
    #    (veja como a arquitetura_a.py faz com formatar), chame o modelo
    #    e devolva Resultado.de_json(resposta.texto).
    # ----------------------------------------------------------------------

    if categoria == "elegibilidade":
        return Resultado("escalar", [], "O RH precisa analisar sua elegibilidade.")

    docs = buscar(categoria, pergunta)
    if not docs:
        return Resultado("nao_sei", [], "Não encontrei essa informação nos documentos.")

    documentos = "\n\n".join(formatar(doc) for doc in docs)
    sistema = f"{REGRAS}\n\n{FORMATO_JSON}\n\nDocumentos disponíveis:\n\n{documentos}"

    resposta = modelo.chamar(
        [modelo.mensagem_do_usuario(pergunta)],
        sistema=sistema,
    )
    return Resultado.de_json(resposta.texto)
