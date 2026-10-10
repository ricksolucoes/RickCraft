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
- `tasks.md` — divisão ordenada do trabalho em tarefas pequenas, executáveis, verificáveis e rastreáveis.

A estrutura não autoriza criar Specifications funcionais sem a decisão de grupo e escopo correspondente. ANALYZE, IMPLEMENT e CONVERGE são etapas/gates, não arquivos obrigatórios. Evidências adicionais persistentes só devem ser introduzidas quando houver necessidade definida.

## 3. Sequência normativa

`SPEC → PLAN → TASKS → ANALYZE → IMPLEMENT → CONVERGE`

Não se pode iniciar IMPLEMENT a partir de SPEC, PLAN ou TASKS sem ANALYZE aprovado. Se um estágio for alterado, todos os estágios posteriores afetados devem ser revalidados.

## 4. Responsabilidades e autoridade

### SPEC

Define o resultado requerido, comportamento, restrições e critérios de aceitação. Não deve antecipar decisões técnicas que pertencem ao PLAN.

### PLAN

Define decisões técnicas e arquiteturais para satisfazer a SPEC. Não altera requisitos silenciosamente. Decisões devem indicar justificativa, impactos, dependências e autoridade decisória.

### TASKS

Decompõe o PLAN em trabalho ordenado, executável, verificável e rastreável. Cada tarefa deve ter origem identificável e permanecer no escopo aprovado.

### ANALYZE

É um gate de consistência entre SPEC, PLAN e TASKS. Verifica requisitos sem cobertura, tarefas sem origem ou fora de escopo, decisões sem cobertura, dependências ausentes, contradições, ambiguidades, critérios de aceitação sem cobertura, testes ausentes e violações de autoridade. É análise; não altera artefatos silenciosamente. Cada achado retorna ao artefato proprietário. Somente resultado aprovado permite IMPLEMENT.

### IMPLEMENT

Executa somente tarefas autorizadas pelo gate ANALYZE aprovado. Não redefine requisitos, arquitetura, contratos, decisões de domínio ou escopo. Alteração necessária retorna ao artefato proprietário e invalida gates posteriores afetados.

### CONVERGE

Compara o produto real e as evidências disponíveis com SPEC, PLAN e TASKS. Verifica implementação, testes, resultados e evidências suficientes. Lacunas retornam ao estágio proprietário, com revalidação das etapas afetadas. Só se declara `CONVERGED` quando não restarem lacunas e houver evidência suficiente.

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