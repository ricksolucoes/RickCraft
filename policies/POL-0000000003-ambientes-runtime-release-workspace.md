# POL-0000000003 — Ambientes, Runtime, Release e Workspace Operacional

- **Estado:** PROPOSTA
- **Escopo:** regras transversais para ambiente de desenvolvimento, árvore canônica do RickCraft, Release, idioma do runtime e workspace operacional
- **Autoridade:** responsável pelo projeto
- **Dependências:** POL-0000000001 — Governança documental; POL-0000000002 — Processo de desenvolvimento orientado por Specification

## 1. Objetivo

Registrar as invariantes que separam o ambiente interno de desenvolvimento do produto distribuível, definem o workspace operacional e orientam a autonomia e o escalonamento de lacunas. Esta Policy complementa as Policies vigentes sem substituir o pipeline SDD, suas etapas, estados, gates ou regras de evidência.

## 2. Ambiente Debug e idioma interno

O ambiente de desenvolvimento/Debug do RickCraft pode conter os artefatos necessários à construção, análise, validação e auditoria, incluindo Policies, Registries, Specifications, PLAN, TASKS, `status.md`, `.workspace/`, documentação de engenharia, evidências, artefatos de ANALYZE e CONVERGE, testes, ferramentas e dependências exclusivas de desenvolvimento. A presença desses itens no Debug não os torna automaticamente conteúdo do Release.

Durante desenvolvimento, governança, SDD, criação da Skill, análise, documentação interna e Debug, o idioma adotado é pt-BR. O projeto interno não deve ser convertido antecipadamente para inglês.

## 3. Árvore canônica do produto

A árvore canônica do produto final é `<LOCAL_DEFINIDO_USUARIO>/RickCraft/`. Todo arquivo estático que efetivamente componha o RickCraft em runtime deve ter sua localização final nessa árvore. Não se deve manter uma segunda árvore de produto para depois convertê-la silenciosamente no Release.

## 4. Release

O Release não é produzido automaticamente. Só deve ser preparado mediante solicitação explícita do responsável pelo projeto. Até essa autorização, o trabalho permanece no ambiente Debug em pt-BR.

Quando autorizado, o Release deve conter somente os arquivos estáticos necessários para iniciar e operar o produto, provenientes da árvore canônica `<LOCAL_DEFINIDO_USUARIO>/RickCraft/`. Deve ser mínimo e suficiente para funcionamento e excluir artefatos exclusivos de desenvolvimento, incluindo Policies, Registries, `specs/`, documentação de construção, evidências de desenvolvimento, artefatos internos de ANALYZE e CONVERGE, testes e ferramentas exclusivamente de desenvolvimento, dependências exclusivas de Debug e memória operacional gerada em runtime.

Todo conteúdo operacional distribuível consumido em runtime por Agents, Skill ou componentes auxiliares deve ser produzido em inglês. A documentação interna e o Debug permanecem em pt-BR. Não se devem gerar automaticamente duplicatas em português e inglês do mesmo artefato operacional.

`.workspace/` é estado operacional gerado em runtime e não deve ser empacotado como Release, mesmo quando o fallback fizer com que exista fisicamente dentro da árvore canônica do RickCraft.

## 5. Workspace operacional

`.workspace/` é memória operacional persistente criada e utilizada pelos Agents. Não é fonte normativa e não substitui Policy, Registry, SPEC, PLAN, TASKS, `status.md`, Decision Owner ou resultado de gate. Pode conter análises, evidências, comparações, handoffs, resultados intermediários, histórico, regressões e informações necessárias à continuidade entre Agents.

Quando informação operacional precisar ser reutilizada, auditada, comparada ou validada por outro Agent, ela deve ser persistida no workspace, sem depender exclusivamente de conversa, memória do modelo ou contexto temporário. Outro Agent deve poder recuperar os artefatos persistidos e compreender seu contexto sem depender exclusivamente da conversa original.

### 5.1 Resolução da raiz

Considerando o produto instalado em `<LOCAL_DEFINIDO_USUARIO>/RickCraft/`, quando o Agent precisar do workspace deve:

1. identificar `<LOCAL_DEFINIDO_USUARIO>`;
2. subir um nível acima desse diretório;
3. tentar criar ou utilizar `<LOCAL_DEFINIDO_USUARIO>/../.workspace/` como localização preferencial.

Se a raiz aplicável ainda não existir, o próprio Agent deve tentar criá-la; a estrutura normal não deve depender de criação manual pelo usuário. Somente se a localização preferencial realmente não puder ser criada ou utilizada, o Agent deve usar `<LOCAL_DEFINIDO_USUARIO>/RickCraft/.workspace/`. A localização preferencial deve sempre ser tentada primeiro; a escolha do fallback não é arbitrária.

Depois de resolver a raiz, o Agent poderá criar estrutura sob `.workspace/<IDANALISE>/<TipoDocumento>/*.md`. A geração de `IDANALISE` e a taxonomia completa dos tipos de documento serão definidas posteriormente pelas Specification e PLAN correspondentes.

### 5.2 Rastreabilidade e histórico

Um Agent não pode sobrescrever silenciosamente uma análise anterior de modo que sua evidência histórica seja perdida. Correções, complementações, reanálises e substituições devem preservar rastreabilidade suficiente para reconstruir o estado anterior, o novo estado e a relação entre ambos. A estratégia física de versionamento e preservação será definida pelo PLAN apropriado.

O workspace deve permitir a Agents posteriores recuperar análises, decisões e evidências; comparar o planejado com o implementado e resultados anteriores com atuais; executar validações adicionais; investigar regressões; produzir novas evidências; e continuar trabalho autorizado. Isso não aprova nem cria arquitetura multiagente, Orchestrator ou protocolo de comunicação.

## 6. Autonomia e escalonamento

O RickCraft deve continuar autonomamente quando o escopo estiver autorizado, a fonte aplicável for inequívoca, existir Decision Owner competente, houver evidência suficiente, não existir conflito material e nenhuma decisão reservada ao humano estiver pendente. A participação prévia de outro Agent, por si só, não exige intervenção humana.

Nenhum Agent pode fechar por suposição uma lacuna material. Diante de contradição, ambiguidade material, conflito entre fontes vigentes, requisitos incompatíveis, evidências incompatíveis, autoridade ausente, informação obrigatória ausente, decisão reservada ao responsável, validação obrigatória indisponível ou dúvida que altere requisito, comportamento, contrato ou arquitetura, o Agent deve registrar a situação, não escolher silenciosamente nem inventar ou completar informação por conveniência, e encaminhá-la à autoridade adequada.

A participação humana é necessária quando houver necessidade real de decisão não delegada, resolução de divergência, esclarecimento de ambiguidade material, fornecimento de informação obrigatória, resolução de conflito normativo, validação que o ambiente não consiga produzir ou outra decisão fora da autoridade disponível. Não é etapa obrigatória de toda execução.

## 7. Relação com SDD e Specifications futuras

O pipeline permanece `SPEC → PLAN → TASKS → ANALYZE → IMPLEMENT → CONVERGE`, com os significados e gates definidos pela POL-0000000002. Esta Policy não altera alocação de IDs, materialização de artefatos SDD, estados, invalidação, Decision Owners ou critérios de evidência e convergência.

Esta Policy estabelece invariantes transversais. Specifications futuras podem detalhar comportamentos verificáveis sem contradizê-las. Uma futura Specification Core poderá definir `IDANALISE`, `TipoDocumento`, conteúdo mínimo dos arquivos, pesquisa, versionamento, regressão, criação do workspace e tratamento de falhas. Tais Specifications não podem alterar silenciosamente a precedência de localização do workspace, seu fallback, a fronteira Debug/Release, o idioma do Release, a exclusão do workspace do pacote nem a proibição de fechar lacunas por suposição.

## 8. Aprovação e limites

Esta Policy permanece `PROPOSTA` até aprovação explícita do responsável pelo projeto e sincronização do estado em `registries/policies.md`, conforme a POL-0000000001. Enquanto proposta, não é requisito normativo vigente.

Esta Policy não cria workspace, IDANALISE, artefatos de runtime, Skill, Agents, Specifications, PLAN, Release ou código, nem autoriza sua implementação.
