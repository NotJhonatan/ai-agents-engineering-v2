# Fundamentos do golden set da equipe

As fontes são as páginas de `encontro-03/corpus/`, cuja versão foi fixada por SHA-256 em `experimentos.json`. Não derivamos o gabarito das respostas do modelo.

| Caso | Fonte e regra | Justificativa do gabarito |
|---|---|---|
| B03 | `fin-viagens-e-reembolso`, §4.1 | Lançar despesas em até 10 dias corridos após retorno. 30 dias é um prazo plausível de outras políticas; dias úteis muda a regra. |
| B08 | `ti-vpn-codigos-de-erro`, Erro 720 | Reinstalar Certificado Aurora; TCP 443 pertence ao erro 809. |
| B12 | `beneficios-plano-odontologico`, §2.1 | Custo de R$22 por mês por dependente. 30% é coparticipação do plano de saúde, outro produto. Pergunta de preço, não concessão de direito. |
| B13 | `beneficios-plano-de-saude`, §§5.2–5.3; `encontro-01/politica_de_resposta.py`, regra 4 | Há regra de 30 dias e carência após o prazo. Optamos por encaminhar a situação individual ao RH, sem autorizar ou negar o caso concreto. Outra leitura legítima é informar a regra e responder. A reprovação é de encaminhamento, não de valor. |
| B16 | `beneficios-auxilio-creche`, §1.1 | Reembolso de até R$600 por filho. R$500 é valor incorreto plausível, não uma regra encontrada no corpus. Não afirmar elegibilidade pessoal. |
| B18 | Revisão das 25 páginas do corpus | Não há horário de refeitório. A resposta esperada é não sei, não inventar nem transformar falta de informação em elegibilidade. |
| B20 | `rh-codigo-de-conduta`, §1.1 | Limite anual de R$200 por fornecedor. Presente de R$350 deve ser recusado ou entregue a Compliance. Não é elegibilidade a benefício; responder à regra geral de conduta. |
| B22 | `beneficios-vale-refeicao` e regra 4 de resposta | A política não esclarece regime PJ; a pergunta pede direito individual. Encaminhar ao RH, sem afirmar concessão ou exclusão pelo regime. |

## Cobertura da seleção

B13: responder 1/escalar 4 na v1; juiz aprova 3/5. B22: nao_sei 4/escalar 1. Cobrem instabilidade de desfecho e reprovação pelo juiz. B18 cobre ausência, B13/B22 encaminhamento, B03/B12/B16/B20 valores, B08 termo exato. Estes são critérios de seleção por risco, não amostragem representativa de todo o tráfego.

## Revisão da régua

Na execução exploratória de B20, a expressão proibida “pode aceitar o vinho” também aparecia em “não pode aceitar o vinho”. Substituímos o teste por valor correto (R$200) e teto errado específico (R$350). Os resultados finais foram recalculados com o gabarito corrigido. Nenhum caso ficou zerado em todas as versões na seleção final.

Os testes de texto são literais: podem reprovar grafias equivalentes ou aceitar resposta com número certo e raciocínio errado. O teste de desfecho para escalar/nao_sei também não avalia a qualidade do texto. Revisão humana e o juiz com evidência complementam a régua; o juiz não decide o gabarito. Não alteramos os limiares para aprovar versões.

## Interpretação da decisão

B13 é um requisito conservador da equipe, pendente de ratificação pelo responsável do domínio. Os modelos v2/v3 explicam corretamente a regra de 30 dias, mas fecham com responder. Não é prova de alucinação ou de concessão indevida de benefício. Se RH aceitar a interpretação de regra geral, o gabarito e a decisão devem ser revisados, com nova medição registrada, em vez de afirmar uma falha de segurança que não foi demonstrada.

V3 passa nos quatro SLOs agregados e melhora globalmente, mas a decisão de promoção também considera casos críticos e N1. O gate usa média pontual, não o limite inferior do IC: 95% de acerto com IC90% 88%–100% não garante acerto real acima de 90%. O A/A mede só as cinco amostras disponíveis; não demonstra toda a variância possível. Replay torna a reprodução idêntica, não adiciona amostras independentes.
