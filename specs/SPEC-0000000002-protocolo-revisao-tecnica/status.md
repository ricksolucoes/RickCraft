# Status — SPEC-0000000002

## Estado corrente

- **Etapa atual:** IMPLEMENT
- **SPEC:** COMPLETE — aprovada pelo responsável pelo projeto
- **PLAN:** COMPLETE — aprovada pelo responsável pelo projeto
- **TASKS:** COMPLETE — aprovada pelo responsável pelo projeto
- **ANALYZE:** PASS — ANALYZE-2026-10-11-SPEC-0000000002-01
- **IMPLEMENT:** IN_PROGRESS - TASK-009 concluida, aguardando revisao
- **CONVERGE:** NOT_STARTED
- **Último gate válido:** ANALYZE-2026-10-11-SPEC-0000000002-01
- **Execution ID:** ANALYZE-2026-10-11-SPEC-0000000002-01

## Início de IMPLEMENT — TASK-001 — 2026-10-11

O responsável autorizou exclusivamente TASK-001 nas versões SPEC `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC`, PLAN `8ED06179C5251CCFC534E9E6A4549D0E81F9FFCDA367F567C935894CA9087EDB` e TASKS `4C40D81D5B013FAA9462F0FA4F68F6160F6FB6CED991582DB19B30642A97A172`, usando o gate válido `ANALYZE-2026-10-11-SPEC-0000000002-01 = PASS`. Os três hashes foram recalculados e conferem; ANALYZE permanece válido porque suas entradas normativas não mudaram. Etapa atual = IMPLEMENT; IMPLEMENT = IN_PROGRESS; TASK-001 = IN_PROGRESS; TASK-002–TASK-013 não iniciadas; CONVERGE = NOT_STARTED.

## Início de IMPLEMENT — TASK-002 — 2026-10-11

O responsável confirmou a aprovação externa da TASK-001. Seus hashes aceitos são `review_protocol.py` `D5A77D092E293FF5E60F07C55A7A751B1BCAEBC382DD5C92FCC4BF50876063C7` (blob Git `77d1fca0d49e5fba99801a40eabc7bbe64e3f033`) e `test_review_protocol.py` `1E2B01EFB17972608BC8F5AC719950D6011465F9D7EDF5530B5D32E49196B1F8` (blob Git `f46e9595cd2a9bc4138dedb1e150118d75593235`). Os hashes de SPEC/PLAN/TASKS foram recalculados e conferem com as versões aprovadas; ANALYZE-01 permanece PASS. A autorização recebida é somente para TASK-002. Etapa atual = IMPLEMENT; TASK-001 = COMPLETE — aprovada após revisão externa; TASK-002 = IN_PROGRESS; TASK-003–TASK-013 não executadas; CONVERGE = NOT_STARTED.

## Início de IMPLEMENT — TASK-003 — 2026-10-11

O responsável confirmou a aprovação externa da TASK-002. Seus hashes aceitos são `review_protocol.py` `3F16B432A421DEE448A9635711DCEEA78D4065404C1B84BB4C5480D21F88C1F2` (blob Git `473ff66c6bec6fecec26d2be288b05e22b6ef37f`) e `test_review_protocol.py` `8129136DEAAADC405CD91A137FBA8F732189FD5CB213C113BA297A2288C08DB2` (blob Git `69251531146b4d87f50099331482cd7cc98c15ba`). Os hashes de SPEC/PLAN/TASKS foram recalculados e conferem com as versões aprovadas; ANALYZE-01 permanece PASS. A autorização recebida é somente para TASK-003. Etapa atual = IMPLEMENT; TASK-001 e TASK-002 = COMPLETE e aprovadas; TASK-003 = IN_PROGRESS; TASK-004–TASK-013 não executadas; CONVERGE = NOT_STARTED.

## IMPLEMENT — TASK-003 — Evidências e verification claims

- **Estado:** TASK-001 e TASK-002 = COMPLETE — aprovadas após revisão externa; TASK-003 = COMPLETE — aguardando revisão; TASK-004–TASK-013 não executadas. IMPLEMENT permanece IN_PROGRESS; ANALYZE permanece PASS; CONVERGE permanece NOT_STARTED.
- **Versões usadas:** SPEC `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC`; PLAN `8ED06179C5251CCFC534E9E6A4549D0E81F9FFCDA367F567C935894CA9087EDB`; TASKS `4C40D81D5B013FAA9462F0FA4F68F6160F6FB6CED991582DB19B30642A97A172`; gate `ANALYZE-2026-10-11-SPEC-0000000002-01 = PASS`.
- **TASK-002 preservada:** hashes aceitos `review_protocol.py` `3F16B432A421DEE448A9635711DCEEA78D4065404C1B84BB4C5480D21F88C1F2` e `test_review_protocol.py` `8129136DEAAADC405CD91A137FBA8F732189FD5CB213C113BA297A2288C08DB2`.
- **Contratos:** adicionados `EvidenceKind`, `VerificationStatus`, `EvidenceReference` e `VerificationClaim`. EvidenceReference preserva kind/origin/reference/target e campos opcionais version/digest/limitation/verifiability, todos explicitamente fornecidos, sem abrir origem, calcular hash ou inferir campo ausente. As quatro classes de evidência e cinco estados de claim são enums distintos. Status de verificabilidade como `MATCHED`, `CHANGED_REASSESS`, `UNAVAILABLE` e `UNVERIFIABLE` permanecem valores opacos separados do estado de VerificationClaim.
- **Validação:** `EXECUTED_OBSERVED` requer ao menos uma `DIRECT_OBSERVATION`; `REPORTED`, `INFERENCE` ou `PERSISTED_EVIDENCE` sozinhos não demonstram execução atual. `HISTORICAL_IDENTIFIED` requer referência `PERSISTED_EVIDENCE` e permanece distinto de execução observada. Claims validam target e versões quando ambas explícitas; coleções são copiadas, referências duplicadas rejeitadas e ordenação canonizada. `NOT_EXECUTED` admite zero referências; `UNAVAILABLE` e `INCONCLUSIVE` permanecem estados distintos. Nenhum booleano ou ausência de erro gera claim positivo.
- **Testes executados:** `python -B -m unittest -v impl.tests.test_review_protocol` — `Ran 70 tests`; `OK`; 70 PASS, 0 FAIL, 0 SKIP. Inclui integralmente os testes regressivos de TASK-001 e TASK-002, além das classes, estados, campos, compatibilidade alvo/versão, imutabilidade e não promoção de histórico/relato/inferência.
- **Hashes SHA-256 finais, calculados duas vezes após a última alteração e leitura UTF-8 estrita:** `review_protocol.py` = `2F9F2AE2512E78572A7561666122967CAF11DBF4253B3846F15B1D1731852C96`; `test_review_protocol.py` = `93981E2A1E04068597900723B188685B8A59FF87925DF0D79616B05DEDC30FC9`.
- **Fronteiras:** runtime importa somente `dataclasses`, `enum`, `typing` e `__future__` da biblioteca padrão; inspeção não encontrou import/chamada de provenance, filesystem/workspace, gap_handling, rede, subprocesso ou Git. Nenhuma observação automática, publicação, persistência, cálculo de hash, efeito externo, Release ou push ocorreu. Nenhum módulo/teste SPEC1 foi alterado.
- **Validação normativa:** hashes SPEC/PLAN/TASKS continuam nas versões aprovadas; ANALYZE-01 permanece PASS e último gate válido. `git diff --check` foi executado ao final.

### CHECKPOINT RICKCRAFT — TASK-003

## Fase executada
IMPLEMENT — TASK-003 — SPEC-0000000002

## Objetivo da execução
Representar evidências e verification claims sem duplicar proveniência SPEC1 nem observar fontes automaticamente.

## Estado
AGUARDANDO_APROVAÇÃO — TASK-003 concluída.

## Gate utilizado
ANALYZE-2026-10-11-SPEC-0000000002-01 = PASS.

## Testes executados
`python -B -m unittest -v impl.tests.test_review_protocol` — 70/70 PASS; 0 FAIL; 0 SKIP.

## Evidências
`review_protocol.py`: `2F9F2AE2512E78572A7561666122967CAF11DBF4253B3846F15B1D1731852C96`.
`test_review_protocol.py`: `93981E2A1E04068597900723B188685B8A59FF87925DF0D79616B05DEDC30FC9`.

## Arquivos alterados
- `impl/src/RickCraft/review_protocol.py`
- `impl/tests/test_review_protocol.py`
- `specs/SPEC-0000000002-protocolo-revisao-tecnica/status.md`

## Próximo passo recomendado
Revisar exclusivamente TASK-003 antes de autorizar TASK-004.

## O que NÃO deve ser feito ainda
Não executar TASK-004, integrar `gap_handling`, executar CONVERGE ou Release; não fazer push.

### HANDOFF PARA REVISÃO — TASK-003

Revisar `review_protocol.py`, `test_review_protocol.py` e este registro. TASK-003 está COMPLETE após 70 testes focais aprovados, incluindo a regressão de TASK-001/002. TASK-004–TASK-013 não foram iniciadas. IMPLEMENT continua IN_PROGRESS; CONVERGE NOT_STARTED. É necessária autorização explícita separada antes de TASK-004.

## IMPLEMENT — TASK-002 — Contexto de autoridade e precedência explícita

- **Estado:** TASK-001 = COMPLETE — aprovada após revisão externa; TASK-002 = COMPLETE — aguardando revisão; TASK-003–TASK-013 não executadas. IMPLEMENT permanece IN_PROGRESS; CONVERGE permanece NOT_STARTED.
- **Versões usadas:** SPEC `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC`; PLAN `8ED06179C5251CCFC534E9E6A4549D0E81F9FFCDA367F567C935894CA9087EDB`; TASKS `4C40D81D5B013FAA9462F0FA4F68F6160F6FB6CED991582DB19B30642A97A172`; gate `ANALYZE-2026-10-11-SPEC-0000000002-01 = PASS`.
- **TASK-001 preservada:** hashes aceitos `review_protocol.py` `D5A77D092E293FF5E60F07C55A7A751B1BCAEBC382DD5C92FCC4BF50876063C7` e `test_review_protocol.py` `1E2B01EFB17972608BC8F5AC719950D6011465F9D7EDF5530B5D32E49196B1F8`; os 27 testes anteriores continuam passando na execução focal conjunta.
- **Implementação TASK-002:** adicionados `AuthorityReference`, `AuthorizedPrecedence` e `AuthorityContext` como dataclasses congeladas. Referência exige source, owner informado, referência de competência e escopos explícitos únicos. Precedência usa direção explícita (`prevailing_source` sobre `subordinate_source`), escopo, autoridade autorizadora e decision reference. O contexto vazio é válido. O contexto rejeita autoridade autorizadora ausente ou fora do escopo, relação duplicada, relações opostas e mais de uma relação ambígua para o mesmo par/escopo. `precedence_for` consulta apenas o par e escopo exatos e retorna a relação declarada ou `None`; não ranqueia nem infere precedência.
- **Autoridade:** owner e competência permanecem declarações/referências recebidas do host. Não há owners hard-coded, autenticação criptográfica, import de Policies/Registries/SPECs, consulta externa, inferência por data/nome/especificidade ou promoção automática de executor/Agent/auditor. Nenhuma integração com `gap_handling` foi adicionada.
- **Testes executados:** `python -B -m unittest -v impl.tests.test_review_protocol` — `Ran 45 tests`; `OK`; 45 PASS, 0 FAIL, 0 SKIP. Os 27 casos da TASK-001 passaram junto com os casos de autoridade/precedência desta tarefa.
- **Hashes SHA-256 após a implementação:** `review_protocol.py` = `3F16B432A421DEE448A9635711DCEEA78D4065404C1B84BB4C5480D21F88C1F2`; `test_review_protocol.py` = `8129136DEAAADC405CD91A137FBA8F732189FD5CB213C113BA297A2288C08DB2`.
- **Fronteiras:** alteração restrita aos dois arquivos existentes da TASK-001 e a este status. Biblioteca padrão somente. Nenhum módulo/teste SPEC1 foi alterado; nenhuma suíte completa, integração, persistência, rede, Git, subprocesso, Release ou push foi executado.
- **Validação:** hashes SPEC/PLAN/TASKS conferem com as bases autorizadas; ANALYZE-01 permanece PASS; `git diff --check` executado ao final.

### CHECKPOINT RICKCRAFT — TASK-002

## Fase executada
IMPLEMENT — TASK-002 — SPEC-0000000002

## Objetivo da execução
Representar e validar autoridade, competência, escopo e precedência explícita.

## Estado
AGUARDANDO_APROVAÇÃO — TASK-002 concluída.

## Gate utilizado
ANALYZE-2026-10-11-SPEC-0000000002-01 = PASS.

## Testes executados
`python -B -m unittest -v impl.tests.test_review_protocol` — 45/45 PASS, incluindo regressão dos 27 casos TASK-001.

## Evidências
`review_protocol.py`: `3F16B432A421DEE448A9635711DCEEA78D4065404C1B84BB4C5480D21F88C1F2`.
`test_review_protocol.py`: `8129136DEAAADC405CD91A137FBA8F732189FD5CB213C113BA297A2288C08DB2`.

## Arquivos alterados
- `impl/src/RickCraft/review_protocol.py`
- `impl/tests/test_review_protocol.py`
- `specs/SPEC-0000000002-protocolo-revisao-tecnica/status.md`

## Próximo passo recomendado
Revisar exclusivamente TASK-002 antes de autorizar TASK-003.

## O que NÃO deve ser feito ainda
Não executar TASK-003, integrar `gap_handling`, executar CONVERGE ou Release; não fazer push.

### HANDOFF PARA REVISÃO — TASK-002

Revisar os dois artefatos de implementação e este registro. TASK-002 está COMPLETE após 45 testes focais aprovados. TASK-001 permanece aprovada; TASK-003–TASK-013 não executadas. IMPLEMENT continua IN_PROGRESS e CONVERGE NOT_STARTED. É necessária autorização explícita separada antes de TASK-003.

## IMPLEMENT — TASK-001 — Pedido, escopo, idioma e autorização

- **Estado:** TASK-001 = COMPLETE, aguardando revisão; TASK-002–TASK-013 não executadas. IMPLEMENT permanece IN_PROGRESS; CONVERGE permanece NOT_STARTED.
- **Versões usadas:** SPEC `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC`; PLAN `8ED06179C5251CCFC534E9E6A4549D0E81F9FFCDA367F567C935894CA9087EDB`; TASKS `4C40D81D5B013FAA9462F0FA4F68F6160F6FB6CED991582DB19B30642A97A172`; gate `ANALYZE-2026-10-11-SPEC-0000000002-01 = PASS`.
- **Arquivos criados:** `impl/src/RickCraft/review_protocol.py`; `impl/tests/test_review_protocol.py`.
- **Modelos:** `ReviewInputError`, `AuthorizationGrant` (exatamente REVIEW, STRUCTURAL_CHANGE, FUNCTIONAL_CHANGE, LOCAL_PERSISTENCE), `RequestedEffect` (LOCAL_PERSISTENCE, EXTERNALITY), `ReviewScope` e `ReviewRequest`. Classes são dataclasses congeladas; coleções de entrada são copiadas para tuplas, entradas não ordenadas são canonicalizadas, e IDs/artefatos/versões são validados sem inferir escopo.
- **Validações:** textos obrigatórios; escopo e IDs explícitos/únicos; dependências e artefatos sem duplicatas; allowlist/exclusions não se sobrepõem; source_versions possui pares não vazios sem identidade duplicada; grants/effects exigem os enums corretos; REVIEW é obrigatório; FUNCTIONAL_CHANGE requer STRUCTURAL_CHANGE; LOCAL_PERSISTENCE solicitado sem grant continua sem autorização; EXTERNALITY é reconhecida, mas não há grant/capacidade externa; `language=None` mantém o default semântico pt-BR e idioma explícito é preservado sem normalização.
- **Classes futuras:** não foram criados modelos de autoridade, precedência, evidência, claims, dimensões, findings, conclusão, mudança, resposta, renderer, pipeline ou persistência.
- **Teste executado:** `python -B -m unittest -v impl.tests.test_review_protocol` — `Ran 27 tests`; `OK`; 27 PASS, 0 FAIL, 0 SKIP. Cobertura inclui escopo/request válidos e inválidos, duplicidade, fronteiras de grants/effects, idioma, imutabilidade e isolamento contra mutação das coleções originais.
- **Hashes SHA-256:** `review_protocol.py` = `D5A77D092E293FF5E60F07C55A7A751B1BCAEBC382DD5C92FCC4BF50876063C7`; `test_review_protocol.py` = `1E2B01EFB17972608BC8F5AC719950D6011465F9D7EDF5530B5D32E49196B1F8`.
- **Fronteiras:** implementação usa somente biblioteca padrão (`dataclasses`, `enum`, `typing`). Inspeção estática não encontrou import/uso de subprocess, socket, urllib, Git, requests, upload/sync ou ferramentas Release; nenhuma externalidade foi executada. Nenhum módulo/teste SPEC1 foi alterado; nenhum teste SPEC1 ou suíte completa foi executado. Nenhum Release ou push ocorreu.
- **Estado normativo:** hashes SPEC/PLAN/TASKS foram confirmados inalterados; ANALYZE-01 continua PASS e último gate válido. Nenhum outro arquivo foi criado/alterado além dos dois artefatos TASK-001 e deste status.

### CHECKPOINT RICKCRAFT — TASK-001

## Fase executada
IMPLEMENT — TASK-001 — SPEC-0000000002

## Objetivo da execução
Implementar somente os modelos de pedido, escopo, idioma, efeitos solicitados e autorização.

## Estado
AGUARDANDO_APROVAÇÃO — TASK-001 concluída.

## Gate utilizado
ANALYZE-2026-10-11-SPEC-0000000002-01 = PASS.

## Testes executados
`python -B -m unittest -v impl.tests.test_review_protocol` — 27/27 PASS.

## Evidências
`review_protocol.py`: `D5A77D092E293FF5E60F07C55A7A751B1BCAEBC382DD5C92FCC4BF50876063C7`.
`test_review_protocol.py`: `1E2B01EFB17972608BC8F5AC719950D6011465F9D7EDF5530B5D32E49196B1F8`.

## Arquivos criados
- `impl/src/RickCraft/review_protocol.py`
- `impl/tests/test_review_protocol.py`

## Arquivos alterados
- `specs/SPEC-0000000002-protocolo-revisao-tecnica/status.md`

## Próximo passo recomendado
Revisar exclusivamente TASK-001 antes de autorizar TASK-002.

## O que NÃO deve ser feito ainda
Não executar TASK-002, CONVERGE ou Release; não fazer push.

### HANDOFF PARA REVISÃO — TASK-001

Revisar `review_protocol.py`, `test_review_protocol.py` e este registro. TASK-001 está COMPLETE após 27 testes focais aprovados. IMPLEMENT continua IN_PROGRESS; TASK-002–TASK-013 não iniciadas; CONVERGE permanece NOT_STARTED. É necessária autorização explícita separada antes de TASK-002.

## Aprovação de TASKS e início de ANALYZE — 2026-10-11

O responsável pelo projeto aprovou TASKS no SHA-256 `4C40D81D5B013FAA9462F0FA4F68F6160F6FB6CED991582DB19B30642A97A172`, blob Git `065c76d6b6c3b0d5236acdd4def6890a1cce0a5a`. A autorização concedida limita-se ao gate ANALYZE; não autoriza IMPLEMENT, CONVERGE ou Release. Os hashes de entrada confirmados são SPEC `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC` e PLAN `8ED06179C5251CCFC534E9E6A4549D0E81F9FFCDA367F567C935894CA9087EDB`.

O execution ID `ANALYZE-2026-10-11-SPEC-0000000002-01` não existia anteriormente neste status. A etapa corrente passou a ANALYZE e o gate a IN_PROGRESS nesta execução. SPEC, PLAN e TASKS permanecem COMPLETE e aprovadas; IMPLEMENT e CONVERGE permanecem NOT_STARTED; último gate válido permanece nenhum.

## ANALYZE — ANALYZE-2026-10-11-SPEC-0000000002-01

- **Data:** 2026-10-11.
- **Resultado:** PASS para as três versões exatas abaixo; nenhum achado bloqueante ou não bloqueante foi identificado.
- **SPEC:** SHA-256 `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC`; blob Git aprovado `97f1a98c4f3b25bf52c0fa71c29502a39e9ca556`.
- **PLAN:** SHA-256 `8ED06179C5251CCFC534E9E6A4549D0E81F9FFCDA367F567C935894CA9087EDB`; blob Git aprovado `0c28cf63a68e09365e1fb3ead7a02e609b60fcfa`.
- **TASKS:** SHA-256 `4C40D81D5B013FAA9462F0FA4F68F6160F6FB6CED991582DB19B30642A97A172`; blob Git publicado `065c76d6b6c3b0d5236acdd4def6890a1cce0a5a`.
- **Pré-flight:** hashes locais recalculados após leitura UTF-8 estrita coincidem integralmente com os valores aprovados. O status não continha execução anterior com este ID. SPEC, PLAN e TASKS não foram alterados nesta execução.
- **Aprovação:** TASKS aprovada pelo responsável em 2026-10-11; autorização limitada exclusivamente a ANALYZE. Este PASS não inicia IMPLEMENT.

### Fontes e método

Foram lidos integralmente README_PTBr.md, README.md, POL-0000000001, POL-0000000002, POL-0000000003, registries/policies.md, registries/spec-groups.md, registries/specifications.md, SPEC-0000000002/spec.md, plan.md, tasks.md e status.md. Foram lidos também SPEC-0000000001/spec.md, plan.md, tasks.md e status.md para os contratos dependentes. Foram inspecionados read-only os módulos citados: `gap_handling.py`, `provenance.py`, `analysis_lifecycle.py`, `document_publisher.py`, `document_recovery.py`, `document_search.py`, `document_catalog.py`, `document_format.py`, `workspace_resolver.py`, `workspace_probe.py` e `rickcraft_root.py`, além da presença e dos testes correspondentes da implementação SPEC1. Nenhum teste foi executado; resultados de testes IMPLEMENT não foram inferidos como existentes para SPEC2.

O gate comparou o conteúdo substantivo dos requisitos, critérios e cenários às decisões e tarefas, e não confiou somente nas matrizes declaradas. Também examinou as fronteiras autorizadas, as dependências, a autoridade, precedência, efeitos, idioma, persistência e estratégias de evidência futura.

### Matriz RF-001–RF-021 → PLAN

Todos SATISFIED nesta análise de consistência:

| RF | Decisão/seção pertinente do PLAN | Avaliação |
|---|---|---|
| RF-001 | D-02, §§2 e 4 | Pedido, escopo, allowlist/exclusions e validação explícitos. |
| RF-002 | D-06, D-10 | Observação, relato, persistência e inferência são distintos e referenciados. |
| RF-003 | D-05, D-07, §§5 e 9 | Aplicabilidade e análise precedem recomendação; N/A não fabrica achado. |
| RF-004 | D-03, D-09, §5 | Grants separados; host/executor e Core têm fronteiras distintas. |
| RF-005 | D-03, D-11 | Review sem grant não altera nem cria mudança para preencher resposta. |
| RF-006 | D-11 | Três blocos semânticos obrigatórios, ordenados, com N/A explícito. |
| RF-007 | D-07 | Finding separa condição, evidência, regra, conclusão, impacto e recomendação. |
| RF-008 | D-07, D-09 | Mudança/proposta vinculada ao objetivo e comportamento/risco. |
| RF-009 | D-06, D-10 | Claims têm estado, alvo/versão e evidência; ausência de erro não é validação. |
| RF-010 | D-04, D-06, D-13 | Dados/autoridade ausentes limitam ou bloqueiam; não são inventados. |
| RF-011 | D-04, §2 | Precedência requer relação explicitamente autorizada; sem ranking implícito. |
| RF-012 | D-05 | Dimensões especializadas são encaminhadas sem decisão substantiva do Core. |
| RF-013 | D-04, D-08 | Conflito sem precedência autorizada não seleciona vencedor nem owner. |
| RF-014 | D-08, D-13 | Bloqueio localizado/transitivo e continuidade apenas de independente apto. |
| RF-015 | D-07, D-11 | Recomendação proporcional e sem código/seção artificial. |
| RF-016 | D-03, D-12, D-15 | Sem externalidade implícita; persistência local apenas opt-in via SPEC1. |
| RF-017 | D-02, D-11, D-15 | Idioma solicitado preservado, None=pt-BR, sem tradução/duplicação; Release futuro separado. |
| RF-018 | D-05 | Dimensões pertinentes consideradas; insuficiência e autoridade especializada preservadas. |
| RF-019 | D-09 | Refatoração sem grant funcional exige claims vinculados a contrato, base/candidata e verificação observada. |
| RF-020 | D-10 | Conclusão limitada a escopo, versões, fontes, evidências e verificações. |
| RF-021 | D-12 | Persistência de continuidade usa contrato SPEC1 sem redefini-lo. |

### Matriz D-01–D-15 → TASKS

Todos SATISFIED quanto a cobertura executável, arquivos, dependências e evidência planejada:

| Decisão | TASK(s) executora(s) | Verificação da análise |
|---|---|---|
| D-01 | 009, 013 | Pipeline coeso no único módulo autorizado; sem orquestrador/Agent. |
| D-02 | 001, 009 | Request/escopo/idioma e pipeline têm testes focais. |
| D-03 | 001, 011 | Grants conservadores e fronteiras negativas cobertas. |
| D-04 | 002, 006 | Contexto/precedência explícitos e conflito exercitados. |
| D-05 | 004, 009 | Assessment especializado e integração sem promoção consultiva. |
| D-06 | 003, 009 | Evidências/claims e estados ligados a alvo/versão. |
| D-07 | 005, 009 | Findings/conclusões e ordenação determinística. |
| D-08 | 006, 009 | Reuso das duas APIs puras existentes, sem duplicar engine. |
| D-09 | 007, 009 | Proposta não edita; prova de base/candidata/contrato/claim. |
| D-10 | 005, 009 | Conclusão limitada e escopo parcial cobertos. |
| D-11 | 008, 009 | Renderer, três blocos, idioma/default, UTF-8 e ausência de duplicata. |
| D-12 | 010 | Integração opt-in em fixture e round-trip com APIs SPEC1. |
| D-13 | 006, 009 | Outcomes conservadores, bloqueio local e dependência. |
| D-14 | 012, 013 | Coleções, desempates, idioma, dependências e clock têm testes previstos. |
| D-15 | 008, 011 | Idioma/Release separados e testes negativos de efeitos. |

TASK-013 é integração/evidência final e não substitui as tarefas de implementação. Não foi encontrada decisão sem tarefa executora anterior. A sequência declarada é coerente com as dependências do modelo e da integração, sem paralelismo oculto.

### Matriz CA-001–CA-021 → TASK/evidência futura

Todos PASS quanto à existência de estratégia futura executável e rastreável; isso não declara que os testes de IMPLEMENT já foram executados:

| CA | TASK(s) | Evidência planejada considerada suficiente |
|---|---|---|
| CA-001 | 001, 009, 012, 013 | Escopo/exclusões e resultado limitado em request/pipeline. |
| CA-002 | 003, 009, 012, 013 | Tipos de evidência, estados de claim e insuficiência. |
| CA-003 | 008, 009, 013 | Ordem da resposta e análise antes de recomendação. |
| CA-004 | 001, 007, 011, 013 | Grants, mudança proibida e snapshots/spies. |
| CA-005 | 001, 008, 011, 013 | Não aplicabilidade sem alteração artificial. |
| CA-006 | 008, 013 | Presença/ordem dos três blocos semânticos. |
| CA-007 | 005, 009, 013 | Liga finding a evidência, regra, impacto e owner. |
| CA-008 | 005, 007, 013 | Justificativa ligada a proposta, objetivo e consequência. |
| CA-009 | 003, 009, 013 | Claim com status, versão/alvo e referência compatível. |
| CA-010 | 002, 003, 006, 013 | Lacuna, owner/precedência ausente e bloqueio sem inferência. |
| CA-011 | 002, 013 | Autoridade normativa e precedência autorizada. |
| CA-012 | 004, 013 | Assessment consultivo versus authoritative e owner. |
| CA-013 | 002, 006, 013 | Sem AuthorizedPrecedence: nenhuma vencedora/autoridade inventada. |
| CA-014 | 006, 009, 013 | Dependência direta/transitiva/desconhecida e escopo independente. |
| CA-015 | 008, 013 | N/A/recomendação sem mecanismo ou complexidade desnecessária. |
| CA-016 | 001, 010, 011, 013 | Opt-in e spies para persistência/rede/Git/subprocess/Release. |
| CA-017 | 001, 008, 012, 013 | None=pt-BR, idioma host fornecido preservado, uma saída, UTF-8; internos pt-BR. |
| CA-018 | 004, 013 | Dimensões pertinentes e insuficientes sem decisão Core especializada. |
| CA-019 | 007, 013 | Boolean isolado rejeitado; claims ligados a contrato e versões. |
| CA-020 | 005, 013 | Classe/arquivo não generaliza para sistema inteiro. |
| CA-021 | 010, 013 | Persistência/recuperação SPEC1 em fixture e sem schema paralelo. |

### Cenários A–O

Todos têm ligação a TASK, requisito/critério e evidência futura sem trabalho fora do PLAN: A → 001/009/011 (CA-004/005); B → 003/009 (CA-002/010); C → 007/009 (CA-004/008/019); D → 004/009 (CA-012/018); E → 002/006 (RF-013/CA-013); F → 006/009 (RF-014/CA-014); G → 003/009 (RF-009/CA-009); H → 001/007 (RF-001/CA-001); I → 008/011 (RF-006/015, N/A); J → 010 (RF-021/CA-021); K → 001/011 (RF-016/CA-016); L → 004/005/013 (RF-015/018); M → 007 (RF-019/CA-019); N → 001/005 (RF-020/CA-020); O → 003/009 (RF-009/CA-009, NOT_EXECUTED). TASK-013 exige verificação da matriz e testes, não mera declaração.

### Revisões especiais e APIs SPEC1

- **TASK-006 / authority:** a tarefa corrigida exige duas fontes normativas incompatíveis sem `AuthorizedPrecedence` → nenhum vencedor; `required_authority` segue ausente quando não fornecida; autoridade válida recebida pode ser registrada como necessidade sem resolver precedência; workspace não compete normativamente; continuidade usa `avaliar_continuidade_localizada`. A API real de `gap_handling.py` aceita `required_authority` opcional, retorna `authoritative_reference=None` e bloqueador para duas normativas, registra `required_information` quando a autoridade não foi fornecida, e tem razões para dependência não avaliada e bloqueios transitivos. A API de conflito não recebe precedência: consistente com D-04/D-08, o protocolo precisa tratar precedência autorizada antes de chamar a classificação de conflito não resolvido; nenhuma TASK pretende alterar a engine SPEC1.
- **TASK-010 / SPEC1:** foram confirmados `criar_ou_retomar_analise` e identidade ANL, `publicar_documento`, `recuperar_analise`/`recuperar_documento(s)`, `pesquisar_documentos` sob demanda, as três verificações de proveniência, catálogo fechado e serialização/validação de formato. Catálogo e formato atuais aceitam `analysis`, `evidence`, `divergence`, `blocker`, `result` e relações `complements`/`supports`/`related_to`/`corrects`/`supersedes`/`invalidates`; publisher/recovery trabalham sobre roots resolvidos e o publisher retorna identidade/hash, sem substituir destino. Resolvedor e root explícitos estão disponíveis. As chamadas fornecidas em PLAN/TASKS são compatíveis com APIs atuais; módulos SPEC1 podem permanecer read-only. Nenhuma mudança SPEC1 é necessária para a integração planejada.
- **Fronteira de arquivos:** todas as TASKS usam apenas `review_protocol.py`, `test_review_protocol.py` e `status.md`; TASK-010 trata módulos SPEC1 somente como dependências. Não há dependência identificada de runtime/teste novo ou alterado fora dessa fronteira.
- **Autoridade/especialistas:** TASK-004 modela pertinência e estado especializado sem decidir Patterns, SOLID, interface, Clean Code, Delphi ou Quality/Audit. Autoridade/contexto vem do host sem autenticação inventada pelo Core. Não se encontrou owner inferido nem precedência por data, especificidade, nome ou ordem.
- **Grants/externalidade:** REVIEW, STRUCTURAL_CHANGE, FUNCTIONAL_CHANGE e LOCAL_PERSISTENCE são separados; ausência de grant nega. EXTERNAL_ACTION permanece não suportada. TASK-011 planeja spies/guards e nenhuma rota de rede, Git remoto, subprocesso, upload, sync ou Release.
- **Idioma:** SPEC RF-017/CA-017, PLAN D-02/D-11/D-15 e TASKS-001/008/012/013 concordam: `None` usa pt-BR, idioma explícito é fornecido pelo host e preservado pelo Core, sem tradução ou segunda resposta; artefatos internos seguem pt-BR e Release permanece futuro/autorização própria.
- **Comportamento e determinismo:** D-09/TASK-007 requerem contrato, versões-base/candidata e claim/verificação observada; booleano isolado não basta. D-14/TASK-012 enumeram ordenação das coleções e desempates, dependências, idioma como input e clock que não controla ordem lógica.

### Limitações, achados e conclusão

- **Achados:** nenhum `ANL-*`; nenhuma lacuna bloqueante ou editorial material identificada.
- **Limitações:** ANALYZE avaliou consistência e suficiência futura dos planos; não executou implementação ou testes de SPEC2, não atestou comportamento futuro e não produziu estado operacional Debug. A prova de execução pertence a IMPLEMENT/CONVERGE conforme seus gates.
- **Validação humana adicional:** não requerida para este gate de consistência; a aprovação humana de TASKS já foi explicitamente registrada e esta conclusão é análise verificável dos artefatos.
- **Conclusão:** PASS. Coberturas RF-001–RF-021, CA-001–CA-021, D-01–D-15 e cenários A–O são coerentes, rastreáveis e executáveis dentro do PLAN/TASKS e da fronteira aprovada; sem contradição material, tarefa órfã, capacidade SPEC1 ausente ou apropriação de autoridade detectada.
- **Autorização resultante:** este PASS habilita solicitar/autorização posterior de IMPLEMENT somente para SPEC `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC`, PLAN `8ED06179C5251CCFC534E9E6A4549D0E81F9FFCDA367F567C935894CA9087EDB` e TASKS `4C40D81D5B013FAA9462F0FA4F68F6160F6FB6CED991582DB19B30642A97A172`. Nenhuma TASK foi iniciada nesta execução.

### CHECKPOINT RICKCRAFT — ANALYZE

- **Fase / execution ID:** ANALYZE — `ANALYZE-2026-10-11-SPEC-0000000002-01`.
- **Estado / resultado:** AGUARDANDO_APROVAÇÃO — PASS.
- **Versões:** SPEC `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC`; PLAN `8ED06179C5251CCFC534E9E6A4549D0E81F9FFCDA367F567C935894CA9087EDB`; TASKS `4C40D81D5B013FAA9462F0FA4F68F6160F6FB6CED991582DB19B30642A97A172`.
- **Cobertura:** RF-001–021 SATISFIED; CA-001–021 com estratégia PASS; D-01–15 cobertas; cenários A–O rastreados; TASK-006 e TASK-010 auditadas especialmente.
- **Achados bloqueantes:** nenhum.
- **Arquivos criados:** nenhum.
- **Arquivos alterados:** somente este `status.md`.
- **Próximo passo:** revisão externa deste ANALYZE; após isso, solicitar autorização separada antes de iniciar TASK-001/IMPLEMENT.
- **Não fazer ainda:** não iniciar IMPLEMENT, CONVERGE ou Release; não fazer push.

### HANDOFF PARA REVISÃO — ANALYZE

Resultado PASS sustentado pelas versões, matrizes e APIs listadas nesta seção. Revisar exclusivamente este registro e os artefatos aprovados referenciados. Próximo passo proposto: revisão externa do ANALYZE. Autorização necessária: autorização explícita separada antes de IMPLEMENT. IMPLEMENT permanece NOT_STARTED; CONVERGE permanece NOT_STARTED.

## Alocação

- ID `SPEC-0000000002`, grupo `000`, sequência `0000002`.
- Slug: `protocolo-revisao-tecnica`.
- Data: 2026-10-11.
- Owner conceitual: RickCraft Core Specialist, conforme grupo 000 vigente.
- Alocado em `registries/specifications.md` antes da materialização desta unidade.

## Registro desta elaboração

Em 2026-10-11, SPEC passou de IN_PROGRESS para COMPLETE após leitura das fontes internas obrigatórias e elaboração de `spec.md`. Nenhuma aprovação ou autorização de PLAN foi inferida. Não foram criados `plan.md`, `tasks.md`, código, testes ou Release.

## Correção final antes da aprovação

Uma revisão externa identificou quatro lacunas comportamentais — dimensões técnicas aplicáveis, preservação comportamental, limite de conclusões positivas e continuidade operacional — e uma imprecisão na redação de precedência normativa. SPEC foi reaberta para correção. Nenhuma arquitetura foi definida; o Registry não foi alterado; PLAN permaneceu NOT_STARTED.

A correção preservou RF-001–RF-017 e CA-001–CA-017, adicionou RF-018–RF-021 e CA-018–CA-021, esclareceu a aplicação de precedência somente quando expressamente autorizada e acrescentou cenários de revisão pertinentes. Após a correção, SPEC retornou a COMPLETE, pronta para revisão e ainda não aprovada.

## Aprovação da SPEC e início de PLAN

Em 2026-10-11, o responsável pelo projeto aprovou SPEC-0000000002, SHA-256 `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC`, referência adicional blob Git `97f1a98c4f3b25bf52c0fa71c29502a39e9ca556`. A aprovação autoriza somente PLAN; não autoriza TASKS, ANALYZE, IMPLEMENT, CONVERGE ou Release.

PLAN passou de NOT_STARTED para IN_PROGRESS nesta execução. SPEC permanece COMPLETE e aprovada. TASKS, ANALYZE, IMPLEMENT e CONVERGE permanecem NOT_STARTED; último gate válido permanece nenhum.

## PLAN — execução de 2026-10-11

O PLAN foi elaborado contra SPEC-0000000002 aprovada no SHA-256 `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC`. O documento define fronteira Core/especialistas, request e grants conservadores, autoridade explícita, evidências/claims, findings, dimensões, uso dos avaliadores de `gap_handling.py`, change proposal sem editor, preservação comportamental baseada em evidência, conclusão limitada, resposta em três seções, persistência optativa SPEC1, falhas, determinismo, riscos e matrizes RF/CA/cenários.

PLAN passou de IN_PROGRESS para COMPLETE, pronto para revisão e não aprovado. Nenhum runtime/teste foi alterado ou executado; nenhum `tasks.md`, ANALYZE, IMPLEMENT, CONVERGE ou Release foi iniciado.

## Fontes internas consultadas

- `README_PTBr.md` e `README.md`, integralmente;
- `policies/POL-0000000001-governanca-documental.md`;
- `policies/POL-0000000002-processo-sdd.md`;
- `policies/POL-0000000003-ambientes-runtime-release-workspace.md`;
- `registries/policies.md`;
- `registries/spec-groups.md`;
- `registries/specifications.md`;
- `specs/SPEC-0000000001-workspace-operacional-rastreavel/spec.md`;
- `specs/SPEC-0000000001-workspace-operacional-rastreavel/status.md`.

Nenhuma documentação externa foi necessária.

## Artefatos desta unidade

| Artefato | Estado |
|---|---|
| `spec.md` | COMPLETE e aprovada; SHA-256 `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC` |
| `plan.md` | COMPLETE e aprovado; SHA-256 `8ED06179C5251CCFC534E9E6A4549D0E81F9FFCDA367F567C935894CA9087EDB`; blob Git `0c28cf63a68e09365e1fb3ead7a02e609b60fcfa` |
| `tasks.md` | COMPLETE, pronta para revisão e não aprovada; SHA-256 `4C40D81D5B013FAA9462F0FA4F68F6160F6FB6CED991582DB19B30642A97A172` |
| `status.md` | Estado corrente desta unidade; UTF-8 |

O registro autoritativo da alocação permanece em `registries/specifications.md`.

## Decisões pendentes

- Revisão/aprovação explícita de `tasks.md`.
- Autorização separada antes de iniciar ANALYZE.

## CHECKPOINT RICKCRAFT

### Fase

Elaboração de SPEC-0000000002 — Protocolo de Revisão Técnica, Escopo e Resposta do RickCraft.

### Objetivo

Definir comportamentos verificáveis para revisão técnica, limites de autorização e autoridade, rastreabilidade de evidência e forma de resposta.

### Estado

AGUARDANDO_APROVAÇÃO.

### O que foi realizado

- Confirmados grupo 000 vigente, owner conceitual e próxima sequência disponível.
- Alocado SPEC-0000000002 no Registry antes da materialização.
- Corrigidos somente `spec.md` e este `status.md`; nenhum mecanismo de PLAN foi escolhido.
- Registrado o SHA-256 completo da versão final de `spec.md` e validado após releitura UTF-8 estrita.

### Arquivos criados

Nenhum nesta correção; os dois arquivos já existiam.

### Arquivos alterados

- `specs/SPEC-0000000002-protocolo-revisao-tecnica/spec.md`
- `specs/SPEC-0000000002-protocolo-revisao-tecnica/status.md`

### Decisões formalizadas

Somente requisitos comportamentais da SPEC. Nenhuma decisão arquitetural.

### Bloqueios

Nenhum para elaboração da SPEC.

### Próximo passo recomendado

Revisar exclusivamente a SPEC-0000000002 corrigida antes de aprová-la e autorizar PLAN.

### O que não deve ser feito ainda

Não iniciar PLAN/TASKS/ANALYZE/IMPLEMENT/CONVERGE, não implementar runtime/testes e não produzir Release.

## HANDOFF PARA REVISÃO — RICKCRAFT

- **Fase:** correção final da SPEC-0000000002 antes da aprovação.
- **Estado:** AGUARDANDO_APROVAÇÃO.
- **Fontes internas:** fontes listadas acima.
- **Artefatos alterados:** `spec.md` e `status.md`; Registry preservado.
- **SHA-256 final de spec.md:** `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC`.
- **Pendência:** revisão e aprovação explícita da versão COMPLETE corrigida.
- **Próximo passo proposto:** revisar exclusivamente SPEC-0000000002 corrigida.
- **Autorização necessária:** aprovação explícita antes de PLAN.
- **Não executar:** PLAN ou qualquer gate/tarefa posterior antes dessa autorização.

## CHECKPOINT RICKCRAFT — PLAN

### Fase executada

PLAN — SPEC-0000000002.

### Objetivo

Definir arquitetura, contratos, fluxo, persistência opcional e estratégia de validação para o Protocolo de Revisão Técnica, Escopo e Resposta.

### Estado

AGUARDANDO_APROVAÇÃO. PLAN COMPLETE, pronta para revisão e não aprovada.

### Versão da SPEC usada

`F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC`.

### Arquivos criados

- `specs/SPEC-0000000002-protocolo-revisao-tecnica/plan.md`

### Arquivos alterados

- `specs/SPEC-0000000002-protocolo-revisao-tecnica/status.md`

### Decisões arquiteturais

D-01–D-15, registradas em `plan.md`.

### Componentes planejados

Um módulo runtime `review_protocol.py` e um teste `test_review_protocol.py`; reuso das APIs existentes SPEC1 e dos avaliadores puros SPEC1 de conflito/continuidade. Sem especialistas, Agents, Orchestrator, editor universal ou dependências externas.

### Estratégia de validação

Grupos A–P, matrizes CA-001–CA-021 e cenários A–O estão mapeados em `plan.md`. Nenhum teste foi criado ou executado nesta fase.

### Decisões pendentes

Aprovação explícita do PLAN; TASKS permanece dependente dessa aprovação.

### Bloqueios

Nenhum bloqueio arquitetural identificado para revisão do PLAN.

### Próximo passo recomendado

Revisar exclusivamente o PLAN da SPEC-0000000002 antes de autorizar TASKS.

### O que não deve ser feito ainda

Não criar TASKS, não executar ANALYZE/IMPLEMENT/CONVERGE e não gerar Release.

## HANDOFF PARA REVISÃO — PLAN

- **Fase:** PLAN — SPEC-0000000002.
- **Estado:** AGUARDANDO_APROVAÇÃO.
- **SPEC aprovada usada:** SHA-256 `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC`.
- **PLAN:** `D0F50D366524246AFDAD9D0DF68490C6BAB882022A1444100BBBA392A07D5C93`.
- **Fontes internas:** READMEs, Policies, Registries, SPEC-0000000002 e dependência SPEC-0000000001 listados no início do status; runtime e testes relevantes inspecionados nesta execução.
- **Artefatos:** `plan.md` e `status.md` atualizado.
- **Cobertura:** RF-001–RF-021, CA-001–CA-021 e cenários A–O mapeados no PLAN.
- **Pendência:** aprovação explícita do PLAN.
- **Próximo passo:** revisar exclusivamente PLAN.
- **Autorização necessária:** aprovação antes de criar `tasks.md`.
- **Não executar:** TASKS, ANALYZE, IMPLEMENT, CONVERGE ou Release antes da autorização.


## Correção final do PLAN — idioma da resposta e estado SDD

A revisão externa identificou incompatibilidade entre RF-017/CA-017 da SPEC aprovada e D-11/D-15, matriz RF-017, CA-017 e contrato de renderização do PLAN. O PLAN foi reaberto e passou temporariamente a IN_PROGRESS. Nenhuma SPEC mudou; nenhum TASKS foi iniciado e nenhuma implementação ocorreu.

A correção define `ReviewRequest.language` como identificador solicitado não vazio ou `None` (default pt-BR), sem locale global. O host fornece os textos e títulos semanticamente correspondentes no idioma pedido; o renderer preserva esses valores, sem tradução ou resposta duplicada. CA-017 agora cobre idioma solicitado e default, resposta única, UTF-8/acentos e idioma pt-BR dos artefatos internos. D-11/D-15 e a matriz RF-017 distinguem artefatos internos, resposta operacional e Release futuro condicionado à Policy 3 e autorização explícita. O determinismo inclui o idioma como entrada e não consulta locale global.

Após a correção, PLAN retornou a COMPLETE, pronto para revisão e não aprovado. SHA-256 anterior preservado como histórico: `D0F50D366524246AFDAD9D0DF68490C6BAB882022A1444100BBBA392A07D5C93`. SHA-256 corrente de `plan.md`, relido e confirmado em UTF-8: `8ED06179C5251CCFC534E9E6A4549D0E81F9FFCDA367F567C935894CA9087EDB`. SPEC continua COMPLETE e aprovada; TASKS, ANALYZE, IMPLEMENT e CONVERGE continuam NOT_STARTED. Runtime/testes não foram alterados ou executados; nenhum Release foi produzido.

### CHECKPOINT RICKCRAFT — correção PLAN

- **Fase:** correção final do PLAN ? SPEC-0000000002.
- **Estado:** AGUARDANDO_APROVAÇÃO.
- **Arquivos alterados:** `plan.md` e `status.md`.
- **Correções:** idioma solicitado/default, renderer, RF-017, CA-017, D-11, D-15, determinismo e etapa corrente PLAN.
- **Próximo passo:** revisar exclusivamente o PLAN corrigido antes de autorizar TASKS.
- **Não executar:** criar `tasks.md`, ANALYZE, IMPLEMENT, CONVERGE, Release ou push.

### HANDOFF PARA REVISÃO — correção PLAN

PLAN está COMPLETE e aguarda aprovação explícita. Arquivos a revisar: `plan.md` e esta seção de `status.md`. Próxima etapa proposta: aprovar/revisar o PLAN antes de criar TASKS. Nenhuma autorização posterior está implícita.

## Aprovação do PLAN e execução de TASKS — 2026-10-11

O responsável pelo projeto aprovou o PLAN exato: SHA-256 `8ED06179C5251CCFC534E9E6A4549D0E81F9FFCDA367F567C935894CA9087EDB`, blob Git `0c28cf63a68e09365e1fb3ead7a02e609b60fcfa`. A autorização recebida limita-se a TASKS; não autoriza ANALYZE, IMPLEMENT, CONVERGE ou Release. A SPEC aprovada permanece no SHA-256 `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC`.

TASKS passou de NOT_STARTED para IN_PROGRESS durante esta execução. Foram definidas TASK-001–TASK-013 com objetivos individuais, origem SPEC/PLAN, dependências, arquivos autorizados, testes/regressões, evidência mínima e exclusões. As matrizes direta/inversa cobrem D-01–D-15, RF-001–RF-021, CA-001–CA-021 e cenários A–O. A inspeção das APIs/runtime e testes existentes serviu para não planejar alterações a módulos SPEC1 já disponíveis.

TASKS retornou a COMPLETE, pronta para revisão e não aprovada. SHA-256 completo de `tasks.md`, relido e confirmado em UTF-8 estrito: `23CB09014D3DCD14D3330B4C8542BB83EFFB9170A77F2F400913349C426425CE`. Nenhum runtime/teste foi alterado ou executado. ANALYZE, IMPLEMENT e CONVERGE permanecem NOT_STARTED; último gate válido permanece nenhum. Nenhum Release foi produzido.

### CHECKPOINT RICKCRAFT — TASKS

- **Fase:** TASKS — SPEC-0000000002.
- **Estado:** AGUARDANDO_APROVAÇÃO; TASKS COMPLETE e pronta para revisão.
- **Arquivos criados:** `tasks.md`.
- **Arquivos alterados:** `status.md`.
- **Tarefas definidas:** TASK-001–TASK-013.
- **Cobertura:** D-01–D-15, RF-001–RF-021, CA-001–CA-021 e cenários A–O, com matrizes direta/inversa.
- **Próximo passo:** revisar exclusivamente `tasks.md` antes de autorizar ANALYZE.
- **Não executar:** ANALYZE, IMPLEMENT, CONVERGE, Release ou push.

### HANDOFF PARA REVISÃO — TASKS

TASKS está COMPLETE e aguarda aprovação explícita. Revisar `tasks.md` e esta evidência em `status.md`. A aprovação não inicia ANALYZE automaticamente; exige autorização separada. Nenhuma implementação ou teste foi executado.

## Correção pontual de TASKS — TASK-006

Uma revisão externa encontrou contradição material na descrição de TASK-006: o texto dizia que conflito normativo sem precedência mantinha uma fonte vencedora, embora a SPEC/PLAN exijam conflito não resolvido sem precedência autorizada. TASKS foi reaberta e passou temporariamente a IN_PROGRESS para esta correção. Nenhuma SPEC ou PLAN mudou; ANALYZE permaneceu NOT_STARTED; nenhuma implementação ocorreu.

A TASK-006 agora declara que nenhuma fonte vencedora é escolhida sem `AuthorizedPrecedence`. `required_authority` continua ausente/`None` quando não foi validamente fornecida; uma autoridade competente já conhecida pode constar como requisito de resolução sem decidir qual fonte vence. Os testes planejados exigem explicitamente: (A) conflito incompatível sem vencedor; (B) ausência de autoridade não preenchida; (C) autoridade válida registrada sem precedência implícita; (D) referência normativa aplicável versus workspace operacional sem autoridade concorrente; e (E) bloqueio localizado/transitivo e continuidade de escopo independente via `avaliar_continuidade_localizada`.

As matrizes RF-013, CA-013, D-04/D-08 e o cenário E já expressavam corretamente ausência de vencedor/precedência autorizada; foram preservadas sem alteração. TASKS retornou a COMPLETE, pronta para revisão e não aprovada. Hash anterior preservado como histórico: `23CB09014D3DCD14D3330B4C8542BB83EFFB9170A77F2F400913349C426425CE`. Novo SHA-256 completo de `tasks.md`, relido em UTF-8 estrito e confirmado: `4C40D81D5B013FAA9462F0FA4F68F6160F6FB6CED991582DB19B30642A97A172`.

SPEC e PLAN permanecem COMPLETE e aprovados. Etapa atual = TASKS; ANALYZE = NOT_STARTED; IMPLEMENT = NOT_STARTED; CONVERGE = NOT_STARTED; último gate válido = nenhum. Runtime/testes, SPEC e PLAN não foram alterados. Nenhum teste foi criado/executado, nenhum Release foi produzido e nenhum push foi feito.

### CHECKPOINT RICKCRAFT — correção pontual TASK-006

- **Estado:** AGUARDANDO_APROVAÇÃO.
- **Arquivos alterados:** `tasks.md` e `status.md`.
- **TASKS anterior:** `23CB09014D3DCD14D3330B4C8542BB83EFFB9170A77F2F400913349C426425CE`.
- **TASKS corrigida:** `4C40D81D5B013FAA9462F0FA4F68F6160F6FB6CED991582DB19B30642A97A172`.
- **Próximo passo:** revisar exclusivamente TASKS corrigida antes de autorizar ANALYZE.
- **Não executar ainda:** ANALYZE, IMPLEMENT, CONVERGE ou Release.

### HANDOFF PARA REVISÃO — correção pontual TASK-006

Revisar exclusivamente a semântica de conflito da TASK-006 e o registro desta correção. TASKS está COMPLETE, pronta para revisão e não aprovada. É necessária autorização explícita separada antes de ANALYZE.

## IMPLEMENT — TASK-004 — Dimensões técnicas e avaliações especializadas — 2026-10-11

A aprovação externa de TASK-003 foi confirmada pelo responsável. Baseline aceita: `review_protocol.py` SHA-256 `2F9F2AE2512E78572A7561666122967CAF11DBF4253B3846F15B1D1731852C96` (blob Git `1705d2d8acac7bb4272db20c65d0afddc4a65034`) e `test_review_protocol.py` SHA-256 `93981E2A1E04068597900723B188685B8A59FF87925DF0D79616B05DEDC30FC9` (blob Git `345972ed0317968b546df6640b6f8c7ae2ebb671`). SPEC, PLAN e TASKS foram recalculadas antes da alteração e conferem, respectivamente, com `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC`, `8ED06179C5251CCFC534E9E6A4549D0E81F9FFCDA367F567C935894CA9087EDB` e `4C40D81D5B013FAA9462F0FA4F68F6160F6FB6CED991582DB19B30642A97A172`. O gate `ANALYZE-2026-10-11-SPEC-0000000002-01` permanece PASS; nenhuma entrada normativa mudou.

TASK-004 passou a IN_PROGRESS e foi concluída nesta execução. Foram adicionados `TechnicalDimension` com exatamente as sete dimensões e sua ordem canônica, `DimensionAssessmentState` com os cinco estados do PLAN, `AssessmentCharacter` e os value objects imutáveis `DimensionAssessment` e `SpecialistAssessment`. As validações exigem tipo e escopo explícitos, evidências tipadas sem duplicatas e coerência entre dimensão/escopo/assessment. `AUTHORITATIVE` exige owner, referência de competência, `AuthorityReference` compatível com o escopo e ao menos uma evidência; `validate_authority` exige que essa mesma referência esteja no `AuthorityContext` explícito. Avaliações consultivas não são promovidas. Nenhum owner é inferido e nenhuma lógica substantiva dos domínios especializados foi implementada.

Verificação executada: `python -B -m unittest -v impl.tests.test_review_protocol` — 82 testes executados, 82 PASS, 0 FAIL, 0 SKIP; inclui regressão das TASK-001, TASK-002 e TASK-003. Nenhuma suíte adicional foi executada. Os value objects não acessam fontes nem executam IO; não chamam Agents, `provenance.py` ou `gap_handling.py`, e não introduzem rede, Git, subprocesso, persistência ou Release. Nenhum módulo ou teste da SPEC1 foi alterado.

Hashes SHA-256 finais, calculados após releitura estrita UTF-8 e confirmados por cálculo repetido:

- `impl/src/RickCraft/review_protocol.py`: `9EF7B449ACA7F65E586196E95AF49784C386BDA9C3577B34EB0A4A4B90EBC3B6`
- `impl/tests/test_review_protocol.py`: `8B2F026B22A91E614C616181BDC56B79702A300F7ABA3D4FC3D22AFD7D19396E`

`git diff --check` passou sem erros. `git status --short` listou somente os três arquivos autorizados. Git emitiu avisos de conversão LF→CRLF para os dois arquivos de código e este status no Windows; não houve erro de whitespace.

Estado corrente: Etapa = IMPLEMENT; SPEC/PLAN/TASKS = COMPLETE e aprovadas; ANALYZE = PASS; IMPLEMENT = IN_PROGRESS; CONVERGE = NOT_STARTED. TASK-001–TASK-003 permanecem COMPLETE e aprovadas; TASK-004 = COMPLETE, aguardando revisão; TASK-005–TASK-013 não executadas. Último gate válido: `ANALYZE-2026-10-11-SPEC-0000000002-01`. Nenhum bloqueio ou limitação adicional identificado.

### CHECKPOINT RICKCRAFT — TASK-004

- **Fase:** IMPLEMENT — TASK-004 — SPEC-0000000002.
- **Objetivo:** modelar dimensões técnicas e avaliações especializadas recebidas sem assumir autoridade substantiva.
- **Estado:** AGUARDANDO_APROVAÇÃO; TASK-004 COMPLETE, aguardando revisão.
- **Arquivos criados:** nenhum.
- **Arquivos alterados:** `review_protocol.py`, `test_review_protocol.py` e este `status.md`.
- **Testes:** comando focal acima; 82/82 PASS, 0 FAIL, 0 SKIP.
- **Próximo passo:** revisar exclusivamente TASK-004 antes de qualquer autorização da TASK-005.
- **Não fazer ainda:** não iniciar TASK-005, CONVERGE ou Release; não fazer push.

### HANDOFF PARA REVISÃO — TASK-004

Revisar `impl/src/RickCraft/review_protocol.py`, `impl/tests/test_review_protocol.py` e este registro. TASK-004 está COMPLETE, aguardando revisão; TASK-005 permanece não executada. É necessária autorização explícita separada antes de TASK-005.

## IMPLEMENT — TASK-005 — Findings rastreáveis e conclusão limitada — 2026-10-11

O responsável confirmou a aprovação externa de TASK-004. Baseline aceita: `review_protocol.py` SHA-256 `9EF7B449ACA7F65E586196E95AF49784C386BDA9C3577B34EB0A4A4B90EBC3B6` (blob Git `018aa1cc3e5d2777b001157b44a3751bad287c98`) e `test_review_protocol.py` SHA-256 `8B2F026B22A91E614C616181BDC56B79702A300F7ABA3D4FC3D22AFD7D19396E` (blob Git `76ff9362d606dbbd7f899598b8254f426f0ec0b0`). SPEC/PLAN/TASKS recalculadas antes da implementação conferem com `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC`, `8ED06179C5251CCFC534E9E6A4549D0E81F9FFCDA367F567C935894CA9087EDB` e `4C40D81D5B013FAA9462F0FA4F68F6160F6FB6CED991582DB19B30642A97A172`. O gate `ANALYZE-2026-10-11-SPEC-0000000002-01` permanece PASS. A autorização abrangeu somente TASK-005.

Etapa atual = IMPLEMENT; IMPLEMENT permanece IN_PROGRESS. TASK-005 passou a IN_PROGRESS durante esta execução e retornou a COMPLETE após implementação e testes. Não houve alteração das entradas normativas nem invalidação do ANALYZE.

Foram adicionados `ReviewFinding`, `ConclusionState`, `ReviewConclusion` e `sort_review_findings`. Finding mantém separados escopo, dimensão, condição, referências de evidência, referência normativa/contratual, conclusão técnica, impacto, recomendação opcional e assessment especializado recebido. EvidenceReference é obrigatória, tipada, sem duplicatas e ordenada deterministicamente. Assessment associado deve coincidir em dimensão e escopo e sua conclusão é preservada; seu caráter CONSULTATIVE/AUTHORITATIVE não é alterado. Não se infere owner.

`ReviewConclusion` permite exatamente LIMITED, BLOCKED e NO_FINDING_IN_SCOPE. Todas as conclusões exigem scopes explícitos, sem wildcard. Bases, versões, evidências e claims são tipados/validados, sem inferir artefato, fonte ou versão. Conclusões não bloqueadas exigem artifact/source e evidência/claim; NO_FINDING_IN_SCOPE requer EvidenceReference observada ou persistida diretamente relacionada às bases. BLOCKED permite ausência de evidência, mas exige scope, artifact/source explícito e limitation. Claims fora das bases e versões contraditórias são rejeitados quando a incompatibilidade é diretamente verificável. A estrutura não possui estado universal de aprovação ou conformidade.

A ordenação de findings segue `(scope, rank canônico de TechnicalDimension, normative_reference, condition.casefold(), condition)`. A recomendação fica associada no mesmo objeto ao finding, à condição, ao contrato, à conclusão e ao impacto. Nenhum ChangeProposal/BehaviorAssessment, renderer, engine de blocker/continuidade, pipeline, persistência, gap_handling, provenance, workspace ou integração externa foi introduzido.

Teste focal executado: `python -B -m unittest -v impl.tests.test_review_protocol`. A primeira execução registrou 99 testes, 2 FAIL e 1 ERROR; os casos apontaram somente ajuste na aceitação do iterável do teste e na ordem de validação das mensagens. Esses pontos foram ajustados dentro de TASK-005. A repetição final executou 99 testes: 99 PASS, 0 FAIL, 0 SKIP. A execução inclui regressão integral dos testes existentes das TASK-001–004. Nenhuma full suite foi executada.

Hashes SHA-256 finais, após releitura UTF-8 estrita e cálculo repetido:

- `impl/src/RickCraft/review_protocol.py`: `3F882DA171C425891A8DA55FAFC95F2F168C8F7255A72B5EBE6430CC0185DB9D`
- `impl/tests/test_review_protocol.py`: `A31F69B04A6D3BD9FF2943FDACB7AAF181EA09F82478111DC5F246DF4D7DEE8C`

Nenhum arquivo SPEC1 foi alterado. Nenhuma rede, Git como efeito de produto, subprocesso, workspace, persistência, Release ou outra externalidade foi usada.

Estado corrente: Etapa = IMPLEMENT; SPEC/PLAN/TASKS = COMPLETE e aprovadas; ANALYZE = PASS; IMPLEMENT = IN_PROGRESS; CONVERGE = NOT_STARTED. TASK-001–TASK-004 = COMPLETE e aprovadas após revisão externa; TASK-005 = COMPLETE, aguardando revisão; TASK-006–TASK-013 não executadas. Último gate válido: `ANALYZE-2026-10-11-SPEC-0000000002-01`. Nenhum bloqueio identificado.

### CHECKPOINT RICKCRAFT — TASK-005

- **Fase:** IMPLEMENT — TASK-005 — SPEC-0000000002.
- **Objetivo:** implementar findings rastreáveis, ordenação determinística e conclusão limitada.
- **Estado:** AGUARDANDO_APROVAÇÃO; TASK-005 COMPLETE, aguardando revisão.
- **Arquivos criados:** nenhum.
- **Arquivos alterados:** `review_protocol.py`, `test_review_protocol.py` e este `status.md`.
- **Testes:** execução final do comando focal; 99 executados, 99 PASS, 0 FAIL, 0 SKIP. Primeira tentativa e correções estão registradas acima.
- **Próximo passo:** revisar exclusivamente TASK-005 antes de qualquer autorização de TASK-006.
- **Não fazer ainda:** não executar TASK-006, CONVERGE ou Release; não fazer push.

### HANDOFF PARA REVISÃO — TASK-005

Revisar `impl/src/RickCraft/review_protocol.py`, `impl/tests/test_review_protocol.py` e este registro. TASK-005 está COMPLETE e aguarda revisão; TASK-006–TASK-013 não foram iniciadas. É necessária autorização explícita separada antes da TASK-006.

## Correção pontual de cobertura — TASK-005 — scope incompatível — 2026-10-11

Uma revisão externa identificou lacuna de cobertura, não defeito funcional demonstrado: os testes de TASK-005 cobriam dimensão incompatível, mas não isolavam o caso de dimensão igual com scope diferente. TASK-005 foi mantida como a tarefa em correção; TASK-006 não foi iniciada.

Foi acrescentado `test_scope_incompativel_no_specialist_assessment_e_rejeitado`. O caso fixa `ReviewFinding.scope = "ClasseCliente"` e `SpecialistAssessment.scope = "OutroEscopo"`, usando `TechnicalDimension.DELPHI_OBJECT_PASCAL` em ambos. O teste confirma as dimensões iguais, os scopes diferentes e espera `ReviewInputError` pela incompatibilidade de dimensão/escopo no finding.

Comando executado: `python -B -m unittest -v impl.tests.test_review_protocol` — 100 testes executados, 100 PASS, 0 FAIL, 0 SKIP. A implementação/runtime permaneceu inalterada e seu SHA-256 foi confirmado como `3F882DA171C425891A8DA55FAFC95F2F168C8F7255A72B5EBE6430CC0185DB9D`. Novo SHA-256 de `test_review_protocol.py`, recalculado duas vezes após releitura UTF-8 estrita: `A52D03DE2DF9A84A34DF91D34D51BE567A947F73EA6B91459F16F8B7E9B1E0D7`.

SPEC/PLAN/TASKS permanecem nos hashes aprovados `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC`, `8ED06179C5251CCFC534E9E6A4549D0E81F9FFCDA367F567C935894CA9087EDB` e `4C40D81D5B013FAA9462F0FA4F68F6160F6FB6CED991582DB19B30642A97A172`; ANALYZE permanece PASS. IMPLEMENT = IN_PROGRESS; TASK-005 = COMPLETE, aguardando revisão; TASK-006–TASK-013 não executadas; CONVERGE = NOT_STARTED. Nenhum módulo SPEC1, runtime ou outro arquivo foi alterado nesta correção. Não houve Release ou push.

### CHECKPOINT RICKCRAFT — correção pontual TASK-005

- **Objetivo:** demonstrar a rejeição de SpecialistAssessment com scope incompatível e dimensão igual.
- **Estado:** AGUARDANDO_APROVAÇÃO; TASK-005 COMPLETE, aguardando revisão.
- **Arquivos alterados nesta correção:** `test_review_protocol.py` e `status.md`.
- **Runtime:** inalterado; SHA-256 confirmado acima.
- **Teste:** comando focal; 100/100 PASS, 0 FAIL, 0 SKIP.
- **Próximo passo:** revisar exclusivamente a correção de cobertura de TASK-005.
- **Não fazer ainda:** não iniciar TASK-006, CONVERGE ou Release; não fazer push.

### HANDOFF PARA REVISÃO — correção pontual TASK-005

Revisar o teste explícito de scope incompatível em `impl/tests/test_review_protocol.py` e este registro. A revisão não autoriza TASK-006; autorização explícita separada continua necessária.

## IMPLEMENT — TASK-006 — Conflitos, lacunas e continuidade localizada — 2026-10-11

O responsável confirmou a aprovação externa de TASK-005. Baseline aceita: `review_protocol.py` SHA-256 `3F882DA171C425891A8DA55FAFC95F2F168C8F7255A72B5EBE6430CC0185DB9D` (blob Git `ac8656a0fc0be9f676f2757cd350cf772d689484`) e `test_review_protocol.py` SHA-256 `A52D03DE2DF9A84A34DF91D34D51BE567A947F73EA6B91459F16F8B7E9B1E0D7` (blob Git `6071c8f1933d45cffecc2d1d36e8f88f51c1d9cf`; commit da correção aprovada `6507383c1f8b24de1a202dc0017b7a298445f81c`). SPEC/PLAN/TASKS foram recalculadas e conferem com `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC`, `8ED06179C5251CCFC534E9E6A4549D0E81F9FFCDA367F567C935894CA9087EDB` e `4C40D81D5B013FAA9462F0FA4F68F6160F6FB6CED991582DB19B30642A97A172`. ANALYZE `ANALYZE-2026-10-11-SPEC-0000000002-01` permanece PASS; as entradas normativas não mudaram.

Etapa atual = IMPLEMENT; TASK-006 passou a IN_PROGRESS e foi concluída nesta execução. Foram adicionados `evaluate_source_conflict` e `evaluate_scope_continuity`. A integração consome read-only `gap_handling.SourceReference`, `ScopeRequest`, `ConflictAssessment`, `ContinuityAssessment`, `avaliar_conflito_fontes` e `avaliar_continuidade_localizada`. O conflito consulta primeiro `AuthorityContext.precedence_for` para o par e scope exatos; precedência válida retorna a relação explícita sem classificar conflito não resolvido. Sem precedência, o resultado SPEC1 é preservado, inclusive ausência de vencedor, `authoritative_reference=None`, blocker requerido e `required_information` quando nenhuma autoridade é informada. `required_authority` é opcional e só é mapeada de uma `AuthorityReference` explicitamente pertencente ao contexto e competente no scope; o campo textual SPEC1 recebe seu `source_reference`, preservando a identidade declarada sem sintetizar owner ou escolher fonte vencedora. Normativa × workspace e incompatibilidade falsa mantêm os resultados do evaluator.

Para continuidade, `ReviewScope.scope_id` e `depends_on` são copiados sem descoberta. `readiness_by_scope` precisa cobrir exatamente os scopes e fornecer, em tupla, os cinco booleanos explícitos na ordem autorização/informação/evidência/autoridade/conflito. Os requests são passados ao evaluator SPEC1 na ordem recebida; resultados e razões não são reordenados. A propagação transitiva e dependências desconhecidas permanecem exclusivamente em `avaliar_continuidade_localizada`. Spies confirmam ausência de chamadas a registradores ou publicador.

Regressão SPEC1: `python -B -m unittest -v impl.tests.test_gap_handling`. A tentativa inicial dentro do sandbox falhou antes das asserções: 89 testes, 178 erros de setup/cleanup por `WinError 5` ao criar/remover fixtures em `%TEMP%`. O mesmo comando foi repetido pelo mecanismo elevado autorizado: 89 testes, 89 PASS, 0 FAIL, 0 SKIP. A falha sandboxada não foi tratada como resultado do produto. Regressão SPEC2: `python -B -m unittest -v impl.tests.test_review_protocol`; a primeira execução teve 117 testes e 2 FAIL porque os asserts esperavam uma versão abreviada da razão de autorização. Os asserts foram ajustados para preservar o texto real de SPEC1 e foi adicionado teste explícito de ramo sem autorização. Repetição final: 118 testes, 118 PASS, 0 FAIL, 0 SKIP.

Não foram chamados `registrar_divergencia`, `registrar_blocker`, `registrar_decisao_existente`, `registrar_resultado` ou `publicar_documento`; não houve persistência, acesso a workspace/Debug, rede, subprocesso, Git como efeito de produto ou Release. Nenhuma regra SPEC1 foi reimplementada. Nenhum módulo/teste SPEC1 foi alterado. Hashes de `gap_handling.py` e `test_gap_handling.py` foram verificados ao final contra os arquivos locais e estão registrados abaixo.

Hashes SHA-256 finais, após releitura UTF-8 estrita e confirmação repetida:

- `impl/src/RickCraft/review_protocol.py`: `409A369F3FB999AC1458644E11A0FE877096FC691B221E07642DE45F08C2550B`
- `impl/tests/test_review_protocol.py`: `6DD95B3C510F25BB0268537879F11670C367496E37D951A654468F93559BB06C`
- `impl/src/RickCraft/gap_handling.py` (read-only): `EC86AD2290C98C7AA76EEAABE5745A06B3B31D779180C173ADD59A6DB308366A`
- `impl/tests/test_gap_handling.py` (read-only): `6D213D565EE2A0F66BFC6857A01822B40184A10AF1641654A45E4575552D8858`

Estado final: TASK-001–TASK-005 = COMPLETE e aprovadas; TASK-006 = COMPLETE, aguardando revisão; TASK-007–TASK-013 não executadas. IMPLEMENT = IN_PROGRESS; ANALYZE = PASS; CONVERGE = NOT_STARTED. Nenhum bloqueio material identificado.

Validação final: `git diff --check` passou. `git status --short` mostra somente `review_protocol.py`, `test_review_protocol.py` e este `status.md`; `gap_handling.py` e `test_gap_handling.py` não aparecem como modificados. Git emitiu somente avisos de conversão LF→CRLF para os três arquivos alterados no Windows.

### CHECKPOINT RICKCRAFT — TASK-006

- **Fase:** IMPLEMENT — TASK-006 — SPEC-0000000002.
- **Objetivo:** integrar conflito e continuidade aos avaliadores puros SPEC1, sem persistência.
- **Estado:** AGUARDANDO_APROVAÇÃO; TASK-006 COMPLETE, aguardando revisão.
- **Arquivos alterados:** `review_protocol.py`, `test_review_protocol.py` e este `status.md`.
- **APIs SPEC1 consumidas:** `SourceReference`, `ScopeRequest`, `ConflictAssessment`, `ContinuityAssessment`, `avaliar_conflito_fontes`, `avaliar_continuidade_localizada`.
- **Testes:** `test_gap_handling` 89/89 PASS em repetição elevada após WinError 5 sandboxado; `test_review_protocol` 118/118 PASS na repetição final.
- **Próximo passo:** revisar exclusivamente TASK-006 antes de qualquer autorização da TASK-007.
- **Não fazer ainda:** não iniciar TASK-007, CONVERGE ou Release; não fazer push.

### HANDOFF PARA REVISÃO — TASK-006

Revisar `impl/src/RickCraft/review_protocol.py`, `impl/tests/test_review_protocol.py` e este registro, além das APIs SPEC1 referenciadas em modo read-only. TASK-006 está COMPLETE e aguarda revisão. É necessária autorização explícita separada antes de TASK-007.

## Início de IMPLEMENT — TASK-007 — 2026-10-11

O responsável autorizou exclusivamente TASK-007 após aprovação externa de TASK-006. Baseline local validada antes de editar: HEAD `616bb8e51eb088b1e023f1cdae01e753d6a21812`, árvore limpa; hashes SHA-256 e blobs de SPEC, PLAN, TASKS, runtime/teste TASK-006 e módulos/testes SPEC1 coincidem com a autorização. TASK-007 = IN_PROGRESS; TASK-008–TASK-013 não iniciadas. Etapa atual = IMPLEMENT; IMPLEMENT = IN_PROGRESS; ANALYZE = PASS; CONVERGE = NOT_STARTED. Nenhum artefato de implementação foi alterado ainda nesta execução.

## IMPLEMENT — TASK-007 — ChangeProposal e preservação comportamental — 2026-10-11

- **Autorização e estado anterior:** TASK-006 foi aprovada pela revisão externa conforme confirmação do responsável nesta execução. A única tarefa autorizada foi TASK-007. SPEC/PLAN/TASKS aprovadas; ANALYZE `ANALYZE-2026-10-11-SPEC-0000000002-01` permanece PASS. TASK-001–TASK-006 estão COMPLETE e aprovadas; TASK-007 está COMPLETE, aguardando revisão; TASK-008–TASK-013 não iniciadas. IMPLEMENT permanece IN_PROGRESS; CONVERGE permanece NOT_STARTED; Release não autorizado.
- **Baseline validada antes de editar:** HEAD `616bb8e51eb088b1e023f1cdae01e753d6a21812`, `git status --short` limpo. SPEC SHA-256 `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC`, blob `97f1a98c4f3b25bf52c0fa71c29502a39e9ca556`; PLAN `8ED06179C5251CCFC534E9E6A4549D0E81F9FFCDA367F567C935894CA9087EDB`, blob `0c28cf63a68e09365e1fb3ead7a02e609b60fcfa`; TASKS `4C40D81D5B013FAA9462F0FA4F68F6160F6FB6CED991582DB19B30642A97A172`, blob `065c76d6b6c3b0d5236acdd4def6890a1cce0a5a`.
- **Baseline TASK-006 e SPEC1 read-only:** `review_protocol.py` `409A369F3FB999AC1458644E11A0FE877096FC691B221E07642DE45F08C2550B`, blob `c376af84cf934af5181e66c7fb6de291027d6ca9`; `test_review_protocol.py` `6DD95B3C510F25BB0268537879F11670C367496E37D951A654468F93559BB06C`, blob `d28bcdc773325a9200307cbb63226fc0daf80bca`; `gap_handling.py` `EC86AD2290C98C7AA76EEAABE5745A06B3B31D779180C173ADD59A6DB308366A`, blob `b0783a88bf7760e97338da9699ed682c2ff49f23`; `test_gap_handling.py` `6D213D565EE2A0F66BFC6857A01822B40184A10AF1641654A45E4575552D8858`, blob `c1e2ed7ee8485476c3e8f3feb1d03d37ba0ca9a7`. Published baseline `status.md` blob `d066694bdb6a0e4d71c48039a4155d12b9fa8bf2`.
- **Contratos implementados:** `ChangeKind`, `BehaviorIntent`, `BehaviorAssessmentState`, `ChangeProposal`, `BehaviorAssessment` e `assess_change_proposal`. A proposta é frozen e declarativa: exige referência, motivo técnico, consequências, scope, targets e intenção; referencia exatamente um `ReviewFinding` existente ou o objetivo, cuja identidade é comparada ao `ReviewRequest.objective`. Versões por target são entradas explícitas e opacas. Não existe campo booleano de preservação. Coleções são copiadas, validadas e canonicalizadas.
- **Autorização e escopo:** REVIEW permanece obrigatório. Proposta STRUCTURAL exige STRUCTURAL_CHANGE; falta desse grant rejeita a avaliação. FUNCTIONAL exige STRUCTURAL_CHANGE e FUNCTIONAL_CHANGE; sem grant funcional retorna `FUNCTIONAL_CHANGE_UNAUTHORIZED`, e com grants retorna `FUNCTIONAL_CHANGE_AUTHORIZED`. Proposta funcional nunca recebe estado de preservação. Todos os targets devem constar literalmente tanto da allowlist quanto dos artefatos do scope; exclusões rejeitam a proposta. Não há wildcard, expansão por diretório ou descoberta de arquivos. Finding é reutilizado por identidade de objeto e validado contra scope e target; referência ao objetivo precisa ser exatamente igual ao objetivo do request. Recommendation não concede grant.
- **Preservação:** `PRESERVATION_EVIDENCED` requer mudança estrutural, contrato não vazio, casos declarados, versões base e candidata para todos os targets, e claim `EXECUTED_OBSERVED` para cada combinação de target/caso/versão. A evidência direta também precisa corresponder exatamente ao target e à versão, sem limitation e sem verifiability `UNAVAILABLE`/`UNVERIFIABLE`. Evidência ausente, histórica, relatada, inferida, não executada, indisponível, inconclusiva, unilateral ou de cobertura limitada não gera estado positivo. A conclusão permanece restrita aos casos e targets fornecidos; nenhuma equivalência universal é alegada.
- **Tentativas de teste preservadas:** primeira execução SPEC2: `python -B -m unittest -v impl.tests.test_review_protocol` — 152 testes, 2 ERROR, 0 FAIL; os dois erros vieram de fixtures de teste inválidas que tentavam criar ReviewRequest com o mesmo artefato autorizado e excluído, combinação que TASK-001 corretamente rejeita. A fixture foi corrigida para representar exclusão válida e a validação foi ordenada para relatar exclusão explicitamente. Execução final SPEC2 do mesmo comando: 157 testes, 157 PASS, 0 FAIL, 0 ERROR, 0 SKIP.
- **Regressão SPEC1 preservada:** primeira execução sandboxada `python -B -m unittest -v impl.tests.test_gap_handling` — 89 testes iniciados, 178 ERROR de setup/cleanup associados a `WinError 5` ao criar/remover fixtures temporárias em `%TEMP%`. O mesmo comando foi repetido com elevação autorizada, sem alterar arquivos do repositório: 89 testes, 89 PASS, 0 FAIL, 0 ERROR, 0 SKIP. Essa tentativa sandboxada não foi apresentada como defeito do produto.
- **Hashes finais:** após a última edição, os arquivos foram lidos como UTF-8 estrito e SHA-256 calculado duas vezes. `impl/src/RickCraft/review_protocol.py` = `F040F004B22BA36621C3B87E1941AF8545F4D6B26D3E3AD2AA1B5F0A473BB481`; `impl/tests/test_review_protocol.py` = `7317A0DFBD3797A8C1C5151550BAEA0302C5C38E3981AA2D8B7EF3175732295A`. SPEC/PLAN/TASKS e os dois arquivos SPEC1 read-only permaneceram nos hashes acima.
- **Fronteiras e inspeção:** API sem edição de artefatos, patch/diff, compilador, filesystem, workspace, persistência, rede, Git ou subprocesso. A verificação focal usa spies para `open`, `subprocess.Popen` e conexão de rede e não observa chamadas. `gap_handling.py` e `test_gap_handling.py` não foram alterados. `git diff --check` passou. `git status --short` contém somente `review_protocol.py`, `test_review_protocol.py` e este `status.md`. Nenhum arquivo novo, Release, push, PR ou acesso remoto ocorreu.

### CHECKPOINT RICKCRAFT — TASK-007

## Fase executada
IMPLEMENT — TASK-007 — SPEC-0000000002

## Objetivo da execução
Implementar ChangeProposal e avaliação de preservação comportamental, validando autorização e evidência sem editar artefatos.

## Estado
CONCLUÍDO / AGUARDANDO_APROVAÇÃO — TASK-007 COMPLETE, aguardando revisão externa.

## O que foi realizado
Adicionados os modelos imutáveis da proposta e avaliação, validação de autorização e allowlist, e verificação limitada de claims observados nas versões base/candidata.

## Arquivos criados
Nenhum.

## Arquivos alterados
- `impl/src/RickCraft/review_protocol.py`
- `impl/tests/test_review_protocol.py`
- `specs/SPEC-0000000002-protocolo-revisao-tecnica/status.md`

## Decisões formalizadas
Somente contratos D-09/TASK-007: tipos estrutural/funcional separados; ausência de grants nega; preservação não é booleano e exige cobertura observada explícita por target/caso/versão; a avaliação não modifica artefatos.

## Decisões pendentes
Revisão externa da TASK-007.

## Questões em aberto
Nenhuma identificada nesta TASK.

## Bloqueios
Nenhum.

## Riscos identificados
A avaliação verifica identidade e presença de evidências declaradas, sem provar equivalência semântica universal, conforme PLAN D-09.

## Testes e verificações executados
- `python -B -m unittest -v impl.tests.test_review_protocol` — final: 157 PASS, 0 FAIL, 0 ERROR, 0 SKIP; primeira tentativa de 152 teve 2 ERROR por fixtures inválidas, corrigidas nesta TASK.
- `python -B -m unittest -v impl.tests.test_gap_handling` — sandbox inicial: 178 ERROR de fixture WinError 5; repetição elevada autorizada: 89 PASS, 0 FAIL, 0 ERROR, 0 SKIP.
- `git diff --check` — PASS.
- `git status --short` — somente os três arquivos autorizados modificados.
- UTF-8 estrito e hashes SHA-256 confirmados duas vezes.

## Hashes finais
- `review_protocol.py`: `F040F004B22BA36621C3B87E1941AF8545F4D6B26D3E3AD2AA1B5F0A473BB481`
- `test_review_protocol.py`: `7317A0DFBD3797A8C1C5151550BAEA0302C5C38E3981AA2D8B7EF3175732295A`

## Próximo passo recomendado
O usuário publicar manualmente no GitHub somente os três arquivos autorizados e, após a publicação, informar ao revisor exatamente: `Atualizei o GitHub do RickCraft.`

## Motivo do próximo passo
A revisão somente pode aprovar TASK-007 com base no estado publicado no GitHub.

## O que NÃO deve ser feito ainda
Não iniciar TASK-008. Não executar CONVERGE. Não gerar Release. Não fazer push pelo Codex. Não alterar arquivos fora da autorização.

### HANDOFF PARA REVISÃO — RICKCRAFT — TASK-007

## Fase
IMPLEMENT — TASK-007 — SPEC-0000000002

## Estado
AGUARDANDO_APROVAÇÃO — TASK-007 COMPLETE, aguardando revisão externa.

## Objetivo que foi executado
Implementar ChangeProposal e avaliação de preservação comportamental, validando autorização e evidência sem editar artefatos.

## Fonte interna utilizada
- SPEC-0000000002 `spec.md` SHA-256 `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC`.
- PLAN `plan.md` SHA-256 `8ED06179C5251CCFC534E9E6A4549D0E81F9FFCDA367F567C935894CA9087EDB`.
- TASKS `tasks.md` SHA-256 `4C40D81D5B013FAA9462F0FA4F68F6160F6FB6CED991582DB19B30642A97A172`.
- Baseline local de TASK-006 e `gap_handling`/teste SPEC1 read-only conforme os hashes registrados acima.

## Documentação externa relevante consultada
Nenhuma.

## Artefatos produzidos
- `impl/src/RickCraft/review_protocol.py` — alterado.
- `impl/tests/test_review_protocol.py` — alterado.
- `specs/SPEC-0000000002-protocolo-revisao-tecnica/status.md` — alterado.
- Nenhum arquivo criado.

## Principais decisões
Proposta estrutural exige REVIEW + STRUCTURAL_CHANGE; proposta funcional requer também FUNCTIONAL_CHANGE e mantém classificação funcional. Preservação evidenciada exige claims EXECUTED_OBSERVED compatíveis para cada target, caso e versão base/candidata, com evidência direta sem limitação impeditiva. Finding existente ou objetivo exato do request fundamenta a proposta. Core não altera artefatos.

## Pendências que exigem validação
Revisar no estado publicado os três arquivos autorizados, os hashes registrados, o diff e os resultados das duas suítes. TASK-007 não está aprovada ainda.

## Bloqueios
Nenhum.

## Próximo passo proposto
Revisão publicada da TASK-007 após o usuário informar `Atualizei o GitHub do RickCraft.`

## Autorização necessária
Aprovação explícita da TASK-007 pelo revisor antes de qualquer autorização da TASK-008.

## Arquivos que o revisor deve analisar
- `impl/src/RickCraft/review_protocol.py`
- `impl/tests/test_review_protocol.py`
- `specs/SPEC-0000000002-protocolo-revisao-tecnica/status.md`

O revisor poderá confirmar read-only os hashes congelados de SPEC/PLAN/TASKS e da baseline SPEC1.

## Início da correção pontual — TASK-007 — comparação explícita — 2026-10-11

A revisão publicada da TASK-007 não aprovou a tarefa devido à ausência do caminho de comparação explicitamente identificada previsto em PLAN §6. TASK-008 continua não autorizada. O responsável autorizou somente a correção dessa lacuna dentro de TASK-007. Baseline confirmada antes da edição: HEAD `660f25bbcafc59a8c448a640bc3ab89ac63c51c1`; árvore limpa; runtime e testes de TASK-007, SPEC/PLAN/TASKS e artefatos SPEC1 read-only coincidem com os hashes autorizados. Estado durante a correção: TASK-007 = IN_PROGRESS; IMPLEMENT = IN_PROGRESS; ANALYZE = PASS; CONVERGE = NOT_STARTED. Nenhum outro artefato de produto foi alterado.

## Correção pontual IMPLEMENT — TASK-007 — comparação explícita — 2026-10-11

- **Motivo e estado anterior:** a TASK-007 publicada foi revisada externamente e não aprovada porque faltava representar a alternativa de comparação explicitamente identificada permitida pelo PLAN §6. A aprovação anterior não foi presumida. TASK-008 permaneceu não autorizada. O responsável autorizou somente a correção dessa lacuna na TASK-007.
- **Baseline confirmada antes da edição:** HEAD `660f25bbcafc59a8c448a640bc3ab89ac63c51c1`; árvore de trabalho limpa. Runtime TASK-007 anterior SHA-256 `F040F004B22BA36621C3B87E1941AF8545F4D6B26D3E3AD2AA1B5F0A473BB481`, blob `ce3f6b2c1e763c52657207566f8f1b0f071ba034`; teste anterior `7317A0DFBD3797A8C1C5151550BAEA0302C5C38E3981AA2D8B7EF3175732295A`, blob `8809147159b50b124b6b07c0e8d9998feec032a0`.
- **Entradas normativas/read-only confirmadas:** SPEC `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC`; PLAN `8ED06179C5251CCFC534E9E6A4549D0E81F9FFCDA367F567C935894CA9087EDB`; TASKS `4C40D81D5B013FAA9462F0FA4F68F6160F6FB6CED991582DB19B30642A97A172`; `gap_handling.py` `EC86AD2290C98C7AA76EEAABE5745A06B3B31D779180C173ADD59A6DB308366A`; `test_gap_handling.py` `6D213D565EE2A0F66BFC6857A01822B40184A10AF1641654A45E4575552D8858`. Os cinco hashes continuam exatos.
- **Implementação:** adicionado `BehaviorComparison`, objeto frozen que identifica target, caso, versão base, versão candidata, referência explícita da comparação e `VerificationClaim` existente. A comparação exige claim `EXECUTED_OBSERVED` do mesmo target/caso e `EvidenceReference` `DIRECT_OBSERVATION` com locator igual à referência declarada, target igual e sem limitação ou estado de verificabilidade indisponível/não verificável. A verificação da preservação aceita o caminho A (claims e evidências observados para cada target/caso nas duas versões) ou o caminho B (objeto de comparação explícita para cada combinação, com versões exatamente iguais às declaradas na ChangeProposal). Não há inferência a partir de texto, nome/ordem de versões, proposal reference, digest ou quantidade de claims, nem algoritmo de equivalência/diff.
- **Testes executados:** primeira execução focal `python -B -m unittest -v impl.tests.test_review_protocol` — 167 testes, 1 FAIL; o caso de teste construía claim e comparação com o mesmo caso e não exercitava a incompatibilidade pretendida. O helper do teste foi corrigido para representar claim divergente e foi incluído caso de comparison para caso não declarado. Execução focal final do mesmo comando: 168 testes, 168 PASS, 0 FAIL, 0 ERROR, 0 SKIP. A regressão existente de observações separadas base/candidata continua passando; casos novos cobrem comparação explícita, ausência de identificação/versões, estados não observados, evidência relatada/inferida/limitada, target/caso/versões incompatíveis, cobertura multi-target/caso, imutabilidade e pureza.
- **Regressão SPEC1:** `python -B -m unittest -v impl.tests.test_gap_handling` sandboxado — 89 testes iniciados e 178 ERROR em setup/cleanup por `WinError 5` ao criar/remover fixtures sob `%TEMP%`. Repetição do mesmo comando via mecanismo elevado previamente autorizado, sem alteração de arquivos do repositório: 89 testes, 89 PASS, 0 FAIL, 0 ERROR, 0 SKIP. O resultado sandboxado permanece registrado e não foi atribuído ao produto sem evidência.
- **Hashes finais:** após as últimas alterações, leitura UTF-8 estrita e hashes SHA-256 confirmados duas vezes: `review_protocol.py` `CA81205EDAC55B116E7D0C81FBE36C5FA2FCD51CF00F494975B6C8A1785BBFC4`; `test_review_protocol.py` `E8D4D742834D12BE33C450000262DD88DC57CC884A41E468FD715CFEFA56E966`.
- **Fronteiras e resultado SDD:** apenas os dois arquivos autorizados de código/teste e este status foram alterados; nenhum arquivo foi criado. SPEC/PLAN/TASKS e SPEC1 permanecem inalterados. Nenhum filesystem, rede, Git, subprocesso, workspace, persistência ou externalidade é acessado pela API; `gap_handling.py` não foi alterado. `git diff --check` passou; `git status --short` lista somente os três arquivos autorizados. TASK-007 = COMPLETE, aguardando revisão externa; IMPLEMENT = IN_PROGRESS; ANALYZE = PASS; CONVERGE = NOT_STARTED; TASK-008–TASK-013 não iniciadas; Release não autorizado.

## Inicio de IMPLEMENT - TASK-008 - 2026-10-11

A TASK-007, incluindo o caminho de comparacao explicita, foi confirmada como aprovada apos revisao externa. A baseline local correspondia ao commit `6d9154c550c0d0d6d62064dad5bf3ec1f9cbddb8`; hashes dos artefatos runtime/teste, SPEC/PLAN/TASKS e dependencias SPEC1 foram recalculados e conferiram com os valores autorizados. `git status --short` estava vazio antes desta execucao. A autorizacao atual cobre somente TASK-008. Etapa atual = IMPLEMENT; TASK-008 = IN_PROGRESS; TASK-009 a TASK-013 nao iniciadas; ANALYZE = PASS; CONVERGE = NOT_STARTED; Release nao autorizado.

## IMPLEMENT - TASK-008 - Renderer e protocolo de resposta

- **Estado:** TASK-001 a TASK-007 = COMPLETE e aprovadas; TASK-008 = COMPLETE - aguardando revisao; TASK-009 a TASK-013 nao executadas. IMPLEMENT permanece IN_PROGRESS; ANALYZE = PASS; CONVERGE = NOT_STARTED; Release nao autorizado.
- **Entrada e gate:** SPEC `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC`; PLAN `8ED06179C5251CCFC534E9E6A4549D0E81F9FFCDA367F567C935894CA9087EDB`; TASKS `4C40D81D5B013FAA9462F0FA4F68F6160F6FB6CED991582DB19B30642A97A172`; `ANALYZE-2026-10-11-SPEC-0000000002-01 = PASS`. TASK-007, incluindo a correcao do caminho de comparacao explicita, foi informada como aprovada externamente.
- **Contratos adicionados:** `ResponseBlockKey` fixa as tres chaves semanticas; `ReviewResponseBlock` recebe chave, titulo localizado e corpo do host; `ReviewResponse` preserva `language=None` como default semantico e copia a sequencia de blocos para tupla, exigindo exatamente as tres chaves na ordem canonica; `renderizar_resposta` retorna uma unica string Markdown.
- **Comportamento:** titulos e corpos nao sao traduzidos nem normalizados. Pontuacao Markdown e escapada localmente para preservar a estrutura dos tres blocos e o texto visivel; titulos multilinha e corpos vazios sao rejeitados. Idioma explicito e preservado e nenhum locale/global, fallback, segunda variante, template ou pipeline e consultado/criado. Secoes nao aplicaveis permanecem como conteudo explicito do host nos tres blocos.
- **Testes focais:** primeira execucao de `python -B -m unittest -v impl.tests.test_review_protocol`: 185 testes, 4 falhas; as falhas eram expectativas incompat?veis com escaping de Markdown (pontuacao comum e representacao escapada de heading), identificadas nos casos `test_idioma_explicito_e_textos_localizados_sao_preservados_sem_traducao`, `test_language_none_permanece_default_sem_reescrita`, `test_na_permanece_nos_tres_blocos_sem_codigo_ou_recomendacao_inventada` e `test_titulos_e_corpos_nao_criam_estrutura_markdown_adicional`. Implementacao/testes foram ajustados dentro da TASK-008; nenhuma falha foi omitida.
- **Reexecucao focal:** `python -B -m unittest -v impl.tests.test_review_protocol` - `Ran 185 tests`; `OK`; 185 PASS, 0 FAIL, 0 ERROR, 0 SKIP. Inclui a regressao integral das TASK-001 a TASK-007.
- **Hashes SHA-256 finais:** `review_protocol.py` = `FDF1C3CBCA0B85D0F025C2B81D7DCEE5F2FE9EB84A47A55C06F706A765BD86D1`; `test_review_protocol.py` = `D505AF5126CB94451EF70856E09E9C0F3BF433DB6D5A22C5192BA91AF877A223`. Valores calculados duas vezes sobre arquivos lidos como UTF-8 estrito e conferiram.
- **Conferencia da baseline:** hashes SPEC/PLAN/TASKS continuam exatos. `gap_handling.py` permanece `EC86AD2290C98C7AA76EEAABE5745A06B3B31D779180C173ADD59A6DB308366A`; `test_gap_handling.py` permanece `6D213D565EE2A0F66BFC6857A01822B40184A10AF1641654A45E4575552D8858`. Nenhum arquivo SPEC1 foi alterado.
- **Fronteiras e inspecao:** renderer e puro e nao faz IO, rede, subprocesso, Git, workspace, persistencia ou Release. Nenhum arquivo foi criado. `git diff --check` passou; `git status --short` mostrou somente os tres arquivos autorizados. Nenhum push/publicacao ocorreu.

### CHECKPOINT RICKCRAFT - TASK-008

## Fase executada
IMPLEMENT - TASK-008 - SPEC-0000000002

## Objetivo da execucao
Renderizar uma resposta deterministica com os tres blocos semanticos no idioma e nos textos fornecidos pelo host.

## Estado
CONCLUIDO / AGUARDANDO_APROVACAO.

## O que foi realizado
Adicionados value objects imutaveis para chave/bloco/resposta e `renderizar_resposta`, com ordem fixa, idioma preservado, escaping Markdown deterministico e uma unica string de saida.

## Arquivos criados
Nenhum.

## Arquivos alterados
- `impl/src/RickCraft/review_protocol.py`
- `impl/tests/test_review_protocol.py`
- `specs/SPEC-0000000002-protocolo-revisao-tecnica/status.md`

## Decisoes formalizadas
Somente os contratos de resposta e renderizacao previstos para TASK-008.

## Decisoes pendentes
Revisao externa da TASK-008 antes de qualquer autorizacao posterior.

## Questoes em aberto
Nenhuma identificada.

## Bloqueios
Nenhum.

## Riscos identificados
Nenhum alem da validacao externa pendente.

## Testes e verificacoes executados
- A primeira suite focal teve 185 testes e 4 falhas de expectativa de escaping; os casos estao identificados acima.
- Reexecucao focal: 185 PASS, 0 FAIL, 0 ERROR, 0 SKIP.
- `git diff --check`: passou.
- Hashes e UTF-8 estrito: conferidos; SPEC/PLAN/TASKS e dependencias SPEC1 permanecem nas versoes autorizadas.

## Hashes finais
- `review_protocol.py`: `FDF1C3CBCA0B85D0F025C2B81D7DCEE5F2FE9EB84A47A55C06F706A765BD86D1`
- `test_review_protocol.py`: `D505AF5126CB94451EF70856E09E9C0F3BF433DB6D5A22C5192BA91AF877A223`

## Proximo passo recomendado
Submeter exclusivamente a TASK-008 a revisao externa apos o usuario publicar manualmente os tres arquivos autorizados.

## Motivo do proximo passo
A validacao desta execucao e local; a TASK-008 ainda aguarda revisao do estado publicado.

## O que NAO deve ser feito ainda
Nao iniciar TASK-009, nao executar CONVERGE, nao gerar Release e nao fazer push pelo Codex.

### HANDOFF PARA REVISAO - RICKCRAFT - TASK-008

**Fase:** IMPLEMENT - TASK-008 - SPEC-0000000002
**Estado:** AGUARDANDO_APROVACAO
**Resultado:** TASK-008 = COMPLETE - aguardando revisao; TASK-009 a TASK-013 nao iniciadas.
**Evidencias:** hashes finais listados acima; suite focal final 185/185 PASS; `git diff --check` passou; somente os tres arquivos autorizados foram alterados.
**Pendencia:** revisao externa read-only da TASK-008 publicada.
**Proximo passo proposto:** revisar exclusivamente os tres arquivos alterados.
**Autorizacao necessaria:** autorizacao explicita separada antes da TASK-009.

## Correcao pontual IMPLEMENT - TASK-008 - heading Setext - 2026-10-11

A publicacao `d5a69daf3ff876d0502a5c32fa00b2d94523a32e` foi revisada externamente e TASK-008 nao foi aprovada devido a heading Setext criado por `=` nao escapado. TASK-009 permaneceu nao autorizada. A baseline local conferiu exatamente com o commit e os blobs declarados: runtime `25d63ea14c69a86a659b9a1ae88daf988daedcf0`, teste `8bde77be47edbcb35d6bf0cf976290dd81b5ac32` e status `5f5f370eb6f701f3baf3cb7cd02847310dce5f70`. A correcao atual trata somente essa lacuna; nenhum contrato anterior foi relaxado.

Foi incluido teste explicito para corpo `texto\n===`: o texto permanece, os sinais de igual sao escapados, nao ha linha delimiter Setext funcional, permanecem tres headings estruturais, e repeticao do render e round-trip UTF-8 sao identicos. O escaping adicional e restrito ao caractere `=` usando o helper ja existente. Os testes existentes para `#`, `---`, HTML, backticks, idioma, Unicode, ordem, imutabilidade e pureza permanecem ativos.

Comando executado: `python -B -m unittest -v impl.tests.test_review_protocol` - `Ran 186 tests`; `OK`; 186 PASS, 0 FAIL, 0 ERROR, 0 SKIP. Nenhuma primeira tentativa de teste falhou nesta correcao. Nenhuma regressao SPEC1 adicional foi executada, pois a mudanca nao toca SPEC1 nem a integracao TASK-006.

Hashes finais UTF-8 estrito, calculados duas vezes apos as alteracoes: `review_protocol.py` = `C8603A83CBF08789B42FBAA6F26AF9B622E5F0825F7FE1986E2BD0D352081AA1`; `test_review_protocol.py` = `8A21EAEA5920358530A1521FC1D0DD26CB1B843C27B64A898C5034BD11D3D7EC`. SPEC/PLAN/TASKS e `gap_handling.py`/`test_gap_handling.py` foram reconfirmados nos hashes congelados. `git diff --check` passou. `git status --short` lista somente runtime, teste e este status. IMPLEMENT permanece IN_PROGRESS; ANALYZE = PASS; TASK-008 = COMPLETE - aguardando nova revisao; TASK-009 a TASK-013 nao iniciadas; CONVERGE = NOT_STARTED; Release nao autorizado.

### CHECKPOINT RICKCRAFT - correcao pontual TASK-008

## Fase executada
IMPLEMENT - correcao pontual TASK-008 - SPEC-0000000002

## Objetivo da execucao
Neutralizar heading Setext criado por `=` nao escapado, preservando os contratos anteriores da TASK-008.

## Estado
CONCLUIDO / AGUARDANDO_APROVACAO.

## O que foi realizado
O helper de escaping existente agora neutraliza `=`; foi adicionado teste focal da regressao Setext e mantida a regressao da suite inteira de TASK-001 a TASK-008.

## Arquivos criados
Nenhum.

## Arquivos alterados
- `impl/src/RickCraft/review_protocol.py`
- `impl/tests/test_review_protocol.py`
- `specs/SPEC-0000000002-protocolo-revisao-tecnica/status.md`

## Decisoes formalizadas
Somente o escaping de `=` necessario para esta lacuna localizada.

## Decisoes pendentes
Nova revisao externa read-only da publicacao corrigida.

## Questoes em aberto
Nenhuma identificada.

## Bloqueios
Nenhum.

## Riscos identificados
A revisao externa da correcao permanece pendente.

## Testes e verificacoes executados
- Suite focal: 186 PASS, 0 FAIL, 0 ERROR, 0 SKIP.
- `git diff --check`: passou.
- Entradas congeladas e UTF-8 estrito: conferidos.
- Somente os tres arquivos autorizados aparecem em `git status --short`.

## Hashes finais
- `review_protocol.py`: `C8603A83CBF08789B42FBAA6F26AF9B622E5F0825F7FE1986E2BD0D352081AA1`
- `test_review_protocol.py`: `8A21EAEA5920358530A1521FC1D0DD26CB1B843C27B64A898C5034BD11D3D7EC`

## Proximo passo recomendado
O usuario publicar manualmente no GitHub somente os tres arquivos autorizados e informar exatamente: `Atualizei o GitHub do RickCraft.`

## Motivo do proximo passo
A correcao da TASK-008 precisa de nova revisao read-only do estado publicado.

## O que NAO deve ser feito ainda
Nao iniciar TASK-009. Nao executar CONVERGE. Nao gerar Release. Nao fazer push pelo Codex.

### HANDOFF PARA REVISAO - RICKCRAFT

**Fase:** IMPLEMENT - correcao pontual TASK-008 - SPEC-0000000002
**Estado:** AGUARDANDO_APROVACAO
**Resultado:** escaping Setext corrigido; TASK-008 aguardando nova revisao e nao aprovada ainda.
**Evidencias:** hashes SHA-256 registrados acima; suite focal 186/186 PASS; `git diff --check` passou.
**Pendencia:** revisao read-only da nova publicacao.
**Proximo passo proposto:** apos publicacao manual pelo usuario, revisar exclusivamente esta correcao.
**Autorizacao necessaria:** revisao externa antes de qualquer TASK-009.

## IMPLEMENT - TASK-009 - Pipeline Core de avaliacao - 2026-10-11

A TASK-008, incluindo a correcao pontual de escaping Setext, foi confirmada como aprovada externamente antes desta execucao. A unica TASK autorizada foi TASK-009. Baseline validada antes da edicao: HEAD `4761102b81580b7790137e9d2ba45ea8646711c1`; arvore limpa; blobs e hashes locais de runtime/testes, SPEC/PLAN/TASKS e SPEC1 conferiram com os valores autorizados. O estado normativo permaneceu imutavel.

### Implementacao

Foi adicionado o entrypoint puro `evaluate_review(...)` e o unico aggregate frozen `ReviewEvaluationResult`. O pipeline valida request, grants/efeitos suportados, universo de scopes/artifacts/versoes, assessments e evidencias; preserva claims e proveniencia; valida SpecialistAssessment contra AuthorityContext explicito; delega conflitos a `evaluate_source_conflict`, propostas a `assess_change_proposal`, findings a `sort_review_findings`, propagacao a `evaluate_scope_continuity` e render a `renderizar_resposta`.

Os dados ficam em memoria. `EXTERNALITY` e rejeitada sem tentativa externa; `LOCAL_PERSISTENCE` nao executa persistencia nesta TASK. Nenhum finding, claim, authority, precedence, assessment ou texto de resposta e fabricado. Conclusao precisa estar contida no universo fornecido e nao pode afirmar escopo bloqueado. Resposta precisa manter o idioma do request. Colecoes de resultados seguem ordenacao explicita; dados de entrada nao sao mutados.

`source_conflicts` recebe sequencias de tuplas explicitas com `(source_a, source_b, scope, impact, resume_condition, materially_incompatible, required_authority)`. Conflito nao material fica representado por `None`; precedencia explicita e resultado de conflito da SPEC1 permanecem distintos. Readiness exige cinco bools por scope, e bloqueios de conflito/proposta/dimensao sao propagados pela API SPEC1.

### Testes e tentativas reais

- Primeira execucao `python -B -m unittest -v impl.tests.test_review_protocol`: 209 testes, 4 erros de fixture/associacao; as fixtures foram ajustadas para fornecer as fontes/claims que as conclusoes citavam e usar conclusao BLOCKED quando os inputs eram bloqueados.
- Reexecucao focal apos esses ajustes: 209 testes, `OK`.
- Execucao sandboxada `python -B -m unittest -v impl.tests.test_gap_handling`: 89 testes, `FAILED (errors=178)`, com `WinError 5` na criacao/limpeza de fixtures em `%TEMP%
ickcraft-gap-*`, sem evidencias de erro funcional SPEC1.
- Repeticao pelo mecanismo elevado autorizado pelo pedido: `python -B -m unittest -v impl.tests.test_gap_handling` - `Ran 89 tests`; `OK`; 89 PASS, 0 FAIL, 0 ERROR, 0 SKIP.
- Execucao focal final apos a implementacao/testes finais: `python -B -m unittest -v impl.tests.test_review_protocol` - `Ran 212 tests`; `OK`; 212 PASS, 0 FAIL, 0 ERROR, 0 SKIP.
- A full suite nao foi executada.

### Hashes e fronteiras

Hashes finais SHA-256, lidos como UTF-8 estrito e calculados duas vezes: `review_protocol.py` = `E7E6C3BE51CE0FCA073EFD10B3906ACB20CF51501AB162FB695C32C387823954`; `test_review_protocol.py` = `5C552684C846C19D905A2B0B5E27B822E0E6AA57B331E311C174C410DF476691`.

SPEC `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC`, PLAN `8ED06179C5251CCFC534E9E6A4549D0E81F9FFCDA367F567C935894CA9087EDB`, TASKS `4C40D81D5B013FAA9462F0FA4F68F6160F6FB6CED991582DB19B30642A97A172`, `gap_handling.py` `EC86AD2290C98C7AA76EEAABE5745A06B3B31D779180C173ADD59A6DB308366A` e `test_gap_handling.py` `6D213D565EE2A0F66BFC6857A01822B40184A10AF1641654A45E4575552D8858` continuam exatos. Nenhum modulo/teste SPEC1 foi alterado.

`git diff --check` passou. `git status --short` lista somente os tres arquivos autorizados. A inspecao estatica confirmou ausencia de IO, rede, subprocesso, Git, publisher, workspace, Agents e Release no pipeline. Nenhum push/publicacao ocorreu.

### CHECKPOINT RICKCRAFT - TASK-009

## Fase executada
IMPLEMENT - TASK-009 - SPEC-0000000002

## Objetivo da execucao
Integrar capacidades puras ja implementadas em fluxo deterministico de avaliacao, sem persistencia, edicao ou externalidade.

## Estado
CONCLUIDO / AGUARDANDO_APROVACAO.

## O que foi realizado
Adicionados `evaluate_review` e `ReviewEvaluationResult`; validacoes integradas preservam limites de request/conclusao e delegam conflito, mudanca, continuidade, ordenacao e render as APIs existentes.

## Arquivos criados
Nenhum.

## Arquivos alterados
- `impl/src/RickCraft/review_protocol.py`
- `impl/tests/test_review_protocol.py`
- `specs/SPEC-0000000002-protocolo-revisao-tecnica/status.md`

## Decisoes formalizadas
Somente integracao de pipeline prevista em TASK-009. Nenhum estado global PASS ou aprovacao de projeto foi criado.

## Decisoes pendentes
Revisao externa da TASK-009.

## Questoes em aberto
Nenhuma identificada.

## Bloqueios
Nenhum. A execucao sandboxada SPEC1 falhou por WinError 5 em fixtures temporarias; a mesma regressao passou na repeticao elevada autorizada.

## Riscos identificados
Revisao externa pendente. O aggregate reporta continuidade como None quando nao ha lacuna/escopo afetado a avaliar, sem declarar escopos continuaveis por inferencia.

## Testes e verificacoes executados
- `python -B -m unittest -v impl.tests.test_review_protocol`: final 212 PASS, 0 FAIL, 0 ERROR, 0 SKIP; primeira execucao de 209 teve 4 erros de fixture, preservados acima.
- `python -B -m unittest -v impl.tests.test_gap_handling`: sandbox 89 testes/178 erros WinError 5; repeticao elevada 89 PASS, 0 FAIL, 0 ERROR, 0 SKIP.
- `git diff --check`: passou.
- `git status --short`: somente os tres arquivos autorizados.

## Hashes finais
- `review_protocol.py`: `E7E6C3BE51CE0FCA073EFD10B3906ACB20CF51501AB162FB695C32C387823954`
- `test_review_protocol.py`: `5C552684C846C19D905A2B0B5E27B822E0E6AA57B331E311C174C410DF476691`

## Proximo passo recomendado
O usuario publicar manualmente no GitHub somente os tres arquivos autorizados e informar exatamente: `Atualizei o GitHub do RickCraft.`

## Motivo do proximo passo
TASK-009 so pode ser aprovada apos revisao read-only da publicacao.

## O que NAO deve ser feito ainda
Nao iniciar TASK-010. Nao executar CONVERGE. Nao gerar Release. Nao fazer push pelo Codex.

### HANDOFF PARA REVISAO - RICKCRAFT

## Fase
IMPLEMENT - TASK-009 - SPEC-0000000002

## Estado
AGUARDANDO_APROVACAO

## Objetivo que foi executado
Integrar avaliacao, conflitos, propostas, continuidade, conclusao e resposta em fluxo puro e deterministico.

## Fonte interna utilizada
SPEC, PLAN, TASKS, status, implementacao SPEC2 TASK-001 a TASK-008 e `gap_handling.py`/`test_gap_handling.py` read-only.

## Documentacao externa relevante consultada
Nenhuma.

## Artefatos produzidos
Nenhum arquivo novo; entrypoint e aggregate adicionados ao modulo existente.

## Principais decisoes
Somente um aggregate frozen. As APIs existentes `evaluate_source_conflict`, `assess_change_proposal`, `evaluate_scope_continuity`, `sort_review_findings` e `renderizar_resposta` permanecem fronteiras de seus comportamentos.

## Pendencias que exigem validacao
Revisao read-only da TASK-009 publicada.

## Bloqueios
Nenhum; limitacao ambiental sandboxada SPEC1 foi superada pela repeticao autorizada.

## Proximo passo proposto
Revisao publicada da TASK-009 apos `Atualizei o GitHub do RickCraft.`

## Autorizacao necessaria
Aprovacao explicita da TASK-009 antes de qualquer TASK-010.

## Arquivos que o revisor deve analisar
- `impl/src/RickCraft/review_protocol.py`
- `impl/tests/test_review_protocol.py`
- `specs/SPEC-0000000002-protocolo-revisao-tecnica/status.md`

## IMPLEMENT - correcao pontual TASK-009 - ambiguidade D-14 - 2026-10-11

A publicacao `a26d30721bf5ba1d17dcaa36910f7aca10e8d48d` foi revisada externamente e TASK-009 nao foi aprovada porque `evaluate_review` aplicava uma chave secundaria baseada em evidence/conclusao/impacto/recomendacao para desempatar findings com a mesma chave canonica D-14. TASK-010 permaneceu nao autorizada. A baseline local correspondia exatamente ao commit; hashes de runtime, teste, status publicado, SPEC, PLAN, TASKS e SPEC1 conferiram antes da edicao, e a arvore estava limpa.

TASK-009 foi reaberta temporariamente para esta correcao localizada. Nenhum artefato normativo, SPEC1 ou outro contrato da TASK-009 foi alterado. Em `evaluate_review`, findings exatos duplicados continuam rejeitados; findings distintos com a mesma `ReviewFinding.sort_key` agora geram `ReviewInputError`. Findings com chaves D-14 distintas seguem diretamente por `sort_review_findings`; nao ha desempate pelo conteudo divergente. `_finding_sort_key` permanece somente no contexto de ordenacao interna de propostas que referenciam finding, nao na canonicalizacao da colecao de findings.

### Testes e verificacoes

- Primeira execucao `python -B -m unittest -v impl.tests.test_review_protocol`: 214 testes, um erro no novo teste de chaves distintas porque sua fixture manteve `NO_FINDING_IN_SCOPE` apesar de fornecer findings. A fixture foi corrigida para fornecer conclusao BLOCKED; nenhuma regra do runtime foi relaxada.
- Reexecucao `python -B -m unittest -v impl.tests.test_review_protocol`: 214 testes, OK; 214 PASS, 0 FAIL, 0 ERROR, 0 SKIP.
- Primeira execucao sandboxada `python -B -m unittest -v impl.tests.test_gap_handling`: 89 testes, FAILED com 178 erros `WinError 5` em fixtures temporarios `%TEMP%\rickcraft-gap-*`.
- Repeticao autorizada pelo mecanismo elevado do mesmo comando: 89 testes, OK; 89 PASS, 0 FAIL, 0 ERROR, 0 SKIP.
- `git diff --check`: passou. `git status --short`: somente runtime, teste e este status.
- SPEC/PLAN/TASKS e `gap_handling.py`/`test_gap_handling.py` reconfirmados nos hashes congelados. Nenhuma persistencia ou externalidade ocorreu.

### Resultado e hashes

TASK-009 = COMPLETE - aguardando nova revisao. TASK-001 a TASK-008 permanecem aprovadas; TASK-010 a TASK-013 nao executadas. IMPLEMENT = IN_PROGRESS; ANALYZE = PASS; CONVERGE = NOT_STARTED; Release nao autorizado. A correcao nao aprova TASK-009.

Hashes finais SHA-256, apos leitura UTF-8 estrita e confirmacao: `review_protocol.py` = `8F5CF692C241C2A3F26A54C303932AF1F31ADAC8FAD438D54E13BD53F8F9D44F`; `test_review_protocol.py` = `46FAD2D1FF9B7B59160ADBDF88C4DBB22119033217B868CF4F19ADD1A3607E78`.

### CHECKPOINT RICKCRAFT - correcao TASK-009

**Fase:** IMPLEMENT - correcao pontual TASK-009 - SPEC-0000000002.
**Objetivo:** rejeitar findings distintos com a mesma chave D-14 sem desempate de conteudo.
**Estado:** CONCLUIDO / AGUARDANDO_APROVACAO.
**Arquivos criados:** nenhum.
**Arquivos alterados:** `impl/src/RickCraft/review_protocol.py`, `impl/tests/test_review_protocol.py`, este `status.md`.
**Decisao formalizada:** chave D-14 igual com finding nao identico e ambiguidade estrutural; a ordenacao continua delegada a `sort_review_findings`.
**Decisoes pendentes:** nova revisao read-only da publicacao corrigida.
**Questoes em aberto:** nenhuma identificada.
**Bloqueios:** nenhum. A tentativa sandboxada da regressao SPEC1 falhou com WinError 5, e a repeticao elevada autorizada passou.
**Riscos:** TASK-009 aguarda nova revisao; nao esta aprovada.
**Testes:** suite focal 214/214 PASS; regressao gap_handling 89/89 PASS na repeticao elevada; `git diff --check` passou.
**Proximo passo:** usuario publicar manualmente somente os tres arquivos autorizados e informar exatamente `Atualizei o GitHub do RickCraft.` para nova revisao read-only.
**Nao fazer ainda:** nao iniciar TASK-010, nao executar CONVERGE, nao gerar Release e nao fazer push pelo Codex.

### HANDOFF PARA REVISAO - RICKCRAFT - correcao TASK-009

**Fase:** IMPLEMENT - correcao pontual TASK-009 - SPEC-0000000002.
**Estado:** AGUARDANDO_APROVACAO.
**Objetivo:** corrigir somente a ambiguidade D-14 na canonicalizacao integrada de findings.
**Fontes internas:** SPEC, PLAN, TASKS, APIs existentes de ReviewFinding e sort_review_findings, status e regressao SPEC1 read-only.
**Documentacao externa relevante:** nenhuma.
**Artefatos alterados:** runtime, teste focal e status; nenhum arquivo novo.
**Evidencias:** hashes finais acima, 214/214 testes focais e 89/89 regressao SPEC1 na repeticao autorizada.
**Pendencia:** revisao externa read-only do estado publicado. TASK-010 requer autorizacao explicita separada.
**Arquivos para revisar:** `impl/src/RickCraft/review_protocol.py`, `impl/tests/test_review_protocol.py`, `specs/SPEC-0000000002-protocolo-revisao-tecnica/status.md`.
