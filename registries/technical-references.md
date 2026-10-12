# Registry de Referências Técnicas

- **Estado do Registry:** VIGENTE
- **Autoridade de aprovação e manutenção:** responsável pelo projeto
- **Policy governante:** [POL-0000000004 — Fontes Técnicas de Referência e Base Conceitual](../policies/POL-0000000004-fontes-tecnicas-referencia.md)
- **Finalidade:** identidade persistente, estado e rastreabilidade das fontes técnicas locais e índices externos controlados. Registrar uma fonte não converte seu conteúdo em regra normativa.

IDs `REF-` têm dez dígitos, são únicos e não reutilizáveis. Hashes locais identificam os bytes registrados; Git blob/revision identifica o objeto correspondente no histórico Git. Para URL mutável, o Registry identifica o índice mantido localmente, não uma versão imutável do conteúdo remoto.

### Adoção inicial

`REF-0000000001`–`REF-0000000003` constituem o conjunto inicial aprovado simultaneamente à entrada em vigor da POL-0000000004, por decisão explícita do responsável pelo projeto. Essa adoção controlada não torna automaticamente referências oficiais outros arquivos já existentes no repositório.

| ID | Título | Estado | Tipo | Caminho | Domínio(s) | Finalidade | Autoridade de adoção | SHA-256 | Git blob/revision | Observações |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `REF-0000000001` | Referência — Padrões de Projeto | VIGENTE | `TECHNICAL_REFERENCE` | [`docs/Referencia Padrões de Projeto.pdf`](../docs/Referencia%20Padr%C3%B5es%20de%20Projeto.pdf) | Design Patterns | Base técnica conceitual conforme o conteúdo efetivamente consultado; não presumir conteúdo sem leitura. | Responsável pelo projeto | `4A76222990FFC2C5932D968F531512E116AFEFED5C5A68E7BEF07AC11E921F99` | `a1b658539ac8a173a785c9b2990141b501817832` | Cópia local binária preservada. |
| `REF-0000000002` | Referência — Refatoração de Projetos | VIGENTE | `TECHNICAL_REFERENCE` | [`docs/Referencia para Refatoração de Porjetos.pdf`](<../docs/Referencia para Refatoração de Porjetos.pdf>) | Clean Code / Refactoring | Base técnica conceitual conforme o conteúdo efetivamente consultado; não presumir conteúdo sem leitura. | Responsável pelo projeto | `E2C27070D124C1A896C2906802F62991B568970D630CC2AC7CD8148CDFCB103B` | `1f6449cabefa19f4c1461cdef8a98495a0f759a7` | Nome de arquivo preservado exatamente, inclusive a grafia `Porjetos`; cópia local binária preservada. |
| `REF-0000000003` | Sites de Referência | VIGENTE | `TECHNICAL_REFERENCE_INDEX` | [`docs/Site_REF.MD`](../docs/Site_REF.MD) | Índice externo controlado | Índice navegacional das fontes externas fornecidas e aprovadas; não fixa snapshot de conteúdo remoto. | Responsável pelo projeto | `10DBB8C5897AA1EE96E3E2BE918879CB3CC003C9CAB2CF808539D0F5AAF536D8` | `847323ea7576e67a71517444c471d3d7160e8b8a` | Contém a referência externa fornecida pelo responsável; URL pode mudar. Registrar URL, data de consulta, locator e snapshot quando conteúdo remoto fundamentar decisão material. |

## Regras de manutenção

- Consultar POL-0000000004 antes de incluir, alterar, substituir ou retirar referências.
- Preservar IDs consumidos e histórico; não reutilizar IDs nem preencher lacunas retroativamente.
- Atualizar hash/revision quando os bytes mudarem; registrar impacto e decisões que dependam materialmente da versão anterior.
- Não acrescentar URLs por descoberta autônoma. Adoção de nova fonte requer autoridade e rastreabilidade.
- Exemplos continuam `REFERENCE_OR_EXAMPLE` salvo regra explicitamente incorporada a artefato normativo competente.
