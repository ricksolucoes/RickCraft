# TASKS — SPEC-0000000002 — Protocolo de Revisão Técnica, Escopo e Resposta

## 1. Identificação e versões de entrada

- **SPEC:** `SPEC-0000000002`, COMPLETE e aprovada; SHA-256 `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC`; blob Git `97f1a98c4f3b25bf52c0fa71c29502a39e9ca556`.
- **PLAN:** COMPLETE e aprovado; SHA-256 `8ED06179C5251CCFC534E9E6A4549D0E81F9FFCDA367F567C935894CA9087EDB`; blob Git `0c28cf63a68e09365e1fb3ead7a02e609b60fcfa`.
- **Data da aprovação do PLAN:** 2026-10-11.
- **Escopo deste artefato:** decompor exclusivamente D-01–D-15, RF-001–RF-021, CA-001–CA-021 e cenários A–O em tarefas ordenadas. TASKS COMPLETE significa pronto para revisão; não executa nem autoriza ANALYZE.
- **Dependência normativa operacional:** SPEC-0000000001 e APIs já existentes, sem alteração de seus módulos ou contratos.

## 2. Regras comuns de execução futura

1. Executar as tarefas na ordem TASK-001 a TASK-013, uma por autorização explícita. A conclusão de TASKS não inicia ANALYZE ou IMPLEMENT.
2. Cada execução futura deve confirmar os hashes e estados correntes dos artefatos aplicáveis, atualizar `status.md` na mesma execução e limitar alterações aos arquivos autorizados na tarefa.
3. A implementação prevista é exclusivamente `impl/src/RickCraft/review_protocol.py`; o teste previsto é exclusivamente `impl/tests/test_review_protocol.py`. Ambas as tarefas podem acrescentar conteúdo a esses mesmos arquivos na ordem definida. `status.md` é atualizado durante futuras execuções IMPLEMENT. Nenhum módulo ou teste existente da SPEC-0000000001 pode ser alterado.
4. Usar Python 3.12 ou compatível e somente biblioteca padrão. Testes usam `unittest` e fixtures temporárias. Não criar outro runtime/test file, metadata de package, schema documental ou dependência externa sem retorno ao PLAN.
5. A avaliação padrão é pura e em memória. Persistência local só pode ocorrer na TASK-010, mediante pedido/intent e grant apropriados, usando APIs aprovadas da SPEC-0000000001 e fixtures; nunca acessar ou publicar no Debug real.
6. Evidência de conclusão contém comandos realmente executados, resultados observados, hashes dos arquivos relevantes, limitações, ausência de efeitos fora do escopo e confirmação das exclusões. Não declarar teste, inspeção ou publicação não executados.
7. A saída preserva o idioma pedido; `None` significa pt-BR. O host fornece conteúdo e títulos localizados; o Core os preserva sem traduzir e sem produzir resposta adicional. Artefatos internos desta unidade permanecem pt-BR. Nenhum Release é produzido.

## 3. Tarefas

### TASK-001 — Pedido, escopo, idioma e autorização

**Objetivo único:** implementar os modelos imutáveis de pedido/escopo e suas validações estruturais e de grants.

- **Origem:** SPEC §§5 RF-001/RF-004/RF-005/RF-016/RF-017; PLAN D-02/D-03 e contratos §4.1.
- **Dependência:** nenhuma tarefa técnica anterior; primeira tarefa oficial.
- **Arquivos autorizados:** `impl/src/RickCraft/review_protocol.py` (criar); `impl/tests/test_review_protocol.py` (criar); `specs/SPEC-0000000002-protocolo-revisao-tecnica/status.md` (evidência IMPLEMENT futura).
- **Trabalho:** definir `ReviewRequest`, `ReviewScope`, `AuthorizationGrant`, `RequestedEffect` e erros de input mínimos; validar objetivo, escopos/IDs, dependências, allowlist/exclusions, valores ausentes/duplicados/contraditórios e grants. REVIEW é obrigatório para avaliar; grant ausente nunca autoriza ação. Definir `language` como identificador não vazio ou `None` (default semântico pt-BR), preservado sem locale global. Não implementar renderer.
- **Testes focais:** pedidos válidos/inválidos; duplicidades e fronteiras; REVIEW ausente; grant de mudança/persistência ausente ou presente; externalidade marcada como não suportada; `language=None` conserva o default e idioma explícito permanece input/metadado.
- **Regressão:** somente os testes focais adicionados e os já criados na mesma unidade.
- **Evidência mínima de COMPLETE:** modelos e validações verificáveis; testes focais passam; pedido sem grants não concede capacidade; nenhuma escrita, rede, subprocesso, Git ou persistência ocorre.
- **Exclusões:** renderer, modelos de autoridade/evidência/dimensão, pipeline, persistência, alteração de artefatos e execução de especialistas.

### TASK-002 — Contexto de autoridade e precedência explícita

**Objetivo único:** representar e validar autoridade, competência, escopo e relações de precedência formalmente autorizadas.

- **Origem:** SPEC RF-010/RF-011/RF-013; PLAN D-04 e §4.2.
- **Dependência:** TASK-001, para escopos e validação compartilhada do módulo.
- **Arquivos autorizados:** `impl/src/RickCraft/review_protocol.py`; `impl/tests/test_review_protocol.py`; `status.md` em IMPLEMENT.
- **Trabalho:** definir `AuthorityContext`, `AuthorityReference` e `AuthorizedPrecedence`; verificar referências, owner/competência e escopos aplicáveis. Ausência de autoridade permanece desconhecida. Precedência só é aplicada com relação, direção, fonte autorizadora, decisão referenciada e escopo explícitos. Nunca inferir por data, especificidade, nome, tipo de Agent ou conveniência.
- **Testes focais:** autoridade completa e ausente; competência/escopo inválidos; precedência autorizada e limitada ao escopo; conflito sem precedência sem vencedor ou owner inventado; não promoção de executor/auditor/Agent.
- **Regressão:** TASK-001.
- **Evidência mínima de COMPLETE:** testes demonstram que autoridade desconhecida não é preenchida e que somente precedência válida e aplicável é reconhecida.
- **Exclusões:** integração com `gap_handling`, leitura de Policies/Registries pelo runtime, autenticação criptográfica e decisão especializada.

### TASK-003 — Evidências e verification claims

**Objetivo único:** representar proveniência de evidências e claims verificáveis sem duplicar o contrato da SPEC-0000000001.

- **Origem:** SPEC RF-002/RF-009/RF-010; PLAN D-06 e §4.4.
- **Dependência:** TASK-002, para referências de autoridade quando necessárias.
- **Arquivos autorizados:** `impl/src/RickCraft/review_protocol.py`; `impl/tests/test_review_protocol.py`; `status.md` em IMPLEMENT.
- **Trabalho:** definir `EvidenceReference` e `VerificationClaim`, distinguindo `DIRECT_OBSERVATION`, `PERSISTED_EVIDENCE`, `REPORTED`, `INFERENCE` e estados `EXECUTED_OBSERVED`, `HISTORICAL_IDENTIFIED`, `NOT_EXECUTED`, `UNAVAILABLE`, `INCONCLUSIVE`. Validar alvo, versão, referência e compatibilidade. Claim positivo exige evidência adequada; histórico não prova execução atual. Reutilizar `provenance.py` quando a operação autorizada exigir, sem criar algoritmo/taxonomia concorrente.
- **Testes focais:** quatro classes distintas; claims sem referência; alvo/versão incompatível; relato/inferência não promovidos a observação; histórico, não executado, indisponível e inconclusivo permanecem distintos.
- **Regressão:** TASKS-001–002.
- **Evidência mínima de COMPLETE:** todo estado positivo é ligado a referência compatível; estados históricos ou ausentes nunca viram verificação executada.
- **Exclusões:** observação automática de fontes, rede, publicação e pesquisa.

### TASK-004 — Dimensões técnicas e avaliações especializadas

**Objetivo único:** modelar aplicabilidade de dimensões e avaliações recebidas sem apropriar autoridade especializada.

- **Origem:** SPEC RF-012/RF-018; PLAN D-05 e §4.3.
- **Dependência:** TASK-003, para referências de evidência.
- **Arquivos autorizados:** `impl/src/RickCraft/review_protocol.py`; `impl/tests/test_review_protocol.py`; `status.md` em IMPLEMENT.
- **Trabalho:** definir `TechnicalDimension`, `DimensionAssessment` e `SpecialistAssessment`; suportar `NOT_APPLICABLE`, `NOT_ASSESSED_INSUFFICIENT_EVIDENCE`, `SPECIALIST_REQUIRED`, `SPECIALIST_ASSESSMENT_RECEIVED`, `CORE_SCOPE_ASSESSMENT`, além de `CONSULTATIVE` e `AUTHORITATIVE`. Uma decisão autoritativa exige owner, competência, referência e escopo válidos. Core pode avaliar pertinência/encaminhar lacuna, não concluir matéria reservada a specialist.
- **Testes focais:** uma e várias dimensões; não aplicável; evidência insuficiente; specialist-required; consulta não vira decisão; alegação autoritativa sem owner/competência/ref não é aceita como decisão.
- **Regressão:** TASKS-001–003.
- **Evidência mínima de COMPLETE:** testes mostram dimensões pertinentes registradas sem aplicação mecânica e fronteira de owner mantida.
- **Exclusões:** chamar Agents/especialistas, implementar Patterns/SOLID ou avaliar conteúdo fora do escopo fornecido.

### TASK-005 — Findings e conclusão limitada

**Objetivo único:** representar achados rastreáveis e conclusões limitadas ao material efetivamente examinado.

- **Origem:** SPEC RF-007/RF-008/RF-020 e CA-007/CA-008/CA-020; PLAN D-07/D-10 e parte de D-14.
- **Dependência:** TASK-004, para dimensão/owner e referências de evidência.
- **Arquivos autorizados:** `impl/src/RickCraft/review_protocol.py`; `impl/tests/test_review_protocol.py`; `status.md` em IMPLEMENT.
- **Trabalho:** definir `ReviewFinding` e `ReviewConclusion`; separar condição/fato, evidência, regra/contrato, conclusão, impacto, recomendação e decisão especializada. Conclusão deve identificar escopos, fontes, versões, evidências e claims. Findings têm ordenação estável conforme chaves definidas no PLAN. Não criar estado de aprovação universal.
- **Testes focais:** ligação rastreável de finding; fato e recomendação separados; ordenação; falta de referência limita/rejeita claim; revisão de uma classe/arquivo não declara conformidade do projeto.
- **Regressão:** TASKS-001–004.
- **Evidência mínima de COMPLETE:** conclusão positiva não excede os escopos/fontes/versões/evidências; CA-020 demonstrado por teste.
- **Exclusões:** renderer, engine de análise, decisão de owner ou mecanismo de edição.

### TASK-006 — Conflitos, lacunas e continuidade localizada

**Objetivo único:** adaptar os modelos Core aos avaliadores puros de conflito e continuidade existentes.

- **Origem:** SPEC RF-010/RF-013/RF-014 e CA-010/CA-013/CA-014; PLAN D-08/D-13 e §§5/8.
- **Dependência:** TASK-005, para findings, evidências e resultados de escopo.
- **Arquivos autorizados:** `impl/src/RickCraft/review_protocol.py`; `impl/tests/test_review_protocol.py`; `status.md` em IMPLEMENT.
- **Trabalho:** integrar somente `gap_handling.avaliar_conflito_fontes` e `avaliar_continuidade_localizada`, adaptando entradas explicitamente fornecidas. Conflito normativo sem precedência autorizada permanece não resolvido: nenhuma fonte vencedora é escolhida. `required_authority` permanece ausente/`None` quando não tiver sido validamente fornecida; autoridade competente já conhecida pode ser registrada como requisito para resolver o conflito, sem escolher uma fonte vencedora. Informação para identificar a autoridade competente pode ser registrada sem sintetizar owner ou autoridade. O conflito entre fonte normativa e workspace operacional preserva o comportamento existente de `gap_handling`: workspace não é autoridade normativa concorrente. Bloqueios propagam transitivamente; dependência não avaliada não é presumida satisfeita; independentes só continuam com todos os critérios verdadeiros. Operação de avaliação não chama persistência.
- **Testes focais:** (A) duas fontes normativas incompatíveis sem `AuthorizedPrecedence` não escolhem vencedora; (B) sem `required_authority` válida, o campo permanece ausente/`None`; (C) autoridade competente válida fornecida pode ser registrada como requisito para resolução, mas não determina fonte vencedora; (D) conflito entre fonte normativa e workspace preserva reconhecimento da referência normativa aplicável, pois workspace não possui autoridade normativa concorrente; (E) dependentes bloqueados e independentes aptos conforme `avaliar_continuidade_localizada`. Cobrir também evidência/informação insuficiente, dependência desconhecida, propagação direta/transitiva e razões localizadas.
- **Regressão:** TASKS-001–005 e `test_gap_handling.py` como regressão read-only.
- **Evidência mínima de COMPLETE:** adaptações passam sem alterar `gap_handling.py`; testes demonstram bloqueio localizado e propagação correta.
- **Exclusões:** duplicar engine, alterar módulos/testes SPEC1, publicar divergence/blocker/result, decidir autoridade ausente.

### TASK-007 — ChangeProposal e preservação comportamental

**Objetivo único:** validar autorização e evidência de propostas de mudança sem editar artefatos.

- **Origem:** SPEC RF-004/RF-008/RF-019 e CA-004/CA-008/CA-019; PLAN D-09 e §6.
- **Dependência:** TASK-006, para resultados de autorização/bloqueio e claims.
- **Arquivos autorizados:** `impl/src/RickCraft/review_protocol.py`; `impl/tests/test_review_protocol.py`; `status.md` em IMPLEMENT.
- **Trabalho:** definir `ChangeProposal` e `BehaviorAssessment` com estados `PRESERVATION_EVIDENCED`, `PRESERVATION_ASSERTED`, `NOT_VERIFIED`, `FUNCTIONAL_CHANGE_AUTHORIZED`, `FUNCTIONAL_CHANGE_UNAUTHORIZED`. Validar base/candidata, contrato, claims, allowlist/exclusions, grants e distinção estrutural/funcional. Boolean isolado `behavior_preserved=True` não prova preservação. O Core registra/valida proposta, sem executar edição.
- **Testes focais:** mudança estrutural com e sem grant; funcional sem autorização bloqueada; evidência vinculada a contrato e versões base/candidata; claim observado/histórico; boolean isolado rejeitado; alvos fora da allowlist/excluídos.
- **Regressão:** TASKS-001–006.
- **Evidência mínima de COMPLETE:** a decisão sobre preservação fica limitada aos contratos/casos com evidência concreta; nenhum artefato é modificado.
- **Exclusões:** editor, patch engine, compilador, framework ou método universal de equivalência.

### TASK-008 — Renderer e protocolo de resposta

**Objetivo único:** renderizar uma única resposta determinística nos três blocos semânticos e no idioma efetivo.

- **Origem:** SPEC RF-003/RF-006/RF-015/RF-017 e CA-003/CA-006/CA-015/CA-017; PLAN D-11, partes de D-14/D-15 e §9.
- **Dependência:** TASK-007, para todos os dados semânticos que podem compor resposta.
- **Arquivos autorizados:** `impl/src/RickCraft/review_protocol.py`; `impl/tests/test_review_protocol.py`; `status.md` em IMPLEMENT.
- **Trabalho:** definir `ReviewResponse` e `renderizar_resposta`. Preservar exatamente três blocos/chaves semânticas, na ordem Análise Crítica, Refatoração, Justificativa Arquitetural. `language=None` significa pt-BR; idioma explícito é preservado. O host fornece títulos equivalentes localizados e conteúdo no idioma pedido; Core formata/escapa Markdown, não traduz e não gera segunda resposta. Indicar não aplicabilidade sem produzir código artificial. Preservar UTF-8 e não consultar locale global.
- **Testes focais:** ordem e presença dos três blocos; N/A conciso; ausência de idioma/default pt-BR; idioma explicitamente diferente preservado nos títulos/conteúdo fornecidos; uma saída apenas; acentos e round-trip UTF-8; idioma como input determinístico.
- **Regressão:** TASKS-001–007.
- **Evidência mínima de COMPLETE:** mesma entrada e idioma geram mesma estrutura/render; idiomas diferentes podem diferir; nenhum mecanismo de tradução ou duplicação é invocado.
- **Exclusões:** tradução automática, catálogo i18n, idioma global/process locale e geração de Release.

### TASK-009 — Pipeline Core de avaliação

**Objetivo único:** integrar as capacidades puras anteriores num fluxo ordenado de avaliação, sem persistência ou efeitos.

- **Origem:** SPEC RF-001–RF-015/RF-018–RF-020; PLAN §5, D-01/D-02–D-11/D-13/D-14.
- **Dependência:** TASK-008; requer modelos e renderer disponíveis para produzir resultado integrado.
- **Arquivos autorizados:** `impl/src/RickCraft/review_protocol.py`; `impl/tests/test_review_protocol.py`; `status.md` em IMPLEMENT.
- **Trabalho:** implementar o fluxo request → validação → dimensões → evidências → assessments → autoridade/conflitos → findings/claims/change → continuidade → conclusão → resposta. A avaliação segue determinismo e bloqueios localizados definidos no PLAN. A etapa não persiste nem executa mudança.
- **Testes focais:** cenários compostos de review-only, evidência insuficiente, decisão especializada, conflito, continuidade, claims não executados e proposta autorizada; interactions entre componentes; ausência de persistência/edição.
- **Regressão:** TASKS-001–008.
- **Evidência mínima de COMPLETE:** casos integrados produzem resultado limitado/bloqueado ou resposta positiva apenas quando dados e grants satisfazem todos os contratos; pipeline não produz efeitos.
- **Exclusões:** SPEC1 persistence, workspace, publicação, subprocessos e externalidade.

### TASK-010 — Persistência optativa e continuidade SPEC1

**Objetivo único:** conectar persistência e continuidade opcionais às APIs existentes da SPEC-0000000001.

- **Origem:** SPEC RF-016/RF-021 e CA-016/CA-021; PLAN D-12 e §7.
- **Dependência:** TASK-009, para persistir somente revisão/resultado já avaliado.
- **Arquivos autorizados:** `impl/src/RickCraft/review_protocol.py`; `impl/tests/test_review_protocol.py`; `status.md` em IMPLEMENT. Módulos SPEC1 são dependências read-only, não alvos de alteração.
- **Trabalho:** sem necessidade, intent ou `LOCAL_PERSISTENCE` explícito, nenhum workspace/documento. Quando necessário e autorizado, consumir lifecycle, publisher, recovery e search (search somente se solicitado), provenance e catálogo/formato transitivamente. Usar apenas tipos `analysis`, `evidence`, `divergence`, `blocker`, `result` e relações existentes quando semanticamente aplicáveis. Fixture temporária controlada; preservar append-only e histórico.
- **Testes focais:** zero persistência sem intent/grant; publicação/recuperação em fixture com APIs reais aprovadas; provenance e relation existentes; busca somente sob pedido; falha não gera receipt fictício nem store alternativo; nenhum Debug real tocado.
- **Regressão:** TASKS-001–009; testes de SPEC1 relevantes executados sem alteração dos arquivos existentes.
- **Evidência mínima de COMPLETE:** prova opt-in/opt-out e round-trip em fixture; hashes e IDs confirmados; nenhum novo tipo/schema/API SPEC1 ou documento operacional real.
- **Exclusões:** alteração de qualquer módulo SPEC1, criação de catálogo/format/schema/recovery paralelo e acesso ao Debug real. Se uma dependência só puder ser atendida por alteração SPEC1, bloquear e retornar ao PLAN.

### TASK-011 — Fronteiras negativas e review-only

**Objetivo único:** consolidar provas de ausência de efeitos implícitos e de enforcement negativo das capacidades já implementadas.

- **Origem:** SPEC RF-004/RF-005/RF-016 e CA-004/CA-005/CA-016; PLAN D-03/D-15 e §§5/10.
- **Dependência:** TASK-010, para incluir a fronteira de persistência implementada e provar ausência de persistência implícita.
- **Arquivos autorizados:** `impl/src/RickCraft/review_protocol.py` somente se defeito dentro da tarefa for identificado; `impl/tests/test_review_protocol.py`; `status.md` em IMPLEMENT.
- **Trabalho:** completar spies/guards que provam zero rede, subprocesso de produto, Git, upload, sync, Release, edição e persistência sem autorização/intenção. External action é não suportada mesmo que mencionada no pedido. Ausência de qualquer grant continua negando ação. Evitar repetir casos focais já suficientes; acrescentar apenas cobertura de fronteira integrada.
- **Testes focais:** snapshots antes/depois em review-only; spies sem chamadas; externalidade rejeitada sem tentativa; recommendation não materializada; persistência sem grant não toca publisher/workspace.
- **Regressão:** TASKS-001–010.
- **Evidência mínima de COMPLETE:** provas negativas por observação/spies, sem introduzir mecanismo externo para testá-lo; nenhum arquivo fora dos alvos autorizados mudou.
- **Exclusões:** implementar integração de rede/Git/upload, ações externas ou novo sistema de autorização.

### TASK-012 — Determinismo e regressões estruturais

**Objetivo único:** validar integralmente as regras D-14 e estabilidade estrutural dos contratos anteriores.

- **Origem:** PLAN D-14/§9; SPEC RF-001–RF-021 e CA-001–CA-021 para regressão estrutural.
- **Dependência:** TASK-011, para testar a unidade completa até as fronteiras negativas.
- **Arquivos autorizados:** `impl/src/RickCraft/review_protocol.py` somente para defeitos demonstrados de D-14; `impl/tests/test_review_protocol.py`; `status.md` em IMPLEMENT.
- **Trabalho:** canonizar e verificar ordenação de scopes, dimensões, findings, evidence, claims e blockers; ties, relações/dependências e idioma como input; clock injetado sem influenciar ordenação lógica. Entradas semanticamente iguais no mesmo idioma produzem estrutura/render equivalentes; idiomas distintos não precisam gerar bytes iguais.
- **Testes focais:** permutações equivalentes; chaves de desempate e empate; ordenação de cada coleção; dependências; dois idiomas; clock fixo/variável com ordem lógica idêntica; regressão dos modelos e pipeline.
- **Regressão:** TASKS-001–011.
- **Evidência mínima de COMPLETE:** D-14 coberta por teste explícito para cada coleção e tie pertinente; nenhuma dependência de ordem acidental de dict/set/filesystem ou locale global.
- **Exclusões:** performance benchmark, paralelismo, IDs aleatórios como ordenação e alterações de runtime SPEC1.

### TASK-013 — Integração final e cobertura de SPEC/PLAN

**Objetivo único:** validar a unidade completa e produzir matriz final de evidências antes de eventual CONVERGE.

- **Origem:** SPEC RF-001–RF-021, CA-001–CA-021 e cenários A–O; PLAN D-01–D-15, §§10–17.
- **Dependência:** TASK-012; última tarefa da sequência.
- **Arquivos autorizados:** `impl/src/RickCraft/review_protocol.py` e `impl/tests/test_review_protocol.py` somente para defeitos internos comprovados durante a tarefa; `status.md` em IMPLEMENT. Não criar artefatos fora dos alvos comuns.
- **Trabalho:** confirmar cobertura inversa/positiva de todos RF, CA, D e cenários; executar testes focais, integração SPEC1 em fixture, regressões negativas e suíte RickCraft completa; registrar hashes, resultados reais, limitações ambientais e evidências. Não declarar gate CONVERGE nem inventar PASS sem evidência.
- **Verificações:** `python -B -m unittest -v impl.tests.test_review_protocol`; regressões materialmente pertinentes; `python -B -m unittest discover -s impl/tests -v`; revisão das matrizes TASKS→D/RF/CA e inversas RF/CA/D→TASK; `git diff --check`.
- **Evidência mínima de COMPLETE:** todos os testes executados passam (SKIP somente se limitação ambiental real e não bloqueante, justificada); cada RF/CA/D/cenário liga-se a teste ou evidência; hashes correspondem às versões avaliadas; nenhum efeito externo/Debug/Release ocorreu.
- **Exclusões:** executar CONVERGE, declarar CONVERGED, gerar Release ou fazer push. Achado não corrigível dentro dos alvos retorna ao proprietário apropriado.

## 4. Matriz TASK → decisões, requisitos e critérios

| TASK | Decisões PLAN | RF cobertos | CA cobertos |
|---|---|---|---|
| TASK-001 | D-02, D-03, parte D-11/D-15 | RF-001, RF-004, RF-005, RF-016, RF-017 | CA-001, CA-004, CA-005, partes CA-016/017 |
| TASK-002 | D-04 | RF-010, RF-011, RF-013 | CA-010, CA-011, CA-013 |
| TASK-003 | D-06 | RF-002, RF-009, RF-010 | CA-002, CA-009, CA-010 |
| TASK-004 | D-05 | RF-012, RF-018 | CA-012, CA-018 |
| TASK-005 | D-07, D-10, parte D-14 | RF-007, RF-008, RF-020 | CA-007, CA-008, CA-020 |
| TASK-006 | D-08, D-13 | RF-010, RF-013, RF-014 | CA-010, CA-013, CA-014 |
| TASK-007 | D-09 | RF-004, RF-008, RF-019 | CA-004, CA-008, CA-019 |
| TASK-008 | D-11, partes D-14/D-15 | RF-003, RF-006, RF-015, RF-017 | CA-003, CA-006, CA-015, CA-017 |
| TASK-009 | D-01, D-02–D-11, D-13/D-14 | RF-001–RF-015, RF-018–RF-020 | CA-001–CA-015, CA-018–CA-020 |
| TASK-010 | D-12 | RF-016, RF-021 | CA-016, CA-021 |
| TASK-011 | D-03, D-15 | RF-004, RF-005, RF-016 | CA-004, CA-005, CA-016 |
| TASK-012 | D-14 | RF-001–RF-021, regressão | CA-001–CA-021, regressão |
| TASK-013 | D-01–D-15, integração | RF-001–RF-021 | CA-001–CA-021 |

## 5. Verificação inversa de cobertura

| Item | TASK(s) que o cobrem |
|---|---|
| RF-001 | TASK-001, TASK-009, TASK-012, TASK-013 |
| RF-002 | TASK-003, TASK-009, TASK-012, TASK-013 |
| RF-003 | TASK-008, TASK-009, TASK-012, TASK-013 |
| RF-004 | TASK-001, TASK-007, TASK-011, TASK-012, TASK-013 |
| RF-005 | TASK-001, TASK-011, TASK-012, TASK-013 |
| RF-006 | TASK-008, TASK-009, TASK-012, TASK-013 |
| RF-007 | TASK-005, TASK-009, TASK-012, TASK-013 |
| RF-008 | TASK-005, TASK-007, TASK-009, TASK-012, TASK-013 |
| RF-009 | TASK-003, TASK-009, TASK-012, TASK-013 |
| RF-010 | TASK-002, TASK-003, TASK-006, TASK-009, TASK-012, TASK-013 |
| RF-011 | TASK-002, TASK-006, TASK-009, TASK-012, TASK-013 |
| RF-012 | TASK-004, TASK-009, TASK-012, TASK-013 |
| RF-013 | TASK-002, TASK-006, TASK-009, TASK-012, TASK-013 |
| RF-014 | TASK-006, TASK-009, TASK-012, TASK-013 |
| RF-015 | TASK-008, TASK-009, TASK-012, TASK-013 |
| RF-016 | TASK-001, TASK-010, TASK-011, TASK-012, TASK-013 |
| RF-017 | TASK-001, TASK-008, TASK-012, TASK-013 |
| RF-018 | TASK-004, TASK-009, TASK-012, TASK-013 |
| RF-019 | TASK-007, TASK-009, TASK-012, TASK-013 |
| RF-020 | TASK-005, TASK-009, TASK-012, TASK-013 |
| RF-021 | TASK-010, TASK-012, TASK-013 |
| CA-001 | TASK-001, TASK-009, TASK-012, TASK-013 |
| CA-002 | TASK-003, TASK-009, TASK-012, TASK-013 |
| CA-003 | TASK-008, TASK-009, TASK-013 |
| CA-004 | TASK-001, TASK-007, TASK-011, TASK-013 |
| CA-005 | TASK-001, TASK-011, TASK-013 |
| CA-006 | TASK-008, TASK-013 |
| CA-007 | TASK-005, TASK-009, TASK-013 |
| CA-008 | TASK-005, TASK-007, TASK-013 |
| CA-009 | TASK-003, TASK-009, TASK-013 |
| CA-010 | TASK-002, TASK-003, TASK-006, TASK-013 |
| CA-011 | TASK-002, TASK-013 |
| CA-012 | TASK-004, TASK-013 |
| CA-013 | TASK-002, TASK-006, TASK-013 |
| CA-014 | TASK-006, TASK-009, TASK-013 |
| CA-015 | TASK-008, TASK-013 |
| CA-016 | TASK-001, TASK-010, TASK-011, TASK-013 |
| CA-017 | TASK-001, TASK-008, TASK-012, TASK-013 |
| CA-018 | TASK-004, TASK-013 |
| CA-019 | TASK-007, TASK-013 |
| CA-020 | TASK-005, TASK-013 |
| CA-021 | TASK-010, TASK-013 |
| D-01 | TASK-009, TASK-013 |
| D-02 | TASK-001, TASK-009, TASK-013 |
| D-03 | TASK-001, TASK-011, TASK-013 |
| D-04 | TASK-002, TASK-006, TASK-013 |
| D-05 | TASK-004, TASK-009, TASK-013 |
| D-06 | TASK-003, TASK-009, TASK-013 |
| D-07 | TASK-005, TASK-009, TASK-013 |
| D-08 | TASK-006, TASK-009, TASK-013 |
| D-09 | TASK-007, TASK-009, TASK-013 |
| D-10 | TASK-005, TASK-009, TASK-013 |
| D-11 | TASK-008, TASK-009, TASK-013 |
| D-12 | TASK-010, TASK-013 |
| D-13 | TASK-006, TASK-009, TASK-013 |
| D-14 | TASK-005, TASK-008, TASK-012, TASK-013 |
| D-15 | TASK-008, TASK-011, TASK-013 |

## 6. Matriz cenário SPEC → TASK

| Cenário | TASK(s) e evidência planejada |
|---|---|
| A — pedido somente de revisão | TASK-001/TASK-009/TASK-011: REVIEW sem grants de mudança; pipeline não edita nem persiste. |
| B — evidência insuficiente | TASK-003/TASK-009: relato fica distinto de observação; conclusão limitada. |
| C — refatoração autorizada | TASK-007/TASK-009: proposta structural é validada e Core não aplica alteração; mudança funcional sem grant bloqueia. |
| D — decisão especializada | TASK-004/TASK-009: consulta não vira decisão e autoridade do owner é preservada. |
| E — conflito normativo | TASK-002/TASK-006: sem precedência autorizada não há vencedor nem autoridade inferida. |
| F — bloqueio transitivo | TASK-006/TASK-009: cadeia bloqueada propaga; escopo independente só continua apto/autorizado. |
| G — validação alegada | TASK-003/TASK-009: claim histórico/relatado sem observação não é executado. |
| H — pedido amplo com limites | TASK-001/TASK-007: allowlist/exclusions restringem proposta e revisão. |
| I — recomendação sem necessidade | TASK-008/TASK-011: seção não aplicável sem código ou alteração artificial. |
| J — continuidade | TASK-010: persistência opt-in, APIs SPEC1 e fixture temporária. |
| K — Release/ação externa sugerida | TASK-001/TASK-011: externalidade rejeitada, sem chamada. |
| L — Pattern sem necessidade concreta | TASK-004/TASK-005/TASK-013: pertinência e finding registram ausência de fundamento; não promover complexidade. |
| M — risco comportamental | TASK-007: preservação exige contrato/base/candidata/evidência; mudança funcional sem grant bloqueia. |
| N — revisão parcial | TASK-001/TASK-005: allowlist e conclusão permanecem limitadas ao arquivo/classe fornecido. |
| O — teste não executado | TASK-003/TASK-009: claim NOT_EXECUTED não sustenta conclusão positiva. |

## 7. Dependências e ordem oficial

| TASK | Dependência técnica/oficial | Razão |
|---|---|---|
| TASK-001 | nenhuma | Define base de request e grants. |
| TASK-002 | TASK-001 | Usa escopo e fronteiras comuns. |
| TASK-003 | TASK-002 | Evidência pode referenciar autoridade/fonte. |
| TASK-004 | TASK-003 | Assessment referencia evidência. |
| TASK-005 | TASK-004 | Finding/conclusão consome dimensões e evidências. |
| TASK-006 | TASK-005 | Bloqueios e conflitos integram resultados/escopos. |
| TASK-007 | TASK-006 | Proposta usa grants, claims e estado de continuidade. |
| TASK-008 | TASK-007 | Resposta renderiza resultados e assessments já modelados. |
| TASK-009 | TASK-008 | Integra componentes e produz resposta sem persistir. |
| TASK-010 | TASK-009 | Persistência registra resultado integrado já avaliado. |
| TASK-011 | TASK-010 | Verifica fronteiras negativas incluindo persistência opt-in. |
| TASK-012 | TASK-011 | Verifica determinismo e regressão da unidade completa. |
| TASK-013 | TASK-012 | Fecha integração, cobertura, hashes e full suite. |

A ordem de execução é linear por controle SDD TASK-by-TASK; as dependências refletem também a composição do módulo e das verificações, sem declarar paralelismo autorizado.

## 8. Fora de escopo destas TASKS

- Não criar Orchestrator, Agent, editor/patch engine, UI/CLI, banco, índice, cache, framework ou dependência externa.
- Não ler Policies/Registries/SPEC/status automaticamente do runtime; o host fornece referências/contexto.
- Não alterar `impl/src/RickCraft/*.py` ou `impl/tests/test_*.py` existentes, especialmente módulos SPEC1 e `gap_handling.py`.
- Não criar formatos/tipos/tokens de documento, catálogo ou relações adicionais à SPEC1.
- Não publicar documentos no Debug real, criar ANL/DOC operacional fora de fixtures, produzir Release ou executar CONVERGE.
- Não iniciar ANALYZE nesta execução de decomposição.

## 9. Prontidão para ANALYZE futuro

Este documento define origem, dependências, arquivos autorizados, verificações e evidência mínima por tarefa. A matriz direta TASK→D/RF/CA e as matrizes inversas acima permitem verificar cobertura, tarefas sem origem e itens sem tarefa. ANALYZE futuro ainda deve avaliar consistência, suficiência, ambiguidade, contradições, fronteiras de autoridade e adequação dos testes; esta decomposição não declara esse gate PASS.

## 10. Estado

TASKS COMPLETE significa somente que a decomposição está completa e pronta para revisão. TASKS não autoriza automaticamente ANALYZE, IMPLEMENT, Release ou qualquer outra etapa.
