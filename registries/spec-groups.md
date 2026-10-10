# Registry de grupos de Specifications

- **Estado do Registry:** PROPOSTA
- **Autoridade para aprovação:** responsável pelo projeto
- **Fonte normativa:** POL-0000000001 — Governança documental; POL-0000000002 — Processo de desenvolvimento orientado por Specification
- **Finalidade:** propor domínios, códigos e Decision Owners conceituais para organizar futuras Specifications.

Este Registry é uma proposta submetida à aprovação. Seus grupos e Decision Owners não estão vigentes, não autorizam atribuição de IDs `SPEC` nem criação de Specifications funcionais. Os códigos abaixo são candidatos associados às propostas; tornam-se alocações vigentes somente após aprovação deste Registry. Policies permanecem no namespace `POL-` e não pertencem ao grupo 000.

## Grupos propostos

| Código | Domínio | Responsabilidade | Decision Owner conceitual | Estado | Observações |
|---|---|---|---|---|---|
| `000` | Core do RickCraft | Definir o comportamento essencial, o escopo funcional e os contratos transversais do próprio RickCraft quando não houver domínio mais específico. | RickCraft Core Specialist | PROPOSTO | Não é grupo guarda-chuva. Não decide Policies nem substitui o responsável pelo projeto; não assume decisões atribuídas aos domínios especializados. |
| `002` | Design Patterns | Avaliar necessidade de Pattern, adequação, inadequação, opção por não aplicar Pattern ou necessidade de contexto adicional. | Design Patterns Specialist | PROPOSTO | Decisão técnica exclusiva de seleção e adequação de Patterns; outros domínios podem apontar restrições e pedir reconsideração. |
| `003` | SOLID | Avaliar conformidade com SRP, OCP, LSP, ISP e DIP e determinar se há violação desses princípios. | SOLID Specialist | PROPOSTO | Pode solicitar reconsideração estrutural, mas não escolhe Pattern, não redefine requisitos e não assume decisões de arquitetura de interfaces. |
| `004` | Arquitetura de Interfaces | Decidir quando contratos de interface são necessários e definir fronteiras, responsabilidades e composição desses contratos. | Interface Architecture Specialist | PROPOSTO | Abrange a regra genérica de interfaces como contratos; exemplos de clientes/repositórios no README não limitam o domínio a esses conceitos. SOLID avalia conformidade com ISP/DIP. |
| `005` | Clean Code | Avaliar legibilidade, clareza, coesão de métodos, Code Smells e necessidade de simplificação sob os critérios genéricos do RickCraft. | Clean Code Specialist | PROPOSTO | Não impõe Pattern, redefine princípios SOLID ou altera convenções próprias de Delphi. Limites de Toxicity Metrics existentes não podem ser alterados por este grupo. |
| `006` | Engenharia Delphi/Object Pascal | Decidir sobre correção e convenções específicas da linguagem e do ecossistema Delphi/Object Pascal, incluindo construções, compatibilidade e aplicação das convenções Delphi existentes. | Delphi Engineering Specialist | PROPOSTO | Não redefine requisitos, arquitetura, escolha de Pattern, avaliação SOLID nem decisão sobre fronteiras de interfaces. |
| `008` | Qualidade e Auditoria | Verificar conformidade com Policies e artefatos aprovados, consistência entre SPEC/PLAN/TASKS/implementação, rastreabilidade e suficiência de evidências; determinar o resultado do gate de auditoria sob os critérios vigentes. | Quality Auditor | PROPOSTO | Pode registrar não conformidade e bloquear avanço quando critérios ou evidências falharem. Não escolhe a correção técnica: encaminha o achado ao Decision Owner responsável. |

Códigos omitidos nesta proposta não são reservados. Inclusão, alteração ou aposentadoria futura deve obedecer às Policies vigentes; um código associado a domínio aprovado não poderá representar outro domínio.

## Matriz de decisão e participação

| Decisão | Decide | Consulta | Pode contestar | Encaminhamento quando houver problema |
|---|---|---|---|---|
| Necessidade, escolha, inadequação ou não uso de Design Pattern | Design Patterns Specialist | SOLID, Arquitetura de Interfaces, Clean Code e Engenharia Delphi conforme o impacto | Os especialistas consultados, apresentando princípio, restrição ou evidência | Retorna ao Design Patterns Specialist para reconsideração; só ele altera a decisão de Pattern. |
| Existência e natureza de violação SOLID | SOLID Specialist | Arquitetura de Interfaces, Design Patterns, Clean Code ou Engenharia Delphi conforme o princípio afetado | Domínio afetado, apresentando contexto e evidência | O especialista SOLID mantém ou revê a conclusão; a decisão de remediação pertence ao domínio proprietário da estrutura afetada. |
| Fronteira e contrato de interface | Interface Architecture Specialist | SOLID e Engenharia Delphi; demais domínios afetados | Domínio afetado, com restrição ou risco explícito | Retorna ao proprietário de Arquitetura de Interfaces; SOLID pode registrar avaliação ISP/DIP, sem substituir a decisão do contrato. |
| Clareza, coesão de método, Code Smells e simplificação genérica | Clean Code Specialist | Engenharia Delphi, SOLID, Design Patterns ou Arquitetura de Interfaces conforme o impacto | Domínio afetado, com restrição ou evidência | Retorna ao Clean Code Specialist para julgamento dos critérios genéricos; decisões técnicas necessárias retornam ao proprietário especializado. |
| Construções, convenções e compatibilidade específicas de Delphi/Object Pascal | Delphi Engineering Specialist | Proprietário do domínio arquitetural afetado e demais especialistas pertinentes | Domínio afetado, com requisito, risco ou evidência | Retorna ao Delphi Engineering Specialist quanto à questão de linguagem; não altera decisões arquiteturais de outro proprietário. |
| Conformidade, rastreabilidade, evidências e disposição do gate de auditoria | Quality Auditor | Decision Owner do requisito, decisão ou artefato auditado | Decision Owner auditado pode apresentar evidência, contestar achado ou apontar conflito de Policy | O Auditor determina o resultado do gate conforme critérios vigentes. Achado técnico retorna ao Decision Owner apropriado; o Auditor não seleciona a solução. Conflito entre Policies vigentes segue POL-0000000001 e bloqueia até resolução competente. |
| Comportamento essencial, escopo funcional ou contrato transversal do RickCraft | RickCraft Core Specialist | Domínios especializados afetados | Qualquer domínio afetado, apresentando conflito ou impacto | Retorna ao Core somente para decisões explicitamente pertencentes ao comportamento central; decisões especializadas permanecem com seus proprietários. |

Consulta e contestação não transferem propriedade. Cada decisão possui um único Decision Owner. Se um pedido envolver decisões diferentes, cada decisão é separada e encaminhada ao proprietário correspondente; o orquestrador futuro poderá rotear e coordenar, mas não substituir o proprietário. Até existir tal mecanismo aprovado, esta regra é apenas governança conceitual e não implementa protocolo de comunicação.

O Quality Auditor possui autoridade sobre o resultado de auditoria/gate, não sobre o conteúdo técnico da correção. Um bloqueio por não conformidade não transfere para ele a decisão do domínio técnico.

## Fronteiras entre domínios

- **Design Patterns × SOLID:** SOLID é proprietário da conclusão sobre conformidade com princípios. Design Patterns é proprietário da decisão de aplicar ou escolher Pattern. Uma violação SOLID pode solicitar reconsideração, mas não troca o Pattern por outro.
- **SOLID × Arquitetura de Interfaces:** SOLID determina se ISP/DIP foram violados; Arquitetura de Interfaces decide o desenho concreto do contrato e suas fronteiras. Cada avaliação permanece no seu domínio.
- **Clean Code × Engenharia Delphi:** Clean Code trata critérios genéricos de leitura, coesão e Code Smells. Engenharia Delphi trata sintaxe, semântica, convenções e compatibilidade próprias de Delphi/Object Pascal. Uma regra Delphi explícita no README não é substituída por preferência genérica de Clean Code.
- **Qualidade/Auditoria × todos os domínios:** Auditoria decide conformidade e disposição do gate conforme critérios vigentes. A correção pertence ao proprietário técnico da decisão auditada.
- **Core × domínios especializados:** Core cobre somente comportamento central e contratos transversais sem proprietário mais específico. Não funciona como instância de recurso para decisões técnicas especializadas.

## Grupos avaliados e não adotados nesta proposta

| Grupo hipotético | Resultado | Justificativa |
|---|---|---|
| `001` Orquestração | Adiado | Coordenação, roteamento e workflow são capacidades/processos transversais. O princípio de que o orquestrador decide quem decide não lhe dá propriedade de decisões técnicas. A arquitetura multiagente e o protocolo ainda não estão definidos. |
| `007` Implementação | Não adotado | IMPLEMENT é etapa normativa do SDD, não domínio técnico independente. Decisões de implementação permanecem com os Decision Owners dos domínios envolvidos e o escopo autorizado pela unidade SDD. |
| `009` Skill | Adiado | Skill é forma futura de empacotamento/ativação, sem requisito funcional ou autoridade distinta demonstrada no README para justificar grupo agora. Comportamento central do RickCraft pode ser tratado em Core enquanto não houver domínio próprio aprovado. |
| `010` Plugin | Adiado | Tecnologia/forma potencial de distribuição, sem responsabilidade atual demonstrada no estado local. |
| `011` MCP / Tools | Adiado | Tecnologia ou mecanismo potencial; não há necessidade concreta nem autoridade de domínio atual demonstrada. |
| `012` Evals | Adiado | Método potencial de avaliação. Quality/Audit já cobre a decisão de conformidade e evidência; não há responsabilidade decisória independente de Evals comprovada agora. |
| `008` Qualidade / Auditoria | Mantido com escopo limitado | Apesar da hipótese reunir conceitos amplos, a responsabilidade distinta de avaliar conformidade, evidência e gates existe no processo vigente. O grupo proposto não toma decisões técnicas de remediação. |
| `005` Clean Code | Mantido com fronteira genérica | É um dos pilares explícitos do README e possui critérios próprios de clareza, coesão, Code Smells e análise de métodos. As convenções de linguagem continuam com Engenharia Delphi. |

## Fundamento local

O `README_PTBr.md` identifica quatro pilares — Design Patterns, SOLID, Programação Orientada a Interfaces e Clean Code — e descreve a finalidade do RickCraft em governança técnica, arquitetura, qualidade e engenharia Delphi/Object Pascal. Também define regras de interfaces, convenções Delphi, limites de Toxicity Metrics, análise crítica e o papel de justificativas arquiteturais. Esses fatos fundamentam os domínios propostos, sem converter exemplos específicos em regras de domínio.

O README não especifica uma arquitetura final de agentes nem proprietários executáveis. Os nomes de Decision Owners acima são papéis conceituais propostos, não agentes implementados.

## Aprovação e uso

Todos os grupos e Decision Owners deste Registry estão `PROPOSTO`. A aprovação do responsável pelo projeto deve mudar o estado do Registry e dos grupos aprovados para `VIGENTE`, mantendo o artefato e o registro consistentes. Somente então os códigos aprovados podem ser usados para atribuir IDs de Specifications. Grupos não aprovados continuam sem alocação; nenhuma Specification funcional é criada por este Registry.