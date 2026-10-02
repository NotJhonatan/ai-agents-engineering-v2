"""TODO 4 — Construir do zero: consultar_rede_credenciada.     (CONTRATO E IMPLEMENTAÇÃO)

Nas ferramentas 1 a 5, a implementação veio pronta e vocês escreveram o contrato.
Aqui não tem nada pronto: vocês escrevem as duas coisas.

O pedido do time de Benefícios
------------------------------
"Todo dia alguém pergunta se tal hospital ou laboratório atende pelo plano. A resposta
está na nossa planilha da rede credenciada, no Google Sheets. Queremos que o assistente
consulte a planilha."

O sistema: a planilha
---------------------
    SHEETS.ler("planilha-rede-credenciada", "prestadores")

devolve o mesmo formato da API do Google Sheets (spreadsheets.values.get):

    {"spreadsheetId": "planilha-rede-credenciada",
     "range": "prestadores!A1:L31",
     "majorDimension": "ROWS",
     "values": [
        ["prestador", "tipo", "especialidades", "cidade", "uf", "bairro", "telefone",
         "atende_24h", "situacao", "codigo_operadora", "valor_negociado_consulta",
         "observacao_interna"],                                            <- cabeçalho
        ["Hospital Jacarandá Paulista", "Hospital", "clínica geral; ...", "São Paulo", ...],
        ...
     ]}

Tudo vem como texto, e a planilha é mantida à mão desde 2021. Olhem os dados antes
de escrever qualquer linha:

    python encontro-02/nova_ferramenta.py          (a partir da raiz: imprime a planilha inteira)

Passo a passo
-------------
  4a. IMPLEMENTAÇÃO: escrevam consultar_rede_credenciada(). Decidam os parâmetros.
      Devolvam um dicionário com a lista de prestadores em "resultados" (um dicionário
      por prestador). Chaves fora de "resultados" também podem voltar ao modelo,
      se o contrato declarar (ex.: a fonte).
  4b. CONTRATO: preencham CONTRATO (descrição, schema, saída), como nos TODOs 1 a 3.
      Os parâmetros do schema precisam bater com os da função.
  4c. TESTE: assim que CONTRATO["parametros"] deixar de ser None, a ferramenta entra
      no catálogo do agente sozinha. Os casos c16 e c17 dependem dela:

          python encontro-02/rodar.py --casos c16 c17 --detalhe

Perguntas para decidir
----------------------
  - Que parâmetros o modelo precisa para chegar ao prestador certo? Quais valores aceitar?
  - "Campinas", "campinas" e "CAMPINAS " são a mesma cidade. Quem resolve isso: o modelo
    ou o código?
  - A planilha tem prestadores descredenciados e em negociação. O modelo deveria vê-los?
  - São Paulo tem mais de dez prestadores. Quantos voltam para o contexto?
  - Quais colunas nunca deveriam entrar no contexto? (O placar tem uma coluna para isso.)
  - Como o agente cita a planilha como fonte?
  - E erros: cidade sem prestador? Tipo que não existe?
"""
import unicodedata

from ferramentas import ErroDeFerramenta   # para devolver erros legíveis ao modelo (veja ferramentas.py)
from sistemas import PlanilhaGoogle

SHEETS = PlanilhaGoogle()
PLANILHA_ID = "planilha-rede-credenciada"
ABA = "prestadores"


def normalizar(texto: str) -> str:
    """'  São Paulo ' -> 'sao paulo'. Minúsculas, sem acento, sem espaço nas pontas."""
    sem_acento = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return " ".join(sem_acento.lower().split())


# ======================================================================
# TODO 4a — a implementação
#
# Troquem a assinatura pelos parâmetros que vocês decidirem (com tipos e valores
# padrão) e escrevam o corpo. Esqueleto sugerido:
#   1. ler a planilha com SHEETS.ler(PLANILHA_ID, ABA)
#   2. transformar cada linha num dicionário (cabeçalho -> valor)
#   3. filtrar (normalizar() ajuda)
#   4. devolver {"resultados": [...], ...}
# ======================================================================
def consultar_rede_credenciada(cidade: str, tipo: str = "todos",
                             somente_24h: bool = False, limite: int = 5) -> dict:
    cidade_alvo = normalizar(cidade)
    tipos = ("todos", "hospital", "laboratorio", "clinica", "pronto_socorro")
    if not cidade_alvo:
        raise ErroDeFerramenta("cidade_vazia", "Informe uma cidade para consultar.")
    if tipo not in tipos:
        raise ErroDeFerramenta("tipo_invalido", "Tipo de prestador não aceito.", aceitos=list(tipos))
    if not isinstance(somente_24h, bool):
        raise ErroDeFerramenta("tipo_invalido", "somente_24h deve ser booleano.")
    if isinstance(limite, bool) or not isinstance(limite, int) or not 1 <= limite <= 5:
        raise ErroDeFerramenta("limite_invalido", "O limite deve ser um inteiro de 1 a 5.")

    linhas = SHEETS.ler(PLANILHA_ID, ABA).get("values", [])
    resultados = []
    if not linhas:
        return {"id": PLANILHA_ID, "resultados": resultados}
    cabecalho = linhas[0]
    campos_publicos = ("prestador", "tipo", "especialidades", "cidade", "uf", "bairro", "telefone")
    for linha in linhas[1:]:
        registro = {campo: linha[i] if i < len(linha) else "" for i, campo in enumerate(cabecalho)}
        tipo_registro = normalizar(registro.get("tipo", "")).replace("-", "_")
        if normalizar(registro.get("cidade", "")) != cidade_alvo:
            continue
        if normalizar(registro.get("situacao", "")) != "ativo":
            continue
        if tipo != "todos" and tipo_registro != tipo:
            continue
        atende_24h = normalizar(registro.get("atende_24h", "")) == "sim"
        if somente_24h and not atende_24h:
            continue
        resultados.append({
            "id": PLANILHA_ID,
            **{campo: str(registro.get(campo, "")).strip() for campo in campos_publicos},
            "atende_24h": atende_24h,
        })
        if len(resultados) >= limite:
            break
    return {"id": PLANILHA_ID, "resultados": resultados}


# ======================================================================
# TODO 4b — o contrato (mesmo formato de contratos.py)
# ======================================================================
CONTRATO = {
    "descricao": (
        "Consulta hospitais, laboratórios, clínicas e pronto-socorros ativos na rede do plano da Aurora. "
        "Use para localizar um prestador em uma cidade. Para urgência, peça somente_24h; "
        "o tipo pronto_socorro seleciona unidades desse tipo na planilha. "
        "Devolve até 5 prestadores e o id planilha-rede-credenciada para citar como fonte. "
        "Depois da consulta, entregue a resposta chamando a ferramenta responder, "
        "com fontes contendo planilha-rede-credenciada e os prestadores encontrados no texto. "
        "Não use para regras ou elegibilidade do plano, nem para diagnóstico médico. "
        "Se a lista estiver vazia, informe que não há prestador correspondente na base consultada."
    ),
    "parametros": {
        "type": "object",
        "properties": {
            "cidade": {"type": "string", "minLength": 1, "maxLength": 100,
                       "description": "Cidade onde o colaborador procura atendimento."},
            "tipo": {"type": "string",
                     "enum": ["todos", "hospital", "laboratorio", "clinica", "pronto_socorro"],
                     "description": "Tipo de prestador; todos quando não houver preferência."},
            "somente_24h": {"type": "boolean", "description": "True para atendimento 24 horas."},
            "limite": {"type": "integer", "minimum": 1, "maximum": 5,
                       "description": "Máximo de prestadores retornados; padrão 5."},
        },
        "required": ["cidade"],
        "additionalProperties": False,
    },
    "saida": ["id", "prestador", "tipo", "especialidades", "cidade", "uf", "bairro", "telefone", "atende_24h"],
}


NOME = "consultar_rede_credenciada"


if __name__ == "__main__":   # olhar os dados antes de escrever a ferramenta
    for linha in SHEETS.ler(PLANILHA_ID, ABA)["values"]:
        print(linha)
