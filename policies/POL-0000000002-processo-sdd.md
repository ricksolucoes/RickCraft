# POL-0000000002 — Processo de desenvolvimento orientado por Specification

- **Estado:** Vigente
- **Escopo:** unidades funcionais do RickCraft desenvolvidas por SDD
- **Autoridade:** responsável pelo projeto aprova esta Policy e alterações; proprietários de domínio mantêm autoridade sobre decisões formalmente delegadas
- **Dependências:** POL-0000000001 — Governança documental

## 1. Objetivo

Definir o fluxo normativo mínimo de desenvolvimento e os gates entre etapas, preservando escopo, autoridade, rastreabilidade e evidência.

## 2. Unidade de trabalho

Após autorização explícita da unidade e alocação do ID em `registries/specifications.md`, cria-se uma pasta em `specs/` cujo nome começa pelo ID e slug da Specification. Ao longo de seu ciclo, a unidade possui:

- `spec.md` — o que deve existir: requisitos, comportamento, restrições e critérios de aceitação;
- `plan.md` — como será construído: decisões técnicas e arquitetura necessárias;
- `tasks.md` — divisão ordenada do trabalho em tarefas pequenas, executáveis, verificáveis e rastreáveis;
- `status.md` — registro persistente obrigatório do estado atual da unidade, dos estados e versões dos artefatos, gates, invalidações e referências às evidências.

Na inicialização, materializar somente `spec.md` e `status.md`, com SPEC em `IN_PROGRESS`. Não criar arquivos vazios como placeholders para etapas não iniciadas. Ao iniciar PLAN, criar `plan.md` e registrar PLAN como `IN_PROGRESS` na mesma execução. Ao iniciar TASKS, criar `tasks.md` e registrar TASKS como `IN_PROGRESS` na mesma execução. ANALYZE, IMPLEMENT e CONVERGE não exigem arquivos próprios. Evidências adicionais persistentes só devem ser introduzidas quando houver necessidade definida.

Quando PLAN estiver `NOT_STARTED`, a ausência de `plan.md` é válida; quando TASKS estiver `NOT_STARTED`, a ausência de `tasks.md` é válida. A ausência do artefato correspondente é inválida a partir de `IN_PROGRESS` e em qualquer estado subsequente dessa etapa. Os arquivos materializados permanecem na unidade se a etapa for depois falha, bloqueada ou invalidada.

O estado inicial registrado em `status.md`, após alocação válida do ID e criação da pasta, `spec.md` e `status.md`, deve ser: etapa atual SPEC; SPEC `IN_PROGRESS`; PLAN `NOT_STARTED`; TASKS `NOT_STARTED`; ANALYZE `NOT_STARTED`; IMPLEMENT `NOT_STARTED`; CONVERGE `NOT_STARTED`; último gate válido: nenhum. A inicialização, por si só, não autoriza qualquer etapa posterior.

`status.md` é um registro transversal, não uma etapa do pipeline e não substitui SPEC, PLAN, TASKS, ANALYZE, IMPLEMENT ou CONVERGE. ANALYZE, IMPLEMENT e CONVERGE continuam sendo etapas/gates, não arquivos próprios. O registro deve ser atualizado na mesma execução em que um estado muda e antes de outro executor usar esse estado. Estado ausente, incompleto, contraditório ou sem referência verificável não autoriza avançar.

A estrutura não autoriza criar Specifications funcionais sem a decisão de grupo e escopo correspondente. Evidências adicionais persistentes só devem ser introduzidas quando houver necessidade definida.

## 3. Sequência normativa

`SPEC → PLAN → TASKS → ANALYZE → IMPLEMENT → CONVERGE`

Não se pode iniciar IMPLEMENT a partir de SPEC, PLAN ou TASKS sem ANALYZE com estado `PASS` válido no `status.md`. Se um estágio for alterado, os estágios e evidências posteriores materialmente dependentes devem ser invalidados e revalidados conforme a regra de dependências abaixo.

### Registro e estados

`status.md` deve permitir a qualquer sessão determinar a etapa atual e o estado de cada etapa. Para SPEC, PLAN e TASKS, usar `NOT_STARTED`, `IN_PROGRESS`, `COMPLETE`, `FAILED`, `BLOCKED` ou `INVALIDATED`. `COMPLETE` indica que o artefato está pronto para alimentar o estágio seguinte; não substitui aprovação exigida por um gate. Para IMPLEMENT, usar os mesmos estados, em que `IN_PROGRESS` comprova início e `COMPLETE` comprova conclusão das tarefas autorizadas. Para toda etapa ainda não iniciada, registrar `NOT_STARTED`.

ANALYZE usa `NOT_STARTED`, `IN_PROGRESS`, `PASS`, `FAIL`, `BLOCKED` ou `INVALIDATED`. `NOT_STARTED` indica gate ainda não executado; `IN_PROGRESS` indica avaliação em execução, ainda sem resultado válido; `PASS` indica gate concluído sem achado bloqueante e com evidência suficiente; `FAIL` indica gate concluído com achado bloqueante; `BLOCKED` indica impedimento à conclusão; `INVALIDATED` indica que um resultado anterior perdeu validade por mudança em dependência. Somente `PASS` válido autoriza IMPLEMENT. `IN_PROGRESS` nunca autoriza IMPLEMENT. `FAIL`, `BLOCKED` ou `INVALIDATED` impedem iniciar ou continuar novo trabalho de implementação dependente até que a causa seja resolvida e ANALYZE volte a `PASS`.

CONVERGE usa `NOT_STARTED`, `IN_PROGRESS`, `CONVERGED`, `NOT_CONVERGED`, `BLOCKED` ou `INVALIDATED`. `NOT_STARTED` indica avaliação ainda não iniciada; `IN_PROGRESS` indica avaliação em execução, ainda sem resultado final; `CONVERGED` indica convergência comprovada pelas evidências exigidas; `NOT_CONVERGED` indica avaliação concluída com lacunas remanescentes; `BLOCKED` indica que não foi possível concluir a avaliação; `INVALIDATED` indica que uma conclusão anterior perdeu validade. Apenas `CONVERGED` válido encerra a unidade como convergida. Lacuna conhecida implica `NOT_CONVERGED`; impedimento de avaliação implica `BLOCKED`.

Se uma execução for interrompida com ANALYZE ou CONVERGE em `IN_PROGRESS`, não se infere resultado final nem se reinicia silenciosamente. A execução seguinte deve verificar o estado persistente e determinar, à luz das evidências existentes, se a avaliação pode ser retomada ou precisa ser reiniciada.

O registro deve identificar para cada artefato relevante sua versão de entrada (por identificador de revisão, hash ou referência equivalente verificável), estado, momento da avaliação e referências à evidência. Artefato em `NOT_STARTED` não possui versão. Em `IN_PROGRESS`, pode haver referência ao artefato de trabalho, mas ela não é versão aprovada para alimentar gate posterior. `COMPLETE` exige referência verificável à versão/revisão usada pela etapa seguinte. `ANALYZE` em `PASS` deve referenciar exatamente as versões `COMPLETE` de SPEC, PLAN e TASKS que analisou; `CONVERGE` em `CONVERGED` deve referenciar exatamente as versões dos artefatos e as evidências que sustentam a convergência. Quando aplicável, `status.md` também deve permitir registrar validação humana requerida, pendente ou concluída, sua evidência referenciada e seu resultado. Deve indicar explicitamente a etapa atual, o último gate válido, mudanças pendentes e etapas invalidadas, incluindo motivo e origem da invalidação. Um executor não pode inferir validade somente por histórico de conversa.

### Invalidação por dependência

Cada análise, tarefa e evidência deve identificar os artefatos e versões dos quais materialmente depende. Ao mudar um artefato, invalidar somente estados, gates e evidências que dependem materialmente da versão anterior, propagando a invalidação pelas dependências registradas. Registrar em `status.md` o artefato alterado, versão anterior e nova, itens invalidados, motivo e revalidações necessárias.

Consequentemente, alteração material em SPEC invalida os itens dependentes em PLAN e TASKS e propaga a invalidação para ANALYZE, IMPLEMENT e CONVERGE apenas na medida em que dependam dessas versões. Alteração em PLAN invalida tarefas dependentes e propaga às análises, implementação e convergência dependentes. Alteração em TASKS invalida ANALYZE e os resultados de implementação/convergência que dependam das tarefas alteradas. Alterações em implementação, testes ou evidências invalidam CONVERGE quando afetarem suas bases. Alterações não materiais devem ser justificadas no registro e não invalidam dependências que permaneçam equivalentes.

Nenhum `PASS` ou `CONVERGED` permanece válido se alguma versão de entrada da qual dependa foi invalidada ou diverge da versão registrada. Até a revalidação, o estado correspondente é `INVALIDATED`; é proibido usar um gate invalidado para autorizar trabalho.

## 4. Responsabilidades e autoridade

### SPEC

Define o resultado requerido, comportamento, restrições e critérios de aceitação. Não deve antecipar decisões técnicas que pertencem ao PLAN.

### PLAN

Define decisões técnicas e arquiteturais para satisfazer a SPEC. Não altera requisitos silenciosamente. Decisões devem indicar justificativa, impactos, dependências e autoridade decisória.

Quando previsível, PLAN deve identificar critérios de aceitação que exijam validação humana ou ambiente indisponível ao agente e definir estratégia de validação suficiente. TASKS deve incluir as verificações necessárias previstas para o trabalho. ANALYZE deve verificar se a estratégia e a cobertura dessas verificações são suficientes.

### TASKS

Decompõe o PLAN em trabalho ordenado, executável, verificável e rastreável. Cada tarefa deve ter origem identificável e permanecer no escopo aprovado.

### ANALYZE

É um gate de consistência entre SPEC, PLAN e TASKS. Verifica requisitos sem cobertura, tarefas sem origem ou fora de escopo, decisões sem cobertura, dependências ausentes, contradições, ambiguidades, critérios de aceitação sem cobertura, testes ausentes e violações de autoridade. É análise; não altera artefatos silenciosamente. Cada achado retorna ao artefato proprietário.

O estado e o resultado da execução devem ser persistidos em `status.md`, incluindo: versões exatas de SPEC, PLAN e TASKS analisadas; estado `IN_PROGRESS`, `PASS`, `FAIL`, `BLOCKED` ou `INVALIDATED`; achados e indicação explícita de quais são bloqueantes; data/identificador da execução; e referências verificáveis às evidências da análise. Antes da primeira execução, o estado é `NOT_STARTED` e ainda não há resultado ou evidência de gate. `PASS` exige ausência de achados bloqueantes e evidência suficiente para revisar as verificações; uma declaração do agente sem essas referências não é PASS válido. Um PASS autoriza IMPLEMENT somente para as versões registradas e enquanto nenhuma dependência for invalidada.

### IMPLEMENT

Executa somente tarefas autorizadas por um `PASS` válido de ANALYZE. IMPLEMENT abrange o trabalho autorizado, que pode incluir implementação de código, criação ou ajuste de testes, execução de testes, build, compilação, uso de ferramentas de validação e coleta de evidências técnicas quando previstos em PLAN/TASKS ou necessários dentro do escopo autorizado. Testes não constituem etapa independente do pipeline: são trabalho de IMPLEMENT e produzem evidências para CONVERGE. Isso inclui testar o próprio RickCraft, inclusive uma Skill em desenvolvimento, por verificações disponíveis e adequadas aos critérios de aceitação; validação humana não é requisito automático quando as evidências técnicas forem suficientes.

Registra em `status.md` início, conclusão ou falha, tarefas executadas e evidências pertinentes, incluindo resultados negativos de testes e verificações. Uma falha encontrada não pode ser apresentada como sucesso; deve retornar ao artefato ou estágio proprietário da causa e as dependências afetadas devem ser revalidadas. IMPLEMENT não redefine requisitos, arquitetura, contratos, decisões de domínio ou escopo. Alteração necessária retorna ao artefato proprietário e invalida gates posteriores afetados.

### CONVERGE

Compara SPEC, PLAN, TASKS e a implementação com as evidências disponíveis. Avalia, conforme aplicável, testes e resultados, build/compilação, outras evidências técnicas, validação humana necessária, critérios de aceitação e comportamento que deveria ser preservado. CONVERGE corresponde à **Garantia Real**: conclusão sustentada pelo conjunto de evidências verificáveis exigidas para a unidade. Não significa ausência matemática de defeitos, certeza absoluta ou garantia universal contra regressões futuras. Lacunas retornam ao estágio proprietário, com revalidação das etapas afetadas.

O RickCraft deve produzir e avaliar as evidências tecnicamente disponíveis no ambiente em que a unidade está sendo desenvolvida e registrar seus resultados. Não deve afirmar teste, validação ou aprovação sem evidência realmente produzida. Ausência de erro aparente no código não comprova funcionamento; compilação ou build, quando disponíveis, também não comprovam por si sós o comportamento funcional completo. Indisponibilidade de ferramenta ou ambiente não é evidência de falha nem de sucesso e deve ser registrada como limitação. Quando todos os critérios de aceitação puderem ser comprovados por evidências tecnicamente disponíveis e suficientes, não se exige validação humana adicional sem necessidade demonstrada.

Validação humana pode compor CONVERGE e é necessária somente quando um critério relevante não puder ser suficientemente comprovado pelas evidências disponíveis e exigir execução ou observação humana. Não é requisito padrão. Se necessária e pendente, deve ser registrada em `status.md` e CONVERGE permanece `IN_PROGRESS`; não se cria estado adicional. A evidência humana concluída deve ser referenciada e incluir seu resultado. Ausente essa necessidade, não deve haver pendência artificial.

Uma validação humana ou teste positivo constitui evidência, não autorização para ignorar etapas ou gates do SDD. Uma mudança solicitada continua sujeita ao pipeline aplicável. Se teste ou validação identificar falha ou critério não atendido, CONVERGE resulta em `NOT_CONVERGED` quando a avaliação puder ser concluída; o achado retorna ao artefato ou estágio proprietário e as dependências afetadas são revalidadas.

O estado e o resultado da execução devem ser persistidos em `status.md` com estado `NOT_STARTED`, `IN_PROGRESS`, `CONVERGED`, `NOT_CONVERGED`, `BLOCKED` ou `INVALIDATED`; versões dos artefatos avaliados; estado de conclusão das tarefas; referências à implementação existente e às evidências dos testes e seus resultados; critérios de aceitação verificados e suas evidências; e lacunas bloqueantes conhecidas ou declaração explícita de que nenhuma foi encontrada. `NOT_STARTED` não possui resultado ou evidência de gate. `CONVERGED` exige cobertura rastreável dos requisitos, tarefas, implementação, testes aplicáveis, resultados, critérios de aceitação e demais evidências necessárias, incluindo validação humana somente quando tecnicamente necessária, além de ausência de lacunas bloqueantes conhecidas. Todas as verificações tecnicamente disponíveis devem ter sido avaliadas. Uma declaração textual sem evidências referenciadas não constitui `CONVERGED` válido.

## 5. Propriedade de decisões

O responsável pelo projeto mantém autoridade sobre decisões não delegadas. Uma decisão pode ter Decision Owner de domínio somente quando essa propriedade for explicitamente aprovada e registrada. O proprietário decide dentro do escopo delegado; outros participantes podem apontar riscos, conflitos, restrições e pedir reconsideração, mas não substituem silenciosamente o proprietário.

O Orquestrador, se vier a ser aprovado como componente futuro, terá autoridade de coordenação, roteamento e controle do workflow; essa função não transfere para ele decisões técnicas delegadas a especialistas. O protocolo de comunicação e qualquer arquitetura de agentes permanecem fora do escopo desta Policy.

## 6. Rastreabilidade mínima

A unidade SDD deve permitir seguir a cadeia:

`requisito → decisão de PLAN → TASK → implementação → teste/evidência → CONVERGE`

O vínculo deve ser verificável nos artefatos e evidências pertinentes. Uma declaração de conclusão sem evidência suficiente não satisfaz CONVERGE.

### Referências Técnicas

Decisões técnicas que dependam materialmente de Technical Reference vigente devem identificar REF ID e versão/identidade aplicável quando necessário à rastreabilidade. Em PLAN, declarar a referência quando uma decisão depender dela. Em ANALYZE, verificar quando materialmente relevante se falta referência necessária, se a fonte é incompatível, se um exemplo foi extrapolado para regra, se adaptação entre linguagens carece de justificativa ou se há conflito não resolvido. Em IMPLEMENT, consultar somente as referências necessárias à tarefa autorizada, sem leitura indiscriminada da base. Em CONVERGE, conferir rastreabilidade à versão pertinente quando a conformidade alegada depender materialmente de uma referência. Isso não cria etapa adicional: o pipeline permanece `SPEC → PLAN → TASKS → ANALYZE → IMPLEMENT → CONVERGE`. A governança detalhada consta em [POL-0000000004 — Fontes Técnicas de Referência e Base Conceitual](POL-0000000004-fontes-tecnicas-referencia.md).

## 7. Referência metodológica externa

GitHub Spec Kit é referência metodológica externa, não autoridade normativa do RickCraft. Sua documentação oficial descreve artefatos e etapas semelhantes e um comando de análise que reporta conflitos, lacunas e ambiguidades para correção na etapa de origem. O RickCraft adota somente as regras explicitadas nesta Policy; comandos, templates, arquivos opcionais e convenções específicas do Spec Kit não são importados automaticamente.

## 8. Limites desta Policy

Esta Policy não aprova requisitos funcionais, grupos de Specification, arquitetura multiagente, distribuição final de Decision Owners, Skill, Plugin, MCP, ferramentas, evals ou runtime. Não inicia automaticamente uma unidade SDD.
