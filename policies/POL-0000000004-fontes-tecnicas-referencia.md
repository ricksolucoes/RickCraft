# POL-0000000004 — Fontes Técnicas de Referência e Base Conceitual

- **Estado:** VIGENTE
- **Escopo:** adoção, identidade, consulta, interpretação, precedência e rastreabilidade de fontes técnicas locais e externas utilizadas pelo RickCraft.
- **Autoridade:** responsável pelo projeto
- **Dependências:** POL-0000000001 — Governança documental; POL-0000000002 — Processo de desenvolvimento orientado por Specification

## 1. Finalidade

O RickCraft mantém uma Base Técnica de Referência persistente para reduzir dependência exclusiva do conhecimento paramétrico de modelos, memória temporária, respostas anteriores e interpretações sem rastreabilidade. Quando houver Technical Reference vigente e materialmente aplicável, o RickCraft não deve substituí-la por conhecimento implícito do modelo; deve consultá-la ou registrar claramente que não pôde consultá-la antes de emitir conclusão que dependa de seu conteúdo. Conhecimento próprio pode apoiar o raciocínio, mas deve ser distinguido de conteúdo sustentado por referência, inferência e conhecimento externo não registrado.

Esta Policy governa o Registry `registries/technical-references.md`. A categoria e a identidade documental permanecem sujeitas à POL-0000000001; o processo SDD permanece sujeito à POL-0000000002.

Technical Reference é uma categoria distinta de Policy, Registry, Specification, PLAN, TASKS, status e evidência operacional do workspace. Ela registra conhecimento de apoio; não define por si só requisito funcional, estado de processo, gate ou evidência de execução.

## 2. Consulta proporcional

Uma Technical Reference em estado `VIGENTE` deve ser consultada quando a questão estiver materialmente em seu domínio e a decisão depender do conceito que ela cobre, quando SPEC/PLAN/revisão/análise declarar dependência daquela referência, ou quando for necessário confirmar o conceito técnico que a fonte registrada pretende fundamentar. Isso não exige reler todas as fontes em toda execução: a seleção é guiada por relevância material e pelo escopo da tarefa autorizada.

Se a fonte necessária não puder ser consultada, não alegar que foi consultada nem apresentar como verificado conteúdo que dela dependa. Registrar a limitação e tratar a conclusão conforme a suficiência de informação/evidência e a autoridade aplicáveis.

## 3. Independência de linguagem e adaptação

**A linguagem utilizada pelo exemplo de uma fonte técnica não limita a aplicabilidade do conceito. O RickCraft deve separar conceito e invariantes de sintaxe e particularidades da linguagem, adaptando a solução ao domínio técnico e à linguagem-alvo sem copiar mecanicamente a implementação de origem.**

Ao consultar uma fonte em outra linguagem, distinguir conceito, intenção, responsabilidades, invariantes, trade-offs e estrutura de colaboração de sintaxe, APIs, biblioteca padrão, modelo de memória, idioms e particularidades da linguagem. O primeiro grupo pode ser transferido conceitualmente quando aplicável; o segundo não deve ser transplantado mecanicamente.

Quando a linguagem-alvo for Delphi/Object Pascal, qualquer adaptação deve respeitar regras Delphi vigentes no RickCraft e as decisões competentes de arquitetura de interfaces, SOLID, Design Patterns, Clean Code e Engenharia Delphi, incluindo ownership/lifetime, memória, semântica de interfaces, generics, exceptions, concorrência e RTTI somente quando materialmente relacionados ao caso. Exemplo em outra linguagem não autoriza solução incompatível com Delphi/Object Pascal.

## 4. Exemplos e força normativa

Código demonstrativo e exemplos de Technical Reference são, por padrão, `REFERENCE_OR_EXAMPLE`; sua presença não torna padrão, estrutura, API ou implementação obrigatórios universalmente. Conceitos podem fundamentar decisões sem que o exemplo seja copiado.

Uma regra extraída somente assume força normativa após incorporação em Policy, Specification aprovada ou outro artefato normativo competente, ou por decisão explícita de Decision Owner dentro de sua autoridade. Não inferir obrigação a partir de exemplo, ilustração, preferência ou repetição na fonte.

## 5. Precedência, conflitos e Decision Owners

Technical Reference informa e fundamenta; não revoga silenciosamente norma vigente. Policies, decisões normativas competentes, SPEC/PLAN/TASKS dentro de seus escopos e gates válidos conservam a autoridade definida pela POL-0000000001, pela POL-0000000002 e pelas relações formais aplicáveis. A hierarquia explicativa é: regra normativa/decisão competente aplicável; contratos SPEC/PLAN/TASKS em seus respectivos escopos; Technical Reference como base conceitual. Esta síntese não cria precedência absoluta entre artefatos normativos que já tenham regras próprias de autoridade.

Se uma Technical Reference conflitar materialmente com regra normativa vigente do RickCraft, a regra normativa permanece aplicável e o conflito relevante deve ser registrado. Se duas Technical References divergirem e nenhuma regra vigente resolver o caso, não escolher silenciosamente: encaminhar ao Decision Owner competente ou ao responsável pelo projeto conforme a autoridade da decisão. Uma Technical Reference não cria nem transfere Decision Owner. Design Patterns mantém seleção/aplicabilidade de Patterns; SOLID, Interface Architecture, Clean Code e Delphi Engineering mantêm seus domínios; Quality/Audit avalia evidência e conformidade; Core não assume decisão especializada.

## 6. Identidade e rastreabilidade

`registries/technical-references.md` é o índice persistente e fonte de identidade das referências. Cada entrada possui ID `REF-` de largura fixa de dez dígitos, título, estado, tipo/classificação, caminho ou URL, domínio, finalidade, autoridade de adoção, identidade verificável (SHA-256, Git blob/revision ou equivalente) e observações. IDs são únicos, não reutilizados e não atribuídos retroativamente.

Quando uma decisão material depender de uma fonte, registrar proporcionalmente seu REF ID, versão/hash, seção/página/locator disponível, conceito utilizado, adaptação de linguagem relevante e eventual divergência em relação ao exemplo. Não impor burocracia desproporcional a uso trivial sem impacto decisório.

Uma fonte registrada não pode mudar silenciosamente mantendo aparência de mesma versão. Mudança material exige identidade/hash ou revisão nova registrada, análise de impacto e reavaliação apenas das decisões que dependam materialmente da versão anterior. Para fontes externas, URLs são referências navegacionais e podem mudar. Quando conteúdo remoto for material, registrar, quando possível, URL, data de consulta, locator e versão/snapshot. Cópia local controlada possui identidade mais estável que URL mutável; conteúdo remoto alterado não deve ser tratado como a mesma evidência histórica sem verificação.

## 7. Aprovação e manutenção

Inclusão, alteração de finalidade/domínio, mudança de estado ou retirada de uma Technical Reference requer autoridade do responsável pelo projeto e atualização rastreável do Registry. A aprovação da categoria não torna todo conteúdo da fonte uma regra RickCraft. A manutenção da lista de URLs em `docs/Site_REF.MD` segue esta Policy e não autoriza descoberta ou inclusão autônoma de sites.

