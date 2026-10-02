# Tool Contract Sheet · Equipe do projeto

**Encontro 2 · Entrega de 10%: documento e código** · Caso: Aurora Tecnologia

**Data:** 01/10/2026

**Integrantes:**

- Jhonatan Pereira
- Pedro Henrique Panegossi
- Gabriela Chaves
- Ana Carolina Wichinieski

As seis ferramentas estão implementadas no catálogo. O exercício usa sistemas simulados e dados fictícios; a avaliação não comprova autorização de acesso em produção.

## 1. Catálogo

| Nome | Quem decide | Descrição | Entrada | Saída | Escopo | Criticidade | Reversível |
|---|---|---|---|---|---|---|---|
| `consultar_politica_rh` | Modelo | Busca regras de férias, trabalho remoto, licenças, jornada e integração | pergunta obrigatória (até 300); tema opcional (enum de 6) | id, titulo, atualizado_em, trecho | Políticas gerais de RH | Baixa | Sim |
| `buscar_base_ti` | Modelo | Consulta orientações técnicas antes de decidir agir | pergunta obrigatória (até 300) | id, titulo, atualizado_em, trecho | Base de TI | Baixa | Sim |
| `consultar_regra_beneficio` | Modelo | Consulta valores, prazos e procedimentos gerais | beneficio obrigatório (enum de 3); pergunta opcional (até 300) | id, titulo, atualizado_em, trecho | Regras gerais de benefícios | Baixa | Sim |
| `abrir_chamado_ti` | Modelo | Cria chamado solicitado ou necessário; não repete automaticamente após timeout | categoria obrigatória (enum de 5); descricao obrigatória (15–500); urgencia opcional (enum de 3) | id, status, categoria, urgencia, prazo_atendimento | Service desk simulado de TI | Média | Com custo |
| `verificar_elegibilidade_beneficio` | Modelo | Faz pré-análise sem confirmar o direito ao benefício; encaminha ao RH | colaborador_id obrigatório (1–40); beneficio obrigatório (enum de 3) | colaborador_id, beneficio, pre_analise, criterios_verificados, aviso | Cadastro fictício do id informado; sem CPF ou salário no retorno | Alta | Sim |
| `consultar_rede_credenciada` | Modelo | Localiza prestadores ativos por cidade, tipo e atendimento 24h | cidade obrigatória (1–100); tipo opcional (enum de 5); somente_24h opcional (booleano); limite opcional (1–5) | id, prestador, tipo, especialidades, cidade, uf, bairro, telefone, atende_24h | Planilha simulada da rede; dados públicos do prestador | Média | Sim |

Todos os contratos rejeitam parâmetros adicionais. A criticidade alta da pré-análise decorre do risco de apresentar a consulta como confirmação de direito, embora ela faça apenas leitura.

## 2. Justificativas

Na arquitetura deste exercício, o modelo escolhe ferramentas e argumentos conforme a pergunta. Essas chamadas não servem como passo obrigatório para todos os atendimentos. Um workflow com rotas específicas continua sendo uma alternativa possível, a avaliar no ADR.

- `consultar_politica_rh`: o conteúdo determina a política e se é preciso consultar mais de uma fonte.
- `buscar_base_ti`: o problema técnico pode aparecer junto de trabalho remoto ou seguro de equipamento.
- `consultar_regra_beneficio`: precisa distinguir regra geral de análise individual e escolher o benefício.
- `abrir_chamado_ti`: depende do pedido e do resultado da base; executar sempre criaria chamados não solicitados.
- `verificar_elegibilidade_beneficio`: só se aplica à consulta individual com id informado; não se deve adivinhar um cadastro.
- `consultar_rede_credenciada`: cidade, tipo e necessidade de atendimento 24h variam; consultar a rede em toda pergunta acrescentaria contexto sem utilidade.

## 3. Contratos completos

- [contratos.py](contratos.py): descrição, JSON Schema e campos de saída das cinco primeiras ferramentas.
- [nova_ferramenta.py](nova_ferramenta.py): implementação e contrato da rede credenciada.

A rede normaliza maiúsculas, acentos e espaços no código, trata linhas com células finais ausentes, exclui prestadores descredenciados ou em negociação, filtra atendimento 24h e limita o retorno a cinco resultados. Cidade sem correspondência devolve lista vazia. Tipo ou limite inválido devolve erro legível. Cada resultado inclui o id da planilha para citação.

A implementação da rede exclui valor negociado, código da operadora e observações internas antes do retorno. A pré-análise devolve apenas os campos declarados no contrato. O prompt de sistema, o executor, o corpus e o gabarito foram preservados.

## 4. Evidência do hands-on

**Quebra escolhida:** 2 · Texto livre no lugar de enum. Remove enums e descrições dos parâmetros, preservando os filtros de saída. Compara os mesmos 17 casos, com o mesmo prompt, em uma repetição por versão.

| Versão | Acertos | Tool errada | Args inválidos | Chamados a mais | Dado sensível | Tokens/caso | Custo/acerto |
|---|---|---|---|---|---|---|---|
| Contrato da dupla | 6/17 | 0 | 0 | 0 | 0 | 7.210 | US$ 0,02410 |
| Quebra 2 | 10/17 | 0 | 15 | 0 | 0 | 9.586 | US$ 0,01959 |

**CSV da comparação:** [comparacao-quebra-2.csv](evidencias/comparacao-quebra-2.csv), cópia integral de `execucao_20261001_220754_q2.csv`. A pasta `evidencias/` pode ser versionada; a pasta original `resultados/` é ignorada pelo Git.

**Custo total da execução:** US$ 0,144592 no contrato normal e US$ 0,195877 na quebra, totalizando US$ 0,340469 nesta comparação. Os testes parciais e a tentativa interrompida têm custos adicionais.

**Interpretação:** retirar enums gerou 15 chamadas com argumentos inválidos e elevou tokens por caso em aproximadamente 33% e custo total em 35%. O modelo conseguiu corrigir alguns argumentos depois de receber os erros do sistema. Os 10 acertos da quebra não demonstram superioridade: houve apenas uma rodada por versão, e o contrato normal teve 11 saídas finais inválidas, contra 6 na quebra. A variação de formato e as chamadas adicionais impedem atribuir toda a diferença de acerto somente aos enums. Não foram medidos intervalos de confiança ou estabilidade do placar.

**Resultado dos casos da rede no comparativo:** c16 e c17 falharam por formato no contrato normal e passaram na quebra, após o modelo usar a ferramenta de encerramento. Isso confirma que os dados necessários podem ser obtidos, mas não demonstra encerramento confiável no contrato normal. Não se alterou o executor para transformar texto livre em acerto.

Para reproduzir a comparação no PowerShell, a partir da raiz:

```powershell
.\.venv\Scripts\python.exe -X utf8 encontro-02\rodar.py --comparar 2 --detalhe
```

A primeira tentativa completa parou por `UnicodeEncodeError` na impressão do terminal Windows. A execução acima terminou com UTF-8 habilitado, sem mudança no código de avaliação. A opção de quebra 4 foi bloqueada pela revisão automática de execução por ampliar os campos enviados à API; a entrega usa a alternativa 2 prevista no roteiro.

**Primeira versão da ferramenta:** c16 e c17 falharam por saída fora do contrato no [primeiro teste](evidencias/teste-primeira-rede-e-elegibilidade.csv). Ambos receberam prestadores corretos, mas a resposta final veio em texto livre. Após orientar explicitamente a citação e o encerramento pela ferramenta `responder`, c16 passou e c17 ainda falhou no [teste após ajuste](evidencias/teste-rede-apos-ajuste.csv). A comparação completa registra o resultado final sem descartar erros.

**Outras observações:** c04 acertou 2 de 3 [repetições anteriores](evidencias/teste-rh-repeticoes.csv), indicando variação no encerramento. c11 e c13 criaram um chamado cada, sem duplicação, mas falharam no formato no [teste após timeout](evidencias/teste-chamados-timeout.csv). No primeiro teste do TODO 3, c14 escalou ao RH sem dados sensíveis; c15 retornou `nao_sei` porque o trecho recebido não continha a faixa etária do benefício. Na comparação final, c14 e c15 passaram nas duas versões.

**O que mudou no contrato:** delimitamos regras gerais versus análise pessoal, restringimos argumentos com enums, mantivemos o id da fonte e explicitamos o tratamento de timeout. A orientação textual de encerramento não garante obediência em todas as chamadas. Os filtros de atividade e normalização da rede são aplicados no código.

**Validação local:** os seis contratos batem com as assinaturas das implementações. Passaram sintaxe, normalização de Campinas, exclusão de descredenciado, filtro 24h de Curitiba, limite de cinco resultados, cidade sem correspondência e ausência de campos comerciais internos na saída da rede.

**Idempotência:** o desafio opcional não foi implementado. O contrato orienta não repetir automaticamente após timeout; isso depende do modelo e não equivale à garantia de idempotência no sistema.

## 5. A ação irreversível do ADR

A ação irreversível definida no ADR do Encontro 1 é comunicar a um colaborador que ele é elegível a um benefício sem análise do RH.

Essa confirmação não é executada por nenhuma ferramenta: `verificar_elegibilidade_beneficio` faz apenas pré-análise, devolve o aviso de que somente o RH confirma e orienta encaminhar a decisão. Abrir chamado é uma escrita reversível com custo. O texto final do modelo continua sujeito a erro e precisa ser avaliado mesmo quando a ferramenta faz somente leitura.
