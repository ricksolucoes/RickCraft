# Registry de Specifications

Registro persistente de alocação de IDs SPEC, mantido conforme [POL-0000000001 — Governança documental](../policies/POL-0000000001-governanca-documental.md) e [POL-0000000002 — Processo de desenvolvimento orientado por Specification](../policies/POL-0000000002-processo-sdd.md).

Este Registry é a fonte de alocação dos IDs SPEC e preserva todos os IDs consumidos, inclusive os de unidades canceladas ou cuja materialização falhou. Diretórios de unidades servem somente para validação de consistência. Este Registry não substitui os artefatos da unidade nem registra o estado operacional do pipeline, que pertence a `status.md`.

## Regra de alocação

Antes de materializar uma unidade SDD:

1. confirmar que o grupo está `VIGENTE` no Registry de grupos;
2. consultar este Registry;
3. usar `0000001` se ainda não houver sequência alocada para o grupo; caso contrário, usar a maior sequência alocada para o grupo acrescida de um;
4. registrar o ID neste Registry;
5. somente então materializar a unidade.

Lacunas nunca são preenchidas retroativamente. Uma alocação consome o ID permanentemente, mesmo que a materialização falhe ou a unidade seja cancelada. Não se registram estados SPEC/PLAN/TASKS/ANALYZE/IMPLEMENT/CONVERGE aqui.

## IDs alocados

| ID completo | Grupo | Sequência | Slug | Título | Caminho da unidade | Data da alocação |
|---|---|---|---|---|---|---|
| `SPEC-0000000001` | `000` | `0000001` | `workspace-operacional-rastreavel` | Workspace Operacional Persistente e Rastreabilidade entre Agents | `specs/SPEC-0000000001-workspace-operacional-rastreavel/` | 2026-10-10 |
| `SPEC-0000000002` | `000` | `0000002` | `protocolo-revisao-tecnica` | Protocolo de Revisão Técnica, Escopo e Resposta do RickCraft | `specs/SPEC-0000000002-protocolo-revisao-tecnica/` | 2026-10-11 |
| `SPEC-0060000001` | `006` | `0000001` | `evidencia-estrutural-convencoes-delphi` | Evidência Estrutural e Convenções Delphi/Object Pascal | `specs/SPEC-0060000001-evidencia-estrutural-convencoes-delphi/` | 2026-10-12 |
