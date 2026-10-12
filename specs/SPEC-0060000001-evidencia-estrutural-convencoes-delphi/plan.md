# PLAN — SPEC-0060000001 — Evidência Estrutural e Convenções Delphi/Object Pascal

## Identificação e autoridade

- **SPEC:** `SPEC-0060000001`
- **Título:** Evidência Estrutural e Convenções Delphi/Object Pascal
- **Grupo:** `006` — Engenharia Delphi/Object Pascal
- **Decision Owner:** Delphi Engineering Specialist, limitado às decisões de linguagem delegadas ao grupo.
- **SPEC aprovada:** SHA-256 `62251E2D0533F2AFA31D0B56928F1F7F69DC1E72D3EC52BB17B23513696D7962`; Git blob `13fdb7aa0324b08bd145b69d0e7d844ff6d1c534`.
- **Data:** 2026-10-12
- **Estado corrente do PLAN:** BLOCKED — revisão externa `PLAN-REV-001`.

Este PLAN define uma arquitetura para satisfazer a SPEC aprovada. Não autoriza nem executa TASKS, ANALYZE, IMPLEMENT, CONVERGE ou Release.

## 1. Objetivo e limites

A unidade recebe código Delphi/Object Pascal e contexto explicitamente autorizado, identifica um subconjunto de construções estruturais, verifica convenções objetivas cuja regra já esteja estabelecida e produz observações limitadas, rastreáveis e compatíveis com o protocolo transversal da SPEC-0000000002.

A implementação será somente de leitura. O código-fonte é dado não confiável: não será compilado, interpretado, executado, importado como módulo ou usado para acionar diretivas externas. A unidade não abre arquivos por conta própria; o host fornece o texto e sua associação a artefato, versão e escopo autorizados. Não haverá escrita, Git, rede, upload, publicação, persistência implícita ou coordenação de outros especialistas.

O Delphi Engineering Specialist decide questões de sintaxe, semântica, recursos, compatibilidade, ecossistema e aplicação ambígua de convenções Delphi. Cada decisão de outro domínio permanece com seu único owner. Em especial, a unidade não escolhe Patterns, avalia SOLID, decide necessidade/fronteira de interfaces, interpreta critérios genéricos de Clean Code nem decide gates Quality/Audit.

## 2. Decisões arquiteturais

### D-01 — Limitar a implementação à base existente

- **Problema:** A capacidade precisa integrar-se ao RickCraft sem criar custo de distribuição desnecessário.
- **Alternativas:** Python 3.12+ e biblioteca padrão; dependência parser externa; serviço/compiler Delphi; runtime separado.
- **Decisão:** Permanecer no runtime Python 3.12+ e stdlib já usado pelo Core. Não adicionar dependência externa, compilador ou serviço nesta unidade.
- **Justificativa:** A SPEC requer observações e verificações delimitadas, não compilação ou gramática completa. Dependência externa só poderia ser reconsiderada mediante lacuna concreta demonstrada e autorização própria.
- **Impacto:** Distribuição e manutenção permanecem alinhadas ao Core; a fronteira sintática limitada deve produzir resultado limitado quando não consegue reconhecer com segurança uma construção.
- **RF/CA:** RF-001–003, RF-011–018; CA-001–003, CA-012–013, CA-019–021.
- **Dependências/owner:** Runtime RickCraft existente; decisão de escopo técnico deste PLAN sob Delphi Engineering, sem autoridade sobre decisões de outros grupos.

### D-02 — Tokenização delimitada seguida de reconhecimento estrutural parcial

- **Problema:** Expressões regulares isoladas confundem tokens em comentários/strings e não resolvem com segurança diretivas, escopos e declarações; parser completo excede a necessidade.
- **Alternativas:** Regex por arquivo; lexer completo Delphi; parser completo/AST; tokenizer controlado com reconhecedores parciais; compilador externo.
- **Decisão:** Usar tokenizer manual e limitado que preserve offsets e classifique identificadores, pontuação, strings, comentários e diretivas; sobre seus tokens, reconhecer somente as formas estruturais enumeradas em D-03. A representação sintática intermediária conterá apenas declarações e relações necessárias às regras desta SPEC.
- **Justificativa:** Separar lexicalmente comentários, strings e diretivas é necessário para evitar falsos reconhecimentos. Reconhecedores parciais são proporcionais às regras cobertas; não se afirma suporte à gramática integral.
- **Impacto:** Não suportar sintaxe relevante resulta em `UNSUPPORTED_CONSTRUCTION` ou `INSUFFICIENT_CONTEXT`, nunca em conformidade presumida. Nenhuma biblioteca ou gramática externa fica implícita.
- **RF/CA:** RF-003–009, RF-011–018; CA-002–009, CA-012, CA-014–015, CA-018, CA-021.
- **Dependências/owner:** Somente stdlib. Delphi Engineering define a interpretação das formas linguísticas suportadas.

### D-03 — Subconjunto estrutural reconhecido

- **Problema:** Definir a menor superfície de código necessária sem fingir análise geral de Delphi.
- **Alternativas:** Gramática completa; reconhecimento sem tipos estruturais; subconjunto declarado com falha segura.
- **Decisão:** Reconhecer, quando a sintaxe estiver dentro do subconjunto suportado:
  - unidade/artefato fornecido e suas declarações de `type`, `const` e `var`;
  - classes, interfaces, classes que declaram implementar interfaces e suas seções de visibilidade;
  - campos, parâmetros, variáveis locais e constantes, com categoria estrutural necessária às convenções;
  - enumerados, diretivas `{$SCOPEDENUMS ON}` e `OFF`, e referências qualificadas a valores de enum;
  - assinaturas de métodos, `function`, `constructor`, `destructor`, parâmetros e tipos de retorno;
  - GUID declarado em interface e implementações de membros requeridos por contrato fornecido;
  - `class function New` e tipo de retorno;
  - atributos como `[weak]` associados a uma declaração;
  - comentário, string e diretiva como regiões lexicais, sem tratá-los como código executável ou declaração.

  Corpos de métodos só serão percorridos na extensão estritamente necessária para localizar declarações locais ou reconhecer referências qualificadas. Não serão analisados para julgamento de qualidade nem para medir Function Length, Parameter Count, If Depth ou Cyclomatic Complexity.
- **Justificativa:** A superfície corresponde às famílias rastreadas pela SPEC e não incorpora gramática ou métrica alheia à unidade.
- **Impacto:** Construções condicionais/geradas ou sintaxe não reconhecida que alterem o resultado geram limitação. Implementação futura não pode ampliar silenciosamente a superfície.
- **RF/CA:** RF-004–012, RF-017–018; CA-004–009, CA-012, CA-014–015, CA-017–018, CA-021.
- **Dependências/owner:** Contratos de interface aprovados e contexto vêm do host/owner competente; a unidade não cria nem aprova esses contratos.

### D-04 — Não avaliar expressões de compilação nem executar diretivas

- **Problema:** Diretivas condicionais, macros e configuração podem mudar a estrutura efetivamente compilada.
- **Alternativas:** Ignorá-las sem sinalização; implementar pré-processador completo; receber contexto e reconhecer diretivas simples, limitando expressões não resolvidas.
- **Decisão:** Registrar diretivas vistas e manter o estado lexical de `SCOPEDENUMS ON/OFF` somente quando a sequência for explícita e incondicional no texto fornecido. Não executar diretivas, includes ou comandos. Não avaliar expressões arbitrárias de compilação, includes, macros nem configuração externa. Se condicionais puderem alterar a conclusão, exigir contexto resolvido fornecido ou retornar resultado limitado.
- **Justificativa:** Evita inventar a configuração efetiva e impede que texto analisado cause efeitos.
- **Impacto:** O resultado descreve o texto/contexto fornecido, não certifica a configuração compilada.
- **RF/CA:** RF-001, RF-006, RF-011–012, RF-016, RF-018; CA-001, CA-007, CA-012–013, CA-015, CA-020.
- **Dependências/owner:** Contexto fornecido pelo chamador; interpretação material permanece com Delphi Engineering.

### D-05 — Token e declaração especializados, sem cópia dos tipos Core

- **Problema:** Observações exigem estrutura local, mas a SPEC proíbe infraestrutura transversal paralela.
- **Alternativas:** Reutilizar/duplicar tipos de request, scope, evidence, finding e autoridade; manter registros internos estreitos e adaptar a saída.
- **Decisão:** Usar registros internos imutáveis mínimos para token/span e declaração/observação Delphi. Eles carregam somente informação sintática e proveniência local. Não criar substitutos de `ReviewRequest`, `ReviewScope`, `EvidenceReference`, `VerificationClaim`, `ReviewFinding`, `SpecialistAssessment`, authority ou precedence.
- **Justificativa:** Isola o reconhecimento Delphi e mantém contratos transversais na SPEC2.
- **Impacto:** O adaptador é responsável por associar uma observação ao contexto Core recebido sem reescrever sua identidade.
- **RF/CA:** RF-002–003, RF-015, RF-017–018; CA-002–003, CA-019, CA-021.
- **Dependências/owner:** SPEC-0000000002 para contratos Core; nenhuma duplicação de tipos.

### D-06 — Entrada autorizada e associação de proveniência

- **Problema:** A unidade precisa limitar análise e evidência aos artefatos consentidos sem ler filesystem.
- **Alternativas:** Descoberta de arquivos no workspace; receber nomes sem checagem; receber texto e identidade autorizada do host e validar associação.
- **Decisão:** A fronteira recebe texto-fonte já fornecido, identificador do artefato, escopo, versão opcional/materialmente exigida, regras aplicáveis e contexto de compatibilidade. Valida que artefato e escopo pertençam à entrada autorizada recebida do host. Não deriva CWD, faz glob, lê `.workspace` ou descobre dependências no disco. A versão não é inferida; ausência que impeça conclusão produz limitação.
- **Justificativa:** Proveniência e limites são verificáveis sem efeitos de filesystem.
- **Impacto:** Carregamento, seleção e autorização dos artefatos permanecem no host.
- **RF/CA:** RF-001–003, RF-011–012, RF-016, RF-018; CA-001–003, CA-012–013, CA-020.
- **Dependências/owner:** Host/Core fornece request e conteúdo. SPEC1 só seria pertinente a persistência futura explicitamente autorizada; esta unidade não persiste.

### D-07 — Localização por offsets e coordenadas reproduzíveis

- **Problema:** A evidência precisa reencontrar a observação no conteúdo exato sem adotar endereço opaco.
- **Alternativas:** Linha/coluna apenas; offset absoluto apenas; nome estrutural; combinação de range e linha/coluna.
- **Decisão:** Cada span contém offsets de início inclusivo/fim exclusivo em pontos de código Unicode do texto original, mais linha e coluna de início/fim baseadas em 1. CRLF conta como uma quebra de linha; LF isolado também. O conteúdo é preservado sem normalização. O registro de observação associa span a artefato, versão quando presente, escopo e tipo de construção.
- **Justificativa:** Offsets identificam precisamente o trecho no texto exato e coordenadas são revisáveis por pessoas e adaptáveis à evidência Core.
- **Impacto:** Locais dependem do hash/identidade do texto; qualquer edição desloca offsets e exige nova observação. Não se usa path do sistema como localização da construção.
- **RF/CA:** RF-002–003, RF-017; CA-002–003, CA-019, CA-021.
- **Dependências/owner:** Texto e identidade do artefato fornecidos pelo host.

### D-08 — Regras lexicais dependem do tipo estrutural

- **Problema:** Conferir prefixo só pelo texto do identificador produz falsos positivos/negativos.
- **Alternativas:** Aplicar prefixo globalmente; classificar estrutura primeiro; submeter toda ocorrência a julgamento humano.
- **Decisão:** Aplicar `T`, `I`, `F`, `A` e `L` somente após reconhecer, respectivamente, tipo/classe, interface, campo privado, parâmetro/argumento e variável local dentro do subconjunto. Aplicar a regra de constantes ao elemento reconhecido como constante: caixa alta, `_` inicial/final e `_` entre palavras compostas, conforme regra interna vigente. Se a declaração/visibilidade for ambígua, não produzir divergência lexical conclusiva.
- **Justificativa:** Separa regra de forma de qualidade semântica do nome.
- **Impacto:** Não gera finding sobre descritividade, abreviação, clareza ou adequação do nome; essas questões seguem a Clean Code Specialist.
- **RF/CA:** RF-004–005, RF-012–014; CA-004–006, CA-015.
- **Dependências/owner:** Regras internas vigentes; Delphi Engineering interpreta ambiguidade de forma linguística e Clean Code mantém julgamento semântico.

### D-09 — Diretivas e enumerações são evidência contextual, não inferência

- **Problema:** A aplicabilidade de `SCOPEDENUMS` pode depender de região, condição e contrato/API.
- **Alternativas:** Exigir ON global; ignorar estado; registrar diretiva/região e qualificação observadas, limitando necessidade contextual.
- **Decisão:** O scanner registra cada evento incondicional ON/OFF e associa enumerações e referências ao estado vigente no ponto textual. Distingue: estado explícito conhecido; estado ausente/desconhecido; referência qualificada; referência não qualificada. Só declara divergência quando a regra explícita e o contexto fornecido determinam sua aplicação. Caso contrário, retorna `OWNER_DECISION_REQUIRED` ou `INSUFFICIENT_CONTEXT`.
- **Justificativa:** Evita transformar fato parcial em obrigação presumida.
- **Impacto:** Regras sobre necessidade de escopo podem requerer decisão do Delphi Engineering Specialist e contexto da API.
- **RF/CA:** RF-006, RF-011–012; CA-007, CA-012, CA-015.
- **Dependências/owner:** Diretivas e contexto explícitos; sem avaliação de preprocessor.

### D-10 — Contratos de interface somente após aprovação externa ao módulo

- **Problema:** Verificar assinatura/visibilidade requer contrato esperado, mas reconhecer uma interface não autoriza decidir se ela deveria existir.
- **Alternativas:** Inferir contrato da implementação; deixar o módulo desenhar interface; aceitar contrato aprovado fornecido pelo host e comparar forma Delphi.
- **Decisão:** O host deve fornecer ou referenciar o contrato de interface já aprovado por Interface Architecture, bem como o conjunto de artefatos no escopo. O módulo verifica apenas forma e semântica Delphi aplicáveis: GUID sintaticamente válido, assinatura, operações por `function` quando prescrito, visibilidade/blocos, membros implementadores, construtor/destrutor, `class function New` e retorno esperado. Não decide necessidade, composição, fronteira ou alteração do contrato.
- **Justificativa:** Mantém separado contrato arquitetural e forma da linguagem.
- **Impacto:** Sem contrato ou regra explícita suficiente, saída limitada; não se fabrica finding de desenho.
- **RF/CA:** RF-007–008, RF-012–014; CA-008, CA-010, CA-018.
- **Dependências/owner:** Contrato aprovado de Interface Architecture; Delphi Engineering para forma linguística.

### D-11 — GUID: unicidade limitada ao universo fornecido

- **Problema:** “Único” não pode ser alegado sobre projeto ou universo não examinado.
- **Alternativas:** Alegar unicidade global; validar formato somente; verificar formato e duplicatas em todos os contratos fornecidos e completamente reconhecidos.
- **Decisão candidata:** A SPEC exige GUID válido e único. Procurar duplicatas somente entre declarações de interface completas, reconhecidas e fornecidas dentro do escopo autorizado da mesma avaliação; identificar esse universo e nunca alegar unicidade mais ampla. O critério técnico para validade sintática do GUID não está suficientemente definido nas fontes internas e depende de fonte técnica Delphi/Object Pascal adequada. Até resolver `DEP-DEL-001`, esta parte da decisão permanece bloqueada; não definir a sintaxe com base em conhecimento implícito.
- **Justificativa:** Prova somente o que foi observado.
- **Impacto:** Não há afirmação de unicidade global do repositório.
- **RF/CA:** RF-001–003, RF-007, RF-012, RF-018; CA-001–003, CA-008, CA-013, CA-015.
- **Dependências/owner:** Artefatos autorizados e contrato fornecidos; critério de validade sintática depende de `DEP-DEL-001`.

### D-12 — Regra de `New` baseada em declaração explícita

- **Problema:** A forma de retorno depende de classe concreta comum versus classe que declara implementar interface.
- **Alternativas:** Inferir intenção pela chamada; decidir que `New`/Factory deve existir; resolver apenas a relação declarada e comparar retorno.
- **Decisão:** Reconhecer `New` somente como `class function` no subconjunto. Determinar a condição de interface a partir da declaração explícita da classe e do contrato fornecido. Classe concreta comum segue o tipo declarado pela API; classe que implementa contrato de interface segue a regra específica de retorno pela interface correspondente. Se a relação/contrato não for resolvida, limitar a conclusão. Não decide necessidade de New, Factory ou Pattern.
- **Justificativa:** Aplica somente a convenção aprovada aos fatos estruturais disponíveis.
- **Impacto:** Casos de herança/aliases/condicionais não reconhecidos ficam limitados, não inferidos.
- **RF/CA:** RF-007–008, RF-012–014; CA-008, CA-011, CA-018.
- **Dependências/owner:** Contrato de interface aprovado; Design Patterns decide Pattern quando material.

### D-13 — `[weak]` é observação de atributo e semântica contextual

- **Problema:** Um atributo demonstrado em exemplo não define solução universal de ownership.
- **Alternativas:** Tratar presença como finding/regra; ignorar semântica; associar atributo à declaração e fornecer interpretação contextual limitada.
- **Decisão:** Reconhecer `[weak]` como atributo somente quando associado inequivocamente a declaração suportada. Registrar a ocorrência e, com contexto suficiente, permitir interpretação Delphi do recurso. Não avaliar arquitetura de ownership/lifetime, ciclo ou necessidade do atributo.
- **Justificativa:** Mantém a distinção entre sintaxe/recurso e desenho arquitetural.
- **Impacto:** Ausência de contexto de compilador/target quando material resulta em limitação.
- **RF/CA:** RF-009, RF-011–014; CA-009, CA-012, CA-015.
- **Dependências/owner:** Contexto Delphi explícito quando aplicável; owner arquitetural para ownership.

### D-14 — Method Toxicity é fronteira de entrada, não medição Delphi

- **Problema:** A SPEC rastreia quatro métricas normativas, mas sua medição não pertence ao grupo 006.
- **Alternativas:** Recalcular métricas no módulo; ignorar a família; aceitar evidência autorizada e apenas relacioná-la ao código/contexto.
- **Decisão:** Não implementar medição de Function Length, Parameter Count, If Depth ou Cyclomatic Complexity. Se evidência válida for fornecida por reviewer/Guard autorizado, a unidade pode associá-la a artefato/span e complementar fatos Delphi estruturais ou esclarecer uma questão material de configuração/linguagem. Não recalcula, não assume autoridade, não interpreta qualidade nem escolhe remediação.
- **Justificativa:** Alinha a arquitetura ao Registry e à fronteira aprovada em RF-010/CA-017/Cenário O.
- **Impacto:** Testes futuros provarão que a unidade recebe/relaciona a evidência e não possui cálculo próprio. Clean Code interpreta aspectos qualitativos; medição cabe a mecanismo/reviewer autorizado.
- **RF/CA:** RF-010, RF-013–014, RF-016, RF-018; CA-016–017; Cenário O.
- **Dependências/owner:** Governança vigente de `NORMATIVE_GUARD`; Clean Code para interpretação qualitativa.

### D-15 — Contexto de compatibilidade explícito

- **Problema:** Versão/compiler/target/diretivas podem alterar semântica e disponibilidade de construções.
- **Alternativas:** Detectar automaticamente; assumir versão atual; receber contexto opcional e limitar conclusões dependentes.
- **Decisão:** Receber como contexto explícito e opcional versão Delphi, compilador, target/plataforma e diretivas/recursos relevantes. Não autodetectar nem assumir valores padrão. A implementação pode derivar somente fatos diretamente presentes no texto fornecido, distinguindo-os de contexto declarado. Se a conclusão depende materialmente de um dado ausente, retornar limitação ou solicitar contexto.
- **Justificativa:** Preserva evidência e evita compatibilidade inventada.
- **Impacto:** Não há promessa de identificar ambiente real de compilação.
- **RF/CA:** RF-002–003, RF-009, RF-011–012; CA-002–003, CA-009, CA-012, CA-015.
- **Dependências/owner:** Host fornece contexto; Delphi Engineering interpreta impacto de linguagem.

### D-16 — Resultados especializados limitados e adaptação à SPEC2

- **Problema:** O host/Core precisa compor resultados Delphi sem que esta unidade crie protocolo, autoridade ou gate.
- **Alternativas:** Retornar PASS global; criar tipos Core paralelos; retornar observações/status especializados e adaptá-los aos tipos SPEC2 existentes.
- **Decisão:** Internamente, distinguir pelo menos `OBSERVED`, `RULE_SATISFIED`, `OBJECTIVE_DIVERGENCE`, `INSUFFICIENT_CONTEXT`, `UNSUPPORTED_CONSTRUCTION`, `INVALID_INPUT` e `OWNER_DECISION_REQUIRED`. São estados de observação local, não estados globais de review/gate. Adaptador fornece ao Core evidência `DELPHI_OBJECT_PASCAL`, `EvidenceReference`, `SpecialistAssessment`, `ReviewFinding` e claims somente quando cabíveis, usando os tipos existentes. Avaliação Delphi substantiva é atribuída ao owner apropriado; automação objetiva não recebe autoridade. Sem autoridade explícita necessária ao assessment, a saída permanece factual/consultiva.
- **Justificativa:** O Core continua dono de composição, autoridade, precedência, renderização e persistência.
- **Impacto:** Ausência de finding não significa conformidade do projeto. Não há conclusão global PASS nem persistência.
- **RF/CA:** RF-003, RF-012–018; CA-003, CA-008–021.
- **Dependências/owner:** SPEC-0000000002. Delphi module não renderiza protocolo, roteia especialistas, decide autoridade global, precedence ou gate.

### D-17 — Determinismo sobre conteúdo e contexto explícitos

- **Problema:** Observações precisam ser reprodutíveis independentemente de ordem incidental e ambiente.
- **Alternativas:** Preservar traversal incidental; ordenar por identificadores/offsets; usar IDs, timestamps ou filesystem como desempate.
- **Decisão:** Processar artefatos na ordem canônica de identidade fornecida e tokens/observações por offset de origem crescente, depois por identificador estável da regra e status definido. Preservar ordem de fonte quando ela for semanticamente necessária (por exemplo, transições ON/OFF de diretiva); ordenar coleções semânticas não ordenadas por chave explicitada. Duplicata exata de observação é consolidada; colisão de mesma identidade/localização/regra com conteúdo incompatível resulta em ambiguidade, sem desempate inventado. Nenhuma identidade depende de hash aleatório, clock, CWD, filesystem, locale, `set` ou insertion order de `dict`.
- **Justificativa:** Ordem lógica deriva do conteúdo e dos identificadores fornecidos.
- **Impacto:** Hash de artefato pode ser carregado como proveniência recebida, não usado como ordenação substituta da regra.
- **RF/CA:** RF-002–003, RF-017–018; CA-002–003, CA-019, CA-021.
- **Dependências/owner:** Contexto e identidade vêm do host; sem geração de IDs globais.

### D-18 — Segurança e garantia estrutural read-only

- **Problema:** Código analisado pode conter instruções textuais ou diretivas que pareçam ações.
- **Alternativas:** Usar toolchain/execução; analisar dados com tokenizer isolado e API sem efeitos; permitir escrita do arquivo para gerar patch.
- **Decisão:** Tratar toda entrada como string de dados. O componente não executa Delphi, comandos, includes, Git ou processos; não abre sockets/rede; não escreve arquivos, workspace, evidência persistente ou patch. Diretivas reconhecidas são apenas fatos lexicais autorizados e nunca comandos. Integração Core, se persistência explicitamente requerida em fase futura, permanece externa e sujeita aos grants e contratos existentes.
- **Justificativa:** Cumpre read-only sem replicar persistence lifecycle.
- **Impacto:** Testabilidade usa texto e fixtures controladas; efeito colateral é falha de conformidade.
- **RF/CA:** RF-001, RF-016, RF-018; CA-001, CA-013, CA-020.
- **Dependências/owner:** Core/SPEC1 somente para uso futuro explícito; nenhum acesso operacional é definido aqui.

## 3. Fluxo técnico

1. **Recepção:** host entrega request/contexto Core, texto dos artefatos autorizados, identidade, versão disponível, escopo e contratos aprovados pertinentes.
2. **Validação da entrada:** conferir associação artefato/escopo e formato de metadados necessários. Dado estruturalmente inválido encerra a análise daquele input com `INVALID_INPUT`; não se busca substituto no disco.
3. **Tokenização:** produzir tokens/spans que distinguem código, comentário, string e diretiva; preservar texto e coordenadas originais. Tokens em comentários/strings não contam como declarações.
4. **Reconhecimento parcial:** construir declarações mínimas suportadas e relações explicitamente declaradas. Registrar estado regional incondicional de SCOPEDENUMS; não resolver pré-processamento geral.
5. **Contextualização:** associar regra vigente, contrato aprovado, versão/target/diretivas e universo de GUIDs efetivamente fornecidos. Separar dado declarado, fato observado e interpretação.
6. **Verificação:** executar comparações lexicais/estruturais explícitas. Questões ambíguas são limitadas ou atribuídas ao Delphi Engineering Specialist; questões de outro domínio são encaminhadas sem decisão local.
7. **Proveniência e ordenação:** anexar identidade/span/contexto e ordenar resultados conforme D-07/D-17.
8. **Adaptação:** converter observações/evidências cabíveis aos contratos existentes da SPEC2. O Core compõe o resultado global e controla autoridade, grants, effects, persistence e renderização.

Nenhum passo lista arquivos, usa CWD, lê `.workspace`, modifica fonte, persiste, executa subprocesso ou produz externalidade.

## 4. Modelo interno e localização

O modelo interno mínimo é composto por:

- **Span:** offsets de início inclusivo/fim exclusivo em pontos de código do texto e coordenadas de linha/coluna 1-based;
- **Token:** categoria lexical, texto original e Span;
- **Declaração observada:** categoria estrutural, nome original, escopo/visibilidade observados, relações declaradas, atributos e Span;
- **Observação:** artefato, versão fornecida (ou ausente explicitamente), escopo, regra aplicada, fato observado, status local, Span e limitação/contexto pertinente.

Essas estruturas não são contratos persistentes nem objetos de review paralelos. Não normalizar/case-fold/strip valores fornecidos para identidade; comparação lexical segue somente a regra pertinente e preserva a grafia original para evidência. Versão ausente permanece ausente. Regras de encoding e carregamento de arquivos ficam no host; o analisador recebe texto já decodificado.

## 5. Erros, suporte parcial e limites de conclusão

- `OBSERVED`: fato reconhecido sem decisão normativa por si só.
- `RULE_SATISFIED`: regra objetiva aplicável e verificável atendida no trecho/escopo observado.
- `OBJECTIVE_DIVERGENCE`: forma observada diverge de regra explícita, com evidência localizada.
- `INSUFFICIENT_CONTEXT`: falta versão, diretiva, artefato, contrato, target ou universo de comparação material.
- `UNSUPPORTED_CONSTRUCTION`: construção fora do subconjunto reconhecido impede conclusão segura.
- `INVALID_INPUT`: identidade/escopo/relação de entrada inconsistente ou texto/metadado estruturalmente inválido.
- `OWNER_DECISION_REQUIRED`: questão depende de interpretação de owner ou pertence a outro domínio.

Uma limitação aplica-se à conclusão que depende do dado ausente; não amplia nem invalida conclusões independentes sustentadas. Não produzir um finding não equivale a conformidade integral. Não existe `PASS` global neste componente.

## 6. Integração com SPEC-0000000002 e dependências

- **SPEC2:** dependência transversal obrigatória. O adaptador mapeia fatos/evidence para dimensão `DELPHI_OBJECT_PASCAL`, `EvidenceReference`, `SpecialistAssessment`, `ReviewFinding` e claims quando aplicável. Preserva artefato, versão, origem/localização e limitações. Claims só são emitidos quando requeridos e sustentados por observação/evidência; não inferir resultado positivo. Avaliação Delphi autoritativa exige owner e competência fornecidos pelo contrato/Core; sem isso, manter caráter factual/consultivo.
- **SPEC1:** nenhuma dependência de runtime para análise read-only. Seus lifecycle/publisher/recovery/search/catalog/format e proveniência não são invocados por este componente. Persistência futura depende de autorização e integração Core própria, fora deste PLAN.
- **Internas:** nenhuma nova infraestrutura transversal; registros privados de token/span/declaração/observação pertencem ao módulo Delphi.
- **Externas:** nenhuma biblioteca, toolchain, serviço ou API externa.
- **Não materiais:** REF-0000000001 (Patterns), REF-0000000002 (Refactoring) e REF-0000000003 (índice externo) permanecem não materiais: decisões aqui são de reconhecimento de linguagem, proveniência e limite de autoridade. Nenhum PDF/site foi consultado.
- **Pendência bloqueante:** `DEP-DEL-001` — fonte técnica governada Delphi/Object Pascal adequada para fundamentar as regras lexicais, sintáticas e semânticas materiais necessárias ao tokenizer e reconhecimento estrutural. Afeta D-02, D-03, D-04, D-11, D-13 e D-15. A arquitetura permanece candidata, mas essas decisões não têm fundamento técnico rastreável suficiente para alimentar TASKS. Detalhes não podem ser preenchidos por suposição ou conhecimento implícito do modelo.

## Dependência técnica bloqueante — referência Delphi/Object Pascal

A revisão externa registrou `PLAN-REV-001 = BLOCKING`: falta uma Technical Reference Delphi/Object Pascal vigente e adequada para decisões técnicas materiais da arquitetura. O desenho não foi rejeitado; permanece proposta candidata até que a base técnica seja resolvida.

Materialidade por decisão:

- **D-02 — Tokenização:** distinguir corretamente comentários, strings, diretivas, identificadores e pontuação exige regras lexicais Delphi não especificadas com suficiência nas fontes internas.
- **D-03 — Reconhecimento estrutural:** reconhecer classes, interfaces, declarações, parâmetros, atributos, visibilidade e assinaturas exige fundamentação sintática Delphi rastreável.
- **D-04 — Diretivas:** tratar diretivas, condições e regiões exige conhecimento técnico não substituível por exemplos internos.
- **D-11 — GUID:** a SPEC exige GUID válido e único; a unicidade continua limitada ao universo fornecido, mas a sintaxe técnica de validade permanece indefinida até haver fonte adequada.
- **D-13 — `[weak]`:** interpretar sua semântica Delphi exige referência técnica rastreável e contexto suficiente.
- **D-15 — Compatibilidade:** versões, compiladores, targets e diretivas podem afetar conclusões; fatos específicos de compatibilidade exigem fonte técnica quando usados.

REF-0000000001 (Design Patterns), REF-0000000002 (Refactoring) e REF-0000000003 (índice externo de Pattern) continuam vigentes para seus domínios, mas não cobrem esta lacuna Delphi. Não são reinterpretadas como referências Delphi nem foram consultadas para tentar resolvê-la.

Enquanto `DEP-DEL-001` estiver aberta, não iniciar TASKS. A implementação não deve substituir a consulta a uma fonte adequada por conhecimento implícito do modelo. A proposta ou adoção de nova Technical Reference requer autorização separada do responsável pelo projeto. Após eventual adoção e consulta, reavaliar somente as decisões materialmente dependentes e atualizar as estratégias de validação afetadas; não reabrir decisões independentes sem motivo.

As matrizes RF/CA/cenários permanecem como rastreabilidade do trabalho proposto, mas estratégias que dependem de D-02/D-03/D-04/D-11/D-13/D-15 não estão tecnicamente prontas para decomposição em TASKS. A cobertura listada não representa prontidão executável enquanto `DEP-DEL-001` não for resolvida.

## 7. Segurança, determinismo e efeitos

O módulo recebe dados em memória e retorna dados em memória. Não possui API para gravar, patchar, executar, carregar módulos ou acessar rede. O fluxo não depende de diretório atual, sistema de arquivos, ordem de enumeração do filesystem, relógio, locale ou estado global. Diretivas e comentários não alteram autoridade nem escopo; nenhuma string do código é interpretada como instrução ao RickCraft.

Entradas equivalentes com mesmo conteúdo/contexto e regras devem produzir observações equivalentes e ordenadas igualmente. Versão/target/diretiva só afetam resultados quando fornecidos e materialmente aplicáveis. Datas, UUIDs e hashes de execução não são identidade lógica nem tie-breaker.

## 8. Estratégia de validação futura

As verificações abaixo são planejamento para TASKS/IMPLEMENT futuros; nenhum teste é criado ou executado nesta fase.

1. Fixtures pequenas e em memória/temporárias para units, classes, visibilidade, campos, parâmetros, variáveis locais, constantes, enums, métodos, constructors/destructors e corpos mínimos.
2. Comentários, strings e diretivas contendo tokens falsos para provar separação lexical; ON/OFF de SCOPEDENUMS em regiões sequenciais e condicionais não resolvidas.
3. Prefixos por categoria estrutural e constantes nos limites de forma prescrita; casos de nome semanticamente questionável encaminhados sem julgamento Delphi.
4. Interface aprovada fornecida: GUID válido/inválido/duplicado no universo dado, signatures, funções, visibilidade, métodos implementadores, Create/Destroy, `New` e tipo de retorno; universo parcial não pode afirmar unicidade global.
5. Classes comuns versus classes que declaram implementar interface para retorno de `New`; contrato ausente/ambíguo limitado.
6. `[weak]` associado e não associado a declaração, com/sem contexto de compatibilidade; nenhuma conclusão universal de ownership.
7. Contexto de versão/compiler/target ausente/presente; condicionais, macros e construções não suportadas não podem gerar falsa conformidade.
8. Limitações, `INVALID_INPUT`, `UNSUPPORTED_CONSTRUCTION` e `OWNER_DECISION_REQUIRED`, com alcance local e proveniência.
9. Localização por offsets/linhas/colunas em LF, CRLF, Unicode e texto sem newline; span sempre aponta ao trecho original.
10. Determinismo em repetição e permutação de coleções semanticamente não ordenadas; preservar sequência semântica das diretivas.
11. Fronteiras de owners: SOLID, Clean Code, Interface Architecture, Patterns, Quality/Audit e Core recebem encaminhamento, sem decisão Delphi indevida.
12. Method Toxicity: evidência externa autorizada é associada ao escopo/trecho; testes demonstram que a unidade não mede as quatro métricas nem interpreta qualidade/remediação.
13. Adaptador contra contratos reais da SPEC2, sem tipos Core duplicados e sem avaliação global, persistência, renderização ou authority/precedence local.
14. Entradas não autorizadas não analisadas; spies/guards demonstram ausência de escrita, subprocess, Git, rede, upload e Release.
15. Fixtures mantidas em memória ou temporárias controladas; nenhuma dependência de `.workspace` real.

## 9. Matriz RF → decisões/seções

| Requisito | Cobertura no PLAN |
|---|---|
| RF-001 | D-06, D-18; §§3, 7 |
| RF-002 | D-06–D-07, D-15–D-17; §§4, 6 |
| RF-003 | D-02, D-05–D-07, D-16; §§3–5 |
| RF-004 | D-03, D-08; §§2, 3 |
| RF-005 | D-03, D-08; §§2, 3 |
| RF-006 | D-03–D-04, D-09; §§2–3 |
| RF-007 | D-03, D-10–D-11; §§2–3 |
| RF-008 | D-03, D-10, D-12; §§2–3 |
| RF-009 | D-03, D-13, D-15; §§2–3 |
| RF-010 | D-14; §§2, 8 |
| RF-011 | D-04, D-09, D-13, D-15; §§2, 5 |
| RF-012 | D-02–D-04, D-06, D-09–D-13, D-15–D-16; §5 |
| RF-013 | D-14, D-16; §§2, 6 |
| RF-014 | D-08, D-10, D-12–D-16; §§1–2, 6 |
| RF-015 | D-05, D-16; §6 |
| RF-016 | D-14, D-18; §§1, 3, 7–8 |
| RF-017 | D-07, D-17; §§4, 7–8 |
| RF-018 | D-02–D-04, D-06, D-08–D-18; §§1, 3, 5, 7 |

## 10. Matriz CA → estratégia de validação

| Critério | Estratégia futura |
|---|---|
| CA-001 | Input autorizado misto; demonstrar que só texto autorizado entra no tokenizador (D-06/D-18). |
| CA-002 | Verificar proveniência e span exato com artefato, escopo, construção e versão aplicável (D-06/D-07). |
| CA-003 | Contrastar fatos observados, regra, interpretação, relato e inferência (D-02/D-05/D-16). |
| CA-004 | Prefixo incompatível para classe/campo/parâmetro/local; finding apenas lexical (D-08). |
| CA-005 | Prefixo formalmente correto com nome semanticamente ruim; não emitir juízo Clean Code (D-08). |
| CA-006 | Constantes em formas válidas e inválidas, com grafia e regra registradas (D-08). |
| CA-007 | Enum/diretiva com API/contexto ausente; resultado limitado e contexto faltante explícito (D-04/D-09). |
| CA-008 | Contrato de interface fornecido, forma divergente; não avaliar necessidade/desenho (D-10/D-11). |
| CA-009 | `[weak]` com contexto suficiente e insuficiente; sem regra universal (D-13/D-15). |
| CA-010 | Solicitações de ISP/DIP e fronteira de interface são encaminhadas aos owners SOLID/Interface Architecture (D-10/D-16). |
| CA-011 | Possibilidade de Pattern gera encaminhamento, sem escolha/rejeição local (D-16). |
| CA-012 | Omitir versão/compiler/target/diretiva material e comprovar limitação sem valor inventado (D-04/D-15). |
| CA-013 | Artefato fora do escopo disponível mas não autorizado; comprovar que não é analisado (D-06/D-18). |
| CA-014 | Regra objetiva válida resulta em `RULE_SATISFIED` sem finding fabricado (D-08/D-16). |
| CA-015 | Fragmento insuficiente/condicional; identificar limite, sem conclusão presumida (D-02/D-04/D-16). |
| CA-016 | Pedido de Quality/Audit produz fatos/evidence e não status de gate (D-16). |
| CA-017 | Fornecer evidência de métrica externa; relacionar ao span e provar ausência de cálculo/interpretação próprios (D-14). |
| CA-018 | `New` em classe comum/implementadora; comparar retorno conforme contrato fornecido (D-10/D-12). |
| CA-019 | Adaptar saída a tipos SPEC2 reais; validar identidade e proveniência, sem tipo paralelo (D-05/D-16). |
| CA-020 | Spies/guards sobre operações; nenhuma escrita, processo, rede ou externalidade (D-18). |
| CA-021 | Repetir entradas equivalentes/permutar coleções não ordenadas e comparar observações; escopo não generalizado (D-07/D-17). |

## 11. Matriz de cenários A–P → estratégia

| Cenário | Tratamento e validação futura |
|---|---|
| A — Prefixo incompatível | D-08 reconhece a categoria e localiza divergência lexical, sem inferir responsabilidade. |
| B — Nome semanticamente questionável | D-08 comprova ausência de decisão Clean Code pelo módulo. |
| C — Constante fora do formato | D-08 registra caixa/underscores observados contra regra explícita. |
| D — SCOPEDENUMS sem contexto | D-04/D-09 produz limitação, não violação presumida. |
| E — Interface aprovada com forma incorreta | D-10/D-11 compara contrato fornecido e forma, sem decidir necessidade. |
| F — ISP/DIP | D-16 encaminha ao SOLID Specialist. |
| G — Necessidade de interface | D-10/D-16 encaminha ao Interface Architecture Specialist. |
| H — Pattern possível | D-16 encaminha ao Design Patterns Specialist, sem seleção. |
| I — `[weak]` | D-13 fornece semântica contextual sem desenho universal de ownership. |
| J — Versão desconhecida | D-15 limita conclusão dependente de versão/compiler/target. |
| K — Código fora do escopo | D-06/D-18 não tokeniza artefato não autorizado. |
| L — Regra objetiva atendida | D-08/D-16 retorna regra satisfeita, sem finding fabricado. |
| M — Evidência insuficiente | D-02/D-11/D-16 identifica contexto/universo faltante. |
| N — Pedido Quality/Audit | D-16 retorna evidence; gate permanece no Quality Auditor. |
| O — Toxicity externa | D-14 associa evidence recebida; não mede nem decide Clean Code/refatoração. |
| P — Convenção `New` | D-10/D-12 confere retorno pela interface no contrato aplicável, sem escolher Factory/Pattern. |

## 12. Revisão interna e estado

A arquitetura deriva da SPEC aprovada, não altera requisitos e não escolhe parser, biblioteca ou ferramenta externa por preferência. Reconhecimento lexical/estrutural está limitado às construções necessárias; ambiguidades e sintaxe não suportada não são promovidas a conformidade. Read-only, integração Core sem duplicação, determinismo, fronteiras de Decision Owner e exclusão da medição Method Toxicity estão tratados explicitamente. As matrizes vinculam RF-001–018, CA-001–021 e cenários A–P às decisões e estratégias futuras. Technical References permanecem não materiais e não consultadas.

Nenhum teste, código, compilação, gate ou Release foi executado ou criado nesta etapa. O PLAN foi submetido à revisão externa na versão SHA-256 `4F0A986BCFF38DE67AE3EAFE8E303FF08DB59AA855C0514E2436880EB783587E` e não foi aprovado devido a `PLAN-REV-001`. Estado corrente: `PLAN = BLOCKED`, não `FAILED`; a arquitetura permanece candidata e o impedimento é resolvível. `DEP-DEL-001` precisa ser resolvida antes de iniciar TASKS. SPEC permanece `COMPLETE — APROVADA`; TASKS, ANALYZE, IMPLEMENT e CONVERGE permanecem `NOT_STARTED`; último gate válido = nenhum; Release = `NÃO AUTORIZADO`.
