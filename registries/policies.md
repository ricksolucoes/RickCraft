# Registry de Policies

Índice de identidade e ciclo de vida mantido conforme [POL-0000000001 — Governança documental](../policies/POL-0000000001-governanca-documental.md). Registrar uma Policy não equivale à sua aprovação.

| ID | Título | Estado | Escopo | Autoridade | Dependências | Sucessora |
|---|---|---|---|---|---|---|
| `POL-0000000001` | Governança documental | VIGENTE | Documentos normativos e registros controlados | Responsável pelo projeto | Nenhuma | — |
| `POL-0000000002` | Processo de desenvolvimento orientado por Specification | VIGENTE | Unidades funcionais SDD | Responsável pelo projeto; Decision Owners somente quando delegados | `POL-0000000001` | — |
| `POL-0000000003` | Ambientes, Runtime, Release e Workspace Operacional | VIGENTE | Ambiente de desenvolvimento, árvore canônica do RickCraft, Release, idioma do runtime e workspace operacional | Responsável pelo projeto | `POL-0000000001`, `POL-0000000002` | — |
| `POL-0000000004` | Fontes Técnicas de Referência e Base Conceitual | VIGENTE | Base técnica de referência, fontes locais/externas, adaptação conceitual cross-language e rastreabilidade | Responsável pelo projeto | `POL-0000000001`, `POL-0000000002` | — |

## Regras de manutenção

- Consultar este índice antes de alocar um ID.
- Não reutilizar IDs nem preencher lacunas numéricas retroativamente.
- Preservar registros de Policies substituídas e aposentadas.
- Alterar o estado somente mediante aprovação da autoridade indicada na Policy.
