# PLAN — SPEC-0000000001 — Workspace Operacional Persistente e Rastreabilidade entre Agents

## Identificação e versão de entrada

- **SPEC:** `SPEC-0000000001`
- **Decision Owner conceitual:** RickCraft Core Specialist
- **Estado ao iniciar:** PLAN `IN_PROGRESS`
- **Versão aprovada da SPEC utilizada:** SHA-256 `A6B14A3ED433C06BE4E470F1579E580C0C93379BDFACAE71E28DD0ACB623D60C`
- **Data de elaboração:** 2026-10-10
- **Escopo:** decisões técnicas para satisfazer RF-001–RF-014 e CA-001–CA-015. Este artefato não cria TASKS, não executa ANALYZE e não autoriza IMPLEMENT.

## 1. Direção arquitetural

Adotar um protocolo local de arquivos Markdown com metadados JSON estruturados, diretórios determinísticos, IDs aleatórios com criação exclusiva, histórico append-only e pesquisa sob demanda. A implementação deve separar responsabilidades lógicas, sem exigir que cada capacidade vire classe, Agent, serviço ou pacote.

O protocolo central não depende de banco de dados, serviço remoto, índice persistente, Git, Orchestrator ou tecnologia OpenAI específica. A integração hospedeira fornece a raiz canônica do produto e acesso de filesystem com as capacidades declaradas neste PLAN. A falta dessas capacidades bloqueia a operação afetada; não autoriza adivinhar caminho, aceitar gravação parcial ou declarar persistência concluída.

## 2. Capacidades lógicas e fronteiras

| Capacidade lógica | Responsabilidade | Limite |
|---|---|---|
| Contrato do host | Fornecer `RickCraftRoot`, eventual `resume_analysis_id` e operações locais de filesystem necessárias. | Não define requisitos, escolhe autoridade técnica ou presume um host específico. |
| Resolução do workspace | Derivar e testar os caminhos preferencial e fallback na ordem normativa. | Não escolhe livremente outro diretório nem classifica erro desconhecido como indisponibilidade. |
| Ciclo da análise | Criar `IDANALISE` para análise nova ou recuperar o ID fornecido para continuidade. | Não usa contador global nem ID da conversa. |
| Catálogo e validação documental | Aplicar a taxonomia controlada e validar metadados/conteúdo mínimo. | Não interpreta documento inválido como evidência válida. |
| Persistência e histórico | Publicar documentos Markdown sem sobrescrita; registrar relações entre versões. | Não apaga nem altera documento histórico. |
| Recuperação e pesquisa | Localizar documentos por análise, tipo, identificadores, entradas, relações e texto. | Não depende de serviço externo ou índice persistente nesta versão. |
| Proveniência e validade | Registrar entradas verificáveis e detectar mudança ou impossibilidade de verificação. | Não presume atualidade de evidência sem identidade verificável da entrada. |
| Tratamento de lacunas | Persistir divergências/bloqueios e interromper somente a parte afetada. | Não decide em nome de Decision Owner nem fecha lacuna por conveniência. |
| Classificação do Release | Excluir estado operacional `.workspace/`, inclusive no fallback fisicamente interno ao produto. | Não gera Release neste PLAN. |

Essas capacidades descrevem responsabilidades, não uma arquitetura de Agents. A integração e o fluxo SDD continuam sujeitos às Policies vigentes.

## 3. Decisões técnicas

| ID | Problema | Alternativas relevantes | Decisão | Justificativa e requisito atendido | Impacto/risco | Autoridade |
|---|---|---|---|---|---|---|
| D-01 | Como o runtime conhece a raiz instalada sem adivinhar pelo diretório corrente? | Inferir do CWD; procurar nomes de pastas; derivar de caminho de Skill; receber caminho explícito do host. | Cada integração fornece `RickCraftRoot`, caminho absoluto da pasta canônica `<LOCAL_DEFINIDO_USUARIO>/RickCraft/`. Validar existência, tipo de diretório e nome lógico `RickCraft`; normalizar separadores e segmentos `.`/`..`. Ausência ou invalidade bloqueia a operação antes de qualquer escrita. | A entrada explícita é determinística e independente da plataforma; atende RF-001 e evita usar CWD, `$HOME` ou inferência. | A integração hospedeira precisa fornecer e testar o valor. Sem isso, não há persistência segura. | Core; invariantes da POL-0000000003 não podem ser alteradas. |
| D-02 | Como testar se o diretório suporta o protocolo sem exigir operações desnecessárias? | Confiar em existência/permissões declaradas; testar as operações usadas pela publicação append-only. | Criar recursivamente o diretório quando ausente. Em subdiretório isolado criado exclusivamente para a sonda, criar um arquivo temporário exclusivo, gravar bytes, executar flush quando suportado/aplicável, ler e comparar os bytes, então publicar por rename/move atômico sem substituição para outro nome temporário exclusivo no mesmo volume e verificar o conteúdo publicado. A sonda é bem-sucedida se essas capacidades passarem. Remover os temporários é limpeza best-effort, não parte do critério de sucesso. | Testa criação de diretório, exclusividade, escrita, durabilidade disponível, leitura/verificação e a publicação atômica sem substituição efetivamente exigida por D-13. Não testa delete como pré-requisito. Atende RF-001/002 sem acrescentar requisito funcional. | Falha de uma capacidade necessária, com causa concreta classificada em D-03, pode autorizar fallback. Falha de limpeza isolada apenas gera `PROBE_CLEANUP_PENDING`; não declara a raiz indisponível nem autoriza fallback. | Core define o protocolo; host/filesystem deve fornecer as capacidades. |
| D-03 | Quando o fallback é autorizado? | Fallback para qualquer erro; fallback apenas para indisponibilidade concreta reconhecida. | Tentar sempre o preferencial primeiro. Usar fallback somente para erro de filesystem classificado como impossibilidade concreta: acesso negado, filesystem somente leitura, componente do caminho que é arquivo, caminho conhecido como não suportado ou limite/quota/espaço que impeça criação/uso. Erro inesperado, erro de configuração de `RickCraftRoot`, falha do mecanismo de sonda sem causa classificável ou erro interno encerra a resolução sem fallback. | Preserva literalmente a precedência da POL-0000000003 e impede transformar erro desconhecido em permissão. Atende RF-001/002 e CA-002/003. | O adaptador deve preservar códigos/causas suficientes para classificar erros; se não puder, resultado é desconhecido e bloqueia. | POL-0000000003; classificação técnica no Core. |
| D-04 | Como manter continuidade se o caminho preferencial ficar disponível ou indisponível entre sessões? | Fixar permanentemente o fallback; migrar/apagar dados; unir leituras acessíveis e gravar no local atualmente prioritário. | Reavaliar o preferencial no início de cada operação e antes de cada publicação. Gravar somente no local selecionado pela regra atual. Quando o preferencial estiver utilizável, pesquisar nele e, se existir, ler o fallback somente como arquivo histórico de leitura; isso não o torna raiz ativa nem autoriza novas gravações nele. Consolidar documentos por `document_id`; não copiar nem apagar conteúdo legado. IDs distintos formam união; mesmo ID com conteúdo diferente gera divergência e bloqueia o uso daquela identidade. Se o preferencial estiver comprovadamente indisponível, o fallback é a raiz ativa acessível. Cada documento registra `workspace_root_kind` (`preferred` ou `fallback`). | Evita migração destrutiva e sincronização/locking global; mantém recuperação de históricos criados sob fallback. Atende RF-005/006/008 e CA-006/007/009. | Uma indisponibilidade simultânea pode tornar histórico inacessível. O RickCraft registra a limitação e não afirma que examinou o histórico inacessível. Corridas de troca de disponibilidade podem distribuir documentos entre raízes; a leitura por união recupera ambos quando acessíveis. | Core sob as invariantes de localização. |
| D-05 | Como identificar análises sem contador global e preservar continuidade? | Sequência central; timestamp isolado; UUID aleatório; timestamp mais contador. | Gerar `ANL-<UUIDv4>` canônico em minúsculas. O identificador usa fonte aleatória adequada do host, é independente da conversa e não inclui contador. O horário UTC permanece em metadados (`created_at_utc`), não no ID. Para análise retomada, usar o `resume_analysis_id` recuperado de handoff/documento persistido; se não fornecido, iniciar nova análise. | UUIDv4 oferece nome portátil e baixa probabilidade prática de colisão sem contador/serviço. Criação exclusiva detecta colisão real. Atende RF-003/006 e CA-004. | Sem fonte aleatória adequada, não substituir por aleatoriedade fraca ou horário; bloquear criação de análise. | Core; IDs são mecanismo do PLAN. |
| D-06 | Como evitar colisões de diretório e documento mesmo sob concorrência? | Verificar e depois criar; criação exclusiva atômica; lock global. | Criar diretório de análise com operação exclusiva/atômica. Se já existir, tratar como colisão, gerar outro UUID e repetir até oito tentativas; ao esgotar, registrar falha e bloquear nova análise. Documentos usam `DOC-<UUIDv4>` e criação exclusiva, também com até oito tentativas. | A própria publicação exclusiva resolve a corrida check-then-create sem lock global. Atende RF-003/005 e CA-004/007. | O host precisa oferecer criação exclusiva; se ausente, persistência não é segura e deve bloquear. | Core. |
| D-07 | Como organizar documentos por tipo com extensibilidade controlada? | Categorias livres; categorias numerosas; catálogo pequeno e versionado. | Usar exatamente oito identificadores canônicos iniciais em minúsculas ASCII: `context`, `analysis`, `evidence`, `decision`, `divergence`, `blocker`, `result`, `handoff`. O catálogo registra versão e finalidade. Toda extensão futura adiciona um identificador novo, sem renomear/reutilizar identificadores existentes; os documentos registram `type_catalog_version`. | Oito categorias cobrem as famílias explicitamente requeridas, sem diretório genérico que esconda classificação. Atende RF-003/004 e CA-005/006. | Evolução do catálogo deve ser compatível com leitura dos documentos anteriores. | Core; conteúdo decisório permanece com o owner de domínio. |
| D-08 | Como manter Markdown legível e metadados determinísticos? | YAML front matter; tabela Markdown interpretada por convenção; bloco JSON padronizado. | Cada `.md` começa com título Markdown e um único bloco cercado `json` contendo objeto de metadados v1; o restante é corpo Markdown com títulos de seção padronizados. O bloco precisa ser JSON válido UTF-8 e passar validação de campos/enumerações. Não usar parser permissivo nem duplicar valores entre front matter e corpo. | JSON é legível e validável deterministicamente; Markdown mantém narrativa humana. Atende RF-004/007/014. | A linguagem de implementação ainda não foi escolhida; deverá fornecer parser JSON confiável, preferencialmente da biblioteca padrão, sem parser artesanal. | Core; formato técnico especificado pelo PLAN. |
| D-09 | Como representar identidade, origem e relação entre documentos? | Nome de arquivo baseado em título; ID de documento distinto de IDANALISE; grafo/banco. | Nomear o arquivo `<document_id>.md`, com `document_id` global `DOC-<UUIDv4>` distinto de `ANL-...`. Metadados comuns: `schema_version`, `type_catalog_version`, `document_id`, `analysis_id`, `document_type`, `created_at_utc`, `purpose`, `origin`, `inputs` e `relations`. `relations` usa tokens `corrects`, `complements`, `supersedes`, `invalidates`, `supports` ou `related_to`, cada um com ID alvo. | IDs de arquivo estáveis e relações explícitas bastam para reconstruir histórico sem grafo/DB. Atende RF-004/005/006 e CA-006/007/009. | Referência inexistente, circular inválida para o tipo ou referência divergente deve ser reportada, não seguida como verdade. | Core e owner do conteúdo da decisão registrada. |
| D-10 | Como corrigir ou invalidar sem perder o anterior? | Atualizar documento no lugar; append-only; sistema de versionamento externo. | Documentos publicados são imutáveis. Correção, complemento, reavaliação, substituição ou invalidação cria novo documento com novo `document_id` e relação tipada para o anterior. Nenhum status atual é gravado por edição no documento antigo; estado derivado é registrado em documento novo e interpretado pelas relações e avaliações posteriores. | Atende RF-005 e CA-007, não depende de Git e preserva cadeia auditável. | Requer descoberta por relações; documentos relacionados inacessíveis resultam em histórico incompleto/blocker. | Core; decisão substantiva continua com Decision Owner competente. |
| D-11 | Como provar identidade das entradas e detectar obsolescência? | Apenas caminho; hash/revisão verificável; afirmar validade quando não versionável. | Para arquivo local, registrar caminho relativo/identificador de origem e SHA-256 dos bytes lidos. Para documento do workspace, registrar `document_id` e SHA-256 do arquivo. Para fonte versionada, registrar também commit/revisão/ETag equivalente quando fornecido. Para conteúdo observável sem revisão/hash recuperável, registrar `verification: UNVERIFIABLE`, motivo e instante observado; evidência assim é histórica, não prova estado atual. Na recuperação, recalcular entradas acessíveis: igualdade = `MATCHED`; divergência = `CHANGED_REASSESS`; inacessível = `UNAVAILABLE`; sem versão verificável = `UNVERIFIABLE`. | SHA-256 e referências de revisão tornam a mudança detectável sem banco. Não proclama validade quando não há versão. Atende RF-004/007/008 e CA-008/009. | Hash identifica bytes, não prova autoria, segurança ou correção semântica. Entradas indisponíveis não podem ser presumidas atuais. | Owner do requisito decide validade substantiva; Core registra proveniência. |
| D-12 | Como pesquisar sem infraestrutura prematura? | Diretório determinístico e varredura; índice local persistente; serviço/embeddings. | Começar por filtros de diretório (`analysis_id`, `document_type`, `document_id`) e varredura sob demanda de metadados JSON e texto Markdown. Pesquisa estruturada usa campos/relations; pesquisa textual usa conteúdo do arquivo. Sem cache/index persistente nesta versão. | É suficiente para volume ainda não medido e preserva simplicidade. Atende RF-006/008/014 e CA-006/009. | Latência crescerá com volume; registrar evidência de necessidade antes de adicionar índice. | Core. |
| D-13 | Como impedir leitura de gravação parcial e sobrescrita concorrente? | Escrever diretamente no destino; lock global; publicar atomicamente arquivo validado. | Gerar documento completo em arquivo temporário exclusivo na mesma pasta de tipo, validar UTF-8/JSON/campos/conteúdo e flush; publicar por rename/move atômico sem substituir destino. Depois verificar que o arquivo final existe e seu hash corresponde. Temporários interrompidos não são documentos e nunca entram na busca `*.md`; não apagar temporário alheio silenciosamente. Sem publish-if-absent atômico, interromper a persistência como indisponível. | IDs exclusivos + publicação atômica bastam para concorrência de append; não há atualização destrutiva nem necessidade de lock global. Atende RF-005/006 e CA-007/009. | Host/filesystem deve oferecer criação exclusiva e publicação atômica no mesmo volume. Temp órfão pode exigir investigação; deve ser reportável. | Core; capability do host é pré-condição de implementação. |
| D-14 | Como manter resultados operacionais fora de publicação externa? | Integrar automaticamente com Git/sync; armazenamento local isolado do fluxo de publicação. | O protocolo só escreve nos caminhos `.workspace`; não invoca Git add/commit/push, rede, upload ou sincronização. Para Release, usar inventário positivo de arquivos estáticos necessários e rejeitar `.workspace/**` em qualquer localização, inclusive `RickCraftRoot/.workspace/`. | Atende RF-012/013 e CA-013/014, preservando POL-0000000003. | O empacotador futuro precisa validar exclusões; nenhuma geração de Release faz parte desta execução. | POL-0000000003 e responsável pelo Release futuro. |

### 3.1 Fronteira das decisões e dependências

PLAN é responsável por fechar as decisões arquiteturais necessárias para que TASKS possa ser decomposta em trabalho executável e inequívoco. TASKS pode detalhar a ordem e os passos, mas não escolher arquitetura. IMPLEMENT executa as decisões aprovadas e não escolhe host, linguagem ou contratos ausentes. A classificação abaixo distingue decisões do desenho desta unidade (A) de contratos/dependências de integração fora de seu escopo atual (B); uma classificação B não torna uma dependência disponível nem autoriza presumir sua resolução.

| Item | Classe | Decisão/contrato e justificativa | Autoridade | Impacto em TASKS | Impacto em ANALYZE | Impacto em IMPLEMENT | Impacto em CONVERGE |
|---|---|---|---|---|---|---|---|
| Materialização da árvore canônica no Debug deste repositório | A — decisão aprovada e registrada | O responsável aprovou `<LOCAL_DEFINIDO_USUARIO> = <RAIZ_REPOSITORIO>/impl/src`. Aplicando sem exceção as fórmulas da POL-0000000003, runtime Debug = `<RAIZ_REPOSITORIO>/impl/src/RickCraft/`, workspace preferencial = `<RAIZ_REPOSITORIO>/impl/.workspace/` e fallback = `<RAIZ_REPOSITORIO>/impl/src/RickCraft/.workspace/`. `impl/src/RickCraft/` materializa a mesma árvore canônica do produto instalado; não é uma segunda árvore independente. | Responsável pelo projeto aprovou a materialização; Core mantém fronteiras funcionais. | Pode decompor criação dos diretórios e conteúdo runtime somente após os gates; não inclui artefatos exclusivamente Debug. | Verifica caminhos e exclusões sem assumir criação física nesta etapa. | Materializa somente após TASKS e ANALYZE PASS, nos limites abaixo. | Evidência futura confirma equivalência estrutural Debug/instalação; `.workspace` segue fora do Release. |
| Quem fornece `RickCraftRoot` | A — contrato arquitetural fechado | O adaptador do host que inicia uma operação fornece `RickCraftRoot` absoluto, validável e correspondente à árvore canônica da POL-0000000003. O protocolo desta unidade recebe essa entrada; não a descobre por CWD, HOME, nome presumido ou localização de Skill. | Core, subordinado à POL-0000000003. | Pode decompor validação/consumo do parâmetro; não precisa escolher um host. | Pode verificar o contrato explícito e sua cobertura em testes de adaptador. | Implementa o limite de entrada, mas não inventa o valor. | Exige evidência de caminho válido e de bloqueio quando ausente/inválido. |
| Escolha do host/runtime e binding que fornece a raiz | B — integração externa não definida nesta unidade | A SPEC não seleciona Codex Skill, Plugin, MCP ou outro host. A documentação de descoberta de Skills não estabelece o contrato RickCraftRoot. O host concreto e o binding para o contrato definido acima precisam ser escolhidos/aprovados pelo responsável antes da integração executável. | Responsável pelo projeto para seleção/integração de plataforma; Core mantém o contrato funcional. | Tarefas abstratas do protocolo são decomponíveis, mas tarefa de binding e teste integrado ao host não pode ser executada sem essa escolha. | ANALYZE pode validar o contrato e testes controlados; não pode alegar validação integrada do host não escolhido. | O binding real fica bloqueado até haver host e acesso ao root. | CA-001 a CA-003 não podem ser declarados comprovados em runtime integrado sem evidência do host; testes controlados comprovam apenas o protocolo/adaptador. |
| Linguagem/runtime de implementação | A — decisão arquitetural obrigatória ainda aberta | A linguagem concreta afeta APIs de caminhos, semântica de exclusividade, flush, rename sem substituição, concorrência, parser e testes. Não existe etapa posterior “PLAN de implementação”; TASKS e IMPLEMENT não podem receber a escolha. Nenhuma linguagem é selecionada aqui por falta de decisão aprovada e de contexto de host suficiente. | Responsável pelo projeto deve decidir ou delegar explicitamente; o PLAN não presume preferência. | Impede finalizar tarefas de implementação executáveis com APIs concretas. | Impede PASS sobre TASKS executáveis e suporte real das operações no ambiente alvo. | Bloqueia início da implementação desta unidade. | Bloqueia comprovação de CA que depende do runtime integrado e, portanto, CONVERGED. |
| Parser JSON | B — requisito de capacidade fechado; mecanismo concreto depende da linguagem | O contrato exige parser estrito conforme JSON, UTF-8 e validação de campos/enums; não exige uma biblioteca específica. Escolher biblioteca/runtime é detalhe de integração derivado da linguagem, não uma decisão a delegar a TASKS. | Core define o contrato; autoridade da linguagem acima decide mecanismo compatível. | Pode registrar critérios de conformidade; não pode escolher parser concreto enquanto linguagem não definida. | Pode analisar testes de conformidade do parser escolhido; sem escolha não aprova implementação. | Bloqueado junto à decisão de linguagem para código concreto. | Resultados de parse/validação só contam com testes verificáveis do mecanismo integrado. |
| SHA-256 e proveniência | B — algoritmo do protocolo fechado; mecanismo concreto depende da linguagem | O PLAN fixa SHA-256 para fingerprints conforme D-11; APIs/biblioteca que o executam dependem do runtime. Se o host/runtime não oferecer implementação confiável, a unidade bloqueia essa capacidade; não se substitui algoritmo silenciosamente. | Core para o contrato; autoridade da linguagem para mecanismo compatível. | Pode incluir testes com vetores conhecidos; implementação executável depende da escolha da linguagem. | Pode verificar a cobertura dos vetores e os casos de proveniência após seleção. | Bloqueado para implementação concreta até seleção e demonstração do mecanismo. | RF-007/008 e CA-008 não convergem sem evidência de hash correto e reavaliação. |
| Capacidades filesystem: diretório recursivo, create-exclusive, escrita, flush aplicável, leitura e publish-atômico sem substituição | B — contrato de integração fechado; suporte do ambiente ainda não demonstrado | A sonda D-02 exige exatamente as capacidades de protocolo; delete não é requisito. O adaptador pode implementá-las ou expô-las, mas não pode enfraquecer exclusividade/publicação. | Core define o contrato; responsável seleciona host; implementação demonstra suporte. | Os testes e critérios são definidos; tarefa de integração só é executável após linguagem/host selecionados. | ANALYZE deve verificar teste de falha/corrida e evidência de suporte; ausência de capacidade bloqueia. | Não implementar persistência insegura como fallback. | CA-001/002/003/005/007/009 e integridade de persistência dependem das capacidades efetivamente demonstradas. |

**Resultado de prontidão:** o contrato de `RickCraftRoot`, a fronteira do host e os requisitos de parser, hash e filesystem estão explicitados. Porém, a linguagem/runtime é uma decisão arquitetural A obrigatória e continua sem autoridade/instrução de escolha registrada. TASKS não pode resolver essa escolha sem violar a separação PLAN/TASKS. Portanto, este PLAN não pode retornar a `COMPLETE`: fica `BLOCKED` até o responsável pelo projeto selecionar ou delegar formalmente host/runtime e linguagem. A decisão também permitirá confirmar, antes de TASKS, se o binding do host fornece `RickCraftRoot` e se as capacidades exigidas existem. Não se cria outra unidade SDD.

## 4. Contrato de raiz e resolução de caminhos

### 4.1 Termos determinísticos

`RickCraftRoot` é a entrada absoluta validada pelo host e corresponde exatamente à pasta canônica `<LOCAL_DEFINIDO_USUARIO>/RickCraft/`.

```text
LocalDefinidoUsuario       = parent(RickCraftRoot)
ParentOfLocalDefinidoUsuario = parent(LocalDefinidoUsuario)
WorkspacePreferencial     = ParentOfLocalDefinidoUsuario / ".workspace"
WorkspaceFallback         = RickCraftRoot / ".workspace"
```

O cálculo usa operações de caminho do filesystem, não concatenação manual de separadores. Não consulta diretório corrente, perfil/home do processo ou nome inferido da conversa. `RickCraftRoot` precisa ser fornecido pelo host em cada início de operação; se não existir, for relativo, não apontar para diretório ou não corresponder à raiz do produto, não se tenta nenhum workspace.

#### Materialização aprovada no ambiente Debug

Neste repositório, a decisão aprovada pelo responsável materializa `<LOCAL_DEFINIDO_USUARIO>` como `<RAIZ_REPOSITORIO>/impl/src`. Aplicando as fórmulas normativas sem alteração:

| Elemento | Caminho derivado em Debug |
|---|---|
| `RickCraftRoot` / árvore canônica | `<RAIZ_REPOSITORIO>/impl/src/RickCraft/` |
| `WorkspacePreferencial` | `<RAIZ_REPOSITORIO>/impl/.workspace/` |
| `WorkspaceFallback` | `<RAIZ_REPOSITORIO>/impl/src/RickCraft/.workspace/` |

`impl/src/RickCraft/` é a materialização da árvore canônica que, na instalação, aparece como `<LOCAL_DEFINIDO_USUARIO>/RickCraft/`; não é uma segunda árvore de produto. A futura estrutura interna deve corresponder à estrutura de runtime, mudando somente o prefixo físico. Essa pasta não é local para Policies, Registries, Specifications, PLAN, TASKS, `status.md`, evidências exclusivamente de desenvolvimento, documentação de construção ou ferramentas exclusivamente de Debug. Somente artefatos destinados ao runtime ou necessários ao funcionamento do RickCraft podem futuramente ser materializados nela. Nenhum dos diretórios acima foi criado nesta execução. O fallback continua condicionado à impossibilidade real de utilização do preferencial conforme D-02/D-03 e POL-0000000003. `.workspace/` permanece estado operacional e não integra o conteúdo estático de Release, inclusive quando estiver fisicamente sob `RickCraftRoot`.

### 4.2 Algoritmo operacional

1. Receber e validar `RickCraftRoot`.
2. Derivar e normalizar os dois caminhos acima, mantendo a precedência estabelecida pela POL-0000000003.
3. Tentar criar recursivamente `WorkspacePreferencial` se ausente.
4. Executar a sonda D-02: testar criação de diretório quando necessária; criar arquivo exclusivo; gravar, flush quando aplicável, ler e comparar; publicar atomicamente sem substituição para outro temporário exclusivo no mesmo volume; verificar os bytes publicados.
5. Se o teste for bem-sucedido, selecionar o preferencial para escrita.
6. Se o resultado for uma impossibilidade concreta classificada em D-03, tentar criar/testar `WorkspaceFallback` da mesma forma. Selecioná-lo somente após sucesso.
7. Se o preferencial produzir erro desconhecido, não tentar o fallback: registrar `WORKSPACE_RESOLUTION_UNKNOWN` onde for possível e bloquear a operação afetada.
8. Se ambos forem comprovadamente inutilizáveis, registrar `WORKSPACE_UNAVAILABLE` se alguma persistência ainda for possível; caso contrário, comunicar na resposta/runtime atual que nenhum registro persistente foi criado.
9. Antes de cada publicação, repetir a verificação de prioridade. A escrita ocorre na raiz atualmente selecionada. Quando ambas as raízes forem legíveis, leitura/recuperação pode unir documentos dos dois locais sem copiar ou apagar conteúdo; conflito de ID/conteúdo vira divergência.

A sonda usa um subdiretório e arquivos temporários exclusivos, com nomes aleatórios e extensão `.tmp`; nenhum deles é documento `*.md`, candidato à pesquisa, análise ou evidência funcional. Criar/escrever/verificar/publicar é a prova das capacidades necessárias. A remoção dos temporários é best-effort: se falhar, registrar `PROBE_CLEANUP_PENDING`, preservar o artefato para investigação e continuar considerando a raiz utilizável quando todas as capacidades necessárias tiverem passado. A existência desse resíduo não autoriza fallback. Uma falha nas capacidades necessárias só autoriza fallback se for uma impossibilidade concreta classificada em D-03; causa desconhecida continua bloqueando. O sistema não tenta caminhos alternativos fora dos dois autorizados.

## 5. Identificadores e estrutura física

### 5.1 Análise nova ou retomada

- Nova análise sem `resume_analysis_id`: gerar `ANL-<UUIDv4>` usando fonte aleatória adequada do host; criar diretório por operação exclusiva.
- Colisão: abandonar o candidato e gerar outro; máximo de oito colisões consecutivas. Esgotado o limite, produzir falha rastreável e não criar análise parcialmente identificada.
- Continuidade/handoff: reutilizar `resume_analysis_id` persistido e verificar se seus documentos podem ser recuperados. Não gerar novo ID somente porque outro Agent assumiu a execução.
- ID inválido ou inexistente durante uma retomada: registrar divergência/bloqueio; não reinterpretar como nova análise sem autorização/contexto suficiente.
- Nenhum contador global, sequência de conversa ou relógio isolado determina identidade. Data/hora UTC serve para ordenação/auditoria nos metadados.

### 5.2 Diretórios e arquivos

```text
.workspace/
└── <ANL-UUIDv4>/
    ├── context/
    │   └── <DOC-UUIDv4>.md
    ├── analysis/
    │   └── <DOC-UUIDv4>.md
    ├── evidence/
    │   └── <DOC-UUIDv4>.md
    ├── decision/
    │   └── <DOC-UUIDv4>.md
    ├── divergence/
    │   └── <DOC-UUIDv4>.md
    ├── blocker/
    │   └── <DOC-UUIDv4>.md
    ├── result/
    │   └── <DOC-UUIDv4>.md
    └── handoff/
        └── <DOC-UUIDv4>.md
```

Diretórios de tipo são criados idempotentemente quando o primeiro documento daquele tipo for persistido. Caminhos derivados usam apenas IDs e valores do catálogo; texto livre, nome de arquivo de usuário e conteúdo de metadado nunca são interpolados como caminho. Arquivos publicados são `*.md` UTF-8.

## 6. Taxonomia inicial de TipoDocumento

Os tokens abaixo são canônicos, estáveis e versionados em `type_catalog_version = 1`. Nomes/descrições nesta tabela são explicação para implementação; não criam oito grupos ou Decision Owners.

| Token | Finalidade e conteúdo esperado | Usar quando | Não usar quando |
|---|---|---|---|
| `context` | Contexto da análise, objetivo, origem resumida, restrições e referências que outro Agent precisa para situar o trabalho. | Fatos de enquadramento ou handoff recebido precisam ser persistidos. | Para registrar uma conclusão, evidência ou bloqueio como se fosse só contexto. |
| `analysis` | Observações, exame das entradas, interpretação, dependências e ligação a evidências. | Um Agent precisa registrar análise reproduzível ou reavaliação. | Para transformar hipótese em fato ou substituir artefato normativo/gate SDD. |
| `evidence` | Verificação realizada, método/ambiente, entrada identificada, observação/resultados e limitações. | Há evidência observável que sustenta ou contradiz uma afirmação. | Para declarar sucesso sem resultado produzido ou sem entrada rastreável. |
| `decision` | Decisão existente, decisão tomada por autoridade competente, seu owner, justificativa e fonte. | Uma decisão precisa ser recuperada por outra execução. | Para delegar/alterar decisão sem autoridade ou registrar preferência sem aprovação necessária. |
| `divergence` | Fontes/observações incompatíveis, referências, impacto e questão que permanece sem resolução. | Há conflito, contradição ou versões divergentes. | Para escolher silenciosamente uma fonte ou solução. |
| `blocker` | Parte afetada, motivo verificável, dependência/autoridade necessária e condição de retomada. | Informação, acesso, autoridade ou validação impede somente uma parte da execução. | Para item aberto sem impacto bloqueante. |
| `result` | Resultado da análise operacional, requisitos observados, evidências, limitações e pendências. | Há uma disposição/resultado que precisa ser recuperado. | Para afirmar gate SDD PASS/CONVERGED sem cumprir POL-0000000002. |
| `handoff` | Contexto mínimo, IDs e relações documentais, trabalho autorizado, situação e próximo passo permitido. | Outro Agent ou sessão deve continuar a mesma análise. | Como substituto da SPEC/PLAN/TASKS/status ou como nova autorização. |

Toda extensão futura exige versão explícita do catálogo, novo token e regra de leitura; não altera o significado ou reutiliza tokens anteriores.

## 7. Formato documental e identidade

### 7.1 Estrutura comum

Cada Markdown inicia com título e um único bloco JSON cercado. Exemplo esquemático de campos, não um template completo:

```json
{
  "schema_version": 1,
  "type_catalog_version": 1,
  "document_id": "DOC-<UUIDv4>",
  "analysis_id": "ANL-<UUIDv4>",
  "document_type": "evidence",
  "workspace_root_kind": "preferred",
  "created_at_utc": "<RFC3339 UTC>",
  "purpose": "<objetivo conciso>",
  "origin": {"kind": "user_request", "reference": "<referência ou resumo mínimo>"},
  "inputs": [],
  "relations": []
}
```

Campos comuns obrigatórios: versão do esquema e catálogo, `document_id`, `analysis_id`, `document_type`, `workspace_root_kind`, `created_at_utc`, `purpose`, `origin`, `inputs` e `relations`. `workspace_root_kind` é `preferred` ou `fallback` e não substitui a regra de resolução; a localização física determina qual diretório ler. Coleções vazias são explícitas quando aplicável. `origin` identifica tipo e referência ou resumo mínimo; não copia conversa/código sensível sem necessidade. Credenciais e segredos não são persistidos. Metadados adicionais específicos do tipo são adicionados de forma versionada, sem reinterpretar campos v1.

O corpo Markdown contém seções consistentes conforme o tipo: contexto/fatos; método e observações; evidências/referências; decisão e owner; divergências; bloqueio/escopo afetado; resultado/limitações; ou handoff/ação permitida. Campos que não se aplicam não devem ser preenchidos com suposições.

### 7.2 Entradas e relações

Uma entrada inclui, conforme aplicável, `kind`, `locator`, `observed_at_utc`, `version_kind`, `version`, `sha256`, `verification` e motivo de não verificação. Para arquivo local, `locator` é o caminho absoluto normalizado no momento da observação; para documento do workspace, é seu `document_id`; para fonte versionada externa, é URI/referência fornecida, sem buscar/publicar a fonte automaticamente. Caminhos locais permanecem dados privados do workspace. `verification` usa `MATCHED`, `CHANGED_REASSESS`, `UNVERIFIABLE` ou `UNAVAILABLE`.

Uma relação contém um token da lista D-09 e `document_id` alvo; para relação entre análises, também informa `analysis_id`. A relação não transfere autoridade decisória. A validação verifica sintaxe, existência e consistência; referência ausente ou conflito de hash é achado, não motivo para adivinhar.

## 8. Versionamento, validade e pesquisa

### 8.1 Append-only e recuperação

O arquivo final é publicado uma única vez. Correção, complemento, substituição, invalidação ou nova avaliação cria um novo `DOC-UUIDv4`, apontando para o anterior com a relação apropriada. Arquivos `.tmp`/pendentes nunca são lidos como documentos e nunca substituem um `.md` publicado. Não apagar um pendente de outra execução; sinalizar para inspeção/recuperação.

Histórico é reconstruído por `analysis_id`, `created_at_utc`, IDs e relações. Se o mesmo `document_id` estiver nas duas raízes legíveis, conteúdo idêntico por SHA-256 é deduplicado logicamente; conteúdo distinto gera `DIVERGENCE_DOCUMENT_ID` e bloqueia uso daquela identidade.

### 8.2 Verificação de entradas

- Arquivo local acessível: recalcular SHA-256 dos bytes atuais e comparar ao registrado.
- Documento do workspace: verificar ID e SHA-256 atual.
- Fonte versionada: comparar identificador de revisão/commit/ETag quando acessível; quando o conteúdo estiver acessível, manter também SHA-256.
- Entrada sem identidade verificável: preservar a observação e seu instante como histórica, marcar `UNVERIFIABLE`; não declarar que corresponde ao estado atual.
- Entrada inacessível: `UNAVAILABLE`; não interpretar ausência de leitura como igualdade.
- Hash divergente ou revisão mudada: `CHANGED_REASSESS`; manter documento antigo e produzir nova avaliação quando autorizada.

A pesquisa inicial não mantém índice persistente: resolve primeiro por caminho/ID/tipo; depois varre metadados JSON para entradas e relações e o texto Markdown para termos livres. Datas UTC ordenam resultados, sem implicar autoridade ou validade. Qualquer filtro que exclua documentos precisa ser explícito e rastreável.

## 9. Escrita concorrente e falhas

### 9.1 Publicação segura

Não há sequência global de escrita; cada Agent cria documentos imutáveis com IDs próprios. Para publicar:

1. confirmar novamente a raiz prioritária e a disponibilidade;
2. validar IDs, tipo e metadados;
3. criar temporário exclusivo na mesma pasta de tipo;
4. gravar UTF-8, flush e ler de volta para validar esquema e conteúdo;
5. publicar com rename/move atômico sem substituição;
6. reler destino e verificar hash;
7. considerar persistido somente após verificação final.

Essa estratégia evita lock global. Se operações exclusivas/rename sem substituição não forem oferecidas pelo host, bloquear a gravação em vez de fazer escrita não atômica ou sobrescrever. Um temporário de execução interrompida não é evidência; sua existência não autoriza afirmar que documento foi persistido.

### 9.2 Matriz de falhas

| Situação | Resposta técnica | Persistência/continuação |
|---|---|---|
| Preferencial ausente, capacidades D-02 passam | Selecionar preferencial. | Prosseguir; resíduo de limpeza best-effort não muda o resultado. |
| Preferencial existe e capacidades D-02 passam | Selecionar preferencial. | Prosseguir; resíduo de limpeza best-effort não muda o resultado. |
| Capacidade necessária falha por causa concreta permitida em D-03 | Tentar fallback e testar suas capacidades D-02. | Prosseguir somente se fallback estiver utilizável; registrar local selecionado. |
| Erro desconhecido no preferencial | Não tentar fallback. | Bloquear parte afetada; registrar se possível, sem afirmar persistência se não for possível. |
| Preferencial indisponível e fallback utilizável | Usar fallback. | Prosseguir; marcar raiz utilizada nos metadados/relatório operacional. |
| Ambos inutilizáveis | Produzir `WORKSPACE_UNAVAILABLE`. | Sem registro no workspace; comunicar a limitação na resposta atual e interromper somente operação que dependa da persistência. |
| Falha durante publicação/rename/verificação final | Manter arquivo publicado como válido somente se validação/hash final confirmarem. | Caso contrário, não declarar salvo; preservar temporário e relatar falha. Nova tentativa usa novo ID, salvo recuperação íntegra do temporário validável. |
| Documento com JSON inválido/campo obrigatório ausente | Rejeitar como artefato recuperável; registrar `INVALID_DOCUMENT`/blocker. | Não usar como evidência nem como decisão. Não sobrescrever. |
| Entrada não versionável | Marcar `UNVERIFIABLE`, motivo e hora; preservar conteúdo observado permitido. | Pode suportar apenas conclusão histórica limitada; não sustenta alegação de validade atual. |
| Referência histórica ausente ou inacessível | Registrar ID, consulta e resultado. | Não inventar conteúdo; bloquear dependência que exija a referência. |
| Falha desconhecida fora da resolução de raiz | Preservar causa/código disponível e encerrar somente operação afetada. | Não reinterpretar como preferência indisponível nem sucesso; persistir apenas se escrita segura continuar comprovada. |
| UUID colide | Gerar novo candidato e usar criação exclusiva. | Após oito colisões, bloquear a criação e registrar falha. |

Falhas ao persistir não podem ser “registradas” no próprio workspace como se a gravação tivesse funcionado. A resposta da execução atual informa claramente que o registro persistente não foi criado. Falhas em uma parte não afetam trabalhos independentes autorizados.

## 10. Privacidade, Debug e Release

- O protocolo grava somente nos caminhos resolvidos pela POL-0000000003; não executa Git, chamadas de rede, upload ou sincronização.
- Registra somente dados necessários para continuidade e auditoria. `origin` usa referência ou resumo conciso; não replica automaticamente prompts, arquivos completos ou segredos.
- `.workspace/` é estado operacional e nunca integra arquivos estáticos do Release.
- O empacotador futuro usa lista positiva dos artefatos de runtime aprovados e uma exclusão de defesa para qualquer caminho `.workspace/**`, incluindo `<LOCAL_DEFINIDO_USUARIO>/RickCraft/.workspace/` no fallback. Teste de pacote deve validar inventário em fixture temporária; este PLAN não gera Release.
- Policies, Registries, `specs/`, `status.md`, testes e evidências de Debug continuam fora do pacote conforme POL-0000000003.
- `plan.md` e documentos internos da unidade permanecem em pt-BR. Identificadores do protocolo são tokens técnicos estáveis; esta decisão não produz duplicatas ou artefatos de Release.

## 11. Rastreabilidade RF → decisão/capacidade/validação

| Requisito | Decisão técnica | Capacidade | Validação planejada |
|---|---|---|---|
| RF-001 | D-01–D-04; caminho absoluto `RickCraftRoot`, derivação determinística e sonda. | Contrato do host; Resolução do workspace | Testes de caminho absoluto, derivação e ordem de chamadas em filesystem temporário/adaptador controlado. |
| RF-002 | D-02–D-04; criação recursiva e fallback condicionado a causa concreta. | Resolução do workspace | Cenários diretório ausente/criável e erro classificado; verificar diretórios resultantes. |
| RF-003 | D-05–D-07; `ANL-UUIDv4`, criação exclusiva, catálogo inicial e estrutura. | Ciclo da análise; Catálogo | Testes de IDs, colisão injetada, diretórios e persistência do mesmo ID em retomada. |
| RF-004 | D-08–D-09; `.md` UTF-8 com JSON v1 e corpo Markdown. | Validação documental; Persistência | Parse/validação de documentos válidos e inválidos e recuperação de metadados. |
| RF-005 | D-10, D-13; append-only, documento novo e relação com anterior. | Persistência e histórico | Comparar bytes/hash do documento antigo antes/depois de correção, complemento e invalidação. |
| RF-006 | D-04–D-10; `resume_analysis_id`, leitura por união e handoff com IDs/relações. | Recuperação e ciclo da análise | Encerrar contexto de uma execução simulada e iniciar outra somente com artefatos persistidos. |
| RF-007 | D-09–D-11; entradas identificadas por revisão/hash e estados de verificação. | Proveniência e validade | Hash igual, divergente, indisponível e não verificável; confirmar saída apropriada sem falso válido. |
| RF-008 | D-04, D-10–D-12; histórico por relações e consulta/recuperação comparável. | Recuperação, proveniência e pesquisa | Comparar versões e evidências anteriores/atuais com documentos-fixture. |
| RF-009 | D-09–D-10 e regras de lacuna; continuar apenas com autoridade/informação/evidência suficientes. | Tratamento de lacunas | Casos tabulares de autonomia permitida e bloqueio por autoridade, ambiguidade, conflito ou evidência. |
| RF-010 | D-07–D-10; tipos `divergence`/`blocker` e parada por parte afetada. | Tratamento de lacunas | Injetar lacuna/conflicto, confirmar registro, causa e escopo afetado sem decisão inventada. |
| RF-011 | Ordem normativa vigente e tipo `decision` limitado a decisões existentes com owner/fonte. | Tratamento de lacunas; Catálogo | Fixture contradiz fonte normativa; fonte normativa prevalece, divergência registrada e gate não é inferido. |
| RF-012 | D-14; classificação do estado operacional fora da lista positiva de Release. | Classificação do Release | Examinar inventário de pacote-fixture com workspace preferencial e fallback interno; ambos excluídos. |
| RF-013 | D-14; somente filesystem local e nenhuma ação de publicação. | Persistência | Espionar interfaces de rede/Git/sync em testes e verificar ausência de chamadas. |
| RF-014 | D-08–D-12; caminhos, campos JSON e varredura textual sob demanda. | Recuperação e pesquisa | Buscar fixture por análise, tipo, documento, entrada, evidência, divergência, bloqueio, resultado e relação. |

## 12. Rastreabilidade CA → evidência e estratégia de validação

Os testes abaixo são estratégia para IMPLEMENT/CONVERGE, não serão executados nesta etapa. “Ambiente especial” indica requisito além de filesystem temporário e adaptador controlável. Validação humana não é automática; nenhuma aceitação deste protocolo exige observação humana quando a evidência determinística disponível for suficiente.

| Critério | Evidência esperada | Verificação técnica prevista | Ambiente especial | Validação humana |
|---|---|---|---|---|
| CA-001 | Diretório de workspace criado após solicitação operacional. | Teste em raiz temporária inexistente; confirmar criação e capacidades D-02. Injetar também falha de limpeza e confirmar que ela não produz fallback. | Não. | Não. |
| CA-002 | Registro de chamadas demonstra preferencial primeiro. | Adaptador filesystem instrumentado confirma derivação e tentativa em `ParentOfLocalDefinidoUsuario/.workspace`. | Não. | Não. |
| CA-003 | Fallback usado apenas após erro concreto; erro desconhecido não muda caminho. | Injetar acesso negado/read-only e erro desconhecido; conferir respectivamente fallback e bloqueio sem fallback. | Não. | Não. |
| CA-004 | Um `ANL-UUIDv4` correlaciona múltiplos documentos; colisão não reutiliza pasta. | Gerador de UUID controlado injeta colisão; validar criação exclusiva e novo candidato. | Fonte aleatória de teste substituível; sem serviço. | Não. |
| CA-005 | Árvore `<workspace>/<analysis_id>/<document_type>/<document_id>.md`. | Inspecionar filesystem temporário para todas as categorias usadas. | Não. | Não. |
| CA-006 | Segunda execução recupera documento/handoff sem conversa original. | Teste de integração sem estado em memória compartilhado, usando somente ID/documentos persistidos. | Dois processos/contexts isolados simuláveis localmente. | Não, salvo se host real impedir teste automatizado. |
| CA-007 | Documento anterior preserva mesmo hash e novo documento aponta a relação correta. | Salvar, corrigir/substituir e comparar hash/relations; tentar colisão de destino. | Não. | Não. |
| CA-008 | Mudança da entrada gera `CHANGED_REASSESS`; desconhecida não aparece como MATCHED. | Alterar arquivo-fixture e testar hash igual/divergente/não verificável/inacessível. | Não. | Não. |
| CA-009 | Agent/execução posterior consulta evidência e adiciona nova validação/comparação relacionada. | Fixture de handoff recuperada em contexto limpo; conferir referências e saída nova sem modificar anterior. | Não. | Não. |
| CA-010 | Lacuna persistida com motivo; somente operação dependente é suspensa. | Injetar conflito, ausência e autoridade não disponível; validar blocker e continuidade de operação independente. | Não. | Não; eventual decisão reservada continua humana por autoridade, não como teste do fluxo. |
| CA-011 | Continuidade quando requisitos, owner e evidências são suficientes; bloqueio quando não são. | Matriz de cenários autorizados e bloqueados, verificando ausência de aprovação artificial. | Não. | Não. |
| CA-012 | Fonte normativa prevalece sobre documento operacional conflitante. | Fixture com Policy e workspace divergentes; conferir registro da divergência sem sobrescrita normativa. | Fontes normativas fixture ou checkout da unidade. | Não. |
| CA-013 | `.workspace` ausente do inventário de Release em ambas as localizações. | Validar manifesto-fixture e política de allowlist/denylist; não produzir pacote Release real. | Não. | Não. |
| CA-014 | Nenhuma publicação externa ocorre só por criar documento. | Spies/mocks em rede, Git e sincronização permanecem sem chamada durante teste local. | Não. | Não. |
| CA-015 | Artefatos internos da unidade permanecem pt-BR; conteúdo operacional distribuível futuro obedece POL-0000000003. | Revisão do conjunto de documentos e inspeção do manifesto-fixture de Release; verificar ausência de duplicatas automáticas. | Não. | Revisão documental pode ser feita pelo Quality Auditor; não exige teste Delphi/observação funcional. |

## 13. Estratégia de testes e evidências

### Camadas

1. **Validação de protocolo:** parser JSON, enums do catálogo, campos obrigatórios, relações e tipos de entrada.
2. **Testes isolados de filesystem:** raízes temporárias, criação de diretório, create-exclusive, escrita, flush quando aplicável, leitura/verificação, publicação atômica sem substituição e classificação de erro. Testar também falha de limpeza sem fallback indevido.
3. **Testes de proveniência/histórico:** SHA-256, revisões, reavaliação, relação append-only e detecção de referências conflitantes.
4. **Integração entre execuções:** remover estado de memória e recuperar por `analysis_id`/handoff persistido.
5. **Concorrência:** tentativas paralelas de IDs e documentos, criação exclusiva, publicação atômica, nenhuma perda ou substituição. Corridas de mudança da raiz verificam união dos dois locais quando ambos acessíveis.
6. **Release/privacy fixture:** inventário temporário confirma exclusão dos dois possíveis `.workspace` e ausência de operações de rede/Git. Nenhum Release real é gerado antes de solicitação própria.

### Evidências para CONVERGE

Persistir, conforme aplicável, versão de SPEC/PLAN/TASKS, resultados e logs determinísticos dos testes, hashes dos arquivos, matriz CA→evidência, limitações do host, falhas observadas e comprovação de que artefatos anteriores não foram sobrescritos. Testes falhos permanecem resultado negativo; correções não apagam a execução anterior. Esta seção planeja validações, não afirma que foram executadas.

## 14. Dependências, decisões pendentes e riscos

### Dependências técnicas identificadas e decisão pendente

- O contrato fechado exige que o adaptador do host que inicia a operação forneça `RickCraftRoot` absoluto e validável, sem inferência por CWD, HOME ou caminho de Skill. A documentação oficial atual consultada descreve Skills como diretórios com `SKILL.md` e, no Codex local, locais de descoberta em `.agents/skills` desde o CWD até a raiz do repositório; ela não estabelece contrato universal para expor a raiz canônica do RickCraft ao protocolo. Portanto, descoberta de Skill não foi tratada como fonte de `RickCraftRoot`. Fonte: [Build skills — documentação oficial OpenAI](https://learn.chatgpt.com/docs/build-skills), seção “Where Codex loads local skills”, consultada em 2026-10-10. Essa documentação é referência tecnológica, não autoridade normativa do RickCraft.
- A escolha do host/runtime concreto e da linguagem permanece necessária antes de transformar o contrato em tarefas de implementação. A linguagem afeta as APIs e semânticas críticas de filesystem, parser e hashing; PLAN não pode transferir essa decisão para TASKS ou IMPLEMENT. O PLAN não registra autorização para escolher entre plataformas ou linguagens.
- O host/filesystem escolhido deverá demonstrar fonte UUIDv4 adequada, criação exclusiva, escrita/leitura, flush quando aplicável e publicação atômica sem substituição no mesmo volume. Delete não é capacidade funcional requerida. Falha de limpeza da sonda não autoriza fallback; falha concreta numa capacidade necessária poderá autorizá-lo conforme D-03.
- Parser JSON estrito e SHA-256 são requisitos de capacidade do protocolo. A implementação concreta deve ser compatível com a linguagem/runtime aprovados; ausência de suporte confiável bloqueia essas capacidades e não autoriza trocar o contrato silenciosamente.

**Bloqueio do PLAN:** linguagem/runtime é decisão arquitetural A ainda sem seleção/delegação registrada. Host/binding é dependência B também ainda não selecionada. Isso impede concluir tarefas de implementação executáveis e impede ANALYZE de aprovar TASKS que afirmem cobertura integrada. O PLAN permanece `BLOCKED` até decisão explícita do responsável sobre host/runtime e linguagem; depois, antes de TASKS, deve-se confirmar que o binding satisfaz o contrato e que as capacidades necessárias estão disponíveis. Não há uma etapa posterior denominada “PLAN de implementação”.

### Riscos

- Se a integração fornecer raiz errada, o workspace seria direcionado incorretamente; validação de caminho e testes de integração do host são obrigatórios.
- Se a localização preferencial estiver indisponível, dados podem estar divididos entre o preferencial e o fallback ao longo do tempo; união por ID recupera documentos acessíveis sem migração destrutiva. Um local inacessível não pode ser declarado examinado.
- Hash prova igualdade dos bytes observados, não correção, autoria nem equivalência semântica.
- Volume alto pode degradar varredura sem índice; só evidência de latência/volume poderá justificar índice futuro.
- Conteúdo operacional pode incluir dados do usuário; minimização e ausência de publicação automática são salvaguardas do protocolo, não autorização para reter dados desnecessários.
- Um host sem escrita local persistente não pode satisfazer esta unidade; deve bloquear a operação dependente e comunicar que nada foi persistido.

## 15. Ordem arquitetural e limites

Ordem de dependência técnica (não é decomposição de tarefas):

1. contrato do host e representação de caminho;
2. resolução/sonda das raízes e classificação de falhas;
3. criação exclusiva de análise e documentos;
4. catálogo, metadados e validação documental;
5. proveniência, relações append-only e detecção de mudança;
6. recuperação/pesquisa e continuidade por handoff;
7. testes de concorrência, falhas e fronteira de Release.

Este PLAN não seleciona uma plataforma final nem implementa Skill/Plugin/MCP/Agents SDK, arquitetura multiagent, Orchestrator, Agents especialistas, Guards, parser Delphi, índice/banco, Evals globais, Git/publicação ou Release. A seleção de host/runtime e linguagem está fora do escopo decisório já aprovado para esta revisão, mas continua sendo uma dependência bloqueante explícita; não é transferida para uma etapa posterior de PLAN, TASKS ou IMPLEMENT. Sua resolução não pode alterar precedência de caminho, fallback, exclusão de `.workspace`, autoridade ou proibição de fechar lacunas por suposição.

## 16. Conclusão da revisão do PLAN

As decisões do protocolo e a estratégia de validação foram corrigidas para os pontos desta revisão, preservando RF-001–RF-014 e CA-001–CA-015. A fronteira do host, os impactos por estágio e as capacidades da sonda estão explícitos. Entretanto, a escolha arquitetural obrigatória de linguagem/runtime e a seleção/binding do host permanecem sem decisão registrada. Como TASKS não pode escolher arquitetura nem receber tarefas concretas de implementação sem essas decisões, o PLAN fica `BLOCKED`, não `COMPLETE`. A alteração material invalida o estado COMPLETE anterior do PLAN; `status.md` registra a revisão em andamento, o bloqueio e a nova referência verificável. Nenhuma implementação, teste ou Release foi executado.
