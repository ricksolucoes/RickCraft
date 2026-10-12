# POL-0000000001 — Governança documental

- **Estado:** Vigente
- **Escopo:** documentos normativos e registros controlados do RickCraft
- **Autoridade:** responsável pelo projeto aprova esta Policy e suas alterações
- **Dependências:** nenhuma

## 1. Objetivo

Estabelecer identificação, autoridade, precedência, ciclo de vida e rastreabilidade mínimos para Policies, Registries e Specifications, evitando regras implícitas e documentos sem finalidade demonstrada.

## 2. Categorias documentais

- **Policy:** regra normativa obrigatória do projeto.
- **Registry:** registro controlado por uma ou mais Policies; não cria regra normativa por si só.
- **Specification:** descreve requisitos e comportamento de uma unidade funcional. Uma Specification funcional deve possuir sua própria unidade SDD.
- **Technical Reference / Referência Técnica:** fonte de conhecimento técnico controlada e identificada persistentemente por Registry. Não se converte automaticamente em Policy; exemplos não criam obrigações por sua mera presença. Princípios técnicos podem fundamentar decisões do domínio competente, subordinados a regras normativas explícitas do RickCraft. A adoção, alteração ou retirada deve ser rastreável conforme POL-0000000004.

Um documento só deve ser criado quando houver necessidade identificada e autoridade para defini-lo. Exemplos e hipóteses não se tornam regras sem aprovação explícita.

## 3. Identidade e nomes

### 3.1 Policies

O identificador segue o formato `POL-0000000001-<slug>`, utilizando o namespace `POL-` adotado pelo projeto. O número é a identidade estável da Policy; o slug é descritivo. A sequência numérica deve manter largura fixa de dez dígitos para ordenação lexical previsível. O identificador não representa versão.

IDs são únicos e não reutilizáveis. Revisões mantêm o mesmo ID. Uma Policy aposentada conserva sua entrada no Registry e seu ID não pode ser atribuído a outro documento. Uma nova Policy recebe o próximo número ainda não utilizado conforme o Registry.

### 3.2 Specifications

O formato adotado para Specifications é `SPEC-GGGSSSSSSS`: `GGG` identifica um grupo/domínio de três dígitos e `SSSSSSS` é uma sequência de sete dígitos dentro do grupo. O ID completo contém dez dígitos após `SPEC-`. Zeros à esquerda são obrigatórios para preservar a largura e a ordenação lexical.

Grupos, seus significados, autoridades e alocações somente podem ser utilizados após aprovação e registro conforme a governança vigente. Enquanto um grupo não estiver aprovado e registrado, não se deve atribuir a ele IDs nem criar Specification funcional. IDs não são versões, não são reutilizados e revisões não criam novo ID. Grupo aposentado não é reaproveitado para domínio diferente.

`registries/specifications.md` é a fonte persistente de alocação e consumo dos IDs de Specification. Antes de materializar uma unidade SDD, deve-se confirmar que o grupo está `VIGENTE`, consultar esse Registry e registrar nele a alocação. A primeira sequência de cada grupo é `0000001`; as seguintes correspondem à maior sequência já alocada para o grupo, acrescida de um. Lacunas não são preenchidas retroativamente. O ID registrado fica consumido permanentemente, inclusive se a materialização falhar ou a unidade for cancelada. Diretórios servem para validação de consistência, não para determinar a próxima sequência.

O Registry deve identificar, no mínimo, ID completo, grupo, sequência, slug, título da Specification, caminho da unidade e data da alocação. O ID deve ser registrado antes da criação da pasta e dos artefatos da unidade.

### 3.3 Slugs e diretórios

Slugs devem ser curtos, descritivos, estáveis e escritos em minúsculas, com palavras separadas por hífen. O diretório de uma Specification deve começar com seu ID, seguido de slug estável. Renomear o slug não muda a identidade da Policy ou Specification.

## 4. Autoridade e precedência

O responsável pelo projeto é a autoridade de aprovação das Policies e de decisões que não tenham sido delegadas formalmente.

Cada Policy deve declarar escopo, autoridade de aprovação e dependências. Uma Policy não pode alterar silenciosamente outra Policy, uma Specification aprovada ou decisão cujo proprietário seja outro domínio.

Uma Policy somente pode restringir, especializar ou substituir regra de outra Policy quando a relação estiver explicitamente declarada em ambas as Policies ou na Policy que estabelece a relação, com referência às cláusulas afetadas, escopo, autoridade que aprovou e condições da relação. Não se presume precedência pela especificidade aparente do escopo, data, nome ou interpretação de quem executa.

Se duas Policies `VIGENTE` forem incompatíveis e não houver relação explícita autorizada que resolva o conflito, a unidade afetada fica `BLOQUEADA` até decisão do responsável pelo projeto. Nenhum agente ou executor escolhe qual regra seguir.

O responsável pelo projeto pode decidir uma mudança normativa. Para governar execuções futuras em caráter permanente, a decisão deve ser incorporada à Policy ou ao artefato normativo correspondente antes de ser aplicada. Uma exceção restrita a uma unidade SDD deve ser registrada no `status.md` dessa unidade, identificando autoridade, data, escopo, regra afetada, decisão, justificativa e referências aos artefatos impactados; ela não altera a regra geral. Uma conversa ou memória de agente, isoladamente, não constitui fonte normativa persistente.

## 5. Ciclo de vida

Estados controlados: `PROPOSTA`, `VIGENTE`, `SUBSTITUÍDA` e `APOSENTADA`.

- `PROPOSTA`: aguarda aprovação; não é requisito normativo vigente.
- `VIGENTE`: aprovada e aplicável.
- `SUBSTITUÍDA`: substituída por outro documento, mantendo histórico e referência ao sucessor.
- `APOSENTADA`: deixou de ser aplicável sem sucessor direto.

A aprovação, alteração, substituição ou aposentadoria deve ser autorizada pelo responsável pelo projeto ou por autoridade formalmente delegada. A alteração mantém o ID, registra a mudança e identifica impactos em documentos dependentes. IDs aposentados não são reutilizados.

Na aprovação, o estado da Policy e sua entrada em `registries/policies.md` devem mudar de `PROPOSTA` para `VIGENTE` e permanecer consistentes. A aprovação só é efetiva para execuções após ambos os registros refletirem `VIGENTE`. Se houver divergência, o estado é inválido para uso normativo e a aplicação da Policy fica `BLOQUEADA` até sincronização pela autoridade competente. O mesmo requisito de consistência aplica-se a mudanças posteriores de estado.

## 6. Registry de Policies

`registries/policies.md` é o índice de identidade e ciclo de vida das Policies. Toda Policy proposta ou aprovada deve ser registrada com ID, título, estado, escopo, autoridade, dependências e, quando aplicável, sucessora. A inclusão no Registry não equivale a aprovação normativa.

O Registry deve preservar entradas substituídas e aposentadas para manter rastreabilidade. Alocações são feitas após consulta ao Registry; lacunas numéricas não são preenchidas retroativamente.

## 7. Rastreabilidade e alterações

Policies devem apontar dependências e documentos afetados. Alterações devem explicar motivo, autoridade, impacto e estado de aprovação. Specifications devem permitir rastrear requisitos a decisões de planejamento, tarefas, implementação e evidências de validação, conforme definido pela Policy SDD.

## 8. Questões reservadas

A aprovação desta Policy não aprova automaticamente os grupos/domínios de Specification, seus Decision Owners, nem qualquer arquitetura de agentes, Skill, Plugin, MCP ou runtime. Essas definições exigem análise e decisão próprias.
