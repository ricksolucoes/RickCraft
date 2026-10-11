# Status — SPEC-0000000002

## Estado corrente

- **Etapa atual:** TASKS
- **SPEC:** COMPLETE — aprovada pelo responsável pelo projeto
- **PLAN:** COMPLETE — aprovada pelo responsável pelo projeto
- **TASKS:** COMPLETE — pronta para revisão, não aprovada
- **ANALYZE:** NOT_STARTED
- **IMPLEMENT:** NOT_STARTED
- **CONVERGE:** NOT_STARTED
- **Último gate válido:** nenhum
- **Execution ID:** nenhum

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
