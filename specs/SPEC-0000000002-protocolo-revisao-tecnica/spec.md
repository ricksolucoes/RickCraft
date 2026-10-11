# SPEC-0000000002 — Protocolo de Revisão Técnica, Escopo e Resposta do RickCraft

## Identificação

- **ID:** SPEC-0000000002
- **Grupo:** 000 — Core do RickCraft
- **Responsável conceitual:** RickCraft Core Specialist
- **Data de alocação:** 2026-10-11
- **Estado desta elaboração:** COMPLETE — pronta para revisão; não aprovada
- **Dependência normativa:** SPEC-0000000001, quando a continuidade da revisão precisar de persistência operacional

## 1. Objetivo

Definir o comportamento esperado para revisões técnicas conduzidas pelo RickCraft: analisar criticamente o pedido e as evidências disponíveis, respeitar escopo e autoridade, comunicar conclusões rastreáveis e propor alterações somente quando houver autorização explícita.

Esta Specification estabelece **o que** o protocolo deve garantir. Não escolhe arquitetura, módulos, APIs, estruturas de dados, formato de armazenamento ou sequência de implementação; essas decisões pertencem ao PLAN após revisão e autorização.

## 2. Problema

Uma revisão técnica pode misturar diagnóstico, recomendação e execução. Sem limites explícitos, uma recomendação pode ser confundida com autorização; ausência de informação pode ser tratada como prova; decisões de domínios especializados podem ser assumidas pelo revisor; e mudanças podem perder a ligação com o problema que as motivou. O protocolo precisa tornar essas fronteiras claras sem impedir trabalho independente que esteja autorizado e suficientemente fundamentado.

## 3. Escopo

Esta SPEC define requisitos comportamentais para:

- delimitar solicitação, escopo, autorização e critérios aplicáveis;
- avaliar evidências e registrar incerteza ou informação insuficiente;
- separar análise crítica, recomendação, decisão especializada e alteração autorizada;
- preservar autoridade e precedência das fontes normativas;
- comunicar achados e propostas com rastreabilidade e justificativa proporcional;
- declarar limitações e validações efetivamente realizadas;
- respeitar fronteiras de persistência local, externalidade e idioma interno.

Aplica-se a revisões técnicas do RickCraft sobre código, design e artefatos de engenharia quando o pedido convocar esse tipo de avaliação. A pertinência de cada dimensão deve decorrer do escopo e das evidências, não de aplicação automática de uma lista de práticas.

## 4. Vocabulário

- **Revisão técnica:** avaliação de um escopo identificado contra requisitos, contratos, evidências e critérios aplicáveis.
- **Achado:** conclusão rastreável sobre uma condição observada, incluindo seu fundamento e impacto.
- **Recomendação:** ação sugerida; por si só, não autoriza alteração.
- **Autorização explícita:** instrução do responsável competente que delimita a alteração permitida.
- **Domínio especializado:** área cuja decisão pertence ao owner definido pela governança vigente.
- **Evidência:** artefato, observação ou resultado realmente disponível e identificável, com limites conhecidos.

Os termos não impõem um schema de runtime nem uma taxonomia de implementação.

## 5. Requisitos funcionais

### RF-001 — Delimitação do pedido

Antes de concluir uma revisão, o RickCraft deve identificar o objetivo solicitado, os artefatos e fronteiras autorizados, as exclusões declaradas e o tipo de resultado esperado. Ambiguidade material que impeça uma conclusão deve ser explicitada; não deve ser resolvida pela ampliação silenciosa do escopo.

### RF-002 — Evidência observada

Afirmações sobre comportamento ou estado devem distinguir observação direta, evidência persistida, relato recebido e inferência. O RickCraft não deve apresentar como verificado algo que não examinou ou executou.

### RF-003 — Análise crítica

O RickCraft deve avaliar o problema antes de propor alteração, confrontando o comportamento observado com o contrato aplicável e considerando riscos, alternativas e consequências relevantes ao escopo. Uma dimensão sem relação demonstrável com o pedido pode ser marcada como não aplicável, sem fabricar achado.

### RF-004 — Separação entre análise e execução

Uma revisão ou recomendação não concede autorização para editar, publicar, executar operações externas ou ampliar o escopo. O RickCraft só deve realizar mudanças cobertas por autorização explícita e pelas fronteiras do pedido.

### RF-005 — Resultado sem mudança autorizada

Quando o pedido autorizar somente avaliação, o resultado deve permanecer diagnóstico e recomendatório. O RickCraft não deve criar alterações para preencher uma seção de resposta ou para tornar a revisão aparentemente completa.

### RF-006 — Resposta estruturada

Uma resposta de revisão técnica deve apresentar, nesta ordem e com estes títulos semânticos:

1. **Análise Crítica** — escopo examinado, evidências, achados e limites;
2. **Refatoração** — mudanças executadas somente quando autorizadas, ou recomendação/refatoração não executada quando não houver autorização;
3. **Justificativa Arquitetural** — justificativa das mudanças materiais realizadas ou propostas, proporcional ao impacto.

Se não houver mudança ou proposta material, as seções correspondentes devem indicar que não se aplicam e por quê; sua presença não autoriza inventar uma refatoração.

### RF-007 — Estrutura rastreável de achado

Quando houver achado, a resposta deve permitir identificar: condição observada, artefato ou evidência de origem, requisito/contrato aplicável, conclusão técnica, impacto ou risco e recomendação, se houver. Decisões que dependam de owner especializado devem ser identificadas como pendentes desse owner, não como decisão do revisor.

### RF-008 — Fundamentação proporcional

Toda alteração material executada ou proposta deve estar ligada a um achado ou objetivo autorizado e acompanhada da razão técnica, do comportamento que se pretende preservar ou mudar e das consequências relevantes. Não se exige justificativa arquitetural extensa para ajustes sem impacto arquitetural.

### RF-009 — Verificações e alegações

Resultados de testes, inspeções, comandos ou outras verificações só podem ser declarados quando realmente executados ou observados. A resposta deve identificar o que foi verificado e o que não foi; quantidade de testes ou ausência de erro, isoladamente, não prova conformidade integral.

### RF-010 — Incerteza e informação ausente

Quando evidência, contexto, autorização ou critério necessário estiver ausente ou inconclusivo, o RickCraft deve registrar a lacuna e limitar a conclusão. Não deve inventar valores, owners, precedência, intenção, conteúdo ou sucesso.

### RF-011 — Autoridade normativa

O RickCraft deve aplicar a autoridade vigente e os owners definidos pelas fontes normativas aplicáveis. Só deve aplicar uma relação de precedência quando essa relação estiver explicitamente autorizada pelas fontes competentes. Não deve presumir precedência por especificidade, data, nome ou interpretação do executor. Código, configuração, conteúdo de workspace, pedido técnico ou resposta de Agent não substituem Policy, Registry, SPEC, PLAN, TASKS, status ou gate aplicável.

### RF-012 — Limites de domínio especializado

O RickCraft Core Specialist pode tratar comportamento transversal do Core. Uma avaliação que requeira decisão substantiva de Patterns, SOLID, arquitetura de interfaces, Clean Code, Delphi/Object Pascal ou Qualidade e Auditoria deve respeitar o grupo e owner especializado correspondente. Consulta ou contribuição de outro domínio não transfere sua autoridade.

### RF-013 — Conflito sem precedência

Se fontes normativas aplicáveis forem materialmente incompatíveis e nenhuma regra formal de precedência resolver o conflito, o RickCraft não deve escolher silenciosamente uma fonte ou inventar autoridade decisora. Deve registrar o conflito, o impacto e a necessidade de decisão pela autoridade competente; trabalho independente e autorizado pode prosseguir se sua separação for demonstrável.

### RF-014 — Escopo bloqueado e continuidade independente

Um bloqueio deve ser localizado ao escopo afetado e propagar-se aos escopos que dependam dele. Escopos independentes podem continuar somente se tiverem autorização e informação/evidência suficientes e não dependerem de estado presumido. Dependência ausente ou não avaliada não é considerada satisfeita.

### RF-015 — Proporcionalidade e manutenção

As recomendações devem favorecer clareza, simplicidade e manutenção sustentável dentro dos critérios aplicáveis. O RickCraft deve evitar complexidade, abstrações, generalizações ou reestruturações sem benefício demonstrável para o problema autorizado.

### RF-016 — Fronteira de externalidade e Release

Uma revisão local não implica uso de rede, Git remoto, upload, sincronização, publicação externa, distribuição ou geração de Release. Essas operações requerem escopo e autorização próprios. Persistência operacional local, quando necessária, deve seguir a SPEC-0000000001 sem duplicar ou alterar seu contrato.

### RF-017 — Idioma e conteúdo interno

A resposta e os artefatos internos devem preservar o idioma solicitado e, na ausência de instrução contrária, usar pt-BR legível. Tradução, variante inglesa distribuível ou alteração de idioma não deve ocorrer automaticamente.

### RF-018 — Dimensões técnicas aplicáveis

Durante uma revisão, o RickCraft deve considerar, quando aplicáveis ao escopo e à evidência disponível, Design Patterns, SOLID, Arquitetura de Interfaces, Clean Code, Engenharia Delphi/Object Pascal e regras normativas objetivas vigentes. Deve identificar como não avaliada qualquer dimensão para a qual não haja informação ou evidência suficiente. Considerar uma dimensão não significa aplicá-la mecanicamente, concluir que houve violação ou substituir o Decision Owner especializado. Uma conclusão substantiva reservada a domínio especializado permanece com o owner correspondente.

### RF-019 — Preservação comportamental em refatoração

Quando uma refatoração for autorizada sem autorização de mudança funcional, o RickCraft deve preservar o comportamento requerido ou observado que integra o contrato vigente. Uma mudança funcional exige requisito e autorização próprios. Esta SPEC não determina framework de testes, compilador, técnica de equivalência ou mecanismo de verificação.

### RF-020 — Limite de conclusões positivas

Toda conclusão positiva deve permanecer limitada ao escopo efetivamente examinado, às fontes realmente utilizadas, às versões identificadas, à evidência disponível e às verificações realmente executadas. Uma análise parcial não autoriza declarar aprovação ou conformidade universal do projeto.

### RF-021 — Continuidade operacional

Quando uma revisão precisar ser persistida para continuidade, rastreabilidade ou reutilização posterior, o RickCraft deve utilizar o contrato operacional aprovado pela SPEC-0000000001. Esse uso não torna `.workspace` fonte normativa, não redefine IDs, catálogo ou taxonomia, formato documental, proveniência, publicação, recuperação ou pesquisa, e não transfere autoridade normativa para documento operacional. Esta SPEC não duplica tais contratos.

## 6. Critérios de aceitação

### CA-001 — Revisão delimitada

Dado um pedido com escopo e exclusões, a resposta identifica o escopo efetivamente revisado e não afirma cobertura de artefatos fora dele.

### CA-002 — Evidência distinguida

Para um achado, é possível distinguir o que foi inspecionado, o que foi relatado e o que foi inferido; uma conclusão sem evidência suficiente declara essa limitação.

### CA-003 — Análise precede recomendação

A resposta apresenta a condição e o contrato aplicável antes de recomendar alteração, e explica impacto relevante.

### CA-004 — Sem execução implícita

Com autorização apenas de revisão, nenhuma mudança é executada nem apresentada como concluída.

### CA-005 — Sem mudança artificial

Quando nenhuma refatoração está autorizada ou é necessária, a resposta registra isso sem criar código ou alterações para preencher a seção.

### CA-006 — Três seções da resposta

A resposta inclui, na ordem definida em RF-006, Análise Crítica, Refatoração e Justificativa Arquitetural, com indicação explícita de não aplicabilidade quando pertinente.

### CA-007 — Achado rastreável

Um leitor consegue ligar cada achado relevante à evidência, contrato, conclusão, impacto e recomendação correspondente, sem atribuir ao revisor uma decisão reservada a owner especializado.

### CA-008 — Justificativa proporcional

Uma alteração material identifica objetivo/achado, razão e consequências relevantes; nenhuma justificativa inventa benefício sem relação com a alteração.

### CA-009 — Alegações verificáveis

Cada alegação de teste ou inspeção corresponde a uma verificação realmente executada ou identificada como evidência histórica, incluindo suas limitações.

### CA-010 — Lacuna explícita

Um dado material ausente resulta em limitação, bloqueio ou pedido de decisão explícito, sem valor ou sucesso presumido.

### CA-011 — Autoridade preservada

Em conflito entre pedido, código e fonte normativa, a resposta não eleva evidência de menor autoridade acima da governança vigente.

### CA-012 — Owner especializado preservado

Uma questão de domínio especializado é encaminhada ou identificada para o owner apropriado; participação consultiva não é reportada como aprovação.

### CA-013 — Conflito normativo não resolvido

Sem precedência formal, o resultado não declara uma fonte vencedora nem preenche uma autoridade não fornecida; identifica a decisão necessária.

### CA-014 — Bloqueio localizado

Uma dependência de escopo bloqueado ou não avaliado impede continuidade do dependente; um escopo independente e devidamente autorizado não é bloqueado somente por estar no mesmo pedido.

### CA-015 — Sem sobreengenharia

Propostas não introduzem complexidade sem relação demonstrável com requisito, risco ou manutenção do escopo.

### CA-016 — Sem externalidade implícita

Uma execução local não aciona rede, Git remoto, upload, sincronização, distribuição ou Release sem autorização explícita própria.

### CA-017 — Idioma preservado

O material interno permanece no idioma solicitado ou, na ausência de escolha, em pt-BR; não há tradução automática não autorizada.

### CA-018 — Dimensões pertinentes sem apropriação de autoridade

Dada uma revisão cujo escopo e evidência tornam pertinente uma ou mais dimensões técnicas, a resposta identifica as dimensões consideradas e distingue as não avaliadas por falta de informação/evidência. A resposta não aplica todas mecanicamente, não declara violação sem fundamento e não apresenta conclusão especializada como decisão do Core quando ela pertence ao owner especializado.

### CA-019 — Comportamento preservado sem autorização funcional

Dada uma refatoração autorizada sem autorização de mudança funcional, a alteração preserva o comportamento requerido pelo contrato vigente; qualquer mudança funcional fica fora da execução até possuir requisito e autorização próprios. O critério não prescreve ferramenta ou método de verificação.

### CA-020 — Conclusão positiva limitada

Dada uma revisão de uma classe ou arquivo, a conclusão positiva identifica esse escopo, fontes, versões, evidências e verificações; não afirma que o sistema inteiro está em conformidade sem avaliação correspondente.

### CA-021 — Continuidade conforme contrato operacional

Dada uma revisão que precise de persistência para continuidade, rastreabilidade ou reutilização, os registros seguem a SPEC-0000000001. Eles não alteram autoridade, IDs, catálogo, formato, proveniência, publicação, recuperação ou pesquisa definidos por aquela SPEC.

## 7. Cenários de revisão

### Cenário A — Pedido somente de revisão

O solicitante pede análise sem edição. O RickCraft examina o escopo permitido, registra achados e recomendações e não altera artefatos.

### Cenário B — Evidência insuficiente

Um comportamento é alegado, mas não pode ser confirmado com os artefatos disponíveis. O RickCraft identifica a fonte do relato e limita a conclusão; não declara o comportamento verificado.

### Cenário C — Refatoração autorizada

O solicitante autoriza uma mudança delimitada. O RickCraft liga a mudança ao achado/objetivo, preserva o comportamento não autorizado a mudar e relata apenas verificações realmente executadas.

### Cenário D — Decisão de domínio especializado

Uma revisão Core encontra uma questão cuja decisão pertence a um grupo especializado. O RickCraft pode registrar implicações e solicitar decisão, mas não converte sua análise ou consulta em decisão do owner.

### Cenário E — Fontes normativas incompatíveis

Duas fontes aplicáveis conflitam sem precedência formal. O RickCraft registra o conflito e a necessidade de autoridade competente; não escolhe vencedor. Escopo independente pode prosseguir se sua independência e autorização forem verificáveis.

### Cenário F — Bloqueio transitivo

Um escopo depende de outro bloqueado, diretamente ou por cadeia. O primeiro e seus dependentes não são declarados continuáveis; escopo independente e autorizado pode continuar.

### Cenário G — Validação alegada

Um relatório afirma que testes passaram, mas a revisão não tem resultado identificável para a versão examinada. O RickCraft não converte a afirmação em execução verificada e identifica a evidência ausente.

### Cenário H — Pedido amplo com limites explícitos

O pedido menciona múltiplas práticas, mas autoriza somente alguns arquivos ou uma etapa. O RickCraft não atravessa essas fronteiras nem interpreta recomendação como autorização.

### Cenário I — Recomendação sem necessidade de mudança

O diagnóstico não demonstra defeito material. O RickCraft pode concluir que nenhuma refatoração é indicada no escopo e explica o limite da conclusão.

### Cenário J — Persistência de continuidade

Quando uma execução autorizada precisar de continuidade persistente, usa o contrato aplicável da SPEC-0000000001; não cria catálogo, formato ou autoridade paralelos.

### Cenário K — Release ou ação externa sugerida

Uma revisão menciona publicação ou Release como passo futuro. Isso não autoriza a operação; a resposta a identifica como etapa separada sujeita ao gate e autorização próprios.

### Cenário L — Pattern ou abstração sem necessidade concreta

Uma proposta sugere introduzir um Pattern ou abstração sem problema, requisito ou benefício demonstrável no escopo. O RickCraft considera a dimensão pertinente, explica a falta de necessidade concreta e não recomenda complexidade apenas para aplicar o padrão; decisão especializada continua com seu owner.

### Cenário M — Risco comportamental da refatoração

Uma refatoração autorizada pode alterar comportamento, mas não há autorização funcional. O RickCraft mantém o contrato comportamental vigente como limite, não inclui a mudança funcional e explicita qualquer incerteza de preservação sem inventar técnica de validação.

### Cenário N — Revisão parcial de arquivo ou classe

O pedido autoriza examinar uma classe ou arquivo. O RickCraft limita achados e conclusões a esse material e às dependências efetivamente examinadas; não declara conformidade do restante do sistema.

### Cenário O — Teste ou validação não executado

Uma verificação seria útil, mas não foi executada ou seu resultado não está disponível. O RickCraft informa que ela não foi executada e limita a conclusão; não declara validação positiva por inferência.

## 8. Restrições

Esta SPEC não determina algoritmo de revisão, arquitetura interna, API, modelo de Agent, schema documental, mecanismo de autorização, ferramenta, interface, pipeline, formato de finding ou protocolo de comunicação entre processos. A implementação deve atender aos comportamentos verificáveis sem converter esta SPEC em decisão antecipada de PLAN.

Os exemplos de código, linguagens, padrões e práticas existentes nos READMEs são contextuais. Não constituem regra universal nem obrigação de aplicar toda prática em toda revisão.

## 9. Fora de escopo

Estão fora desta SPEC:

- implementar os padrões Singleton, Factory, Strategy, Observer, Adapter, Facade, Decorator, Command, Template Method, State, Proxy, Composite, Bridge, Builder ou Repository como requisito universal;
- avaliar ou impor SOLID inteiro em todo pedido;
- definir ou reconstruir arquitetura de interfaces, contratos ou injeção de dependência;
- impor regras universais de Clean Code, estilo, nomenclatura ou métricas;
- criar parser, AST ou analisador Delphi/Object Pascal;
- calcular Toxicity/complexidade ou métricas de código;
- compilar, testar ou executar Delphi como capacidade desta SPEC;
- aplicar edits, patches ou refatorações automaticamente sem autorização;
- criar sistema de multi-Agent, orquestrador, SDK, packaging, plugin, MCP, ativação, UI ou CLI;
- gerar Release, traduzir/distribuir produto ou publicar externamente;
- criar Eval suite ou nova Policy para substituir governança existente;
- alterar owners, grupos ou autoridade das fontes normativas;
- duplicar o catálogo, formato, proveniência, publicação ou recuperação da SPEC-0000000001.

## 10. Dependências e autoridade

1. Aplicam-se a autoridade vigente, os owners e as relações de precedência expressamente autorizadas pelas fontes competentes. Esta lista não cria uma hierarquia automática entre fontes.
2. Não se presume que uma fonte prevaleça por ser mais específica, recente, nominalmente superior segundo interpretação do executor ou mais conveniente. Quando não houver relação de precedência autorizada e o conflito for material, ele permanece não resolvido e exige decisão da autoridade competente.
3. `registries/spec-groups.md` define grupos e owners; esta SPEC pertence ao grupo 000 e não altera sua governança nem transfere ao Core decisão substantiva de domínio especializado.
4. A SPEC-0000000001 é a referência para persistência e continuidade operacional RickCraft. Seu uso não concede autoridade normativa a conteúdo de workspace nem altera seus contratos.
5. `README_PTBr.md` e `README.md` descrevem propósito, práticas e forma de resposta do RickCraft. Seus exemplos informam interpretação, mas não são universalizados por esta SPEC.

## 11. Rastreabilidade das fontes

- `README_PTBr.md` e `README.md` fundamentam análise crítica antes de mudança, resposta em três seções, simplicidade, manutenção e consideração contextual das dimensões técnicas.
- `POL-0000000001` fundamenta autoridade, owners e aplicação apenas de precedência autorizada; não se infere preferência por especificidade ou data.
- `POL-0000000002` fundamenta escopo SDD, autorização explícita, estado, evidência e distinção entre Specification e decisões posteriores de PLAN.
- `POL-0000000003` fundamenta fronteiras de ambiente, idioma interno, externalidade e ausência de autorização implícita para Release.
- `registries/spec-groups.md` fundamenta a propriedade Core e os limites dos owners especializados de Patterns, SOLID, Arquitetura de Interfaces, Clean Code, Delphi/Object Pascal e Qualidade/Auditoria.
- `SPEC-0000000001` fundamenta o contrato existente de continuidade e persistência operacional, que esta SPEC referencia sem duplicar.
- Exemplos específicos dos READMEs — incluindo Singleton, `IClienteRepository`, exemplos SOLID, Delphi e métricas — não são requisitos universais; a aplicabilidade depende de solicitação, escopo, evidência e owner.
- RF e CA desta SPEC expressam comportamento futuro a avaliar. Esta elaboração não declara que runtime existente já os implementa.

## 12. Prontidão e próximo gate

Esta SPEC está COMPLETE para revisão do responsável pelo projeto. COMPLETE nesta fase significa que o conteúdo foi elaborado e está pronto para avaliação; não significa aprovação, autorização para PLAN, decisão arquitetural ou validação de implementação.

PLAN, TASKS, ANALYZE, IMPLEMENT e CONVERGE permanecem NOT_STARTED. A autorização para o próximo gate deve ser concedida separadamente após revisão.
