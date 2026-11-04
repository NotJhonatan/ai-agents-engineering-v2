# Nota de chunking · ValidAI

**Caso:** Aurora · **Data:** 04/11/2026
**Integrantes:** Jhonatan Pereira; Pedro Henrique Panegossi; Gabriela Chaves; Ana Carolina Wichinieski.

## 1. O que adotamos

Seções Markdown (`##`) com título e seção prefixados; busca híbrida (vetor + BM25/RRF), modelo local `intfloat/multilingual-e5-small`, **k=3**. Apenas `autoridade=oficial`; maior `vigencia` por `politica` entre 9 candidatos, retornando até 3.

## 2. Por quê

Tabela do avaliador original: **encontrados/casos (contaminados)**. Contaminação: trecho enganoso antes do correto, ou sem ele. São 25 páginas e 19 perguntas; 3 sem resposta não entram no placar.

| configuração | normal | excecao | conflito | termo-exato | autoridade | total |
|---|---|---|---|---|---|---|
| base: tamanho 400 · vetor | 7/7 (0) | 2/2 (1) | 2/3 (3) | 3/3 (1) | 1/1 (0) | 15/16 (5) |
| estrutura · vetor | 6/7 (0) | 2/2 (0) | 2/3 (3) | 3/3 (0) | 1/1 (0) | 14/16 (3) |
| estrutura · BM25 | 5/7 (0) | 2/2 (0) | 1/3 (3) | 3/3 (0) | 1/1 (0) | 12/16 (3) |
| estrutura · híbrida | 6/7 (0) | 2/2 (0) | 1/3 (3) | 3/3 (0) | 1/1 (0) | 13/16 (3) |
| estrutura · híbrida · vigente | 6/7 (0) | 2/2 (0) | 3/3 (0) | 3/3 (0) | 1/1 (0) | 15/16 (0) |
| estrutura · híbrida · vigente · oficial | 6/7 (0) | 2/2 (0) | 3/3 (0) | 3/3 (0) | 1/1 (0) | 15/16 (0) |

Mudamos um parâmetro por configuração. Estrutura zerou contaminação em exceções e termos exatos. Na híbrida, vigência elevou conflitos de 1/3 para 3/3. Adotamos a última: mantém **15/16 (93,75%)** da base, reduzindo contaminação de **5 para 0**. Autoridade não melhorou o placar; exclui resumos como fonte normativa. Uma rodada; mede recuperação, não resposta final ou latência.

## 3. O que ela não resolve

**N5 — roubo de notebook:** `ti-equipamentos#1` contém o procedimento inteiro, mas o top 3 traz devolução, introdução e erro 720. Causa: chunking/contexto e ranking; “notebook” ficou na introdução separada. Avaliar enriquecimento de contexto ou reranking.

**S1 — previdência privada:** retorna licenças, seguro e plano odontológico. Falta informação no corpus; a etapa de resposta deve verificar suporte, dizer “não sei” e encaminhar a Benefícios. RRF não é probabilidade. O filtro de vigência também pode conservar versão antiga se a nova não for recuperada; validar versões na ingestão é melhoria futura.

## 4. O que a ingestão precisa garantir

| Metadado | Responsável e atualização | Efeito se estiver errado |
|---|---|---|
| `politica` | Dono, na criação/migração; identificador comum às versões | Não agrupa versões ou mistura políticas |
| `vigencia` | Dono, em cada aprovação; ingestão valida data ISO | Escolhe versão errada; data não garante aplicabilidade |
| `autoridade` | Área responsável, ao publicar/reclassificar | Resumo vira regra ou oficial é descartada |
| `titulo`, seção, `dono`; `id`/`arquivo`, `chunk_id` | Autor atualiza contexto e dono; ingestão mantém origem/ids ao reindexar | Perde contexto, citação ou responsável |

**Evidências:** [trechos, versões e hashes](evidencias/experimentos.json). Reprodução na raiz, com `.venv`: `python -X utf8 encontro-03/experimento_equipe.py`.
