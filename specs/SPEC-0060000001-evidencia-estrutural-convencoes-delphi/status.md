# Status da unidade SDD

## Identificação

- **SPEC:** `SPEC-0060000001`
- **Título:** Evidência Estrutural e Convenções Delphi/Object Pascal
- **Grupo:** `006` — Engenharia Delphi/Object Pascal
- **Decision Owner conceitual:** Delphi Engineering Specialist
- **Caminho:** `specs/SPEC-0060000001-evidencia-estrutural-convencoes-delphi/`
- **Data de alocação:** 2026-10-12
- **Última atualização:** 2026-10-12

## Estado atual

- **Etapa atual:** SPEC
- **SPEC:** COMPLETE — aguardando revisão externa
- **PLAN:** NOT_STARTED
- **TASKS:** NOT_STARTED
- **ANALYZE:** NOT_STARTED
- **IMPLEMENT:** NOT_STARTED
- **CONVERGE:** NOT_STARTED
- **Último gate válido:** nenhum
- **Release:** NÃO AUTORIZADO

## Baseline e autorização

- **Baseline publicada confirmada:** `cb19efc246a13412f493c294ce319b4bfd06a56e`.
- A árvore estava limpa antes desta execução.
- ID `SPEC-0060000001` alocado no Registry de Specifications para o grupo vigente `006`, primeira sequência `0000001`, em 2026-10-12.
- Esta execução está autorizada exclusivamente para a fase SPEC. Nenhuma etapa posterior foi iniciada ou autorizada.

## Dependências Core verificadas

- SPEC-0000000001: SPEC, PLAN, TASKS COMPLETE; ANALYZE PASS; IMPLEMENT COMPLETE; CONVERGE CONVERGED. Último gate válido: `CONVERGE-2026-10-11-SPEC-0000000001-02`. A clarificação cronológica e sua correção documental final foram consideradas; CONVERGE-01 e INVALIDATED são históricos.
- SPEC-0000000002: CONVERGE-2026-10-12-SPEC-0000000002-01 = CONVERGED; seu status publicado não registra invalidação posterior.
- SPEC2 é a dependência de protocolo transversal. SPEC1 é dependência somente quando persistência operacional for necessária; esta SPEC não duplica seus contratos.

## Fontes internas lidas

- `README_PTBr.md`, integralmente, incluindo convenções Delphi, Toxicity Metrics, exemplos de interfaces/`New`/`[weak]`, postura de revisão, protocolo de resposta e escopo dos padrões.
- `registries/spec-groups.md`, integralmente, com atenção ao grupo 006, owners, auditoria não exaustiva das famílias do README e fronteiras entre domínios.
- `registries/specifications.md`, integralmente; não havia alocação anterior para grupo 006.
- Policies vigentes POL-0000000001, POL-0000000002, POL-0000000003 e POL-0000000004.
- SPEC-0000000001 e status corrente para dependência de persistência e estado de convergência.
- SPEC-0000000002 e status corrente para autoridade, evidência, SpecialistAssessment, findings e protocolo transversal.

## Technical References

REF-0000000001, REF-0000000002 e REF-0000000003 foram considerados não materiais para esta elaboração. Nenhum PDF foi aberto e nenhum conteúdo externo foi consultado. A fonte funcional desta SPEC são as regras internas vigentes e seu Registry de ownership.

## Resultado da fase SPEC

Foi criada a Specification funcional read-only para observações rastreáveis Delphi/Object Pascal, verificações objetivas e encaminhamento de interpretações/decisões ao owner competente. A revisão interna conferiu limites de autoridade, rastreabilidade das famílias de regras Delphi identificadas, critérios verificáveis, compatibilidade conceitual com SPEC2 e ausência de decisões de implementação.

SPEC fica `COMPLETE — aguardando revisão externa`. PLAN, TASKS, ANALYZE, IMPLEMENT e CONVERGE permanecem `NOT_STARTED`. Nenhum teste, gate, código ou Release foi executado ou criado.


## Correção da SPEC após revisão externa — 2026-10-12

A correção partiu da baseline publicada `a166626a331b33e16e14b7f177025e841a2abe0c`; Registry, SPEC e status correspondiam às identidades confirmadas antes da edição. A primeira versão da SPEC (SHA-256 `153959624CC41A2F018AF4353FC114AA4DC9A9C6088B10129F31463CAF7A20D2`) foi revisada externamente e **NÃO APROVADA**. Foram registrados:

- `SPEC006-REV-001` — bloqueante: RF-010, CA-017, Cenário O e a rastreabilidade atribuiam indevidamente ao grupo 006 a medição das quatro Method Toxicity Metrics.
- `SPEC006-REV-002` — editorial/rastreabilidade: a linha de `New` associava incorretamente CA-021.

A correção da fase SPEC preservou o ID e o Registry. RF-010, CA-017 e Cenário O agora definem que reviewer autorizado ou Guard competente fornece a medição; a unidade Delphi pode relacionar a evidência fornecida e acrescentar fatos Delphi pertinentes, mas não mede nem assume propriedade dessa verificação. Clean Code conserva a interpretação qualitativa e a decisão de remediação. Engenharia Delphi só trata questão material de linguagem/configuração dentro de sua competência. A família permanece na matriz como fronteira rastreada, não como capacidade de medição proprietária do grupo 006.

A referência `New` na matriz foi corrigida para `RF-008; CA-018; cenário P`; CA-021 não é associada a `New`. A revisão adicional confirmou preservadas as fronteiras de prefixos/nomes, constantes, `SCOPEDENUMS`, contratos de interface aprovados, necessidade de interfaces, `New`, `[weak]`, SOLID, Patterns, Clean Code, Quality/Audit e Core. Nenhuma decisão de PLAN foi introduzida.

REF-0000000001–0000000003 permanecem não materiais; nenhum PDF ou conteúdo externo foi consultado. Nenhum gate foi criado ou executado. SPEC retorna a `COMPLETE — aguardando nova revisão externa`; PLAN, TASKS, ANALYZE, IMPLEMENT e CONVERGE continuam `NOT_STARTED`. Release permanece não autorizado.

SHA-256 UTF-8 estrito de `spec.md` após a correção: `62251E2D0533F2AFA31D0B56928F1F7F69DC1E72D3EC52BB17B23513696D7962`.


## Aprovação da SPEC e início de PLAN — 2026-10-12

A revisão externa aprovou `SPEC-0060000001` sobre a versão publicada de `spec.md`, SHA-256 `62251E2D0533F2AFA31D0B56928F1F7F69DC1E72D3EC52BB17B23513696D7962` (Git blob `13fdb7aa0324b08bd145b69d0e7d844ff6d1c534`). SPEC = `COMPLETE ? APROVADA` para essa identidade.

A autorização recebida cobre exclusivamente PLAN. PLAN passa a `IN_PROGRESS`; TASKS, ANALYZE, IMPLEMENT e CONVERGE permanecem `NOT_STARTED`. Esta aprovação não é ANALYZE PASS nem autoriza etapas posteriores ou Release.

## Conclusão do PLAN — 2026-10-12

Para evitar ambiguidade de leitura do registro anterior, a aprovação externa da SPEC-0060000001 significa `APPROVED` para a versão de `spec.md` SHA-256 `62251E2D0533F2AFA31D0B56928F1F7F69DC1E72D3EC52BB17B23513696D7962` (blob `13fdb7aa0324b08bd145b69d0e7d844ff6d1c534`). A autorização cobriu somente PLAN; não foi ANALYZE PASS nem autorização de etapa posterior.

O PLAN foi elaborado e revisado internamente contra a SPEC aprovada, Policies, Registry do grupo 006 e contratos pertinentes das SPEC1/SPEC2. A arquitetura escolhida usa Python 3.12+ e stdlib, tokenizer controlado e reconhecimento estrutural parcial, com resultados limitados para sintaxe/contexto não suportados. Não escolhe parser externo, não implementa gramática completa, não duplica contratos Core, não executa código e não tem efeitos de filesystem/rede/persistência.

A integração entrega observações/evidências Delphi aos contratos existentes da SPEC-0000000002; o Core mantém agregação, authority, precedence, renderização e persistência. SPEC1 não é invocada por esta unidade read-only. Method Toxicity permanece uma fronteira: a unidade não mede Function Length, Parameter Count, If Depth ou Cyclomatic Complexity; pode somente relacionar evidência fornecida por reviewer/Guard autorizado e acrescentar fatos Delphi pertinentes. Clean Code conserva a interpretação qualitativa.

As matrizes do PLAN cobrem RF-001–RF-018, CA-001–CA-021 e Cenários A–P por decisão e estratégia de validação futura. REF-0000000001–0000000003 permanecem não materiais; não foram consultadas. Nenhum teste, código, build, gate ou Release foi executado ou criado.

PLAN = `COMPLETE — aguardando revisão externa`, sobre `plan.md` SHA-256 `4F0A986BCFF38DE67AE3EAFE8E303FF08DB59AA855C0514E2436880EB783587E`. Isso não significa aprovação externa. Etapa atual = PLAN. SPEC = `COMPLETE — APROVADA` para a identidade indicada acima. TASKS, ANALYZE, IMPLEMENT e CONVERGE permanecem `NOT_STARTED`; último gate válido = nenhum; Release = `NÃO AUTORIZADO`.

## Revisão externa e bloqueio do PLAN — 2026-10-12

O PLAN foi submetido à revisão externa na versão SHA-256 `4F0A986BCFF38DE67AE3EAFE8E303FF08DB59AA855C0514E2436880EB783587E` (Git blob `8eb44d6a73cb3402c3415b5345926a9460a181ec`). A revisão registrou `PLAN-REV-001 = BLOCKING`; o PLAN não foi aprovado. O bloqueio decorre da ausência de Technical Reference Delphi/Object Pascal vigente e suficiente para fundamentar decisões técnicas materiais da arquitetura, não de rejeição do desenho arquitetural. A proposta permanece candidata e o impedimento é resolvível; PLAN = `BLOCKED`, não `FAILED`.

Foi identificada a dependência bloqueante `DEP-DEL-001` — fonte técnica governada Delphi/Object Pascal para as regras lexicais, sintáticas e semânticas materiais necessárias ao tokenizer e ao reconhecimento estrutural. Decisões afetadas: D-02, D-03, D-04, D-11, D-13 e D-15. Em particular, o critério técnico para sintaxe de GUID válido permanece pendente; a alegação de unicidade continua limitada ao universo completo fornecido e verificável. O PLAN foi corrigido para não declarar que a regra interna define atualmente essa sintaxe. A estratégia e as matrizes RF/CA/cenários permanecem rastreáveis, mas as partes dependentes não estão prontas para decomposição em TASKS.

REF-0000000001 (Design Patterns), REF-0000000002 (Refactoring) e REF-0000000003 (índice externo de Pattern) permanecem vigentes nos respectivos escopos, porém não cobrem a lacuna Delphi identificada. Não foram reinterpretadas como referências Delphi, e PDFs/sites não foram consultados. Nenhuma Technical Reference foi escolhida, adotada ou adicionada; isso requer autorização separada do responsável pelo projeto. Até resolver `DEP-DEL-001`, TASKS não deve começar, e conhecimento implícito do modelo não substitui fonte governada.

SPEC permanece `COMPLETE — APROVADA` para SHA-256 `62251E2D0533F2AFA31D0B56928F1F7F69DC1E72D3EC52BB17B23513696D7962` (blob `13fdb7aa0324b08bd145b69d0e7d844ff6d1c534`). Estado corrente: PLAN = `BLOCKED`; TASKS, ANALYZE, IMPLEMENT e CONVERGE = `NOT_STARTED`; último gate válido = nenhum; Release = `NÃO AUTORIZADO`. Esta correção não executou gate, teste, código ou Release.

## Clarificação de PLAN-REV-001 / DEP-DEL-001 — autoridade das regras internas

Esta clarificação preserva `PLAN-REV-001 = BLOCKING`, mas delimita seu escopo como estritamente técnico. As regras normativas RickCraft já definidas pelas fontes internas competentes — incluindo `README_PTBr.md`, a SPEC aprovada, Registry e Policies — permanecem válidas, aplicáveis e fora do bloqueio. Conforme POL-0000000004, Technical Reference informa e fundamenta; não substitui nem revoga silenciosamente norma vigente, e não recebe autoridade para redefini-la.

`DEP-DEL-001` significa exclusivamente base técnica rastreável da linguagem Delphi/Object Pascal necessária para implementar corretamente o reconhecimento lexical, sintático e semântico limitado previsto no PLAN. Ela não define nem revisa o que o RickCraft exige. Abrange, conforme materialidade, reconhecimento de identificadores, palavras reservadas, strings, comentários, diretivas, pontuação, atributos, declarações, classes/interfaces, assinaturas, visibilidade, GUIDs, `[weak]` e diferenças técnicas por versão/compiler/target. O subconjunto e as regras RickCraft continuam sendo os já determinados internamente; eventual referência não o amplia automaticamente.

Em D-11, possuir GUID válido e único é requisito normativo RickCraft, e o universo de unicidade permanece delimitado pelo PLAN. Somente o reconhecimento técnico da representação sintática válida depende de base Delphi adequada. Em D-04, a aplicabilidade de `SCOPEDENUMS` continua sendo norma interna; a dependência pode explicar sua representação e efeitos técnicos. Em D-13, `[weak]` não se torna regra universal. Em D-02/D-03/D-15, a dependência fundamenta como reconhecer texto/construções e diferenças da linguagem, não altera convenções ou requisitos RickCraft.

Nenhuma Technical Reference foi selecionada, adotada ou consultada nesta execução. REF-0000000001–0000003 permanecem vigentes em seus domínios originais, mas não cobrem a lacuna técnica Delphi. PLAN permanece `BLOCKED` até resolução autorizada de `DEP-DEL-001`; o bloqueio atinge a implementação técnica do reconhecimento nos casos dependentes, não a autoridade nem a cobertura normativa dos RF/CA. TASKS continua não autorizada e `NOT_STARTED`; ANALYZE, IMPLEMENT e CONVERGE permanecem `NOT_STARTED`; último gate válido = nenhum; Release = `NÃO AUTORIZADO`.
