# POL-0000000002 — Processo de desenvolvimento orientado por Specification

- **Estado:** Proposta para aprovação
- **Escopo:** unidades funcionais do RickCraft desenvolvidas por SDD
- **Autoridade:** responsável pelo projeto aprova esta Policy e alterações; proprietários de domínio mantêm autoridade sobre decisões formalmente delegadas
- **Dependências:** POL-0000000001 — Governança documental

## 1. Objetivo

Definir o fluxo normativo mínimo de desenvolvimento e os gates entre etapas, preservando escopo, autoridade, rastreabilidade e evidência.

## 2. Unidade de trabalho

Cada unidade funcional aprovada possui uma pasta em `specs/` cujo nome começa pelo ID e slug da Specification. Contém, no mínimo:

- `spec.md` — o que deve existir: requisitos, comportamento, restrições e critérios de aceitação;
- `plan.md` — como será construído: decisões técnicas e arquitetura necessárias;
- `tasks.md` — divisão ordenada do trabalho em tarefas pequenas, executáveis, verificáveis e rastreáveis;
- `status.md` — registro persistente obrigatório do estado atual da unidade, dos estados e versões dos artefatos, gates, invalidações e referências às evidências.

`status.md` é um registro transversal, não uma etapa do pipeline e não substitui SPEC, PLAN, TASKS, ANALYZE, IMPLEMENT ou CONVERGE. ANALYZE, IMPLEMENT e CONVERGE continuam sendo etapas/gates, não arquivos próprios. O registro deve ser atualizado na mesma execução em que um estado muda e antes de outro executor usar esse estado. Estado ausente, incompleto, contraditório ou sem referência verificável não autoriza avançar.

A estrutura não autoriza criar Specifications funcionais sem a decisão de grupo e escopo correspondente. Evidências adicionais persistentes só devem ser introduzidas quando houver necessidade definida.

## 3. Sequência normativa

`SPEC → PLAN → TASKS → ANALYZE → IMPLEMENT → CONVERGE`

Não se pode iniciar IMPLEMENT a partir de SPEC, PLAN ou TASKS sem ANALYZE com estado `PASS` válido no `status.md`. Se um estágio for alterado, os estágios e evidências posteriores materialmente dependentes devem ser invalidados e revalidados conforme a regra de dependências abaixo.

### Registro e estados

`status.md` deve permitir a qualquer sessão determinar a etapa atual e o estado de cada etapa. Para SPEC, PLAN e TASKS, usar `NOT_STARTED`, `IN_PROGRESS`, `COMPLETE`, `FAILED`, `BLOCKED` ou `INVALIDATED`. `COMPLETE` indica que o artefato está pronto para alimentar o estágio seguinte; não substitui aprovação exigida por um gate. Para IMPLEMENT, usar os mesmos estados, em que `IN_PROGRESS` comprova início e `COMPLETE` comprova conclusão das tarefas autorizadas. Para toda etapa ainda não iniciada, registrar `NOT_STARTED`.

ANALYZE usa exclusivamente `PASS`, `FAIL`, `BLOCKED` ou `INVALIDATED`. Só `PASS` válido autoriza IMPLEMENT. `FAIL`, `BLOCKED` ou `INVALIDATED` impedem iniciar ou continuar novo trabalho de implementação dependente até que a causa seja resolvida e ANALYZE volte a `PASS`.

CONVERGE usa exclusivamente `CONVERGED`, `NOT_CONVERGED`, `BLOCKED` ou `INVALIDATED`. Apenas `CONVERGED` válido encerra a unidade como convergida. Lacuna conhecida implica `NOT_CONVERGED`; impedimento de avaliação implica `BLOCKED`.

O registro deve identificar para cada artefato relevante sua versão de entrada (por identificador de revisão, hash ou referência equivalente verificável), estado, momento da avaliação e referências à evidência. Deve indicar explicitamente a etapa atual, o último gate válido, mudanças pendentes e etapas invalidadas, incluindo motivo e origem da invalidação. Um executor não pode inferir validade somente por histórico de conversa.

### Invalidação por dependência

Cada análise, tarefa e evidência deve identificar os artefatos e versões dos quais materialmente depende. Ao mudar um artefato, invalidar somente estados, gates e evidências que dependem materialmente da versão anterior, propagando a invalidação pelas dependências registradas. Registrar em `status.md` o artefato alterado, versão anterior e nova, itens invalidados, motivo e revalidações necessárias.

Consequentemente, alteração material em SPEC invalida os itens dependentes em PLAN e TASKS e propaga a invalidação para ANALYZE, IMPLEMENT e CONVERGE apenas na medida em que dependam dessas versões. Alteração em PLAN invalida tarefas dependentes e propaga às análises, implementação e convergência dependentes. Alteração em TASKS invalida ANALYZE e os resultados de implementação/convergência que dependam das tarefas alteradas. Alterações em implementação, testes ou evidências invalidam CONVERGE quando afetarem suas bases. Alterações não materiais devem ser justificadas no registro e não invalidam dependências que permaneçam equivalentes.

Nenhum `PASS` ou `CONVERGED` permanece válido se alguma versão de entrada da qual dependa foi invalidada ou diverge da versão registrada. Até a revalidação, o estado correspondente é `INVALIDATED`; é proibido usar um gate invalidado para autorizar trabalho.

## 4. Responsabilidades e autoridade

### SPEC

Define o resultado requerido, comportamento, restrições e critérios de aceitação. Não deve antecipar decisões técnicas que pertencem ao PLAN.

### PLAN

Define decisões técnicas e arquiteturais para satisfazer a SPEC. Não altera requisitos silenciosamente. Decisões devem indicar justificativa, impactos, dependências e autoridade decisória.

### TASKS

Decompõe o PLAN em trabalho ordenado, executável, verificável e rastreável. Cada tarefa deve ter origem identificável e permanecer no escopo aprovado.

### ANALYZE

É um gate de consistência entre SPEC, PLAN e TASKS. Verifica requisitos sem cobertura, tarefas sem origem ou fora de escopo, decisões sem cobertura, dependências ausentes, contradições, ambiguidades, critérios de aceitação sem cobertura, testes ausentes e violações de autoridade. É análise; não altera artefatos silenciosamente. Cada achado retorna ao artefato proprietário.

O resultado deve ser persistido em `status.md`, incluindo: versões exatas de SPEC, PLAN e TASKS analisadas; resultado `PASS`, `FAIL` ou `BLOCKED`; achados e indicação explícita de quais são bloqueantes; data/identificador da execução; e referências verificáveis às evidências da análise. `PASS` exige ausência de achados bloqueantes e evidência suficiente para revisar as verificações; uma declaração do agente sem essas referências não é PASS válido. Um PASS autoriza IMPLEMENT somente para as versões registradas e enquanto nenhuma dependência for invalidada.

### IMPLEMENT

Executa somente tarefas autorizadas por um `PASS` válido de ANALYZE. Registra em `status.md` início, conclusão ou falha, tarefas executadas e evidências pertinentes. Não redefine requisitos, arquitetura, contratos, decisões de domínio ou escopo. Alteração necessária retorna ao artefato proprietário e invalida gates posteriores afetados.

### CONVERGE

Compara o produto real e as evidências disponíveis com SPEC, PLAN e TASKS. Verifica implementação, testes, resultados e evidências suficientes. Lacunas retornam ao estágio proprietário, com revalidação das etapas afetadas.

O resultado deve ser persistido em `status.md` com estado `CONVERGED`, `NOT_CONVERGED`, `BLOCKED` ou `INVALIDATED`; versões dos artefatos avaliados; estado de conclusão das tarefas; referências à implementação existente e às evidências dos testes e seus resultados; critérios de aceitação verificados e suas evidências; e lacunas bloqueantes conhecidas ou declaração explícita de que nenhuma foi encontrada. `CONVERGED` exige cobertura rastreável dos requisitos, tarefas, implementação, testes aplicáveis e critérios de aceitação, além de ausência de lacunas bloqueantes conhecidas. Uma declaração textual sem evidências referenciadas não constitui `CONVERGED` válido.

## 5. Propriedade de decisões

O responsável pelo projeto mantém autoridade sobre decisões não delegadas. Uma decisão pode ter Decision Owner de domínio somente quando essa propriedade for explicitamente aprovada e registrada. O proprietário decide dentro do escopo delegado; outros participantes podem apontar riscos, conflitos, restrições e pedir reconsideração, mas não substituem silenciosamente o proprietário.

O Orquestrador, se vier a ser aprovado como componente futuro, terá autoridade de coordenação, roteamento e controle do workflow; essa função não transfere para ele decisões técnicas delegadas a especialistas. O protocolo de comunicação e qualquer arquitetura de agentes permanecem fora do escopo desta Policy.

## 6. Rastreabilidade mínima

A unidade SDD deve permitir seguir a cadeia:

`requisito → decisão de PLAN → TASK → implementação → teste/evidência → CONVERGE`

O vínculo deve ser verificável nos artefatos e evidências pertinentes. Uma declaração de conclusão sem evidência suficiente não satisfaz CONVERGE.

## 7. Referência metodológica externa

GitHub Spec Kit é referência metodológica externa, não autoridade normativa do RickCraft. Sua documentação oficial descreve artefatos e etapas semelhantes e um comando de análise que reporta conflitos, lacunas e ambiguidades para correção na etapa de origem. O RickCraft adota somente as regras explicitadas nesta Policy; comandos, templates, arquivos opcionais e convenções específicas do Spec Kit não são importados automaticamente.

## 8. Limites desta Policy

Esta Policy não aprova requisitos funcionais, grupos de Specification, arquitetura multiagente, distribuição final de Decision Owners, Skill, Plugin, MCP, ferramentas, evals ou runtime. Não inicia automaticamente uma unidade SDD.