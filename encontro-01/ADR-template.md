# Agent Decision Record — Equipe do projeto

**Caso:** Dúvidas Internas do Colaborador — Aurora Tecnologia
**Data:** 01/10/2026

**Integrantes:**

- Jhonatan Pereira
- Pedro Henrique Panegossi
- Gabriela Chaves
- Ana Carolina Wichinieski
**Status:** decisão registrada para o protótipo; requisito de qualidade pendente para liberação aos colaboradores.

## 1. Contexto

A Aurora Tecnologia recebe dúvidas recorrentes sobre RH, TI e benefícios. O assistente deve usar as políticas internas, citar fontes, reconhecer ausência ou conflito de informação e encaminhar elegibilidade pessoal ao RH. O exercício compara três arquiteturas sobre os mesmos 10 casos e um corpus de 12 documentos. A escolha equilibra acerto, custo, latência e autonomia necessária para esse escopo.

**Ação irreversível do caso:** comunicar a um colaborador que ele é elegível a um benefício sem análise do RH. Uma correção posterior não desfaz a informação recebida nem decisões tomadas com base nela. Nenhuma das arquiteturas está autorizada a confirmar esse direito individual.

## 2. Alternativas consideradas

Medições de 01/10/2026 com `claude-haiku-4-5-20251001`. A e B rodaram uma vez; C rodou três vezes nos mesmos 10 casos. Em C, acertos e custo total abaixo são médias por rodada; p50 e p95 consideram as 30 execuções individuais.

| Arquitetura | Acertos | Custo total | p50 | p95 | Custo por acerto | Variou entre execuções? |
|---|---|---|---|---|---|---|
| A · Prompt único | 9/10 | US$ 0,03925 | 2,16 s | 3,91 s | US$ 0,00436 | Não medido em repetições controladas |
| B · Workflow | 8/10 | US$ 0,01624 | 1,89 s | 2,20 s | US$ 0,00203 | Não medido em repetições controladas |
| C · Agente em loop | 9/10 em cada rodada | US$ 0,05602 | 4,02 s | 6,36 s | US$ 0,00622 | 0 de 10 casos variaram no desfecho |

**Onde cada uma errou, e por quê:**

- **A — c07:** respondeu ao valor do vale-refeição usando `beneficios-vale-refeicao`, embora todos os documentos estivessem no contexto e o gabarito exigisse reconhecer o conflito com `rh-guia-de-integracao`.
- **B — c07 e c10:** não reconheceu o conflito do vale-refeição; no caso de licença-paternidade e inclusão do bebê no plano, citou apenas `rh-licencas`. Buscar em um único tema limita a cobertura de perguntas que exigem mais de uma área.
- **C — c07 nas três rodadas:** respondeu ao valor do vale-refeição citando apenas `beneficios-vale-refeicao`. A autonomia para buscar não garantiu que a fonte conflitante fosse consultada. Os demais nove casos passaram nas três rodadas, incluindo c09 (encaminhamento ao RH) e c10 (duas áreas).

O indicador de variação do executor compara somente o campo `desfecho`; não compara texto, fontes, custo ou quantidade de chamadas. Em C, as chamadas variaram de 1 a 3 por pergunta mesmo com zero variação de desfecho. A consistência do erro de c07 não representa confiabilidade.

**Evidências versionáveis:**

- [A e B — execução atual](evidencias/comparacao-a-b.csv): 20 resultados, sem erros de API.
- [C — três repetições](evidencias/agente-c-tres-repeticoes.csv): 30 resultados, sem erros de API.
- [Histórico de A](evidencias/historico-a-20260929.csv): 9/10; custo US$ 0,03949.
- [Histórico de B](evidencias/historico-b-20260929.csv): 7/10; custo US$ 0,01533. O c03 encaminhou uma dúvida sobre prazo como elegibilidade; na execução atual, esse caso passou. A diferença evidencia variação entre execuções, sem constituir um teste controlado de estabilidade de B.

Os custos são estimativas do medidor, usando US$ 1,00 por milhão de tokens de entrada e US$ 5,00 de saída configurados no ambiente, não valores reconciliados com a fatura. As 50 execuções atuais custaram US$ 0,223542 no medidor. Latências refletem estas chamadas à API; os processos de A/B e C rodaram simultaneamente e não constituem um benchmark isolado ou um SLA. O avaliador confere desfecho e fontes obrigatórias, não a qualidade completa do texto.

## 3. Decisão

**Adotar a arquitetura A, prompt único, para o protótipo controlado com os 12 documentos atuais.**

A atingiu o mesmo acerto de C, com aproximadamente 30% menos custo por acerto e menor latência nesta medição. B é a alternativa mais barata, mas perdeu uma resposta que depende de duas áreas. Para este corpus pequeno, o loop autônomo não trouxe ganho de acerto que justifique sua complexidade e custo. Esta decisão é específica do escopo medido.

**Requisito antes de liberar respostas automáticas aos colaboradores:** corrigir o tratamento de conflito e obter c07 e c09 corretos em três rodadas completas consecutivas, além de 10/10 acertos em cada uma. Enquanto c07 continuar respondendo a uma informação contraditória, o protótipo deve ser usado com revisão humana. A medição atual não satisfaz esse requisito.

**Escopo de autonomia:** localizar informações no corpus e elaborar respostas gerais com fontes; reconhecer ausência e conflitos com `nao_sei`; encaminhar elegibilidade pessoal ao RH. O sistema não pode confirmar direito individual, alterar cadastros, conceder benefícios nem executar ações nos sistemas da empresa.

**Critério de parada:** A faz uma chamada por pergunta, sem loop. Na avaliação de C, o limite foi de 6 chamadas; ao atingir esse limite sem concluir, o código encaminha ao RH. Esse teto permite buscas complementares e uma resposta final, contendo gasto e duração. Nenhuma das 30 execuções de C chegou ao limite. O loop implementado é equivalente ao da solução de referência em `solucao-encontro-01/arquitetura_c.py`.

## 4. Trade-offs assumidos

- Aceitamos maior custo que B para obter cobertura do caso de duas áreas nesta versão: US$ 0,00436 por acerto em A contra US$ 0,00203 em B.
- A envia todo o corpus em cada pergunta. O custo e o tamanho do contexto crescem com a quantidade de documentos; a decisão deve ser reavaliada ao ampliar o corpus.
- Todos os documentos atuais são políticas gerais fictícias. A não implementa controle de acesso por fonte; documentos restritos não podem ser incluídos sem uma camada de autorização.
- A inclusão de todas as fontes não impediu o erro de conflito. A revisão humana e o requisito de liberação são necessários até corrigir c07.
- Uma execução de A/B e três de C são evidência limitada. O gabarito automático não detecta toda afirmação incorreta no texto e não substitui avaliação de conteúdo.

## 5. Critério de reversão

Os limites abaixo são critérios de engenharia propostos para futuras medições, não resultados já demonstrados:

1. **Troca para workflow:** se o custo por acerto de A ultrapassar US$ 0,00600 em duas avaliações completas consecutivas, substituir A por um workflow B revisado com recuperação de múltiplas áreas. Antes da troca, esse workflow deve alcançar 10/10 em três rodadas, acertar c07 e c09 em todas e manter custo por acerto de até US$ 0,00300. A versão B medida aqui ainda não atende a esse critério.
2. **Reavaliação da autonomia:** considerar C se superar A em pelo menos um acerto por rodada nas mesmas três rodadas, acertar c07 e c09 em todas, custar até US$ 0,00700 por acerto e manter p95 abaixo de 8 s. C atualmente não demonstrou o ganho exigido.
3. **Falha de segurança ou qualidade:** qualquer confirmação indevida de elegibilidade ou resposta afirmativa diante do conflito conhecido suspende a liberação automática e mantém o atendimento sob revisão do RH até a correção e nova avaliação. O erro atual de c07 já impede a liberação.

## 6. Reprodução

A partir da raiz do repositório, com a chave válida no `.env`:

```powershell
.\.venv\Scripts\python.exe -X utf8 encontro-01\rodar.py --arq a b --detalhe
.\.venv\Scripts\python.exe -X utf8 encontro-01\rodar.py --arq c --repeticoes 3 --detalhe
```

A pasta `evidencias/` contém as cópias usadas neste ADR e pode ser versionada. `resultados/` continua sendo a saída local ignorada pelo Git.
