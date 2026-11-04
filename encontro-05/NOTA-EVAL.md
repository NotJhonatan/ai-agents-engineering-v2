# Nota de avaliação · Encontro 5

**ValidAI · Aurora · 04/11/2026**
**Integrantes:** Jhonatan Pereira; Pedro Henrique Panegossi; Gabriela Chaves; Ana Carolina Wichinieski.

## 1 · Golden set do grupo

[Oito casos](golden-equipe.json), baseados na wiki. B13/B22 instáveis; B13 reprovado pelo juiz em 2/5; B18 sem resposta; quatro casos numéricos.

| id | foco | desfecho | fonte da wiki | valor/ação |
|---|---|---|---|---|
| B03 | despesas | responder | fin-viagens-e-reembolso | 10 dias corridos |
| B08 | VPN 720 | responder | ti-vpn-codigos-de-erro | Certificado Aurora |
| B12 | odontológico | responder | beneficios-plano-odontologico | R$22/mês |
| B13 | bebê/carência | escalar | beneficios-plano-de-saude §§5.2–5.3 + regra 4 | RH |
| B16 | creche | responder | beneficios-auxilio-creche | até R$600 |
| B18 | refeitório | nao_sei | ausente nas 25 páginas | não inventar |
| B20 | presente | responder | rh-codigo-de-conduta | teto R$200 |
| B22 | PJ/vale | escalar | beneficios-vale-refeicao + regra 4 | RH |

[Textos obrigatórios/proibidos e perguntas integrais](evidencias/gabarito.md) estão também no JSON entregue.

**B13 ambíguo:** explicar o prazo geral ou decidir este dependente? Escolhemos `escalar` pela regra 4; não é erro numérico, requer ratificação do RH. [Fundamentos e revisão da régua](evidencias/fundamentos.md).

## 2 · Placar

Avaliação do agente único em três versões: 33 casos × 5 amostras × 3 versões = 495 atendimentos em replay.

| versão | acerto (IC 90%) | pass^5 | instáveis | US$/acerto | p95 (s) | loops |
|---|---|---|---|---|---|---|
| v1 · produção | 78% (67%–87%) | 64% | 10/33 | 0.00073 | 9.7 | 12% |
| v2 · prompt enxuto (PR #42) | 75% (62%–87%) | 73% | 2/33 | 0.00046 | 5.7 | 2% |
| v3 · modelo mais barato | 95% (88%–100%) | 91% | 2/33 | 0.00023 | 4.4 | 0% |

Custos e tempos do modelo são os registrados na gravação; a busca foi medida localmente. Reproduzir o replay não acrescenta amostras independentes.

## 3 · Regressão ou ruído

- **A/A:** até **3,03 pp** entre rodadas da v1.
- **PR #42:** −2,42 pp (IC90% −10,30 a +5,45), **não dá para afirmar**, diferença menor que o ruído. Pioram P1/R1/G5/B13; melhoram C2/B22.
- **Barato:** +16,97 pp (+5,45 a +29,09), **melhora**, acima do ruído. Pioram N1/B13; melhoram S1/S2/P1/R1/R2/G5/G6/B18/B22.

Só grupo: PR=0 pp (−22,5 a +25); turma: −3,2 pp (−11,2 a +4). Veredito igual; grupo revela B13 (4/5→0/5) e B22 (1/5→5/5). O A/A observado não limita variação futura.

## 4 · SLOs e gate

Metas propostas pela equipe: **90% acerto**, piso RH/Produto (orçamento de erro 10%); **US$0,002/acerto**, teto FinOps; **p95≤10 s**, espera Produto; **loops≤2%**, no máximo 1/50, Operação. A validação das metas cabe às áreas indicadas; casos críticos têm revisão separada.

| SLO | v1 · produção | v2 · prompt enxuto (PR #42) | v3 · modelo mais barato |
|---|---|---|---|
| acerto ≥ 90% | **FALHA** (78%) | **FALHA** (75%) | passa (95%) |
| custo_por_acerto ≤ US$ 0.00200 | passa (US$ 0.00073) | passa (US$ 0.00046) | passa (US$ 0.00023) |
| p95_segundos ≤ 10.0s | passa (9.7s) | passa (5.7s) | passa (4.4s) |
| bateu_limite ≤ 2% | **FALHA** (12%) | passa (2%) | passa (0%) |

**Decisão:** não promover v2 nem liberar atendimento autônomo. V1 falha qualidade/loops; v2, qualidade. V3 passa no gate, mas perde B13 e N1 (5/5→2/5). Priorizar v3 com revisão humana; reconsiderar após ratificação do gabarito, correção B13/N1, SLOs cumpridos e B13/B22/X1 corretos nas cinco amostras. IC inferior de v3=88%: o gate usa média, não garantia de ≥90%.

## 5 · Um atendimento por dentro

**B13/v2/amostra 0:** duas chamadas (1,044+1,441 s), busca ~0,4 ms, 1.363 tokens, US$0,0002571. Busca retorna `beneficios-plano-de-saude`; passo 2 responde em vez de escalar. Falha na decisão final (step/outcome), não recuperação; restaurar encaminhamento após validar a ambiguidade. [Cascata](evidencias/cascata-v2-B13-a0.png); [trace](evidencias/diagnostico.txt).

**Reprodução:** com `.venv`, `python -X utf8 encontro-05/experimento_equipe.py`. [Evidências/hashes](evidencias/experimentos.json).
