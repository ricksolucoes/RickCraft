# PLAN — SPEC-0000000002 — Protocolo de Revisão Técnica, Escopo e Resposta

## Identificação e versões de entrada

- **SPEC:** `SPEC-0000000002` — COMPLETE e aprovada pelo responsável pelo projeto.
- **SHA-256 aprovado de spec.md:** `F43B54ACBC1C6D7F4A2B1F9647E9FCBB7D46EE788C5D35E875CC5C0BC04AEFAC`.
- **Referência adicional do blob aprovado:** `97f1a98c4f3b25bf52c0fa71c29502a39e9ca556`.
- **Grupo/Decision Owner conceitual:** 000 — RickCraft Core Specialist.
- **Data:** 2026-10-11.
- **Estado ao iniciar:** PLAN `IN_PROGRESS`.
- **Escopo:** decidir como satisfazer RF-001–RF-021 e CA-001–CA-021. Este PLAN não cria TASKS, não executa ANALYZE, não implementa e não autoriza estágio posterior.
- **Runtime alvo:** continuidade com Python 3.12 ou compatível e biblioteca padrão, conforme o runtime da SPEC-0000000001; essa escolha vale para esta unidade, não universaliza o runtime RickCraft.

## 1. Direção arquitetural

Implementar um protocolo Core determinístico, local e sem efeitos colaterais implícitos, concentrado em um módulo novo `impl/src/RickCraft/review_protocol.py`. O módulo valida um pedido tipado, agrega contexto de autoridade, evidências e avaliações especializadas explicitamente fornecidos, classifica escopos e findings, valida claims/propostas contra autorização, forma uma conclusão limitada e renderiza a resposta em três seções.

O caminho principal é uma avaliação em memória: não descobre arquivos, não lê Policies/Registries/SPECs por conta própria, não edita artefatos, não inicia processos, não chama rede e não publica. A integração host fornece entradas e executa separadamente uma alteração já autorizada. Continuidade persistente é uma operação optativa e explícita sobre as APIs da SPEC-0000000001.

O desenho não terá ReviewManager, ReviewService, ReviewEngine, ReviewFactory, ReviewRepository, ReviewFacade ou ReviewOrchestrator. Um arquivo com modelos imutáveis, validação, funções puras de avaliação/consolidação e um renderer simples é suficiente para a primeira versão. Se a implementação demonstrar necessidade de divisão, TASKS não poderá criá-la sem retorno a PLAN.

## 2. Fronteira de capacidades e componentes

| Componente | Responsabilidade | Fronteira |
|---|---|---|
| Host RickCraft | Fornecer pedido, grant de autorização, contexto de autoridade, referências/versões de artefatos, evidências observadas e avaliações especializadas recebidas. | Não pode omitir dados e esperar que Core os descubra; os valores não são confiáveis apenas por estarem presentes. |
| `review_protocol.py` (novo) | Validar estruturas, decidir aplicabilidade/estado, aplicar gates de autorização, compor findings/conclusão e renderizar resposta determinística. | Funções sem I/O; não altera arquivos, chama ferramentas externas, executa especialistas ou cria workflows. |
| `gap_handling.py` (existente) | Reutilizar `avaliar_conflito_fontes` para classificação de conflito fornecido e `avaliar_continuidade_localizada` para requisitos booleanos explícitos por escopo. | Não duplicar avaliadores de conflito/propagação. Sua API atual não autentica authority context nem implementa precedência fornecida; o protocolo valida esses inputs antes de chamar a função e mantém autoridade separada. Funções `registrar_*` só são usadas quando a persistência do blocker/divergence/result for autorizada. |
| APIs SPEC-0000000001 (existentes) | Persistência opcional via `document_publisher.publicar_documento`; continuidade/leitura por `document_recovery`; busca opcional por `document_search`; identidade/proveniência por `analysis_lifecycle` e `provenance`; layout e formato por `document_catalog`/`document_format`. | Reutilizar os contratos publicados. Nenhum módulo da SPEC-0000000001 será modificado por esta unidade. |
| `test_review_protocol.py` (novo) | Testar modelos, funções puras, falhas conservadoras, renderização, integração fixture SPEC1 e limites de efeitos. | Não publicar no Debug real nem produzir Release. |

### 2.1 Módulos existentes consultados

- **Reuso direto:** `gap_handling.py` para conflito/continuidade; `document_publisher.py` para publicação optativa; `document_recovery.py` para recuperar IDs explícitos; `document_search.py` para pesquisa quando solicitada; `provenance.py` para entradas locais/versões; `analysis_lifecycle.py` para criar/retomar análise somente quando a operação de persistência exigir identidade.
- **Reuso transitivo por APIs aprovadas:** `document_catalog.py` e `document_format.py` são usados pelo publicador; `workspace_resolver.py`, `workspace_probe.py` e `rickcraft_root.py` são chamados pelas APIs de persistência/host conforme os contratos delas.
- **Não reutilizados diretamente pelo fluxo puro:** funções de persistência de `gap_handling.py`, pesquisa e lifecycle não são chamadas por avaliação padrão; fazê-lo criaria efeito ou custo desnecessário. Não há classes de request/evidence/finding/response nesses módulos, por isso o modelo de revisão pertence ao novo módulo.
- **Nenhum módulo existente precisa mudar.** Se uma incompatibilidade material aparecer, parar e registrar bloqueio antes de propor alteração aos módulos converged.

### 2.2 Compatibilidade de importação

O runtime atual importa módulos diretamente a partir de `impl/src/RickCraft` e usa biblioteca padrão. O novo módulo seguirá esse padrão, sem package metadata ou dependência nova. Runtime não importa `policies/`, `registries/`, `specs/`, `status.md`, testes ou anexos de desenvolvimento; a aplicação host carrega/verifica as fontes normativas e passa referências e decisões explicitamente.

## 3. Decisões técnicas

| ID | Problema | Alternativas relevantes | Decisão | Justificativa / RF-CA | Impacto e risco | Autoridade |
|---|---|---|---|---|---|---|
| D-01 | Como manter Core pequeno sem virar orquestrador? | Vários serviços/Agents; módulo puro coeso; acoplar a gap handling. | Um novo `review_protocol.py` com value objects imutáveis e funções explícitas de validar, avaliar, consolidar e renderizar; sem agente, manager, service, factory ou orquestrador. | Coesão e teste sem IO; atende RF-001–RF-010, RF-018–RF-020 e CA relacionados. | Um módulo pode crescer; se coesão se perder, nova decisão de PLAN será necessária, não subdivisão automática. | Core, sob SPEC aprovada. |
| D-02 | Como descrever objetivo, escopo, versões e autorização sem workflow genérico? | Dicionário livre; dezenas de flags; request dataclass validada. | `ReviewRequest` imutável contendo objetivo, lista ordenada de `Scope`, artefatos autorizados/excluídos, resultado solicitado, grants, indicação de efeitos pedidos, idioma e referências de versão/fontes conhecidas. IDs de escopo são únicos e dependências explícitas. Campos requeridos não têm defaults permissivos; texto vazio, duplicado ou contraditório é input inválido. | Modelo finito e validável; atende RF-001/004/010/014/017 e CA-001/004/010/014/017. | Um contrato coeso é mais verboso que dict; validação estrita evita inferência de escopo. | Core. |
| D-03 | Como separar review, refatoração, função, persistência e externalidade? | Booleanos truthy; uma autorização geral; grants enumerados separados. | `AuthorizationGrant` enumerado: `REVIEW`, `STRUCTURAL_CHANGE`, `FUNCTIONAL_CHANGE`, `LOCAL_PERSISTENCE`. O request deve conter `REVIEW` para avaliar; alteração estrutural exige grant próprio, alteração funcional exige também `FUNCTIONAL_CHANGE`; persistência exige `LOCAL_PERSISTENCE`. Ausência significa negado. `EXTERNAL_ACTION` é uma classe explicitamente reconhecida como fora do protocolo e sempre rejeitada, mesmo se o host a marcar autorizada. Não há grant por recomendação. | Não confunde revisão/alteração nem persiste por implicação; atende RF-004/005/016 e CA-004/005/016. | Host precisa construir grants inequívocos. Externalidade não é capacidade ativável por configuração. | Responsável concede grants; Core aplica a fronteira. |
| D-04 | Como evitar que conteúdo operacional substitua autoridade? | Runtime carrega Policies/Registries; host fornece contexto tipado; inferir pelo nome/data. | `AuthorityContext` é entrada explícita do host, com fontes identificadas, autoridade/owner e referências a decisões existentes. Precedência só é utilizável por um `AuthorizedPrecedence` explícito que identifique relação, escopo, fonte que autoriza e authority reference. Ausência, fonte sem autoridade demonstrada ou relação fora do escopo não resolve o conflito. Runtime não ranqueia por data, especificidade ou nome. | Preserva POL-0000000001 e RF-011–RF-013, RF-018; suporta CA-011–013/018. | O Core valida consistência estrutural e referência fornecida, mas não autentica assinatura/identidade do responsável nem carrega registry; confiança na proveniência do contexto é responsabilidade do host e deve constar na limitação. | Autoridade vigente e responsável pelo projeto; conteúdo do Core não cria owner. |
| D-05 | Como distinguir dimensões Core e especializadas? | Algoritmos Core para cada prática; disparo de Agents; avaliação explícita recebida. | `TechnicalDimension` identifica Patterns, SOLID, Interface Architecture, Clean Code, Delphi/Object Pascal, objective norms e Quality/Audit quando pertinente. `DimensionAssessment` usa estados `NOT_APPLICABLE`, `NOT_ASSESSED_INSUFFICIENT_EVIDENCE`, `SPECIALIST_REQUIRED`, `SPECIALIST_ASSESSMENT_RECEIVED` ou `CORE_SCOPE_ASSESSMENT`. Resultado especializado inclui owner/authority reference, escopo, evidências, conclusão e marcador `CONSULTATIVE`/`AUTHORITATIVE`. Só estado authoritative com fonte de competência explícita conta como decisão do owner; consulta nunca é promovida. Core pode marcar pertinência e encaminhar lacuna, não emitir conclusão substantiva especializada. | Contrato capability-boundary sem agente; atende RF-012/018 e CA-012/018. | Integridade do owner vem do contexto do host. Se insuficiente, status fica specialist-required/blocked. | Owners listados em `registries/spec-groups.md`; Core apenas agrega. |
| D-06 | Como representar evidência sem confundir relato e fato? | Texto livre único; copiar input; referência tipada com proveniência. | `EvidenceReference` imutável distingue `DIRECT_OBSERVATION`, `PERSISTED_EVIDENCE`, `REPORTED` e `INFERENCE`; inclui origem, locator/ref, versão/hash quando aplicável, limitação e verificabilidade. Um `VerificationClaim` identifica afirmação, status (`EXECUTED_OBSERVED`, `HISTORICAL_IDENTIFIED`, `NOT_EXECUTED`, `UNAVAILABLE`, `INCONCLUSIVE`), versão do alvo e referências de evidência. Claim positivo exige pelo menos uma referência compatível; ausência de erro não cria status positivo. Para local file/workspace/versioned source usar registros de `provenance.py`, sem recalcular outra taxonomia/hash. | Atende RF-002/009/010 e CA-002/009/010. | Evidência relatada ou inferida continua distinguível e nunca vira observação por coerção. | Core valida; origem da evidência é quem a fornece. |
| D-07 | Como estruturar findings rastreáveis sem issue tracker? | Texto livre; object mínimo; framework genérico. | `ReviewFinding` contém condição observada, evidências/origens, regra/contrato, conclusão técnica, impacto/risco, recomendação opcional, escopo, dimensão e autoridade/owner da conclusão quando pertinente. Fato, conclusão, recomendação e decisão são campos separados. Sem ID aleatório; ordenação determinística por escopo, dimensão canônica, referência normativa e chave textual estável. | Atende RF-007/008 e CA-003/007/008. | IDs determinísticos não são identidade documental; persistência atribui `DOC-UUIDv4` pelo publicador. | Core; conclusões especializadas cabem ao owner. |
| D-08 | Como reaproveitar tratamento de lacunas e dependências? | Reimplementar regras; reaproveitar `gap_handling`; persistir sempre. | Adaptar inputs explícitos aos `SourceReference`, `DivergenceCase`, `ScopeRequest` e avaliadores puros já existentes em `gap_handling.py`. Usar `avaliar_conflito_fontes` para classificação de incompatibilidade que não foi resolvida por precedência formal fornecida; usar `avaliar_continuidade_localizada` para autorização/informação/evidência/autoridade/conflito e propagação direta/transitiva. Nunca chamar registrar/publisher durante avaliação pura. | Reutiliza comportamento testado; atende RF-010/013/014 e CA-010/013/014. | `gap_handling` presume relação normativa sobre workspace conforme SPEC1. O adaptador só usa essa regra quando as categorias de fonte e contrato SPEC1 se aplicam; conflito entre normativas permanece sem vencedor até relação autorizada. | Contrato converged SPEC1 e seus owners. |
| D-09 | Como validar proposta e preservar comportamento sem editor universal? | Editor/patch engine Core; apenas autorização textual; envelope de mudança + evidência. | O protocolo não modifica artefatos. Recebe `ChangeProposal` do host/executor contendo kind (structural/functional), artefatos-alvo, versão-base, versão candidata, referência do diff/artefato e verificações disponíveis. Valida alvos contra allowlist/exclusions e grants. Para refatoração sem grant funcional, qualquer alteração declarada funcional é rejeitada/bloqueada. `BehaviorAssessment` distingue `PRESERVATION_EVIDENCED`, `PRESERVATION_ASSERTED`, `NOT_VERIFIED`, `FUNCTIONAL_CHANGE_AUTHORIZED`, `FUNCTIONAL_CHANGE_UNAUTHORIZED`; não há booleano `behavior_preserved`. Estado positivo requer claims verificáveis ligados a versão-base e candidata, critérios/contratos e saída de verificação observada; alegação isolada não satisfaz. | Não reduz CA-019 e não cria patch engine; atende RF-004/008/019 e CA-004/008/019. | Equivalência semântica geral não pode ser provada por Core de forma universal. Resultado limita-se aos contratos/casos verificados; sem evidência suficiente, não declara preservação e bloqueia a conclusão positiva daquele change. | Solicitante autoriza; host/executor altera; Core só valida autorização/evidência. |
| D-10 | Como limitar conclusões e validation claims? | Um PASS geral; conclusion com base explícita; texto sem estrutura. | `ReviewConclusion` referencia escopos, artefatos/versões, fontes e evidências/verificações que a sustentam, estado `LIMITED`, `BLOCKED` ou `NO_FINDING_IN_SCOPE`. Não existe estado “projeto aprovado” no protocolo. Claims seguem D-06. Conclusão sem referências ou que exceda os conjuntos examinados é inválida; classe única não pode concluir sobre projeto inteiro. | Atende RF-002/009/020 e CA-002/009/020. | Pode não caber no formato conciso; renderer pode resumir, mas não ampliar escopo. | Core e evidência fonte. |
| D-11 | Como conservar três seções e saída testável em qualquer idioma solicitado? | String livre; template rígido cheio de campos; resposta semântica + renderer mínimo. | `ReviewResponse` mantém três blocos semânticos ordenados. `renderizar_resposta` preserva `ReviewResponse.language`, copiado do `ReviewRequest.language`; `None` significa pt-BR. O host fornece os títulos localizados e o conteúdo textual no idioma solicitado; o Core preserva esses textos sem tradução, sem criar uma segunda variante. Os títulos correspondem semanticamente, nesta ordem, a Análise Crítica, Refatoração e Justificativa Arquitetural. A seção de Refatoração registra mudança autorizada/executada ou recomendação não executada/não aplicável; a seção arquitetural é concisa e não aplicável quando não houver impacto material. Não criar código para preencher seção. Ordenar findings/dimensões/claims antes do render. | Atende RF-003/006/015/017 e CA-003/006/015/017. | O Core não verifica semanticamente a língua natural fornecida pelo host; registra essa fronteira como limitação e não declara tradução. | Core preserva idioma solicitado; host fornece conteúdo localizado. |
| D-12 | Quando persistir/reutilizar histórico? | Persistência automática; armazenamento paralelo; opt-in sobre SPEC1. | Avaliação pura nunca persiste. Um `PersistenceIntent` opt-in requer `LOCAL_PERSISTENCE`, motivo de continuidade/rastreabilidade/reuso e root + analysis identity fornecidos/derivados pelas APIs aprovadas. Publicar uma revisão principal como `analysis` através de `publicar_documento`; registrar verificações individualizadas como `evidence` apenas quando necessário e autorizado. Usar `inputs` e relações existentes; ao retomar, recuperar por IDs explícitos; pesquisa só quando explicitamente solicitada. Não criar tipo/relação, formato, catálogo, publicação ou recovery alternativos. | Atende RF-016/021 e CA-016/021; reusa SPEC1 sem duplicação. | Persistence indisponível limita persistência, mas não falsifica sucesso; relatório em memória pode sobreviver se o pedido permitir. | SPEC1 aprovada para contratos operacionais. |
| D-13 | Como manter erros conservadores sem taxonomia excessiva? | Exceção universal; numerosos subtipos; poucos erros de input e outcomes de avaliação. | Erros de input/configuração estrutural levantam `ReviewInputError` (subtipos locais somente para request, authority/evidence shape se diagnóstico exigir). Falta de autorização, owner, evidência ou precedência é outcome com blockers localizados, não exceção genérica. Mudança não autorizada é rejected/blocking outcome. Falha de persistência retorna/propaga erro operacional com causa preservada e `persisted=False`; jamais receipt fictício. Escopo inválido bloqueia a revisão inteira; lacuna localizada bloqueia escopo e dependentes por `gap_handling`; escopo independente elegível continua. | Atende RF-001/010/014/016 e CA-001/010/014/016. | O renderer precisa explicar erro sem chamar estado bloqueado de PASS. | Core/SPEC1 no limite de persistência. |
| D-14 | Como tornar processo e resultados determinísticos? | Ordem de dict/set/filesystem; ordenação canônica; IDs aleatórios para findings. | Tuplas no modelo; validar unicidade; canonicalizar referências sem alterar identidade fornecida; ordenar dimensões por sequência enum definida, findings por `(scope_id, dimension_rank, source_ref, condition.casefold(), condition)`, evidências por `(kind, source_ref, version_ref, locator)`, bloqueios por `(scope_id, reason_code, dependency_id)` e claims por `(target_ref, version_ref, status_rank, claim)`. Relações preservam ordem declarada somente quando for semântica do pedido; listas de findings/conclusões são canonicalizadas. Timestamp vem de clock explicitamente injetável e não define identidade/ordem lógica. | Atende determinismo e CA-009/014; testável com igualdade de estruturas e render. | Conflitos de chaves iguais com conteúdo distinto são input ambíguo e bloqueiam ou rejeitam; não dependem de ordem de filesystem. | Core. |
| D-15 | Como manter efeitos, idioma e Release fora da avaliação? | Capacidade externa configurável; APIs locais sem integração; integração silenciosa. | Artefatos de governança, desenvolvimento e Debug desta unidade (SPEC, PLAN, TASKS, status, testes, documentação interna e evidência de desenvolvimento) permanecem em pt-BR conforme Policy 3. A resposta operacional preserva o idioma explicitamente solicitado em `ReviewRequest.language`; `None` usa pt-BR. O host fornece conteúdo e títulos localizados; o Core não traduz nem gera segunda versão automaticamente. Conteúdo distribuível de Release é futuro, fora desta SPEC/PLAN, e só poderá seguir a Policy 3 após autorização explícita. O módulo não importa subprocess, socket, urllib, Git, SDKs, network/upload/sync ou Release; persistência local é somente a chamada optativa SPEC1. `.workspace`, Policies, Registries, specs e testes ficam fora de payload futuro conforme Policy 3. | Atende RF-016/017 e CA-016/017. | A verificação linguística do conteúdo do host não é automática; a fronteira não presume que texto localizado foi traduzido corretamente. Integração futura de externalidade requer mudança autorizada. | POL-0000000003; host fornece idioma/conteúdo; responsável por Release futuro autoriza essa etapa. |

## 4. Contratos de dados planejados

Os nomes abaixo são decisões deste PLAN para tornar a arquitetura executável; nenhum cria schema documental ou taxonomia normativa. Implementação futura pode usar dataclasses/enums stdlib sem alterar a semântica.

### 4.1 Pedido e autorização

- `ReviewRequest`: `objective`, `scopes`, `authorized_artifacts`, `excluded_artifacts`, `expected_outcome`, `authorization_grants`, `requested_effects`, `language`, `source_versions`. `language` é `None` ou um identificador de idioma não vazio fornecido pelo solicitante, preservado sem locale global; `None` significa pt-BR. O host fornece os textos da resposta e os títulos localizados dos três blocos nesse idioma; o Core valida presença/ordem sem alegar validar ou traduzir língua natural. Identificador e textos da resposta são entradas determinísticas.
- `ReviewScope`: ID estável local, descrição factual, `depends_on` explícito e conjunto de artefatos abrangidos. IDs únicos; dependência desconhecida não é satisfeita por suposição.
- `AuthorizationGrant`: `REVIEW`, `STRUCTURAL_CHANGE`, `FUNCTIONAL_CHANGE`, `LOCAL_PERSISTENCE`.
- `RequestedEffect`: `LOCAL_PERSISTENCE`, `EXTERNALITY`. Se `EXTERNALITY` estiver presente, protocolo não executa e retorna input/escopo não suportado com causa clara; não é possível converter uma autorização textual em capacidade externa.
- `ChangeProposal`: somente registro de proposta/alteração produzida pelo host, com artefatos/versões e tipo; não carrega patch executável pelo Core.

Uma proposta estrutural exige REVIEW + STRUCTURAL_CHANGE. Para mudança funcional exige REVIEW + STRUCTURAL_CHANGE + FUNCTIONAL_CHANGE ou uma autorização funcional delimitada equivalente; alteração de comportamento sem grant funcional é rejeitada. O Core verifica todos os alvos dentro da allowlist e fora das exclusões. Ausência de grant sempre nega a operação correspondente.

### 4.2 Autoridade

`AuthorityContext` contém `AuthorityReference` explícita para fonte, owner, competência/fonte que comprova competência e escopos em que se aplica. `AuthorizedPrecedence` declara par ordenado de fontes, direção da precedência, autoridade que a autorizou, referência da decisão e escopo aplicável.

O protocolo não define quem é competente a partir do nome do arquivo, número da versão, data, grupo genérico ou texto do workspace. Se a evidência da autoridade estiver ausente, o owner não é conhecido. Uma referência fornecida pelo host é rastreada como input; seu mero formato não equivale a verificação criptográfica. Sem relação autorizada, incompatibilidade material fica unresolved; somente escopos dependentes ficam bloqueados e são enviados à função de continuidade SPEC1.

### 4.3 Dimensões especializadas

Enums iniciais correspondem aos domínios relevantes: `PATTERNS`, `SOLID`, `INTERFACE_ARCHITECTURE`, `CLEAN_CODE`, `DELPHI_OBJECT_PASCAL`, `OBJECTIVE_NORMATIVE_RULES`, `QUALITY_AUDIT`. Estados explícitos: `NOT_APPLICABLE`, `NOT_ASSESSED_INSUFFICIENT_EVIDENCE`, `SPECIALIST_REQUIRED`, `SPECIALIST_ASSESSMENT_RECEIVED`, `CORE_SCOPE_ASSESSMENT`.

Uma `SpecialistAssessment` contém dimensão, scope, conclusão, evidências, owner e referência de competência; seu caráter `CONSULTATIVE` ou `AUTHORITATIVE` é obrigatório. Se `AUTHORITATIVE` não tiver owner/competência/referência correspondente, é inválida como decisão e resulta em blocker specialist-required. Core não chama especialista; o host entrega avaliação recebida.

### 4.4 Evidence, claim, finding e conclusão
- `ReviewResponse`: idioma efetivo (`language`, igual ao pedido ou `None` para pt-BR) e exatamente três blocos semânticos ordenados. Cada bloco carrega a chave semântica (`CRITICAL_ANALYSIS`, `REFACTORING`, `ARCHITECTURAL_JUSTIFICATION`), título localizado e corpo textual fornecidos pelo host. O renderer apenas escapa/formata Markdown de modo determinístico e preserva os textos; não traduz nem produz resposta secundária.

- `EvidenceReference`: classe de proveniência (`DIRECT_OBSERVATION`, `PERSISTED_EVIDENCE`, `REPORTED`, `INFERENCE`), origem, referência/locator, alvo/versão, digest quando aplicável, limitação e verificabilidade.
- `VerificationClaim`: afirmação, alvo/versão, estado (`EXECUTED_OBSERVED`, `HISTORICAL_IDENTIFIED`, `NOT_EXECUTED`, `UNAVAILABLE`, `INCONCLUSIVE`) e um ou mais EvidenceReference. Claim positivo exige referência(s) compatíveis; resultado ausente não significa PASS.
- `ReviewFinding`: scope, dimensão, condição observada, referência(s) de evidência, regra/contrato, conclusão técnica, impacto, recomendação opcional, owner/authority se a conclusão exigir.
- `BehaviorAssessment`: estados citados em D-09 e referências de base/candidata/contrato/claims; nenhum campo bool isolado prova preservação.
- `ReviewConclusion`: status delimitado, scopes, fontes, versões, evidências e claims que a sustentam. O estado não pode representar aprovação universal do projeto.

## 5. Fluxo de avaliação

Fluxo determinístico do Core, sem execução de trabalho:

1. Validar estrutura do `ReviewRequest`; confirmar `REVIEW` explícito, grants, escopos únicos, dependências e artefatos. Input estrutural inválido falha antes de qualquer chamada a persistência.
2. Validar que efeitos requeridos cabem nesta unidade. Externalidade não é executável; persistência exige grant explícito e intenção separada.
3. Fixar o universo examinado com artefatos e versões fornecidos. Itens excluídos nunca entram no alcance por inferência.
4. Classificar cada dimensão quanto a aplicabilidade com base no escopo/evidência fornecidos. Registrar explicitamente dimensões não aplicáveis e não avaliadas.
5. Validar referências de evidência e seus estados; não promover `REPORTED`/`INFERENCE` para observação executada. Usar provenance SPEC1 para observação/comparação local já produzida, sem reler arbitrariamente origens.
6. Incorporar avaliações especializadas recebidas, preservando owner e caráter consultivo/autoritativo. Não invocar Agents.
7. Confrontar fontes com regras de autoridade/precedência explicitamente fornecidas. Sem precedência autorizada, marcar conflito e montar DivergenceCase; usar avaliador SPEC1 e preservar required_authority não fornecida como `None`.
8. Avaliar findings/claims e ChangeProposal. Validar grants, allowlist/exclusões, tipo de mudança e evidência de preservação; alteração física não ocorre no módulo.
9. Montar `ScopeRequest` explícitos para `avaliar_continuidade_localizada`, incluindo dependências, autorização e suficiência; propagar bloqueios transitivos; não marcar unknown dependency como satisfeita.
10. Compor uma conclusão que cite escopos, fontes, versões, evidências e verificações disponíveis. Uma classe/arquivo não eleva escopo a projeto.
11. Ordenar dimensões, findings, blockers e claims conforme D-14; renderizar as seções obrigatórias em ordem fixa.
12. Somente se persistência foi necessária, pedida e autorizada, publicar a resposta/registro por SPEC1 após avaliação. Falha ao persistir não altera o resultado para persisted nem impede comunicação não persistida quando o host a permitir.

## 6. Preservação comportamental e validação de mudança

Core não tem editor nem entende equivalência semântica de todo domínio. O host/executor apresenta `ChangeProposal` com referência às versões base/candidata, artefatos afetados e claims de verificação disponíveis. A política de grants impede reconhecer funcional change como refatoração sem autorização.

`PRESERVATION_EVIDENCED` só pode ser produzido se houver: contrato/comportamento requerido identificado; versão base e candidata identificadas; escopo dos casos/contratos verificados; claim com status EXECUTED_OBSERVED e evidência localizável de resultado para ambas as versões ou comparação explicitamente identificada; nenhuma lacuna material conhecida entre o escopo validado e a conclusão alegada. Claims com mesmo target/status/assertion associados a versões distintas permanecem distintos por `version_ref`. Referência histórica identificada não é execução atual. Testes sem resultados ou flag booleana desacompanhada de evidence não bastam. Evidência não cobre comportamento além dos casos declarados; conclusão é restrita a eles.

Se apenas houver afirmação, estado `PRESERVATION_ASSERTED`; se faltar execução/evidência, `NOT_VERIFIED`; se houve funcional change autorizado, registrar como tal sem chamá-lo de preservação; funcional change sem autorização é `FUNCTIONAL_CHANGE_UNAUTHORIZED`, bloqueia esse escopo. O PLAN não prescreve framework, compilador, método formal, suite ou equivalência. Critério futuro é a ausência de claim positiva sem referência verificável suficiente, não prova matemática de equivalência universal.

## 7. Persistência e continuidade pela SPEC-0000000001

### 7.1 Decisão de quando persistir

Persistência não é default. Avaliação pode terminar em resposta efêmera. Persistir só quando objetivo de continuidade/rastreabilidade/reuso requer histórico e o pedido dá grant `LOCAL_PERSISTENCE`; o host fornece a análise/root explicitamente, usando `analysis_lifecycle` para criar/retomar quando ainda não há analysis_id, e `document_publisher` para publicação. O protocolo não cria `.workspace` alternativo nem escreve status SDD.

### 7.2 Mapeamento no catálogo existente

- Documento principal de revisão: `analysis`, cujo propósito cobre exame, interpretação, dependências e ligação a evidências.
- Documento separado de evidência: `evidence`, somente quando houver resultado observável que precise de registro próprio. Não criar um por finding automaticamente.
- Lacuna/conflito/bloco operacional: reutilizar `registrar_divergencia`, `registrar_blocker` ou `registrar_resultado` de `gap_handling.py` quando persistência local estiver autorizada; não usar `decision` para recomendação/proposta.
- Relações: reutilizar tokens aprovados, mais tipicamente `supports`, `related_to` ou `complements`, com analysis_id para alvo cross-analysis conforme contrato SPEC1. Não inventar token.
- Entradas persistidas documentais usam referências/proveniência permitidas da SPEC1. Não copiar fontes completas, prompts ou segredos por default.

Conteúdo SDD normativo permanece fora do workspace; documento operacional não aprova PLAN/TASKS nem vira fonte de precedência. Não mudar schema, catálogo ou APIs SPEC1.

### 7.3 Recuperação

Continuidade começa com `analysis_id`/`document_id` explicitamente recuperável. Usar `recuperar_documento`/`recuperar_analise` e, se request pedir consulta, `pesquisar_documentos`. Inputs históricos podem ser reavaliados apenas por mecanismos SPEC1 e resultados apresentados; recuperação não altera documento original. Não varrer automaticamente o workspace para descobrir autoridade ou ampliar escopo.

## 8. Falhas e resultado parcial

| Condição | Resposta planejada |
|---|---|
| Tipos/IDs/escopos duplicados ou formato estrutural inválido | `ReviewInputError`; rejeitar request antes de avaliação/efeitos. |
| Grant REVIEW ausente | Negar execução da revisão; não inferir do contexto/conversa. |
| Grant de mudança/persistência ausente | Preservar análise, recusar aquela ação e declarar resultado não executado. |
| Ação externa pedida | Rejeitar como não suportada; nenhuma tentativa de subprocesso, rede, Git, upload, sync ou Release. |
| Autoridade/owner não fornecido ou competência não provada | Mark authority unknown; bloquear somente findings/decisions dependentes; produzir requerimento de informação sem preencher required_authority. |
| Fonte incompatível sem precedência explicitamente autorizada | Divergence + blocker via evaluator SPEC1; dependentes bloqueados, nenhuma vencedora inferida. |
| Evidência faltante, histórica ou não verificável | Conclusão limitada/claim inconclusive; bloquear somente as decisões que exigem evidência atual. |
| ChangeProposal fora da allowlist/excluída | Rejeitar change; não executar edição. |
| Funcional change não autorizado | Bloquear proposal e dependentes; refatoração não passa como conforme. |
| Dependência direta/transitiva bloqueada ou desconhecida | Usar `avaliar_continuidade_localizada`; dependentes não continuáveis; independentes continuam se todos os critérios explícitos forem satisfeitos. |
| Persistência SPEC1 indisponível/falha | Preservar cause; `persisted=false`, nenhum receipt fictício; comunicar limite. Não tentar store alternativo. |
| Falha interna inesperada | Propagar erro com contexto; não converter em ausência, sucesso ou UNAVAILABLE sem causa apropriada. |

Input inválido que torna todo o request ambíguo bloqueia revisão inteira. Escopo/owner/evidência localizada gera resultado parcial; só parte afetada e dependências são bloqueadas. Escopo independente pode avançar sem executar qualquer trabalho físico pelo Core.

## 9. Determinismo e privacidade

- `tuple`/enums finitos no runtime; rejeitar chaves de escopo repetidas, relações de dependência contraditórias e dados de tipo desconhecido.
- Ordenação estável: dimensões por ordem canônica definida em D-05; scopes por scope ID; findings por `(scope_id, dimension_rank, normative_reference, condition.casefold(), condition)`; evidence refs pela chave D-14 `(kind, source_ref, version_ref, locator)`; claims pela chave D-14 `(target_ref, version_ref, status_rank, claim)`; blockers por `(scope_id, reason_code, dependency_id)`. Strings não são normalizadas de modo a mudar o valor original usado como evidência.
- Renderização mantém sempre os três blocos semânticos na ordem Análise Crítica -> Refatoração -> Justificativa Arquitetural; os títulos exibidos podem ser equivalentes localizados fornecidos pelo host. O texto é preservado no idioma de `ReviewRequest.language`, ou pt-BR quando `None`. Mesma resposta + mesmo idioma produz estrutura/render determinísticos; idioma integra a entrada e não se consulta locale global. Nenhuma segunda variante traduzida é produzida. Ordem de sources fornecida pelo request só é preservada se semanticamente indicada; conjunto sem ordem é ordenado antes de render.
- Clock, se necessário para registro, é entrada injetável e UTC; não participa de identidade, validade, precedence ou ordenação de findings.
- Armazenar apenas referências/digests e resumos necessários. Minimizar conteúdo sensível. Nada é enviado a serviços externos.

## 10. Estratégia de testes e evidência

Implementação futura usa `unittest` da biblioteca padrão, fixtures temporárias e doubles sobre entradas externas. Testes não acessam `.workspace` real nem criam documento operacional Debug. Testes de persistência usam RickCraftRoot fixture e APIs reais SPEC1 aprovadas; invariantes sem efeitos usam mocks/spies de subprocess, `os.system`, socket, urllib, Git wrappers e publisher.

Grupos automatizáveis requeridos:

| Grupo | Prova planejada |
|---|---|
| A. Escopo/autorização | Campo ausente/duplicado, exclusão, review-only, grants explícitos, combinações incompletas/contraditórias. |
| B. Evidência/claims | Quatro classes de evidência; claim positive sem ref rejeitado; historical vs executed; target/version incompatível; indisponível/inconclusivo. |
| C. Findings | Separar fato, conclusão, recomendação, decisão; campos rastreáveis e ordenação. |
| D. Autoridade especializada | Owner conhecido/desconhecido; consulta não vira autoridade; competência/ref faltante bloqueia. |
| E. Dimensões | Uma/múltiplas pertinentes; N/A; insuficiência; specialist-required; resultado autorizado/consultivo. |
| F. Conflito/lacuna/continuidade | Sem precedence; precedence explicitamente fornecida; gaps SPEC1; dependência desconhecida/direta/transitiva; independente. |
| G. Review-only | Snapshot dos arquivos inalterado; publisher/editor e APIs externas sem chamadas. |
| H. Refatoração autorizada | Proposta somente dentro da allowlist, grant structural ausente/presente, alteração funcional separada. |
| I. Comportamento | Cobertura base/candidata com evidence, historical only, boolean flag isolada, mudança funcional permitida/proibida. |
| J. Anti-overengineering | Pattern/abstração sem problema/benefício não é promovido; alternativa simples preservada. |
| K. Resposta | Três seções em ordem e indicação concisa não aplicável; nenhum código artificial. |
| L. Conclusão limitada | Uma classe/arquivo não gera conclusão sobre sistema; metadados de escopo/fontes/versões/evidence presentes. |
| M. Persistência SPEC1 | Opt-in com grant: `analysis`/`evidence`, publicação append-only, recuperação por ID, proveniência, relações e sem persistência quando dispensável. |
| N. Externalidade | Spies provam zero processo, rede, Git, upload, sync e Release na avaliação/runtime. |
| O. Idioma | `language=None` produz conteúdo/títulos pt-BR fornecidos pelo host; idioma explicitamente solicitado é preservado, com títulos localizados dos três blocos e conteúdo no mesmo idioma; uma única resposta; acentos/UTF-8 preservados; sem locale global ou tradução automática. |
| P. Determinismo | Permutações semanticamente equivalentes produzem ordering/render equivalente; estabilidade dos ties e dependencies. |

Além dos grupos, cada CA tem estratégia individual na matriz da seção 12; cada cenário A–O é ligado a casos futuros na seção 13. Fixtures não são evidência de comportamento em runtime real; hashes e versões serão registrados em IMPLEMENT/CONVERGE quando esses estágios forem autorizados.

## 11. Compatibilidade e impacto na SPEC-0000000001

| Área | Plano de uso | Arquivos anteriores |
|---|---|---|
| Request, authority, dimensions, findings, conclusion, renderer | Novo `review_protocol.py` | Nenhuma alteração prevista. |
| Lacunas e propagação | `gap_handling.avaliar_conflito_fontes` + `avaliar_continuidade_localizada`; registros existentes somente no modo persistido autorizado | `gap_handling.py` consumido, sem mudança contratual. |
| Proveniência | `provenance.py` ao chamar observar/verificar permitido | Sem duplicar SHA-256/inputs. |
| Persistência | `analysis_lifecycle.py`, `document_publisher.py`; `document_format.py` valida; catálogo existente | Nenhuma mudança de schema ou módulo planejada. |
| Recuperação/pesquisa | `document_recovery.py` e `document_search.py` com IDs explícitos | Somente leitura; histórico imutável. |
| Root/resolução/sonda | APIs existentes chamadas transitivamente pelo publisher/recovery | D-02 executa somente nas operações SPEC1 que as exigem. |

Se durante IMPLEMENT for inevitável mudar qualquer módulo da SPEC1, parar antes da alteração. Registrar módulo, contrato, causa, efeito sobre evidências já converged e estratégia de revalidação; requer revisão do PLAN/autoridade conforme POL-0000000002. Não corrigir silenciosamente.

## 12. Matriz RF → decisão e seção do PLAN

| RF | Decisão/seção que o satisfaz | Limite principal |
|---|---|---|
| RF-001 | D-02, D-14; §§4.1, 5, 8 | Pedido e fronteiras explícitas; inválido bloqueia. |
| RF-002 | D-06, D-10; §§4.4, 5, 9 | Classe e origem da evidência visíveis. |
| RF-003 | D-01, D-05, D-07; §§2, 5 | Avaliar contrato/evidência antes de recomendação. |
| RF-004 | D-03, D-09; §§4.1, 5, 6 | Review e alteração em grants distintos; Core não edita. |
| RF-005 | D-03, D-11; §§5, 7 | Review-only não executa nem preenche seção artificial. |
| RF-006 | D-11; §§4.4, 9 | Três blocos Markdown semânticos em ordem fixa. |
| RF-007 | D-07; §4.4 | Finding liga fato/evidence/contrato/conclusão/impacto/recomendação. |
| RF-008 | D-07, D-09; §§4.4, 6 | Mudança liga-se ao objetivo e comportamento previsto. |
| RF-009 | D-06, D-10; §§4.4, 10 | Claim positivo requer resultado/ref identificáveis. |
| RF-010 | D-04, D-06, D-13; §§4.2, 8 | Sem preencher dado ausente; limita/bloqueia. |
| RF-011 | D-04, D-08; §§4.2, 5 | Autoridade e precedência vêm do contexto explícito host. |
| RF-012 | D-05; §§2.1, 4.3 | Core agrega estados; owners decidem conteúdo especializado. |
| RF-013 | D-04, D-08; §§4.2, 5, 8 | Conflito sem precedência mantém escopo dependente bloqueado. |
| RF-014 | D-08, D-13; §§5, 8 | Reusa propagação transitiva e unknown dependencies SPEC1. |
| RF-015 | D-01, D-11; §§1, 5, 10 | Nenhum componente/abstração sem necessidade demonstrada. |
| RF-016 | D-03, D-12, D-15; §§4.1, 7, 9 | Persistência local opt-in; externalidade fora do produto. |
| RF-017 | D-02, D-11, D-15; §4.1, 9 | Artefatos internos em pt-BR; resposta no idioma solicitado ou pt-BR default; sem tradução/duplicação automática; Release futuro segue Policy 3 somente após autorização. |
| RF-018 | D-05; §§4.3, 10 | Considerar aplicabilidade sem aplicar mecanicamente ou tomar owner. |
| RF-019 | D-09; §6 | Sem functional grant, preservar contrato e exigir evidência; não define mecanismo. |
| RF-020 | D-10; §§4.4, 5 | Conclusão carrega scope/source/version/evidence/checks. |
| RF-021 | D-12; §7 | Persistência e continuidade seguem SPEC1 sem duplicação. |

## 13. Matriz CA → testes/evidência futura

| CA | Evidência/testes planejados |
|---|---|
| CA-001 | `test_request_scope_bounds_review`: request unitário sobre arquivo lista escopo examinado e nega artefato não listado. |
| CA-002 | `test_evidence_kinds_remain_distinct`: direct/persisted/reported/inference permanecem estados distintos. |
| CA-003 | `test_analysis_and_contract_precede_recommendation`: finding/render conserva condição, regra e impacto antes da recomendação. |
| CA-004 | `test_review_only_never_applies_change`: snapshot de fixture e spies de escrita/editor/publisher permanecem iguais/sem chamada. |
| CA-005 | `test_unrequested_refactor_is_not_materialized`: nenhuma proposta/código gerado quando ausente grant/necessidade. |
| CA-006 | `test_response_sections_order_and_not_applicable_text`: renderer produz exatamente três seções na ordem aprovada. |
| CA-007 | `test_finding_links_fact_evidence_rule_and_owner`: campos e refs podem ser seguidos sem decisão de owner apropriada. |
| CA-008 | `test_change_justification_references_goal_and_impact`: proposta material sem relação/razão é rejeitada ou fica limitada. |
| CA-009 | `test_claim_requires_matching_version_evidence`: claim positivo sem execução ou versão/evidence compatível é rejeitado; histórico identificado permanece histórico. |
| CA-010 | `test_missing_authority_or_evidence_limits_result`: lacuna gera estado explícito, nunca placeholder/sucesso. |
| CA-011 | `test_runtime_does_not_promote_workspace_or_agent_text`: fontes operacionais não substituem contexto de autoridade; owner/gate não inferidos. |
| CA-012 | `test_specialist_consultation_is_not_decision`: consultative fica consultative e assessment autoritativa sem authority ref bloqueia. |
| CA-013 | `test_unordered_normative_conflict_stays_unresolved`: duas fontes incompatíveis sem AuthorizedPrecedence geram DivergenceCase/blocker, sem referência vencedora/owner inventado. |
| CA-014 | `test_transitive_block_and_independent_scope`: A bloqueado → B/C dependentes bloqueados, B independente autorizado permite continuação; unknown dependency não satisfeita. |
| CA-015 | `test_abstraction_without_need_is_not_promoted`: alternativa Pattern/abstração sem problema/benefício não passa; não há pattern selector. |
| CA-016 | `test_no_external_call_or_implicit_persistence`: ausência de external grant/intent resulta zero rede/Git/upload/sync/Release; publisher não chamado sem persistence opt-in. |
| CA-017 | `test_response_language_requested_and_default`: sem idioma, host fornece conteúdo/títulos pt-BR e render preserva pt-BR; com idioma explicitamente diferente (ex.: `en`), host fornece conteúdo e títulos localizados e render preserva esse idioma nos três blocos; cada chamada produz uma única resposta, sem variante duplicada; round-trip UTF-8 preserva acentos; arquivos internos da unidade são verificados em pt-BR. O teste valida preservação dos textos fornecidos, não tradução automática nem correção linguística genérica. |
| CA-018 | `test_dimension_applicability_states_and_owner_boundary`: uma/várias dimensões, N/A, insuficiente, specialist-required, authoritative/consultative; Core não promove consulta. |
| CA-019 | `test_behavior_preservation_requires_concrete_evidence`: change structural sem functional grant passa apenas com contract + base/candidate + claim verificável; boolean alone e historical-only não passam; functional unauthorized bloqueia. |
| CA-020 | `test_single_class_conclusion_is_scope_limited`: entrada uma classe Delphi não permite texto/estado “projeto conforme”; conclusão referencia só classe/versão/evidence. |
| CA-021 | `test_optional_continuity_uses_spec1`: sem necessidade/grant nenhum workspace/doc; com grant fixture usa `analysis` por publisher, recupera por ID, mantém provenance, histórico e ausência de external calls. |

## 14. Matriz cenário SPEC → validação futura

| Cenário | Validação planejada |
|---|---|
| A — somente review | CA-004: request REVIEW sem change; snapshots e mocks provam ausência de escrita/publicação. |
| B — evidência insuficiente | CA-002/010: relato sem observação resulta limite/inconclusivo. |
| C — refatoração autorizada | CA-008/019: structural grant aceito, funcional change sem grant recusado, apenas host executa. |
| D — owner especializado | CA-012/018: avaliação Core pode encaminhar; consultiva não vira decisão. |
| E — conflito sem precedence | CA-013: duas fontes normativas incompatíveis sem relation resultam blocker e não escolhem vencedora. |
| F — bloqueio transitivo | CA-014: cadeia A←B←C bloqueada; scope independente continua se apto. |
| G — validation alegada | CA-009: resultado sem arquivo/version/evidence identificável não é declarado executado. |
| H — pedido amplo com limites | CA-001/004: artefato fora da allowlist permanece fora mesmo se citado como recomendação. |
| I — sem mudança necessária | CA-005/006: renderer informa refatoração não aplicável sem gerar código. |
| J — continuidade | CA-021: opt-in fixture recupera histórico com SPEC1. |
| K — Release/externalidade sugerida | CA-016: mention não ativa externalidade, mocks sem chamadas. |
| L — abstração sem necessidade | CA-015: Pattern sem problema/benefício não é promovido. |
| M — risco de comportamento | CA-019: sem evidência base/candidata, não declara preservação; sem functional grant bloqueia. |
| N — arquivo/classe parcial | CA-020: conclusão de um arquivo permanece limitada ao arquivo e versões. |
| O — teste não executado | CA-009: claim status NOT_EXECUTED; conclusão não é positiva sobre o comportamento. |

## 15. Riscos e mitigação

| Risco | Mitigação do PLAN |
|---|---|
| Core assume decisão especializada | D-05 separa applicability/assessment e exige owner/competência para autoridade. |
| Protocolo vira Orchestrator | Funções puras de agregação; host injeta entradas; nenhum Agent ou chamada de especialista. |
| Excesso de abstrações | Um módulo de runtime e um de teste; value objects somente para contratos que precisam validação. |
| Duplicar `gap_handling` | Adaptadores usam seus avaliadores puros; sem segunda engine. |
| Duplicar persistência SPEC1 | Todas as escritas/leitura passam pelas APIs atuais e tipos existentes. |
| Claims positivos sem evidência | Claim requer ref + alvo/version + estado observável; no caso contrário resultado limitado. |
| Escopo excessivamente amplo | allowlist/exclusions do request validada antes de proposta; conclusion prende-se aos mesmos refs. |
| Autorização permissiva | enum grants ausentes = denied; no truthy/default; efeitos externos não suportados. |
| Output rígido demais | Modelo semântico mínimo, renderer Markdown simples e campos não aplicáveis concisos. |
| Output livre demais | Claims, findings e seções estruturados, com teste de ordering e referencias. |
| Runtime depende de artefatos de desenvolvimento | AuthorityContext recebido do host; nenhum carregamento de Policies/Registries/SPECs no runtime. |
| Release futuro inclui state/docs | fora de runtime, inventory/exclusion Policy3 e tests futuros; nenhum release produzido agora. |
| Comportamento universal alegado com evidência parcial | CA-019 exige base, candidata, contrato e resultados; claims limitados a casos observados. |
| Fonte host mal declarada como autoridade | `AuthorityReference` carrega competência/fonte; contexto sem ref cria blocker; limitação da verificação host aparece na resposta. |
| Persistence failure parece sucesso | Receipt só vem da API SPEC1 confirmada; causa preservada e persisted false. |

## 16. Dependências, decisões pendentes e prontidão

- **Decisões arquiteturais deste PLAN:** D-01–D-15 acima.
- **Dependências:** SPEC-0000000001 converged e suas APIs/document contracts; owners e authority fornecidos pelo host segundo governança vigente; runtime Python 3.12+ com stdlib.
- **Decisão pendente bloqueante:** nenhuma para esta versão do PLAN. Persistência é optativa e usa APIs aprovadas; falta de autoridade/evidência é outcome localizado em runtime, não indecisão arquitetural.
- **Validação humana futura:** decisão de owner especializado ou autorização funcional pertence à autoridade respectiva, não a uma execução automatizada Core. Isso não cria validação humana para testes mecanicamente verificáveis.
- **Risco/limite:** sem host que forneça versões/authority/evidence, REVIEW pode produzir apenas resultado limitado e não pode alegar aprovação positiva.

## 17. Estado do estágio

Este PLAN conclui decisões suficientes para decomposição em TASKS, mas está apenas pronto para revisão. PLAN COMPLETE não significa aprovação do PLAN nem autoriza TASKS. Este documento não executa testes, ANALYZE ou IMPLEMENT, não altera runtime, não cria workspace e não produz Release. Após revisão/aprovação explícita separada, TASKS poderá decompor D-01–D-15 e as matrizes desta unidade.
