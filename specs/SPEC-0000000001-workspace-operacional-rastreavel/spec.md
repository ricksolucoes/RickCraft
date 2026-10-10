# SPEC-0000000001 — Workspace Operacional Persistente e Rastreabilidade entre Agents

## Identificação

- **Grupo:** `000` — Core do RickCraft
- **Decision Owner conceitual:** RickCraft Core Specialist
- **Estado da etapa SPEC:** COMPLETE
- **Slug:** `workspace-operacional-rastreavel`
- **Idioma:** pt-BR

## Objetivo

Definir o comportamento funcional necessário para que o RickCraft mantenha memória operacional persistente, organizada e rastreável entre Agents. Uma execução posterior deve conseguir recuperar o contexto operacional necessário para dar continuidade ao trabalho, auditar, comparar e validar resultados sem depender exclusivamente de conversa anterior, memória do modelo, contexto temporário ou inferências não registradas.

## Problema

Informações operacionais que existem somente durante uma sessão podem se perder quando ela termina ou quando outro Agent assume o trabalho. Sem persistência contextual e rastreabilidade, não é possível recuperar com segurança análises anteriores, entender suas entradas, distinguir resultados por categoria, verificar se evidências ainda correspondem às entradas atuais ou reconstruir alterações relevantes.

## Escopo

Esta Specification define requisitos funcionais para o workspace operacional utilizado pelos Agents durante o funcionamento do RickCraft: localização conforme a regra vigente, criação quando necessária, organização por análise e tipo de documento, persistência de documentos Markdown, recuperação entre Agents, histórico, comparação, validade de evidências, autonomia e tratamento de lacunas.

O workspace operacional não é uma unidade SDD. Os documentos nele persistidos não são automaticamente `spec.md`, `plan.md`, `tasks.md` ou `status.md`. O pipeline SDD governa a construção e evolução do RickCraft; `.workspace/` guarda informação operacional produzida durante o uso do RickCraft.

## Requisitos funcionais

### RF-001 — Resolver a localização do workspace

O RickCraft deve localizar o produto instalado em `<LOCAL_DEFINIDO_USUARIO>/RickCraft/`, identificar `<LOCAL_DEFINIDO_USUARIO>` e tentar criar ou utilizar primeiro `<LOCAL_DEFINIDO_USUARIO>/../.workspace/`. Somente se esse local realmente não puder ser criado ou utilizado, deve utilizar `<LOCAL_DEFINIDO_USUARIO>/RickCraft/.workspace/`. O fallback não pode ser escolhido arbitrariamente. Esta ordem preserva a invariante da POL-0000000003.

### RF-002 — Criar o workspace quando necessário

Quando uma operação autorizada necessitar do workspace e a raiz aplicável ainda não existir, o RickCraft deve tentar criá-la. A operação normal não deve depender de o usuário criar manualmente a raiz ou a estrutura interna de uma nova análise. Falhas de criação devem ser registráveis e compreensíveis; o mecanismo concreto de tratamento pertence ao PLAN.

### RF-003 — Organizar documentos por análise e tipo

Os documentos operacionais devem ser organizados conceitualmente como:

```text
.workspace/
└── <IDANALISE>/
    └── <TipoDocumento>/
        └── *.md
```

Cada análise deve possuir um IDANALISE que permita distingui-la de outras análises, correlacionar seus documentos, localizar seus resultados e preservar sua identidade durante sua execução, sem depender da conversa original. A estrutura deve permitir classificar documentos de maneira inequívoca por TipoDocumento, localizá-los por tipo, manter organização consistente e permitir extensibilidade controlada. O algoritmo/formato físico do IDANALISE e a taxonomia final de TipoDocumento não são definidos nesta SPEC.

### RF-004 — Persistir artefatos operacionais em Markdown

Os artefatos operacionais persistidos sob o workspace devem utilizar arquivos `*.md`. Cada documento deve fornecer contexto suficiente para que outro Agent compreenda o que foi registrado. Quando aplicável, deve ser possível identificar IDANALISE, TipoDocumento, objetivo da análise, origem da solicitação, arquivos ou elementos analisados, versões/revisões relevantes, fatos observados, decisões existentes, evidências, divergências, lacunas, bloqueios, resultado e referências a documentos relacionados. Esta SPEC não determina o formato físico desses dados.

### RF-005 — Preservar histórico rastreável

Corrigir, complementar, reavaliar, substituir ou invalidar um documento não pode destruir silenciosamente informação histórica relevante. Deve permanecer possível reconstruir o conteúdo ou estado anterior, o novo conteúdo ou estado e a relação entre eles. O mecanismo físico de versionamento não é definido nesta SPEC.

### RF-006 — Permitir continuidade entre Agents

Um Agent posterior deve poder localizar, recuperar e interpretar artefatos operacionais produzidos por outro Agent e utilizá-los como entradas de trabalho autorizado. A troca de Agent, por si só, não deve exigir intervenção humana. A recuperação deve permitir, quando aplicável, comparar o que foi planejado com o observado, validar evidências anteriores, investigar regressões, produzir nova evidência e continuar o trabalho autorizado.

### RF-007 — Rastrear entradas e validade de evidências

Quando uma análise ou evidência depender de arquivo, conteúdo, versão, revisão, estado ou outra evidência, essa dependência deve ser identificável. Se uma entrada relevante divergir da entrada considerada anteriormente, o RickCraft deve conseguir identificar que a análise ou validação anterior pode necessitar reavaliação. A SPEC não escolhe fingerprint, hash ou outro mecanismo técnico.

### RF-008 — Viabilizar comparação e investigação de regressão

Quando aplicável, os dados persistidos devem permitir recuperar informações necessárias para comparar estado anterior e atual; análise anterior e nova; decisão prevista e resultado observado; implementação observada anteriormente e atual; evidência anterior e nova; e resultado anterior e atual. Esta SPEC não define algoritmo de regressão.

### RF-009 — Continuar autonomamente dentro da autoridade disponível

O RickCraft deve poder continuar autonomamente quando possuir informação suficiente, não houver ambiguidade material nem conflito normativo, a decisão estiver dentro da autoridade disponível, as evidências forem suficientes e não houver decisão reservada ao humano. A participação ou troca de Agent, por si só, não deve bloquear a continuidade.

### RF-010 — Registrar e encaminhar lacunas materiais

Nenhum Agent pode completar por suposição informação necessária que esteja ausente ou ambígua. Diante de divergência material, contradição, ambiguidade relevante, evidência incompatível, informação obrigatória ausente, decisão sem autoridade disponível, conflito entre fontes ou validação necessária indisponível, o RickCraft deve:

1. persistir a ocorrência;
2. indicar por que não pode decidir autonomamente;
3. interromper somente a parte afetada;
4. encaminhar a questão à autoridade adequada.

O RickCraft não deve inventar resposta para continuar o fluxo.

### RF-011 — Respeitar a autoridade das fontes

O workspace é memória operacional, não fonte normativa. Quando aplicáveis, Policies, Registries, Specifications, PLAN, TASKS, `status.md`, Decision Owners e gates válidos mantêm sua autoridade conforme a governança. Se um documento operacional divergir de fonte normativa aplicável, a fonte normativa prevalece e a divergência deve ser registrada.

### RF-012 — Manter o workspace fora do Release

O conteúdo de `.workspace/` não é conteúdo estático do Release. Isso permanece verdadeiro quando o fallback fizer a pasta existir fisicamente em `<LOCAL_DEFINIDO_USUARIO>/RickCraft/.workspace/`.

### RF-013 — Não publicar conteúdo operacional implicitamente

A existência de conteúdo no workspace não autoriza push, upload, publicação ou envio a serviço externo. A SPEC não define integração com Git ou serviços externos.

### RF-014 — Permitir pesquisa futura

A organização dos dados deve permitir pesquisa futura por IDANALISE, TipoDocumento, arquivo analisado, decisão, evidência, divergência, bloqueio, resultado e relação com outra análise. Esta SPEC não escolhe ferramenta nem estratégia de pesquisa.

## Critérios de aceitação

- **CA-001:** Quando necessário e inexistente, o RickCraft tenta criar o workspace.
- **CA-002:** A primeira localização tentada é `<LOCAL_DEFINIDO_USUARIO>/../.workspace/`.
- **CA-003:** O fallback `<LOCAL_DEFINIDO_USUARIO>/RickCraft/.workspace/` só é utilizado diante de impossibilidade real de criar ou utilizar o local preferencial.
- **CA-004:** Cada análise possui IDANALISE capaz de distingui-la e correlacionar seus documentos.
- **CA-005:** A organização segue `.workspace/<IDANALISE>/<TipoDocumento>/*.md`.
- **CA-006:** Outro Agent consegue localizar e interpretar artefatos persistidos sem depender exclusivamente da conversa original.
- **CA-007:** Histórico relevante não é perdido por sobrescrita silenciosa e a relação entre estados pode ser reconstruída.
- **CA-008:** É possível identificar quando evidência anterior depende de entrada que posteriormente mudou e que pode exigir reavaliação.
- **CA-009:** Outro Agent pode utilizar evidências anteriores para executar validação ou comparação autorizada.
- **CA-010:** Lacunas materiais não são fechadas por suposição; a ocorrência e o motivo do impedimento são persistidos, e somente a parte afetada é interrompida e encaminhada.
- **CA-011:** A execução autônoma continua quando não há bloqueio, ambiguidade material, conflito, insuficiência de evidência ou decisão pendente de autoridade.
- **CA-012:** O workspace não substitui fontes normativas e divergências são registradas com prevalência da fonte aplicável.
- **CA-013:** `.workspace/` não é incluído no Release, inclusive quando fisicamente localizado dentro da árvore do produto por fallback.
- **CA-014:** Conteúdo do workspace não é publicado ou enviado externamente apenas por existir.
- **CA-015:** O idioma desta documentação interna/Debug permanece pt-BR; a regra de idioma do runtime distribuível continua subordinada à POL-0000000003.

## Fora de escopo

Esta SPEC não define nem implementa:

- algoritmo, formato físico ou estratégia de geração de IDANALISE;
- taxonomia final de TipoDocumento;
- formato físico dos metadados;
- mecanismo de versionamento, locking, fingerprint ou hash;
- banco de dados, SQLite, embeddings ou busca vetorial;
- mecanismo/ferramenta de pesquisa;
- Orchestrator ou arquitetura completa multiagent;
- Agents SDK, MCP, Plugin, Guards, Skill completa ou Evals;
- integração com Git ou serviço externo;
- Release, código ou implementação.

Essas decisões técnicas permanecem para PLAN, dentro dos limites normativos vigentes.

## Rastreabilidade das fontes

Esta rastreabilidade identifica as fontes consultadas e como seus requisitos foram tratados. A extração cobre regras aplicáveis a esta unidade; exemplos do README não foram promovidos a regras universais.

| Fonte | Seção/cláusula | Requisito derivado | Tratamento nesta SPEC |
|---|---|---|---|
| POL-0000000001 — Governança documental | Identificação de Specifications e regras de grupo/ID | A unidade usa ID `SPEC-GGGSSSSSSS` autorizado e pertence a grupo vigente; a alocação persistente é feita no Registry próprio antes de materializar a unidade. | Identificação desta SPEC e alocação registrada em `registries/specifications.md`; não cria requisitos de runtime do workspace. |
| POL-0000000002 — Processo SDD | Artefatos da unidade, inicialização progressiva e distinção de etapas/gates | Artefatos SDD pertencem à construção/evolução do RickCraft; a unidade começa por SPEC e não materializa artefatos de estágios não iniciados. | Esta SPEC separa documentos operacionais em `.workspace/` de `spec.md`, `plan.md`, `tasks.md` e `status.md`. O status registra SPEC concluída e etapas posteriores não iniciadas. |
| POL-0000000002 — Processo SDD | Rastreabilidade e análise de fontes | Requisitos devem manter relação verificável com fontes aplicáveis; decisões de solução técnica pertencem ao PLAN. | Esta seção rastreia as fontes. Algoritmos, tecnologias e mecanismos físicos foram deixados fora de escopo. |
| POL-0000000003 — Ambientes, Runtime, Release e Workspace Operacional | Debug e idioma | O desenvolvimento e os artefatos internos permanecem em pt-BR. | SPEC e status redigidos em pt-BR; CA-015 preserva o limite de idioma aplicável. |
| POL-0000000003 — Ambientes, Runtime, Release e Workspace Operacional | Árvore canônica do produto e fronteira do Release | O produto fica em `<LOCAL_DEFINIDO_USUARIO>/RickCraft/`; conteúdo operacional gerado não se torna automaticamente conteúdo estático do Release. | RF-001, RF-012 e CA-013 preservam a árvore e a exclusão do workspace do Release. |
| POL-0000000003 — Ambientes, Runtime, Release e Workspace Operacional | Resolução da raiz, fallback e criação de `.workspace/` | Tentar primeiro `<LOCAL_DEFINIDO_USUARIO>/../.workspace/`; usar `<LOCAL_DEFINIDO_USUARIO>/RickCraft/.workspace/` somente se a localização preferencial realmente não puder ser criada/utilizada; tentar criar a raiz necessária. | RF-001, RF-002 e CA-001 a CA-003 formalizam a ordem sem escolher mecanismo técnico. |
| POL-0000000003 — Ambientes, Runtime, Release e Workspace Operacional | Estrutura operacional | Organizar por `<IDANALISE>/<TipoDocumento>/*.md`; IDs e taxonomia serão detalhados posteriormente. | RF-003 e RF-004; geração do ID e taxonomia final permanecem fora de escopo. |
| POL-0000000003 — Ambientes, Runtime, Release e Workspace Operacional | Persistência, continuidade, histórico e interoperação | Informação reutilizável deve persistir; histórico não deve ser silenciosamente perdido; Agents posteriores devem poder recuperar e comparar artefatos. | RF-005, RF-006 e RF-008. |
| POL-0000000003 — Ambientes, Runtime, Release e Workspace Operacional | Autonomia, escalonamento e proibição de fechar lacunas | Continuar quando autoridade e evidência forem suficientes; não resolver lacunas materiais por suposição; registrar e encaminhar impedimentos. | RF-009 e RF-010. |
| POL-0000000003 — Ambientes, Runtime, Release e Workspace Operacional | Natureza do workspace e relação com fontes normativas | Workspace é estado operacional, não fonte normativa nem substituto de artefatos/gates; a futura SPEC pode detalhar comportamento sem alterar invariantes. | RF-011 e CA-012; esta SPEC detalha o comportamento funcional dentro das invariantes. |
| POL-0000000003 — Ambientes, Runtime, Release e Workspace Operacional | Persistência e publicação | Memória operacional deve ser recuperável por outras sessões; o workspace não entra automaticamente no Release nem autoriza publicação externa. | RF-006, RF-012 e RF-013. |
| `registries/policies.md` | Entradas POL-0000000001, POL-0000000002 e POL-0000000003 | As três Policies vigentes são as fontes normativas aplicáveis nesta unidade. | Confirmadas como VIGENTE; seus conteúdos aplicáveis são rastreados nas linhas acima. |
| `registries/spec-groups.md` | Grupo `000` — Core do RickCraft; matriz de decisão e fronteiras | Core é domínio vigente para comportamento central e contratos transversais, sem absorver decisões especializadas. | A unidade delimita comportamento central de continuidade operacional; não assume decisões dos demais domínios nem transforma exemplos Delphi em regra. Decision Owner conceitual: RickCraft Core Specialist. |
| `registries/spec-groups.md` | Auditoria de cobertura e rastreabilidade de fontes | Matriz de cobertura contém famílias, não catálogo exaustivo; a SPEC inicial deve extrair e rastrear todas as regras aplicáveis das fontes. | As fontes pertinentes e cláusulas aplicáveis estão identificadas nesta tabela; ausência de item individual na matriz não elimina regra da fonte. |
| `README_PTBr.md` | “Sobre o RickCraft”, “Objetivos”, “Pilares Técnicos” e “Uso com Inteligência Artificial” | O RickCraft atua como camada de governança técnica para desenvolvimento assistido por IA, considerando consistência, baixo acoplamento, coesão, testabilidade e manutenção. | Contextualiza a finalidade da capacidade de continuidade e recuperação. Não define localização, estrutura ou tecnologia de workspace. |
| `README_PTBr.md` | Exemplos de Design Patterns, SOLID e programação orientada a interfaces | Exemplos demonstram princípios e estruturas em contexto específico. | Consultados como referência; nenhum trecho de código ou exemplo foi convertido em requisito universal desta SPEC. |

## Decisões reservadas ao PLAN

O PLAN deverá escolher soluções técnicas que satisfaçam os requisitos sem violar as invariantes das Policies: geração do IDANALISE, taxonomia controlada de TipoDocumento, formato dos metadados, versionamento e recuperação histórica, identificação de mudanças de entradas, organização física e pesquisa. Esta lista não prescreve tecnologia, linguagem, banco, biblioteca ou ferramenta.
