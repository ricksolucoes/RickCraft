# Status da unidade SDD

## Identificação

- **SPEC:** `SPEC-0000000001`
- **Título:** Workspace Operacional Persistente e Rastreabilidade entre Agents
- **Grupo:** `000` — Core do RickCraft
- **Caminho:** `specs/SPEC-0000000001-workspace-operacional-rastreavel/`
- **Última atualização:** 2026-10-10

## Estado atual

- **Etapa atual:** PLAN
- **SPEC:** COMPLETE
- **PLAN:** COMPLETE
- **TASKS:** NOT_STARTED
- **ANALYZE:** NOT_STARTED
- **IMPLEMENT:** NOT_STARTED
- **CONVERGE:** NOT_STARTED
- **Último gate válido:** Nenhum
- **Aprovação da SPEC:** Aprovada explicitamente pelo responsável pelo projeto em 2026-10-10; versão aprovada: SHA-256 `A6B14A3ED433C06BE4E470F1579E580C0C93379BDFACAE71E28DD0ACB623D60C`.
- **Aprovação do PLAN:** Aguardando revisão e aprovação explícita do responsável; COMPLETE não significa aprovado.

## Artefatos e versões

| Artefato | Estado | Referência verificável | Observação |
|---|---|---|---|
| `spec.md` | COMPLETE | SHA-256 `A6B14A3ED433C06BE4E470F1579E580C0C93379BDFACAE71E28DD0ACB623D60C` | Versão elaborada e revisada internamente em 2026-10-10; aprovada explicitamente pelo responsável pelo projeto em 2026-10-10. |
| `plan.md` | COMPLETE | SHA-256 `32F659539BF611C80D9A9F28983902A5B54C45673333158AB4595CCC1141F6BB` | Revisado em 2026-10-10 para remover inconsistências de lifecycle da sonda D-02, sincronizar o mecanismo de publicação `os.link` e explicitar a regeneração integral em colisões de `DOC-UUIDv4`. Python 3.12/stdlib, host e binding permanecem inalterados. A sonda D-02 não foi executada com sucesso; a prova auxiliar em TEMP foi inconclusiva por acesso negado. Aguardando aprovação explícita; ainda não autoriza TASKS. |
| `tasks.md` | NOT_STARTED | Sem versão | Ausência válida enquanto TASKS não iniciar. |

## Histórico de estado

| Data | Etapa | Estado | Registro |
|---|---|---|---|
| 2026-10-10 | SPEC | IN_PROGRESS | Estado durante elaboração inicial, após alocação válida do ID e materialização de `spec.md` e `status.md`. |
| 2026-10-10 | SPEC | COMPLETE | Elaboração e revisão interna concluídas; referência verificável de `spec.md` registrada acima. Esta conclusão não substitui a aprovação do responsável nem autoriza PLAN. |
| 2026-10-10 | Aprovação da SPEC | Registrada | O responsável pelo projeto aprovou explicitamente a versão COMPLETE de `spec.md` identificada pelo SHA-256 `A6B14A3ED433C06BE4E470F1579E580C0C93379BDFACAE71E28DD0ACB623D60C`. A aprovação não é gate ANALYZE nem CONVERGE e não autoriza PLAN. |
| 2026-10-10 | PLAN | IN_PROGRESS | Início autorizado pelo responsável; elaboração baseada na versão aprovada de SPEC identificada pelo SHA-256 `A6B14A3ED433C06BE4E470F1579E580C0C93379BDFACAE71E28DD0ACB623D60C`. |
| 2026-10-10 | PLAN | IN_PROGRESS | Revisão material corretiva autorizada; validação da referência COMPLETE anterior e recálculo após correção. |
| 2026-10-10 | PLAN | BLOCKED | Revisão atualizada; a linguagem/runtime obrigatória permanece sem decisão registrada e o host/binding ainda não foi selecionado. A versão COMPLETE anterior deixou de representar o conteúdo atual. A nova referência é registrada na tabela acima. TASKS não foi autorizado. |
| 2026-10-10 | PLAN | BLOCKED | Registrada a decisão explícita do responsável para materializar `<LOCAL_DEFINIDO_USUARIO>` como `<RAIZ_REPOSITORIO>/impl/src` no Debug. As fórmulas normativas e a precedência de workspace permanecem inalteradas; nenhum diretório foi criado. A decisão não aprova o PLAN nem resolve os bloqueios de host/runtime, binding e linguagem. |
| 2026-10-10 | PLAN | IN_PROGRESS | Revisão autorizada para registrar o host Debug aprovado e decidir linguagem/runtime sob delegação explícita do responsável ao RickCraft Core Specialist. |
| 2026-10-10 | PLAN | COMPLETE | Codex Local no VS Code registrado como host inicial desta unidade; binding fornece RickCraftRoot explicitamente; Python 3.12/stdlib selecionado; mecanismos de JSON, UUIDv4, SHA-256 e publicação no filesystem definidos. A prova auxiliar em TEMP foi negada por permissões antes da escrita e é inconclusiva; D-02 exige sonda de cada raiz antes de uso. PLAN apto para revisão, não aprovado. |
| 2026-10-10 | PLAN | IN_PROGRESS | Início da correção final de consistência autorizada; SPEC e arquitetura selecionada preservadas. Revisão limitada à redação de D-02/D-06/D-13, referências ao mecanismo de publicação e coerência da colisão documental. |
| 2026-10-10 | PLAN | COMPLETE | Corrigidas as referências que condicionavam a conclusão do PLAN à prova operacional, as menções a `rename` como mecanismo atual e o tratamento de colisão para regenerar ID, metadados, bytes e temporário coerentemente. D-02 continua obrigatória antes de usar cada raiz e não foi registrada como executada/aprovada. PLAN apto para revisão e aprovação explícita; TASKS não autorizado. |

## Pendências e invalidações

- **Mudanças pendentes:** Nenhuma registrada.
- **Etapas invalidadas:** Nenhuma etapa posterior foi iniciada; a versão COMPLETE anterior de PLAN foi invalidada pela revisão material. A versão atual de PLAN está COMPLETE e aguarda aprovação explícita.
- **Decisões/dependências pendentes:** Nenhuma decisão arquitetural pendente. A sonda D-02 continua sendo critério operacional obrigatório antes de usar cada raiz; a prova auxiliar em TEMP foi inconclusiva por restrição de acesso do ambiente desta sessão.
- **Bloqueios:** Nenhum bloqueio do PLAN. O resultado da sonda D-02 determinará se cada raiz pode ser usada e se o fallback normativo se aplica; falha desconhecida bloqueia a operação afetada.
- **Próxima autorização necessária:** Aprovação explícita do PLAN atualizado antes de iniciar TASKS.
