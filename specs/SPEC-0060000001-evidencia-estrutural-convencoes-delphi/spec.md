# SPEC-0060000001 — Evidência Estrutural e Convenções Delphi/Object Pascal

## Identificação

- **ID:** `SPEC-0060000001`
- **Grupo:** `006` — Engenharia Delphi/Object Pascal
- **Decision Owner conceitual:** Delphi Engineering Specialist
- **Data de alocação:** 2026-10-12
- **Estado da etapa SPEC:** COMPLETE — aguardando revisão externa
- **Slug:** `evidencia-estrutural-convencoes-delphi`
- **Idioma:** pt-BR
- **Dependências:** SPEC-0000000002 para protocolo transversal de revisão; SPEC-0000000001 somente quando persistência operacional for necessária, conforme os contratos vigentes.

## Objetivo

Definir o comportamento requerido para produzir observações Delphi/Object Pascal rastreáveis e verificar convenções objetivas da linguagem em código explicitamente fornecido e autorizado. A unidade distingue fatos mecânicos de interpretação especializada e preserva os limites de autoridade dos demais Decision Owners.

Esta SPEC define o que a capacidade deve garantir. Não escolhe parser, lexer, AST, biblioteca, expressão regular, compilador, representação intermediária, estratégia híbrida ou arquitetura de implementação; essas decisões pertencem a PLAN futuro.

## Problema

O RickCraft possui convenções Delphi e contratos declarados em suas fontes internas, mas a simples identificação de uma forma de código não autoriza julgar nome, arquitetura, princípios SOLID, necessidade de interface, escolha de Pattern ou conformidade de gate. Uma capacidade Delphi precisa registrar fatos e contexto suficientes para revisão por seu owner, sem ampliar autoridade ou converter exemplos em regras universais.

## Escopo

Esta unidade especifica uma capacidade especializada, limitada ao escopo explicitamente autorizado, que:

- observa código Delphi/Object Pascal e identifica construções relevantes às verificações aplicáveis;
- relaciona observações ao artefato, versão quando fornecida ou necessária, escopo e localização revisável;
- confere formas lexicais e estruturais objetivamente prescritas nas fontes vigentes;
- atribui ao Delphi Engineering Specialist interpretações que dependam de semântica, compatibilidade ou convenção Delphi ambígua;
- limita conclusões quando faltarem contexto, versão, target, diretiva ou evidência;
- produz evidência e achados Delphi que possam ser consumidos pelo protocolo transversal da SPEC-0000000002, sem duplicar seus contratos.

O comportamento é READ-ONLY. A unidade não edita nem reescreve código e não materializa recomendações como mudanças.

## Vocabulário

- **Observação Delphi:** fato identificado no código fornecido, com contexto e localização suficientes para revisão.
- **Verificação objetiva:** comparação mecânica entre forma observada e regra explícita, sem decidir desenho ou correção.
- **Interpretação Delphi:** decisão técnica sobre sintaxe, semântica, recurso, compatibilidade, ecossistema ou aplicação ambígua de convenção, atribuída ao Delphi Engineering Specialist.
- **Guard:** mecanismo futuro de verificação objetiva. Não é Decision Owner, não altera regras e não escolhe correção.
- **Resultado limitado:** registro de que evidência ou contexto disponível não sustenta conclusão mais ampla.

Esses termos descrevem comportamento requerido, não schema ou implementação.

## Requisitos funcionais

### RF-001 — Entrada explicitamente delimitada

A capacidade deve analisar somente código, artefatos, versões e escopos explicitamente fornecidos e autorizados. Não deve buscar ou incluir conteúdo fora do limite autorizado.

### RF-002 — Rastreabilidade da observação

Cada observação ou finding deve ser relacionável ao artefato examinado, à versão quando fornecida ou materialmente necessária, ao escopo, à construção observada e a uma localização suficiente para revisão posterior. A forma física da localização não é definida nesta SPEC.

### RF-003 — Evidência observada separada de inferência

O resultado deve distinguir fato diretamente observado, regra/fonte aplicada, interpretação, inferência e informação relatada. Não pode declarar como verificada uma construção que não foi examinada.

### RF-004 — Verificação de convenções lexicais Delphi

Quando as regras vigentes forem aplicáveis e o elemento estiver no escopo, a capacidade deve poder verificar a forma prescrita para prefixos `T`, `I`, `F`, `A` e `L`, identificando o tipo de elemento ao qual a convenção se aplica. A checagem lexical não decide se o nome é semanticamente claro, descritivo ou adequado; essa decisão pertence a Clean Code.

### RF-005 — Verificação da forma de constantes

Quando a regra vigente for aplicável, a capacidade deve verificar se constantes estão em caixa alta, começam e terminam com `_` e, quando compostas, separam palavras com `_`. O resultado deve apontar forma observada e regra, sem inferir qualidade semântica.

### RF-006 — Enumerados com escopo

A capacidade deve registrar fatos observáveis sobre `{$SCOPEDENUMS ON/OFF}` e o acesso qualificado de valores quando pertinente. Decidir se determinado enumerado ou contexto exige escopo pode requerer contexto de API e interpretação Delphi; sem esse contexto, o resultado deve ser limitado e não declarar violação por suposição.

### RF-007 — Forma Delphi de contratos de interface aprovados

Quando existir contrato de interface aprovado e fornecido no escopo, a capacidade deve poder verificar aspectos Delphi prescritos, conforme aplicáveis: GUID válido e único no contexto verificável; assinaturas; uso de `function` quando exigido pelo contrato vigente; presença de blocos/visibilidades prescritos; implementação de membros; posição de construtor e destrutor; convenção `class function New`; e tipo de retorno declarado. A verificação não decide se a interface deveria existir nem define fronteira, composição ou responsabilidade do contrato.

### RF-008 — Convenção `New`

Quando uma classe adotar `New` e a regra aplicável estiver definida, a observação deve distinguir retorno do tipo declarado pela API da regra mais específica de retorno pela interface correspondente quando a classe implementar contrato de interface. A capacidade não decide se Factory, Pattern ou método `New` é arquiteturalmente necessário.

### RF-009 — Recursos e semântica da linguagem

A capacidade pode produzir evidência e interpretação sobre recursos Delphi/Object Pascal, incluindo `[weak]`, dentro de contexto suficiente. Uma ocorrência de `[weak]` não é, por si só, finding nem solução universal. Conclusões sobre desenho de ownership/lifetime e relações arquiteturais são encaminhadas ao Decision Owner competente.

### RF-010 — Métricas estruturais explicitamente configuradas

Quando o escopo e a evidência permitirem, a capacidade deve poder registrar as quatro medidas e limites objetivos definidos no README vigente: Function Length acima de 20 linhas, Parameter Count acima de 6, If Depth acima de 5 e Cyclomatic Complexity acima de 6. O resultado contém medida, limite, escopo e localização revisável. Ultrapassar limite exige análise, mas não autoriza refatoração automática nem decide legibilidade, coesão, responsabilidade ou necessidade de extração, que permanecem com Clean Code ou o owner pertinente.

### RF-011 — Contexto de compatibilidade

Quando uma conclusão depender de versão do Delphi, compilador, plataforma/target, diretiva ou recurso habilitado, esses dados devem ser fornecidos ou estabelecidos por evidência adequada. A capacidade não inventa nem infere valores ausentes; sem eles, limita a conclusão ou solicita contexto.

### RF-012 — Ambiguidade e evidência insuficiente

Quando a construção ou regra aplicável não puder ser interpretada com contexto suficiente, a capacidade deve registrar ambiguidade/limitação e o dado necessário. Não presume intenção, diretiva, versão, plataforma, semântica de lifetime ou contrato arquitetural, nem emite conclusão autoritativa fora de sua competência.

### RF-013 — Separação entre verificação e Decision Owner

Um Guard ou executor pode reportar divergência objetiva contra regra já estabelecida. Não se torna autoridade por detectar a divergência, não altera a regra, não escolhe remediação e não determina se a regra deve ser aplicada em um caso ambíguo. Interpretação substantiva Delphi permanece no Delphi Engineering Specialist; decisão em outro domínio permanece com seu único owner.

### RF-014 — Fronteiras de autoridade preservadas

O Delphi Engineering Specialist decide somente questões de sintaxe, semântica, recursos, compatibilidade, ecossistema e interpretação de convenções Delphi ambíguas. Não decide seleção de Patterns; existência/natureza de violação SOLID; necessidade, fronteira ou composição arquitetural de interfaces; critérios genéricos de Clean Code; gates Quality/Audit; requisitos Core; nem decisões de outros owners. Evidência, consulta e contestação não transferem propriedade. Questões de outro domínio são encaminhadas ao owner correspondente.

### RF-015 — Compatibilidade com protocolo Core

Resultados Delphi devem poder fornecer evidência à dimensão `DELPHI_OBJECT_PASCAL` e alimentar, conforme o protocolo transversal da SPEC-0000000002 e o PLAN futuro, `EvidenceReference`, `SpecialistAssessment`, `ReviewFinding` e claims pertinentes. Esta unidade não redefine nem duplica esses contratos.

### RF-016 — READ-ONLY e ausência de efeitos implícitos

A capacidade observa, classifica, mede quando aplicável e produz evidência/achados. Não edita arquivos, aplica refatorações, cria interfaces, seleciona Patterns, corrige automaticamente, publica Release ou executa Git, rede, upload ou outra ação externa. Finding ou recomendação não é autorização para mudança física.

### RF-017 — Determinismo proporcional

Para as mesmas entradas, contexto, regras vigentes e autoridade, fatos e verificações objetivas devem produzir resultados equivalentes e rastreáveis. Limitações e ambiguidades devem ser representadas consistentemente. Esta exigência não prescreve algoritmo ou representação técnica.

### RF-018 — Sem ampliação silenciosa

A capacidade não analisa outra dimensão ou artefato, não promove exemplo a regra, não presume autorização e não amplia conclusão além do escopo e evidência examinados. Uma regra objetiva válida pode resultar em ausência de finding Delphi.

## Critérios de aceitação

- **CA-001:** Dado um pedido com arquivos/escopos autorizados e outros fora deles, as observações se restringem ao material autorizado.
- **CA-002:** Uma observação identifica artefato, escopo, construção e localização suficiente; versão é vinculada quando fornecida ou materialmente necessária.
- **CA-003:** O resultado permite distinguir fato observado, regra aplicada, interpretação, relato e inferência.
- **CA-004:** Prefixo objetivamente incompatível com o tipo de identificador resulta em evidência delimitada à forma lexical, sem decidir qualidade semântica do nome.
- **CA-005:** Nome com prefixo correto, mas cuja qualidade semântica seja questionável, não produz decisão de Clean Code pelo Delphi Engineering Specialist.
- **CA-006:** Constante fora do formato prescrito gera fato objetivo com forma observada e regra aplicável.
- **CA-007:** Diante de `SCOPEDENUMS` sem contexto suficiente para determinar se o escopo é exigido, o resultado permanece limitado e identifica contexto faltante.
- **CA-008:** Uma forma incorreta em contrato de interface aprovado pode gerar finding Delphi sem decidir se a interface deveria existir ou redesenhar seu contrato.
- **CA-009:** Uma ocorrência de `[weak]` tem sua semântica Delphi discutida somente quando o contexto sustenta a interpretação; não é tratada como solução universal de ownership/lifetime.
- **CA-010:** Dúvida sobre ISP/DIP é encaminhada ao SOLID Specialist; dúvida sobre necessidade ou fronteira de interface, ao Interface Architecture Specialist.
- **CA-011:** Possibilidade de Pattern não faz a unidade selecionar, recomendar como decisão própria, rejeitar ou implementar o Pattern; a questão é encaminhada ao Design Patterns Specialist.
- **CA-012:** Se versão Delphi, compilador, target ou diretiva for material e desconhecido, a unidade não inventa esse valor e limita a conclusão.
- **CA-013:** Código fora do escopo explicitamente autorizado não é analisado nem usado como evidência.
- **CA-014:** Regra objetiva comprovadamente válida pode resultar em nenhuma divergência/findings para aquela regra.
- **CA-015:** Evidência insuficiente resulta em limitação ou solicitação de contexto, sem conclusão positiva ou negativa presumida.
- **CA-016:** Solicitação de Quality/Audit para verificação produz evidência da regra observada, sem decidir PASS, FAIL ou CONVERGED.
- **CA-017:** Medidas de Toxicity excedidas são reportadas com métrica/limite/localização quando mensuráveis; não causam edição nem recomendação automática de extração.
- **CA-018:** `New` de classe que implementa interface é avaliado conforme a regra de retorno da interface aplicável; a capacidade não decide necessidade de Factory ou Pattern.
- **CA-019:** Resultado pode ser consumido pelos contratos da SPEC-0000000002 sem criar substitutos de seus tipos ou protocolo.
- **CA-020:** Execução exclusivamente read-only não edita código, aplica patch, cria arquivo de código ou executa externalidade; resultado/recomendação não concede autorização.
- **CA-021:** Entradas equivalentes sob as mesmas regras e contexto produzem observações objetivas equivalentes; o resultado declara seu escopo e não generaliza para código não examinado.

## Cenários de aceitação

### Cenário A — Prefixo incompatível com elemento

Um campo privado usa prefixo diferente de `F`. A unidade registra identificador, forma, regra lexical aplicável e localização. Não infere que o campo tenha responsabilidade inadequada.

### Cenário B — Nome lexicalmente válido, semanticamente questionável

Uma variável local possui prefixo `L`, mas o nome parece vago. A unidade pode preservar o fato lexical; não decide que o nome viola Clean Code nem cria finding sem avaliação do Clean Code Specialist.

### Cenário C — Constante fora do formato

Uma constante declarada como `NomeCompleto` é comparada com a convenção vigente. A unidade reporta a forma e os requisitos de caixa alta e underscores, sem renomeá-la.

### Cenário D — Enumerado e contexto de escopo insuficiente

Há enumeração sem diretiva identificável no trecho fornecido, mas não há contexto suficiente para decidir se o enumerado requer escopo. A unidade registra a limitação e não presume violação.

### Cenário E — Forma Delphi de interface aprovada

O contrato aprovado determina retorno por interface e visibilidades. Uma assinatura divergente pode gerar finding de conformidade Delphi; a unidade não decide se o contrato ou a interface deveria existir.

### Cenário F — Dúvida de ISP ou DIP

Uma interface parece ampla ou uma dependência concreta causa dúvida. A unidade pode fornecer fatos Delphi observados e encaminha a decisão sobre ISP/DIP ao SOLID Specialist.

### Cenário G — Necessidade de interface

Um chamador pergunta se determinada classe deveria expor interface. A unidade não decide necessidade ou fronteira do contrato; encaminha ao Interface Architecture Specialist.

### Cenário H — Pattern possível

Uma forma Delphi poderia ser expressa com um Pattern. A unidade não seleciona Pattern nem usa o exemplo de Pattern como prescrição; encaminha a decisão ao Design Patterns Specialist.

### Cenário I — Atributo `[weak]`

O código contém `[weak]`. Com contexto suficiente, a unidade explica a semântica do recurso Delphi relevante; não conclui que `[weak]` seja solução universal nem decide desenho de ownership/lifetime.

### Cenário J — Versão Delphi desconhecida

Uma conclusão depende de versão do compilador ou target, mas esses dados não foram fornecidos. A unidade não inventa configuração e limita o resultado.

### Cenário K — Código fora do escopo

O pedido autoriza uma unit, mas outra unit referenciada também está disponível. A segunda não é analisada até que seu escopo seja autorizado.

### Cenário L — Regra objetiva atendida

O identificador ou declaração examinada atende à regra objetiva aplicável. A unidade registra verificação correspondente e não fabrica finding.

### Cenário M — Evidência insuficiente

Um fragmento não permite determinar a declaração completa, unicidade de GUID ou contexto de diretiva. A unidade identifica o limite e solicita o material faltante.

### Cenário N — Pedido de Quality/Audit

Quality/Audit pede evidência sobre forma de declaração. A unidade reporta fatos, regra e limites; o Quality Auditor conserva a decisão do gate.

### Cenário O — Toxicity excedida

Uma função supera um dos limites explícitos de métrica. A unidade registra valor, limite e localização quando mensuráveis; a interpretação de coesão e remediação retorna a Clean Code ou ao owner pertinente. Nenhuma extração é aplicada automaticamente.

### Cenário P — Convenção `New`

Uma classe concreta implementa interface e declara `New` retornando a classe. A unidade confronta a declaração com a convenção aplicável que exige retorno pela interface, sem decidir se criação por `New` ou Factory é necessária.

## Restrições

1. Cada decisão tem um único Decision Owner conforme `registries/spec-groups.md`; consulta e contestação não transferem propriedade.
2. Delphi Engineering decide questões de linguagem e convenções Delphi ambíguas, não questões pertencentes a Patterns, SOLID, Interface Architecture, Clean Code, Quality/Audit ou Core.
3. Um Guard verifica regra existente; não se torna owner, não redefine regra e não escolhe remediação.
4. Exemplos contextuais do README, incluindo Singleton, encadeamento entre interfaces e `[weak]`, não são convertidos em obrigações além das regras expressamente enunciadas.
5. Toxicity acima do limite exige análise, mas não determina refatoração. Legibilidade, coesão, responsabilidade e extração permanecem julgamento do owner correspondente.
6. Conclusões ficam limitadas a artefatos, versões, contextos e localizações efetivamente examinados.
7. A unidade é read-only e não realiza externalidade nem operação Git/rede/Release.
8. Compatibilidade e detalhes de implementação permanecem para PLAN; esta SPEC não fixa ferramenta ou método de análise.

## Fora de escopo

Esta SPEC não decide nem implementa:

- parser, lexer, AST, biblioteca, regex, compilador, toolchain, representação intermediária ou estratégia de análise;
- implementação Python ou qualquer runtime;
- arquitetura de agentes, Orchestrator, Skill, package, Plugin ou MCP;
- refatoração automática, edição de `.pas`, `.dpr`, `.dpk` ou `.inc`, patch ou correção;
- seleção ou adequação de Design Patterns;
- avaliação ou redefinição de SRP/OCP/LSP/ISP/DIP;
- necessidade, fronteira, responsabilidade ou composição arquitetural de interfaces;
- julgamento genérico de clareza, coesão, Code Smells, legibilidade ou decisão de refatorar;
- Quality Gate, PASS/FAIL/CONVERGED ou autorização;
- Release, Git, rede, upload ou publicação externa;
- duplicação de `ReviewRequest`, `ReviewScope`, `EvidenceReference`, `VerificationClaim`, `ReviewFinding`, `SpecialistAssessment`, authority/precedence, lifecycle, publisher ou gap handling do Core.

## Dependências e autoridade

1. `registries/spec-groups.md` define o grupo `006` e o Delphi Engineering Specialist como owner de questões Delphi/Object Pascal. Esta SPEC não amplia essa autoridade.
2. A fonte normativa de cada convenção permanece o artefato vigente que a estabeleceu; esta unidade especifica observação e evidência, não cria unilateralmente regras fora do escopo autorizado.
3. O Design Patterns Specialist decide necessidade e seleção de Pattern; o SOLID Specialist decide existência/natureza de violação SOLID; o Interface Architecture Specialist decide necessidade e fronteira de interface; Clean Code decide critérios genéricos de clareza/cohesão/refatoração; Quality Auditor decide conformidade e gate; Core mantém comportamento transversal. Cada decisão permanece com seu owner único.
4. A SPEC-0000000002 fornece protocolo transversal de escopo, evidência, specialist assessment e findings. Esta SPEC define somente a compatibilidade necessária para resultados Delphi.
5. A SPEC-0000000001 aplica-se somente quando houver necessidade de persistência operacional; não é duplicada nem alterada por esta unidade.
6. Policies vigentes e contratos normativos do RickCraft prevalecem conforme as relações de autoridade formalmente estabelecidas. Nenhuma regra é escolhida por preferência, conveniência ou exemplo.

## Rastreabilidade inicial do domínio Engenharia Delphi/Object Pascal

A primeira Specification do domínio realiza a extração das regras Delphi aplicáveis encontradas nas fontes internas pertinentes. A matriz abaixo identifica cada regra individual/família aplicável do README e do Registry, a sua classificação, owner e tratamento. Os localizadores usam títulos de seção do `README_PTBr.md` e do `registries/spec-groups.md`, para permanecerem legíveis sem fixar números de linha. A matriz não promove exemplos a requisitos universais.

| Fonte e localização | Regra/fato rastreado | Papel e Decision Owner | Tratamento nesta SPEC |
|---|---|---|---|
| `README_PTBr.md` — “4. Clean Code” → “Convenção de Nomenclatura Delphi”; `registries/spec-groups.md` — auditoria da regra de prefixos | Classe `T`, interface `I`, campo privado `F`, argumento/parâmetro `A`, variável local `L`; a forma literal é separável da qualidade semântica do nome. | Verificação objetiva de convenção; Delphi Engineering interpreta ambiguidade. Clean Code é owner da qualidade semântica do nome. | RF-004; CA-004/005. Forma lexical incluída; julgamento semântico excluído/encaminhado. |
| `README_PTBr.md` — “4. Clean Code” → “Declaração de Variáveis”; `registries/spec-groups.md` — mesma família | Menor escopo, proximidade de declaração, nome descritivo e evitar abreviações obscuras. Prefixo `L` é convenção Delphi; descritividade e clareza são critérios interpretativos. | Clean Code Specialist para clareza e julgamento; Delphi Engineering apenas para a convenção de linguagem aplicável. | Prefixo coberto em RF-004. Julgamento genérico excluído; não há finding automático por heurística de nome. |
| `README_PTBr.md` — “Regra para Constantes”; `registries/spec-groups.md` — auditoria da regra de constantes | Caixa alta, `_` no início e fim e `_` entre palavras compostas. | Regra lexical objetiva; Delphi Engineering interpreta somente ambiguidade de aplicação. | RF-005; CA-006. Incluída como forma verificável, sem inferir conteúdo/qualidade do nome. |
| `README_PTBr.md` — “Enumerados com Escopo”; `registries/spec-groups.md` — auditoria de `SCOPEDENUMS` | Usar `{$SCOPEDENUMS ON}` quando enumeração exigir escopo explícito; qualificar acesso pelo tipo quando ativo; `OFF` pode limitar alcance da diretiva. | Fato de diretiva/acesso verificável; decisão de quando escopo é necessário pertence à interpretação Delphi e pode depender do owner da API. | RF-006; CA-007. Verificação de diretiva/acesso incluída; necessidade contextual limitada/encaminhada. |
| `README_PTBr.md` — “Programação Orientada a Interfaces” → regras antes de “Contrato e Implementação Básicos”; `registries/spec-groups.md` — “Estrutura declarativa de interfaces” | Operações de interface usam `function` conforme regra; métodos implementadores em `protected`; bloco `private` presente; `Create` protegido; `Destroy; override` público; GUID válido e único. | Contrato/necessidade/fronteira: Interface Architecture Specialist. Forma e semântica Delphi: Delphi Engineering Specialist. | RF-007; CA-008. Apenas contratos aprovados e fornecidos são verificados; desenho e necessidade excluídos. |
| `README_PTBr.md` — “Programação Orientada a Interfaces” e “Criação de Classes por New”; `registries/spec-groups.md` — família `New` | `class function New` retorna interface correspondente quando a classe implementa interface; na regra geral da classe concreta, retorna o tipo declarado pela própria API. | Forma Delphi e compatibilidade: Delphi Engineering; contrato que decide retorno abstrato/interface: Interface Architecture; escolha de Factory/Pattern pertence ao owner correspondente. | RF-008; CA-018/021 e cenário P. Precedência específica preservada; necessidade de `New`/Factory fora de escopo. |
| `README_PTBr.md` — exemplos em “Programação Orientada a Interfaces”, referência `[weak]`; `registries/spec-groups.md` — família de referências entre interfaces | `[weak]` é mostrado num exemplo para referência fraca em relação bidirecional e prevenção de ciclo de contagem; não é regra universal. | Semântica do atributo: Delphi Engineering. Desenho de ownership/lifetime e contrato: owner arquitetural competente. O exemplo permanece `REFERENCE_OR_EXAMPLE`. | RF-009; CA-009; cenário I. Inclui interpretação contextual e exclui prescrição universal. |
| `README_PTBr.md` — “Method Toxicity Metrics”, quatro subseções e “Aplicação pelo RickCraft”; `registries/spec-groups.md` — auditoria de métricas | Limites configurados: Function Length `20`, Parameter Count `6`, If Depth `5`, Cyclomatic Complexity `6`; ultrapassar exige análise, não divisão automática. | Medição objetiva/Guard; Clean Code Specialist interpreta legibilidade, responsabilidade, coesão e extração; outros owners decidem suas questões próprias. | RF-010; CA-017; cenário O. Métricas e limites incluídos; remediação e julgamento Clean Code não apropriados. |
| `README_PTBr.md` — exemplos Pascal de Singleton, interfaces e `New`; `registries/spec-groups.md` — “Fundamento local” e `REFERENCE_OR_EXAMPLE` | Exemplos demonstram construções/contextos; exemplos de Pattern não obrigam sua adoção. Observação de sincronização de Singleton é contextual ao Pattern. | Pattern: Design Patterns Specialist. Sintaxe/semântica Delphi quando material: Delphi Engineering. | Restrição 4 e fora de escopo. Nenhum exemplo específico é universalizado; regras expressas nas demais linhas continuam verificáveis. |
| `registries/spec-groups.md` — linha `006`, matriz de decisão e fronteiras entre Clean Code, Delphi, Interfaces, SOLID e Quality | Engenharia Delphi decide sintaxe, semântica, recursos, compatibilidade, ecossistema e aplicação ambígua de convenções; Guards podem verificar formas objetivas sem ganhar autoridade. | Delphi Engineering Specialist no domínio delegado; cada outro domínio conserva seu owner único. | RF-013/014; restrições e cenários F–N. Fronteiras e encaminhamentos explicitados. |
| `POL-0000000001`, `POL-0000000002`, `POL-0000000003` e `POL-0000000004`; `SPEC-0000000002` | Identidade/alocação, sequência SDD, autoridade, escopo, evidência, ambiente/read-only, referências técnicas e protocolo transversal de achados são regidos por fontes próprias. | Responsável pelo projeto/owners delegados; Core é dono do protocolo transversal; SPEC2 define contratos de resposta/evidência. | Incorporados por esta rastreabilidade e pelas dependências/limites; contratos e mecanismos não são duplicados. |

### Regras sem aplicação funcional nesta unidade

- Os 23 Patterns GoF, inclusive Singleton, Adapter, Factory, Strategy e demais padrões apresentados no README, não são selecionados por esta unidade. O README trata-os como padrões a utilizar quando houver justificativa, e o Registry atribui seleção/aplicabilidade ao Design Patterns Specialist. São contexto de fronteira, não regras de análise Delphi autônoma.
- SRP, OCP, LSP, ISP e DIP são decisões do SOLID Specialist. Fatos de sintaxe/declaração podem ser fornecidos como evidência, mas esta SPEC não determina violação.
- A necessidade, fronteira e composição de interfaces pertencem ao Interface Architecture Specialist. Esta SPEC só verifica forma Delphi de contrato previamente aprovado e no escopo.
- Menor escopo, clareza, nome descritivo, coesão, Code Smells, excesso conceitual e necessidade de extração são decisões de Clean Code ou do owner técnico correspondente. Medidas objetivas são reportáveis, sem se apropriar de interpretação ou correção.
- Objetivo geral de manutenção, postura de revisão, protocolo de resposta e exemplos de solução do README não adicionam regra Delphi individual além das regras explicitamente rastreadas acima; o protocolo pertence à SPEC2 e não é duplicado.
- As Technical References REF-0000000001 (Design Patterns), REF-0000000002 (Refactoring) e REF-0000000003 (índice de sites de Pattern) foram avaliadas como não materiais para esta elaboração: a unidade extrai convenções internas e delimita autoridade, sem selecionar Pattern ou técnica de refatoração. Nenhuma dessas fontes foi consultada.

## Prontidão e próximo gate

Esta SPEC está `COMPLETE — aguardando revisão externa`. A conclusão desta etapa significa que os requisitos, critérios, cenários, limites e rastreabilidade foram elaborados e revisados internamente; não significa aprovação externa, decisão de implementação ou gate posterior.

PLAN, TASKS, ANALYZE, IMPLEMENT e CONVERGE permanecem `NOT_STARTED`. Nenhuma etapa posterior está autorizada sem decisão separada.
