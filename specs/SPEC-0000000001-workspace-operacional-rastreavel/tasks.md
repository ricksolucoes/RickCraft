# TASKS — SPEC-0000000001 — Workspace Operacional Persistente e Rastreabilidade entre Agents

## Identificação e versões de entrada

- **SPEC:** `SPEC-0000000001` — COMPLETE e aprovada; SHA-256 `A6B14A3ED433C06BE4E470F1579E580C0C93379BDFACAE71E28DD0ACB623D60C`.
- **PLAN:** COMPLETE e aprovado; SHA-256 `32F659539BF611C80D9A9F28983902A5B54C45673333158AB4595CCC1141F6BB`.
- **Decision Owner conceitual:** RickCraft Core Specialist.
- **Estado ao iniciar o fatiamento:** TASKS `IN_PROGRESS`.
- **Ambiente:** Debug em pt-BR; Python 3.12 ou compatível; somente biblioteca padrão; sem dependências externas.
- **Limite:** Este artefato decompõe decisões aprovadas. Não redefine requisitos/arquitetura, não executa testes, não inicia ANALYZE nem autoriza IMPLEMENT.

## Convenções de execução

- Executar as tarefas pela ordem e dependências declaradas; dependências indicam pré-requisito, não autorizam trabalho fora do escopo SDD.
- Código e testes descritos abaixo pertencem a IMPLEMENT e só poderão ser executados após um `ANALYZE = PASS` válido e autorização aplicável.
- Usar `unittest` da biblioteca padrão quando adequado. Fixtures/adaptadores de filesystem podem simular falhas em testes controlados; nenhuma simulação substitui a sonda D-02 da raiz real.
- Ao executar D-02 em IMPLEMENT, sondar cada raiz antes de usá-la. Não presumir que a sonda passou. Falha classificada segue D-03; erro desconhecido bloqueia a operação sem fallback.
- Não materializar nesta etapa `impl/`, `impl/src/RickCraft/`, `.workspace/`, scripts, runtime ou arquivos de teste.

## Tarefas ordenadas

### TASK-001 — Materializar o componente runtime e receber RickCraftRoot explicitamente

- **Objetivo:** Na futura IMPLEMENT autorizada, criar a estrutura runtime Debug sob `impl/src/RickCraft/` e fornecer ao componente determinístico uma entrada explícita para `RickCraftRoot`, sem descoberta heurística.
- **Origem na SPEC:** RF-001, RF-002; CA-001, CA-015.
- **Origem no PLAN:** D-01; seções 1, 2, 3.1, 4.1, 4.2 e 15; materialização Debug aprovada.
- **Dependências:** Nenhuma.
- **Artefatos/componentes previstos:** Estrutura canônica de runtime Debug; componente de entrada/integração local Python; testes unitários de validação de entrada.
- **Trabalho autorizado:** Materializar a raiz canônica Debug em `impl/src/RickCraft/`; implementar o contrato de recebimento explícito de caminho absoluto, aceitando a forma de argumento/parâmetro já admitida pelo PLAN; validar existência, tipo de diretório e identidade lógica `RickCraft`; bloquear antes de escrita se ausente, relativo, inválido ou incompatível.
- **Verificações/testes previstos:** Entradas válida, ausente, relativa, inexistente, arquivo em vez de diretório e raiz incompatível; comprovar que CWD, HOME, caminho/nome da Skill e busca heurística não são usados para derivar a raiz.
- **Evidência esperada:** Resultado dos testes e registro do valor de `RickCraftRoot` efetivamente fornecido no ambiente controlado, sem expor informação desnecessária.
- **Critérios de conclusão:** Componente recebe a raiz explicitamente; rejeições ocorrem antes de qualquer escrita; a árvore Debug corresponde à árvore canônica, mudando somente o prefixo físico.
- **Exclusões/limites:** Não escolher host universal, mecanismo de empacotamento ou outra linguagem; não materializar nesta execução; não colocar Policies, Registries, SPEC/PLAN/TASKS/status, evidências exclusivamente Debug ou documentação de construção na árvore runtime.

### TASK-002 — Derivar caminhos e preservar precedência de localização

- **Objetivo:** Implementar a derivação determinística das raízes preferencial e fallback a partir do `RickCraftRoot` validado e tentar primeiro a preferencial.
- **Origem na SPEC:** RF-001, RF-002; CA-001, CA-002, CA-003.
- **Origem no PLAN:** D-01, D-02, D-03, D-04; seções 3.1, 4.1 e 4.2.
- **Dependências:** TASK-001.
- **Artefatos/componentes previstos:** Resolvedor de caminhos; testes de filesystem controlado/adaptador instrumentado.
- **Trabalho autorizado:** Derivar `LocalDefinidoUsuario = parent(RickCraftRoot)`, `WorkspacePreferencial = parent(LocalDefinidoUsuario)/.workspace` e `WorkspaceFallback = RickCraftRoot/.workspace`; criar recursivamente a raiz aplicável quando necessária; manter a precedência definida pela POL-0000000003.
- **Verificações/testes previstos:** Confirmar os caminhos derivados no fixture Debug; registrar a ordem de chamadas preferencial antes do fallback; cobrir raiz existente e ausente; verificar que nenhuma terceira localização seja tentada.
- **Evidência esperada:** Testes controlados com caminhos absolutos e sequência observada de operações.
- **Critérios de conclusão:** Fórmulas e precedência são reproduzidas sem consultar CWD/HOME nem selecionar caminho alternativo arbitrário; criação ocorre somente quando a operação autorizada necessita do workspace.
- **Exclusões/limites:** O teste controlado não comprova capacidades da raiz real; a classificação de erro e a sonda ficam nas tarefas relacionadas.

### TASK-003 — Implementar sonda D-02 e decisão de fallback D-03

- **Objetivo:** Verificar, antes do uso de cada raiz, as capacidades necessárias ao protocolo append-only e aplicar a regra de fallback sem inferir capacidade.
- **Origem na SPEC:** RF-001, RF-002, RF-010; CA-001, CA-002, CA-003, CA-010.
- **Origem no PLAN:** D-02, D-03, D-13; seções 3.1, 4.2, 9.2, 14 e 15.
- **Dependências:** TASK-001, TASK-002.
- **Artefatos/componentes previstos:** Sonda isolada em subdiretório/artefatos `.tmp`; classificação de erros; testes com filesystem temporário/adaptador; execução futura da sonda na raiz real quando IMPLEMENT for autorizada.
- **Trabalho autorizado:** Na futura implementação, testar mkdir quando necessário, criação exclusiva, escrita, flush/fsync quando aplicável, leitura/verificação e publicação por `os.link` no mesmo filesystem com destino ausente; verificar conteúdo final e que destino preexistente não seja substituído. Classificar resultados segundo D-03. Limpeza de temporários é best-effort; resíduo `.tmp` é reportável, não é documento `*.md` válido e sua falha isolada não aciona fallback.
- **Verificações/testes previstos:** (a) preferencial utilizável; (b) impossibilidade concreta classificada e fallback utilizável; (c) erro desconhecido no preferencial sem fallback; (d) fallback inutilizável; (e) ambas as raízes inutilizáveis; (f) falha isolada de limpeza sem fallback; (g) colisão/destino preexistente sem substituição; (h) sonda em fixture controlada. Durante IMPLEMENT, executar a sonda real na raiz antes de usá-la, preferencialmente primeiro e fallback somente nas condições D-03.
- **Evidência esperada:** Para testes controlados, logs/resultados por capacidade e classe de falha. Para raiz real, registro da raiz sondada, operações realmente verificadas, resultado e eventual resíduo; não marcar como aprovada sem evidência produzida.
- **Critérios de conclusão:** Somente raízes que passam todas as capacidades necessárias podem ser usadas; erro desconhecido bloqueia; fallback só ocorre após impossibilidade concreta classificada; falha de limpeza não muda o resultado.
- **Exclusões/limites:** Esta TASKS não executa a sonda. Nenhuma evidência anterior inconclusiva em TEMP conta como PASS. Não enfraquecer D-02 nem adicionar operações de delete como pré-requisito.

### TASK-004 — Criar e retomar análises com ANL-UUIDv4

- **Objetivo:** Implementar a identidade de análises novas e a retomada por ID persistido, com criação exclusiva e tratamento de colisão conforme o PLAN.
- **Origem na SPEC:** RF-003, RF-006, RF-009; CA-004, CA-006, CA-011.
- **Origem no PLAN:** D-04, D-05, D-06; seções 5.1, 9.2 e 11.
- **Dependências:** TASK-001, TASK-002, TASK-003.
- **Artefatos/componentes previstos:** Serviço/funções de ciclo de análise; testes unitários de UUID e integração de diretório controlado.
- **Trabalho autorizado:** Gerar `ANL-<UUIDv4>` por `uuid.uuid4()`; criar diretório exclusivamente; em colisão gerar novo candidato até oito colisões consecutivas; ao exceder o limite, bloquear e produzir falha rastreável. Em retomada, reutilizar `resume_analysis_id` fornecido e verificar recuperação; ID inválido/inexistente produz divergência/bloqueio e não vira análise nova silenciosamente.
- **Verificações/testes previstos:** Formato/versão UUIDv4; colisão injetada e novo candidato; limite de oito; retomada preservando identidade; ID inválido/inexistente; ausência de contador global ou relógio como identidade.
- **Evidência esperada:** Resultados determinísticos com gerador substituível em teste, caminhos/IDs observados e motivo de bloqueio quando aplicável.
- **Critérios de conclusão:** Análise nova possui identidade única para fins do protocolo e diretório exclusivo; retomada usa o ID persistido sem depender da conversa.
- **Exclusões/limites:** Não definir ID fora de `ANL-<UUIDv4>` nem gerar ID a partir de sequência, timestamp ou conversa.

### TASK-005 — Aplicar catálogo documental e árvore por TipoDocumento

- **Objetivo:** Criar a organização controlada de documentos sob análise e tipo, usando os oito tokens aprovados no PLAN.
- **Origem na SPEC:** RF-003, RF-004; CA-004, CA-005.
- **Origem no PLAN:** D-06, D-07; seções 5.2, 6 e 11.
- **Dependências:** TASK-004.
- **Artefatos/componentes previstos:** Catálogo versão 1; resolvedor de pasta por tipo; testes unitários de catálogo e layout.
- **Trabalho autorizado:** Reconhecer exatamente `context`, `analysis`, `evidence`, `decision`, `divergence`, `blocker`, `result` e `handoff`; criar diretório de tipo idempotentemente quando seu primeiro documento for persistido; montar caminhos somente com IDs e tokens do catálogo.
- **Verificações/testes previstos:** Cada token gera caminho esperado; token desconhecido/reutilizado ou entrada de texto livre em caminho é rejeitado; layout `<workspace>/<analysis_id>/<document_type>/<document_id>.md`; catálogo versionado como `type_catalog_version = 1`.
- **Evidência esperada:** Testes de catálogo, caminhos derivados e rejeições.
- **Critérios de conclusão:** Documentos ficam classificados de forma inequívoca e recuperável por tipo, com extensibilidade sujeita a nova versão/token, sem alteração do catálogo v1.
- **Exclusões/limites:** Não criar categorias adicionais, taxonomia livre, grupo SPEC ou Decision Owner.

### TASK-006 — Serializar e validar documentos Markdown com JSON v1 e UTF-8 estrito

- **Objetivo:** Implementar o formato documental decidido e rejeitar conteúdo que não satisfaça sua estrutura.
- **Origem na SPEC:** RF-004, RF-011; CA-005, CA-006, CA-012.
- **Origem no PLAN:** D-08, D-09; seções 7.1, 7.2 e 11.
- **Dependências:** TASK-005.
- **Artefatos/componentes previstos:** Serializador/parser de documento; validação estrutural; testes unitários `unittest`.
- **Trabalho autorizado:** Produzir `.md` em UTF-8 com título Markdown, um único bloco JSON cercado contendo objeto v1 e corpo Markdown; exigir os campos comuns definidos no PLAN. Usar `json.loads`/`json.dumps`; validar campos/enums e UTF-8 estritamente; rejeitar nomes de propriedades duplicados e constantes não JSON como NaN/Infinity; validar relações contra os tokens existentes no PLAN.
- **Verificações/testes previstos:** Documentos válidos; bytes UTF-8 inválidos; JSON sintaticamente inválido; chaves duplicadas; NaN/Infinity; campos obrigatórios ausentes; enums inválidos; relação malformada; campos/categorias não inferidos por suposição.
- **Evidência esperada:** Casos de aceitação/rejeição com entrada e resultado verificáveis; nenhum conteúdo inválido aceito como documento recuperável.
- **Critérios de conclusão:** Metadados parseiam e validam segundo o esquema decidido; corpo Markdown conserva contexto suficiente conforme o tipo; conteúdo inválido é rejeitado sem sobrescrever documento publicado.
- **Exclusões/limites:** Não criar schema externo, parser artesanal, dependência ou formato alternativo; não transformar exemplos do README em requisitos universais.

### TASK-007 — Registrar proveniência e validade por SHA-256

- **Objetivo:** Identificar as entradas de documentos/evidências e detectar quando sua identidade verificável mudou ou não pôde ser confirmada.
- **Origem na SPEC:** RF-004, RF-007, RF-008; CA-008, CA-009.
- **Origem no PLAN:** D-11; seções 7.2, 8.2, 11 e 13.
- **Dependências:** TASK-006.
- **Artefatos/componentes previstos:** Cálculo/validação de proveniência; testes de hashing e estado de verificação.
- **Trabalho autorizado:** Calcular `hashlib.sha256` sobre bytes exatos; registrar `hexdigest()` hexadecimal minúsculo com 64 caracteres; armazenar caminho/identificador permitido, revisão/commit/ETag quando fornecido, instante e resultado de verificação. Aplicar `MATCHED`, `CHANGED_REASSESS`, `UNAVAILABLE` e `UNVERIFIABLE` sem inferir atualidade.
- **Verificações/testes previstos:** Vetor conhecido de SHA-256; igualdade; conteúdo alterado; revisão divergente; entrada inacessível; entrada sem versão/hash verificável; preservar a observação histórica sem declará-la atual.
- **Evidência esperada:** Digest e estado observado por caso; referência à entrada utilizada, sem afirmar autoria/correção semântica.
- **Critérios de conclusão:** Bytes exatos produzem digest reproduzível; estados correspondem às evidências de acesso/comparação; mudança identificada pode exigir reavaliação.
- **Exclusões/limites:** Não trocar algoritmo, hash, encoding dos bytes de entrada nem declarar MATCHED sem comparação verificável.

### TASK-008 — Publicar documentos imutáveis com os.link e tratar colisões

- **Objetivo:** Persistir documentos completos sem gravação parcial ou substituição e preservar coerência entre identidade interna e filename.
- **Origem na SPEC:** RF-004, RF-005; CA-005, CA-007.
- **Origem no PLAN:** D-06, D-09, D-10, D-13; seções 7, 8.1, 9.1, 9.2 e regra de colisão D-06/D-13.
- **Dependências:** TASK-004, TASK-005, TASK-006, TASK-007.
- **Artefatos/componentes previstos:** Publicador append-only; temporários exclusivos; testes de filesystem controlado, colisão e concorrência.
- **Trabalho autorizado:** Criar temporário exclusivo na pasta de tipo; escrever bytes completos, flush/fsync quando aplicável e validar conteúdo/hash antes da publicação; publicar com `os.link(temp, destination)` no mesmo filesystem; destino preexistente nunca é substituído; reler destino e confirmar hash final. Colisão confirmada de `DOC-UUIDv4` gera novo UUID, reconstrói metadados, serializa novamente bytes, recalcula validações/hash e cria novo temporário. `filename` deriva do mesmo ID interno. Respeitar limite de até oito colisões de D-06; falhas de outra causa seguem D-03. Temporários `.tmp` são best-effort para limpeza e nunca documentos `*.md` válidos.
- **Verificações/testes previstos:** Destino ausente e preexistente; provar que o destino preexistente permanece byte a byte inalterado; colisão forçada; assegurar novo ID, metadados, serialização, hash, temporário e igualdade filename/document_id; limite de tentativas; interrupção antes/depois da publicação; hash final; tentativas concorrentes sem sobrescrita; arquivo `.tmp` excluído da descoberta documental.
- **Evidência esperada:** Logs/resultados dos cenários, IDs envolvidos, hashes antes/depois e confirmação de imutabilidade; falha nunca é reportada como persistência bem-sucedida.
- **Critérios de conclusão:** Publicação ocorre somente por `os.link` após validação; colisão preserva identidade coerente; destino final só é considerado persistido após verificação final; nenhuma degradação para rename, cópia ou check-then-write.
- **Exclusões/limites:** Não adicionar locking global, API de delete, substituição, recuperação que reutilize bytes da identidade colidida ou fallback alternativo ao mecanismo aprovado.

### TASK-009 — Recuperar documentos, histórico, retomada e união das raízes

- **Objetivo:** Permitir que nova execução recupere documentos anteriores, reconstrua relações e detecte divergências entre as duas raízes quando aplicável.
- **Origem na SPEC:** RF-005, RF-006, RF-007, RF-008, RF-011; CA-006, CA-007, CA-008, CA-009, CA-012.
- **Origem no PLAN:** D-04, D-09, D-10, D-11; seções 7.2, 8.1, 8.2, 9.2 e 11.
- **Dependências:** TASK-003, TASK-004, TASK-006, TASK-007, TASK-008.
- **Artefatos/componentes previstos:** Leitor/recuperador; validação de relações; testes de integração em contextos/processos isolados.
- **Trabalho autorizado:** Recuperar por `analysis_id` e `document_id`; retomar pelo `resume_analysis_id`; ler a raiz atualmente preferencial e, quando acessível e permitido pelo D-04, o fallback somente como histórico; unir documentos por identidade; reconstruir cadeia via `created_at_utc`, IDs e relações `corrects`, `complements`, `supersedes`, `invalidates`, `supports`, `related_to`. Conteúdo idêntico pelo SHA-256 pode ser deduplicado logicamente; mesmo ID com conteúdo diferente gera `DIVERGENCE_DOCUMENT_ID` e bloqueia o uso dessa identidade.
- **Verificações/testes previstos:** Nova execução sem memória compartilhada recupera contexto persistido; recuperar por cada identificador; retomada não gera novo ID; histórico anterior permanece imutável; versões/relações reconstruíveis; fallback histórico legível é unido sem copiar/apagar; divergência de mesmo ID/conteúdo distinto bloqueia; entrada inacessível não é declarada examinada.
- **Evidência esperada:** Fixtures persistidas antes da nova sessão, referências e resultados de recuperação/comparação; hashes que demonstrem preservação do histórico.
- **Critérios de conclusão:** Outro contexto usa somente os artefatos recuperados como evidência rastreável; divergências e lacunas permanecem explícitas; autoridade normativa não é transferida ao workspace.
- **Exclusões/limites:** Não migrar, copiar ou apagar documentos históricos; não depender da conversa original nem considerar `.workspace` fonte normativa.

### TASK-010 — Implementar filtros e pesquisa sob demanda

- **Objetivo:** Tornar recuperáveis documentos por análise, tipo, identificador, metadados, entrada, relação e termos textuais sem infraestrutura persistente adicional.
- **Origem na SPEC:** RF-006, RF-008, RF-014; CA-005, CA-006, CA-009.
- **Origem no PLAN:** D-07, D-08, D-09, D-12; seções 6, 7, 8.2 e 11.
- **Dependências:** TASK-005, TASK-006, TASK-008, TASK-009.
- **Artefatos/componentes previstos:** Consulta/filtros de arquivos e metadados; testes funcionais com fixtures.
- **Trabalho autorizado:** Resolver primeiro por `analysis_id`, `document_type` e `document_id`; depois varrer metadados JSON para entradas/relações e corpo Markdown para termos livres; ordenar por data UTC sem atribuir autoridade/validade por ordenação.
- **Verificações/testes previstos:** Localizar por cada filtro e por combinações; localizar entrada, evidência, divergência, bloqueio, resultado e relação; verificar filtro que exclui resultado como explícito/rastreável; rejeitar documento inválido como fonte confiável.
- **Evidência esperada:** Casos-fixture com consultas e conjunto de resultados esperado, incluindo limitações/inacessibilidade.
- **Critérios de conclusão:** Categorias previstas na SPEC podem ser encontradas pela organização e varredura decididas, sem índice/cache persistente.
- **Exclusões/limites:** Não adicionar grep como contrato obrigatório, banco, SQLite, embeddings, serviço ou índice persistente.

### TASK-011 — Registrar lacunas, respeitar autoridade e limitar interrupção

- **Objetivo:** Implementar registro e encaminhamento de divergências/bloqueios, mantendo a autoridade normativa e interrompendo somente a parte afetada.
- **Origem na SPEC:** RF-009, RF-010, RF-011; CA-010, CA-011, CA-012.
- **Origem no PLAN:** D-08, D-09, D-10; seções 2, 6, 7.1, 8, 9.2 e 11.
- **Dependências:** TASK-006, TASK-008, TASK-009.
- **Artefatos/componentes previstos:** Registro operacional nos tipos `divergence`, `blocker`, `decision` e `result` conforme catálogo; testes de comportamento e autoridade.
- **Trabalho autorizado:** Persistir a ocorrência, a razão para não decidir, o escopo/parte afetada, a autoridade ou informação necessária e a condição de retomada; continuar trabalho independente autorizado; fazer prevalecer Policies/Registries/SPEC/PLAN/TASKS/status/gates aplicáveis sobre conteúdo conflitante do workspace. Registrar decisões existentes com owner e fonte, sem criar decisões ou autoridade.
- **Verificações/testes previstos:** Informação obrigatória ausente; ambiguidade material; conflito normativo/fontes; evidência incompatível/insuficiente; owner indisponível; operação independente autorizada continua; decisão fica sem fechamento por suposição; workspace conflitante não substitui fonte normativa.
- **Evidência esperada:** Documento de divergência/bloqueio com causa, escopo, autoridade necessária e referências; confirmação da continuidade ou interrupção por cenário.
- **Critérios de conclusão:** Não há escolha silenciosa; somente a parte dependente é suspensa; prosseguimento autônomo ocorre apenas quando escopo, autoridade e evidência forem suficientes.
- **Exclusões/limites:** Não inventar política de autoridade, protocolo multiagente, Orchestrator ou solução técnica para lacuna; não permitir ao Auditor/Executor substituir Decision Owner.

### TASK-012 — Verificar fronteiras de Release, idioma e ausência de publicação externa

- **Objetivo:** Demonstrar por verificações controladas que o workspace e o fluxo operacional não são incluídos/publicados externamente por implicação.
- **Origem na SPEC:** RF-012, RF-013; CA-013, CA-014, CA-015.
- **Origem no PLAN:** D-14; seções 10, 11, 12, 13 e 14; POL-0000000003.
- **Dependências:** TASK-001, TASK-003, TASK-008, TASK-010, TASK-011.
- **Artefatos/componentes previstos:** Fixtures temporárias de inventário/manifesto; testes com interfaces externas observadas por doubles/spies.
- **Trabalho autorizado:** Verificar a lista positiva dos arquivos estáticos necessários em fixture de pacote e exclusão defensiva de `.workspace/**`, inclusive fallback fisicamente sob `RickCraftRoot`; verificar que o protocolo não invoca Git add/commit/push, rede, upload ou sincronização. Confirmar pt-BR nos artefatos internos Debug e conformidade do conteúdo operacional distribuível futuro com a regra de inglês da Policy quando aplicável ao inventário-fixture.
- **Verificações/testes previstos:** Workspace preferencial e fallback ausentes do inventário; hooks/spies de Git, rede, upload e sync sem chamadas; nenhuma geração de Release real; sem duplicação automática pt-BR/inglês do mesmo artefato operacional.
- **Evidência esperada:** Manifestos-fixture e resultados de spies; registro explícito de que Release real não foi produzido.
- **Critérios de conclusão:** Estado operacional `.workspace` é excluído das duas localizações; persistência local não publica dados; fronteira de idioma Debug/Release segue POL-0000000003.
- **Exclusões/limites:** Não implementar empacotador/Release, publicar ou enviar dados, ou traduzir os artefatos SDD internos.

### TASK-013 — Executar suíte de integração, regressão e cobertura dos critérios

- **Objetivo:** Validar conjuntamente os componentes da unidade e produzir evidências rastreáveis para todos os critérios de aceitação antes de CONVERGE.
- **Origem na SPEC:** RF-001–RF-014; CA-001–CA-015.
- **Origem no PLAN:** D-01–D-14; seções 11–16.
- **Dependências:** TASK-001 a TASK-012.
- **Artefatos/componentes previstos:** Suíte `unittest` de integração/regressão e relatório de evidências; fixtures controladas; execução independente de processos/contextos.
- **Trabalho autorizado:** Integrar os testes já previstos nas tarefas; cobrir fluxos de criação, persistência, recuperação, comparação, falha e continuidade; executar em contexto novo sem memória compartilhada; registrar versões das entradas, resultados, falhas e limitações. Executar as validações tecnicamente disponíveis no ambiente IMPLEMENT sem declarar prova que não foi produzida.
- **Verificações/testes previstos:** Matriz CA-001–CA-015; rastreabilidade requisito/decisão/tarefa; teste concorrente e colisões controladas; preservação de histórico; recuperação interexecução; falhas de sonda/fallback; exclusões de publicação; regressão dos documentos anteriores. A raiz real somente pode ser usada se sua sonda D-02 passar; teste-fixture não substitui esse resultado.
- **Evidência esperada:** Resultados individualizados por CA, entradas/versões, logs determinísticos e referências reproduzíveis; resultados negativos preservados; matriz final de cobertura.
- **Critérios de conclusão:** Todos os critérios aplicáveis possuem evidência ou limitação/bloqueio explícito; nenhum sucesso é inferido de ausência de erro; a evidência está pronta para avaliação por ANALYZE/CONVERGE nas etapas próprias.
- **Exclusões/limites:** Esta TASKS não executa os testes. Esta tarefa futura não declara PASS de ANALYZE ou CONVERGED; não inicia etapas/gates por si só.

## Matriz de rastreabilidade RF → decisão do PLAN → TASK

| Requisito | Decisão/seção do PLAN | TASK de cobertura |
|---|---|---|
| RF-001 | D-01–D-04; §§3.1, 4.1–4.2 | TASK-001, TASK-002, TASK-003 |
| RF-002 | D-02–D-04; §§4.2, 9.2 | TASK-002, TASK-003 |
| RF-003 | D-05–D-07; §§5–6 | TASK-004, TASK-005 |
| RF-004 | D-07–D-09, D-13; §§6–7, 9 | TASK-005, TASK-006, TASK-008 |
| RF-005 | D-09–D-10, D-13; §§8–9 | TASK-008, TASK-009 |
| RF-006 | D-04–D-10, D-12; §§5, 8, 11 | TASK-004, TASK-009, TASK-010, TASK-013 |
| RF-007 | D-09–D-11; §§7.2, 8.2 | TASK-006, TASK-007, TASK-009 |
| RF-008 | D-04, D-10–D-12; §§8, 11 | TASK-007, TASK-009, TASK-010 |
| RF-009 | D-08–D-10; §§2, 6, 9.2 | TASK-011 |
| RF-010 | D-03, D-07–D-10; §§3.1, 6, 9.2 | TASK-003, TASK-011 |
| RF-011 | D-08–D-10; §§2, 7, 9.2 | TASK-006, TASK-009, TASK-011 |
| RF-012 | D-14; §10 | TASK-012 |
| RF-013 | D-14; §§10, 13 | TASK-012 |
| RF-014 | D-07–D-09, D-12; §§6–8 | TASK-005, TASK-006, TASK-010 |

## Matriz de rastreabilidade CA → TASK → verificação/evidência

| Critério | TASK | Verificação/evidência prevista |
|---|---|---|
| CA-001 | TASK-002, TASK-003, TASK-013 | Criar raiz ausente quando necessária; registrar operações e resultado de D-02 sem presumir sucesso. |
| CA-002 | TASK-002, TASK-003 | Fixture instrumentada prova tentativa do preferencial primeiro; derivação Debug confere com o PLAN. |
| CA-003 | TASK-003 | Erro concreto classificado aciona fallback; erro desconhecido não; evidência por cenário. |
| CA-004 | TASK-004 | UUIDv4 válido, diretório exclusivo, correlação e colisões/limite documentados. |
| CA-005 | TASK-005, TASK-006 | Estrutura por análise/tipo e `.md` com formato validado. |
| CA-006 | TASK-009, TASK-010, TASK-013 | Novo processo/contexto recupera e interpreta documentos sem conversa original. |
| CA-007 | TASK-008, TASK-009 | Bytes/hash anteriores permanecem imutáveis; nova versão relaciona o documento anterior; destino não é substituído. |
| CA-008 | TASK-007, TASK-009 | Mudança de entrada gera `CHANGED_REASSESS`; inacessibilidade/não verificabilidade não vira igualdade. |
| CA-009 | TASK-009, TASK-013 | Evidência anterior é recuperada por outro contexto e usada em nova validação/comparação relacionada. |
| CA-010 | TASK-011 | Lacuna é persistida com motivo, impacto e autoridade; apenas parte afetada interrompida. |
| CA-011 | TASK-011, TASK-013 | Cenários de autonomia autorizada e bloqueio por ambiguidade, conflito, evidência ou autoridade. |
| CA-012 | TASK-006, TASK-009, TASK-011 | Fonte normativa prevalece sobre documento de workspace conflitante; divergência fica evidenciada. |
| CA-013 | TASK-012 | Manifesto-fixture exclui `.workspace` preferencial e fallback interno. |
| CA-014 | TASK-012 | Spies comprovam ausência de chamadas externas/Git; inventário e evidência localizados. |
| CA-015 | TASK-012, TASK-013 | Revisão dos artefatos internos pt-BR e fixture do conteúdo runtime distribuível conforme POL-0000000003. |

## Cobertura das decisões D-01 a D-14

| Decisão do PLAN | TASK de cobertura |
|---|---|
| D-01 — RickCraftRoot e entrada explícita | TASK-001, TASK-002 |
| D-02 — Sonda das capacidades necessárias por raiz | TASK-003 |
| D-03 — Classes de falha e fallback | TASK-003 |
| D-04 — Reavaliação de raízes, leitura histórica/união | TASK-002, TASK-009 |
| D-05 — ANL-UUIDv4 e retomada | TASK-004 |
| D-06 — Criação exclusiva, colisões e limite de tentativas | TASK-004, TASK-008 |
| D-07 — Catálogo TipoDocumento | TASK-005 |
| D-08 — JSON v1, UTF-8 e validação | TASK-006 |
| D-09 — Identidade, filename, metadados e relações | TASK-006, TASK-008, TASK-009 |
| D-10 — Append-only e histórico | TASK-008, TASK-009 |
| D-11 — Proveniência e SHA-256 | TASK-007, TASK-009 |
| D-12 — Pesquisa sem índice persistente | TASK-010 |
| D-13 — Publicação por os.link e verificação final | TASK-003, TASK-008 |
| D-14 — Privacidade e exclusão de Release/publicação | TASK-012 |

## Limites do estágio

TASKS é o fatiamento completo do PLAN aprovado; `TASKS = COMPLETE` não é `ANALYZE = PASS`, não inicia IMPLEMENT e não demonstra que a sonda D-02 ou qualquer teste passou. Não executar testes, ANALYZE, código, instalação, Release ou materialização de diretórios nesta etapa. O próximo estágio possível é ANALYZE após revisão do estado publicado.
