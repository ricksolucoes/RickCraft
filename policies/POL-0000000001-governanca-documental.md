# POL-0000000001 — Governança documental

- **Estado:** Proposta para aprovação
- **Escopo:** documentos normativos e registros controlados do RickCraft
- **Autoridade:** responsável pelo projeto aprova esta Policy e suas alterações
- **Dependências:** nenhuma

## 1. Objetivo

Estabelecer identificação, autoridade, precedência, ciclo de vida e rastreabilidade mínimos para Policies, Registries e Specifications, evitando regras implícitas e documentos sem finalidade demonstrada.

## 2. Categorias documentais

- **Policy:** regra normativa obrigatória do projeto.
- **Registry:** registro controlado por uma ou mais Policies; não cria regra normativa por si só.
- **Specification:** descreve requisitos e comportamento de uma unidade funcional. Uma Specification funcional deve possuir sua própria unidade SDD.

Um documento só deve ser criado quando houver necessidade identificada e autoridade para defini-lo. Exemplos e hipóteses não se tornam regras sem aprovação explícita.

## 3. Identidade e nomes

### 3.1 Policies

O identificador segue o formato `POL-0000000001-<slug>`, preservando o namespace `POL-` proposto pelo projeto. O número é a identidade estável da Policy; o slug é descritivo. A sequência numérica deve manter largura fixa de dez dígitos para ordenação lexical previsível. O identificador não representa versão.

IDs são únicos e não reutilizáveis. Revisões mantêm o mesmo ID. Uma Policy aposentada conserva sua entrada no Registry e seu ID não pode ser atribuído a outro documento. Uma nova Policy recebe o próximo número ainda não utilizado conforme o Registry.

### 3.2 Specifications

O formato inicial proposto é `SPEC-GGGSSSSSSS`: `GGG` identifica um grupo/domínio e `SSSSSSS` é uma sequência de sete dígitos dentro dele. O ID completo contém dez dígitos após `SPEC-`. Deve-se preservar a largura com zeros à esquerda para ordenação lexical.

O formato é mantido sem alteração nesta proposta. Grupos, seus significados, autoridades e alocações ainda dependem de decisão do responsável pelo projeto. Até que sejam aprovados e registrados, não se deve atribuir grupo nem criar Specification funcional. IDs não são versões, não são reutilizados e revisões não criam novo ID. Grupo aposentado não é reaproveitado para domínio diferente.

### 3.3 Slugs e diretórios

Slugs devem ser curtos, descritivos, estáveis e escritos em minúsculas, com palavras separadas por hífen. O diretório de uma Specification deve começar com seu ID, seguido de slug estável. Renomear o slug não muda a identidade da Policy ou Specification.

## 4. Autoridade e precedência

O responsável pelo projeto é a autoridade de aprovação das Policies e de decisões que não tenham sido delegadas formalmente.

Cada Policy deve declarar escopo, autoridade de aprovação e dependências. Uma Policy não pode alterar silenciosamente outra Policy, uma Specification aprovada ou decisão cujo proprietário seja outro domínio.

Em caso de conflito, prevalece nesta ordem: decisão explícita do responsável pelo projeto; Policy aprovada de escopo mais específico; Policy aprovada de escopo geral; documentos não normativos. Uma Policy não pode sobrepor decisão explícita posterior do responsável. Conflitos entre Policies de mesmo nível são questão em aberto até resolução explícita; não devem ser resolvidos por interpretação silenciosa.

## 5. Ciclo de vida

Estados controlados: `PROPOSTA`, `VIGENTE`, `SUBSTITUÍDA` e `APOSENTADA`.

- `PROPOSTA`: aguarda aprovação; não é requisito normativo vigente.
- `VIGENTE`: aprovada e aplicável.
- `SUBSTITUÍDA`: substituída por outro documento, mantendo histórico e referência ao sucessor.
- `APOSENTADA`: deixou de ser aplicável sem sucessor direto.

A aprovação, alteração, substituição ou aposentadoria deve ser autorizada pelo responsável pelo projeto ou por autoridade formalmente delegada. A alteração mantém o ID, registra a mudança e identifica impactos em documentos dependentes. IDs aposentados não são reutilizados.

## 6. Registry de Policies

`registries/policies.md` é o índice de identidade e ciclo de vida das Policies. Toda Policy proposta ou aprovada deve ser registrada com ID, título, estado, escopo, autoridade, dependências e, quando aplicável, sucessora. A inclusão no Registry não equivale a aprovação normativa.

O Registry deve preservar entradas substituídas e aposentadas para manter rastreabilidade. Alocações são feitas após consulta ao Registry; lacunas numéricas não são preenchidas retroativamente.

## 7. Rastreabilidade e alterações

Policies devem apontar dependências e documentos afetados. Alterações devem explicar motivo, autoridade, impacto e estado de aprovação. Specifications devem permitir rastrear requisitos a decisões de planejamento, tarefas, implementação e evidências de validação, conforme definido pela Policy SDD.

## 8. Questões reservadas

A aprovação desta Policy não aprova automaticamente os grupos/domínios de Specification, seus Decision Owners, nem qualquer arquitetura de agentes, Skill, Plugin, MCP ou runtime. Essas definições exigem análise e decisão próprias.