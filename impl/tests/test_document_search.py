from __future__ import annotations

import hashlib
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib import request


RUNTIME_DIRECTORY = Path(__file__).resolve().parents[1] / "src" / "RickCraft"
sys.path.insert(0, str(RUNTIME_DIRECTORY))

from document_catalog import DOCUMENT_TYPES
from document_format import serializar_documento
from document_recovery import RecoveredDocument
from document_search import SearchInputError, SearchQuery, pesquisar_documentos
from workspace_resolver import RaizWorkspaceSelecionada, TipoRaizWorkspace


ANALYSIS_A = "ANL-aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
ANALYSIS_B = "ANL-bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
DOC_1 = "DOC-10000000-0000-4000-8000-000000000001"
DOC_2 = "DOC-10000000-0000-4000-8000-000000000002"
DOC_3 = "DOC-10000000-0000-4000-8000-000000000003"
DOC_4 = "DOC-10000000-0000-4000-8000-000000000004"
DOC_5 = "DOC-10000000-0000-4000-8000-000000000005"
DOC_6 = "DOC-10000000-0000-4000-8000-000000000006"
DOC_7 = "DOC-10000000-0000-4000-8000-000000000007"
DOC_8 = "DOC-10000000-0000-4000-8000-000000000008"
DOC_9 = "DOC-10000000-0000-4000-8000-000000000009"
DOC_10 = "DOC-10000000-0000-4000-8000-000000000010"


class DocumentSearchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(
            prefix="rickcraft-search-", dir=Path(__file__).resolve().parent
        )
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "repo" / "impl" / "src" / "RickCraft"
        self.root.mkdir(parents=True)
        self.preferred = self.root.parent.parent / ".workspace"
        self.fallback = self.root / ".workspace"
        self.preferred.mkdir(parents=True)
        self.resolver = Mock(
            return_value=RaizWorkspaceSelecionada(
                TipoRaizWorkspace.PREFERENCIAL, self.preferred
            )
        )
        self.evaluator_factory = self._evaluator_factory
        self.files: dict[str, tuple[Path, bytes]] = {}
        self._seed_documents()

    @staticmethod
    def _evaluator_factory():
        class Evaluator:
            evidencias: tuple[object, ...] = ()

            def __call__(self, _path):
                raise AssertionError("resolver controlado não deve executar D-02")

        return Evaluator

    @staticmethod
    def _metadata(
        analysis_id: str,
        document_id: str,
        document_type: str,
        *,
        created: str,
        purpose: str,
        inputs: list[dict[str, object]] | None = None,
        relations: list[dict[str, object]] | None = None,
        extra: dict[str, object] | None = None,
    ) -> dict[str, object]:
        value: dict[str, object] = {
            "schema_version": 1,
            "type_catalog_version": 1,
            "document_id": document_id,
            "analysis_id": analysis_id,
            "document_type": document_type,
            "workspace_root_kind": "preferred",
            "created_at_utc": created,
            "purpose": purpose,
            "origin": {"kind": "test", "reference": "TASK-010"},
            "inputs": inputs or [],
            "relations": relations or [],
        }
        if extra:
            value.update(extra)
        return value

    def add_document(
        self,
        workspace: Path,
        analysis_id: str,
        document_id: str,
        document_type: str,
        *,
        body: str,
        created: str = "2026-10-10T12:00:00Z",
        purpose: str | None = None,
        inputs: list[dict[str, object]] | None = None,
        relations: list[dict[str, object]] | None = None,
        extra: dict[str, object] | None = None,
    ) -> tuple[Path, bytes]:
        metadata = self._metadata(
            analysis_id,
            document_id,
            document_type,
            created=created,
            purpose=purpose or f"Purpose {document_id}",
            inputs=inputs,
            relations=relations,
            extra=extra,
        )
        path = workspace / analysis_id / document_type / f"{document_id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        data = serializar_documento("Documento de teste", metadata, body)
        path.write_bytes(data)
        self.files[document_id] = (path, data)
        return path, data

    def _seed_documents(self) -> None:
        self.add_document(
            self.preferred, ANALYSIS_A, DOC_1, "evidence",
            body="Evidência sobre coração e decisão técnica.",
            created="2026-10-10T12:00:00Z", purpose="Relatório técnico",
            inputs=[{"kind": "workspace_document", "locator": DOC_5, "verification": "MATCHED"}],
            relations=[{"relation_type": "supports", "document_id": DOC_5, "analysis_id": ANALYSIS_B}],
            extra={"quality": {"approved": True, "score": 2}},
        )
        self.add_document(
            self.preferred, ANALYSIS_A, DOC_2, "result",
            body="Resultado da análise robusta.", created="2026-10-09T12:00:00Z",
            purpose="Resultado final", inputs=[{"kind": "local_file", "locator": "source.py"}],
            relations=[{"relation_type": "related_to", "document_id": DOC_1}],
        )
        self.add_document(
            self.preferred, ANALYSIS_A, DOC_3, "divergence",
            body="Divergência entre referências.", created="2026-10-10T12:00:00Z",
        )
        self.add_document(
            self.preferred, ANALYSIS_A, DOC_4, "blocker",
            body="Bloqueio aguardando autoridade.", created="2026-10-11T12:00:00Z",
        )
        self.add_document(
            self.preferred, ANALYSIS_B, DOC_5, "context",
            body="Contexto da segunda análise.", created="2026-10-08T12:00:00Z",
        )
        self.add_document(
            self.preferred, ANALYSIS_A, DOC_6, "analysis",
            body="Análise textual sem acentos.", created="2026-10-10T12:00:00Z",
        )
        self.add_document(
            self.preferred, ANALYSIS_A, DOC_7, "decision",
            body="Decisão e evidência registradas.", created="2026-10-10T12:00:00Z",
        )
        self.add_document(
            self.preferred, ANALYSIS_B, DOC_8, "handoff",
            body="Handoff para a próxima sessão.", created="2026-10-12T12:00:00Z",
        )

    def search(self, query: SearchQuery | None = None, **kwargs):
        return pesquisar_documentos(
            self.root,
            query,
            resolver=kwargs.pop("resolver", self.resolver),
            avaliador_factory=self.evaluator_factory,
            **kwargs,
        )

    @staticmethod
    def ids(result):
        return {document.document_id for document in result.matches}

    def test_01_consulta_sem_filtros_lista_documentos_validos(self):
        result = self.search()
        self.assertEqual(len(result.matches), 8)
        self.assertTrue(all(isinstance(item, RecoveredDocument) for item in result.matches))

    def test_02_filtro_analysis_id(self):
        self.assertEqual(self.ids(self.search(SearchQuery(analysis_id=ANALYSIS_B))), {DOC_5, DOC_8})

    def test_03_analysis_id_invalido_rejeitado_antes_da_recuperacao(self):
        resolver = Mock(side_effect=AssertionError("não deve recuperar"))
        with self.assertRaises(SearchInputError):
            self.search(SearchQuery(analysis_id="ANL-invalido"), resolver=resolver)
        resolver.assert_not_called()

    def test_04_filtro_document_type(self):
        self.assertEqual(self.ids(self.search(SearchQuery(document_type="evidence"))), {DOC_1})

    def test_05_document_type_invalido_rejeitado_antes_da_recuperacao(self):
        resolver = Mock(side_effect=AssertionError("não deve recuperar"))
        with self.assertRaises(SearchInputError):
            self.search(SearchQuery(document_type="Evidence"), resolver=resolver)
        resolver.assert_not_called()

    def test_06_filtro_document_id(self):
        self.assertEqual(self.ids(self.search(SearchQuery(document_id=DOC_1))), {DOC_1})

    def test_07_document_id_invalido_rejeitado_antes_da_recuperacao(self):
        resolver = Mock(side_effect=AssertionError("não deve recuperar"))
        with self.assertRaises(SearchInputError):
            self.search(SearchQuery(document_id="DOC-../fora"), resolver=resolver)
        resolver.assert_not_called()

    def test_08_document_id_inexistente_retorna_zero_matches(self):
        missing = "DOC-10000000-0000-4000-8000-000000000099"
        self.assertEqual(self.search(SearchQuery(document_id=missing)).matches, ())

    def test_09_metadata_equals_localiza_valor_exato(self):
        self.assertEqual(self.ids(self.search(SearchQuery(metadata_equals={"purpose": "Relatório técnico"}))), {DOC_1})

    def test_10_metadata_equals_exclui_nao_correspondente(self):
        result = self.search(SearchQuery(document_id=DOC_1, metadata_equals={"purpose": "outro"}))
        self.assertEqual(result.matches, ())
        self.assertEqual(result.exclusions[0].reasons, ("metadata",))

    def test_11_metadata_nao_coage_tipos(self):
        self.assertEqual(self.search(SearchQuery(document_id=DOC_1, metadata_equals={"quality": {"approved": 1, "score": 2}})).matches, ())

    def test_12_input_equals_encontra_kind(self):
        self.assertEqual(self.ids(self.search(SearchQuery(input_equals={"kind": "workspace_document"}))), {DOC_1})

    def test_13_input_equals_encontra_locator(self):
        self.assertEqual(self.ids(self.search(SearchQuery(input_equals={"locator": DOC_5}))), {DOC_1})

    def test_14_input_equals_exige_pares_no_mesmo_input(self):
        self.assertEqual(self.search(SearchQuery(document_id=DOC_1, input_equals={"kind": "local_file", "locator": DOC_5})).matches, ())

    def test_15_relation_equals_encontra_relation_type(self):
        self.assertEqual(self.ids(self.search(SearchQuery(relation_equals={"relation_type": "supports"}))), {DOC_1})

    def test_16_relation_equals_encontra_document_id_alvo(self):
        self.assertEqual(self.ids(self.search(SearchQuery(relation_equals={"document_id": DOC_5}))), {DOC_1})

    def test_17_relation_equals_encontra_analysis_id_explicito(self):
        self.assertEqual(self.ids(self.search(SearchQuery(relation_equals={"analysis_id": ANALYSIS_B}))), {DOC_1})

    def test_18_text_terms_encontra_substring_literal_no_corpo(self):
        self.assertEqual(self.ids(self.search(SearchQuery(text_terms=("cora",)))), {DOC_1})

    def test_19_text_terms_usa_casefold(self):
        self.assertEqual(self.ids(self.search(SearchQuery(text_terms=("EVIDÊNCIA",)))), {DOC_1, DOC_7})

    def test_20_text_terms_preserva_acentuacao_pt_br(self):
        self.assertEqual(self.ids(self.search(SearchQuery(text_terms=("coração",)))), {DOC_1})

    def test_21_varios_termos_textuais_combinam_com_and(self):
        self.assertEqual(self.ids(self.search(SearchQuery(text_terms=("coração", "decisão")))), {DOC_1})

    def test_22_termo_ausente_exclui_documento(self):
        result = self.search(SearchQuery(document_id=DOC_1, text_terms=("inexistente",)))
        self.assertEqual(result.matches, ())
        self.assertIn("text", result.exclusions[0].reasons)

    def test_23_termo_vazio_e_rejeitado(self):
        with self.assertRaises(SearchInputError):
            self.search(SearchQuery(text_terms=("  ",)))

    def test_24_metadata_mapping_vazio_e_rejeitado(self):
        with self.assertRaises(SearchInputError):
            self.search(SearchQuery(metadata_equals={}))

    def test_25_input_mapping_vazio_e_rejeitado(self):
        with self.assertRaises(SearchInputError):
            self.search(SearchQuery(input_equals={}))

    def test_26_relation_mapping_vazio_e_rejeitado(self):
        with self.assertRaises(SearchInputError):
            self.search(SearchQuery(relation_equals={}))

    def test_27_analysis_id_e_document_type_combinam_com_and(self):
        self.assertEqual(self.ids(self.search(SearchQuery(analysis_id=ANALYSIS_A, document_type="evidence"))), {DOC_1})

    def test_28_document_type_e_text_combinam_com_and(self):
        self.assertEqual(self.ids(self.search(SearchQuery(document_type="evidence", text_terms=("coração",)))), {DOC_1})

    def test_29_analysis_id_e_metadata_combinam_com_and(self):
        self.assertEqual(self.ids(self.search(SearchQuery(analysis_id=ANALYSIS_A, metadata_equals={"purpose": "Relatório técnico"}))), {DOC_1})

    def test_30_input_e_text_combinam_com_and(self):
        self.assertEqual(self.ids(self.search(SearchQuery(input_equals={"kind": "workspace_document"}, text_terms=("coração",)))), {DOC_1})

    def test_31_relation_e_document_type_combinam_com_and(self):
        self.assertEqual(self.ids(self.search(SearchQuery(relation_equals={"relation_type": "supports"}, document_type="evidence"))), {DOC_1})

    def test_32_document_id_e_metadata_combinam_com_and(self):
        self.assertEqual(self.ids(self.search(SearchQuery(document_id=DOC_1, metadata_equals={"purpose": "Relatório técnico"}))), {DOC_1})

    def test_33_tipo_evidence_e_localizavel(self):
        self.assertEqual(self.ids(self.search(SearchQuery(document_type="evidence"))), {DOC_1})

    def test_34_tipo_divergence_e_localizavel(self):
        self.assertEqual(self.ids(self.search(SearchQuery(document_type="divergence"))), {DOC_3})

    def test_35_tipo_blocker_e_localizavel(self):
        self.assertEqual(self.ids(self.search(SearchQuery(document_type="blocker"))), {DOC_4})

    def test_36_tipo_result_e_localizavel(self):
        self.assertEqual(self.ids(self.search(SearchQuery(document_type="result"))), {DOC_2})

    def test_37_documento_invalido_nao_entra_em_matches(self):
        bad_path = self.preferred / ANALYSIS_A / "evidence" / f"{DOC_9}.md"
        bad_path.write_bytes(b"documento invalido")
        self.assertNotIn(DOC_9, self.ids(self.search()))

    def test_38_finding_de_documento_invalido_permanece_disponivel(self):
        (self.preferred / ANALYSIS_A / "evidence" / f"{DOC_9}.md").write_bytes(b"invalido")
        result = self.search()
        self.assertIn("INVALID_DOCUMENT", {finding.code for finding in result.findings})

    def test_39_document_id_divergente_nao_entra_em_matches(self):
        path = self.fallback / ANALYSIS_A / "evidence" / f"{DOC_10}.md"
        path.parent.mkdir(parents=True)
        data = serializar_documento("Divergente", self._metadata(ANALYSIS_A, DOC_10, "evidence", created="2026-10-10T12:00:00Z", purpose="Divergente"), "Outra cópia")
        path.write_bytes(data)
        self.add_document(self.preferred, ANALYSIS_A, DOC_10, "evidence", body="Cópia original", purpose="Divergente")
        self.assertNotIn(DOC_10, self.ids(self.search()))

    def test_40_document_id_direcionado_preserva_divergencia_sem_vencedor(self):
        path = self.fallback / ANALYSIS_A / "evidence" / f"{DOC_10}.md"
        path.parent.mkdir(parents=True)
        path.write_bytes(serializar_documento("Divergente", self._metadata(ANALYSIS_A, DOC_10, "evidence", created="2026-10-10T12:00:00Z", purpose="Divergente"), "Cópia conflitante"))
        self.add_document(self.preferred, ANALYSIS_A, DOC_10, "evidence", body="Cópia original")
        result = self.search(SearchQuery(document_id=DOC_10))
        self.assertEqual(result.matches, ())
        self.assertEqual([item.document_id for item in result.divergences], [DOC_10])

    def test_41_copias_identicas_deduplicam_em_uma_identidade_logica(self):
        path, data = self.files[DOC_1]
        duplicate = self.fallback / ANALYSIS_A / "evidence" / path.name
        duplicate.parent.mkdir(parents=True)
        duplicate.write_bytes(data)
        result = self.search(SearchQuery(document_id=DOC_1))
        self.assertEqual(len(result.matches), 1)
        self.assertEqual(len(result.matches[0].locations), 2)

    def test_42_exclusao_registra_document_id(self):
        result = self.search(SearchQuery(document_type="blocker"))
        exclusion = next(item for item in result.exclusions if item.document_id == DOC_1)
        self.assertEqual(exclusion.document_id, DOC_1)

    def test_43_exclusao_registra_motivo(self):
        result = self.search(SearchQuery(document_type="blocker"))
        exclusion = next(item for item in result.exclusions if item.document_id == DOC_1)
        self.assertEqual(exclusion.reasons, ("document_type",))

    def test_44_exclusao_preserva_multiplos_motivos(self):
        query = SearchQuery(analysis_id=ANALYSIS_B, document_type="blocker", metadata_equals={"purpose": "ausente"}, text_terms=("ausente",))
        result = self.search(query)
        exclusion = next(item for item in result.exclusions if item.document_id == DOC_1)
        self.assertEqual(exclusion.reasons, ("analysis_id", "document_type", "metadata", "text"))

    def test_45_resultados_ordenados_por_created_at_utc(self):
        result = self.search()
        self.assertEqual([d.document_id for d in result.matches], [DOC_5, DOC_2, DOC_1, DOC_3, DOC_6, DOC_7, DOC_4, DOC_8])

    def test_46_empate_de_data_ordenado_por_document_id(self):
        tied = [d.document_id for d in self.search().matches if d.created_at_utc == "2026-10-10T12:00:00Z"]
        self.assertEqual(tied, sorted(tied))

    def test_46a_ordenacao_usa_instante_utc_e_nao_compara_texto(self):
        self.add_document(self.preferred, ANALYSIS_A, DOC_9, "decision", body="fraction", created="2026-10-10T00:00:00.100Z")
        self.add_document(self.preferred, ANALYSIS_A, DOC_10, "decision", body="whole", created="2026-10-10T00:00:00Z")
        ordered = [item.document_id for item in self.search(SearchQuery(document_type="decision")).matches]
        self.assertEqual(ordered, [DOC_10, DOC_9, DOC_7])

    def test_47_ordenacao_e_busca_nao_modificam_metadata(self):
        before = {doc: path.read_bytes() for doc, (path, _data) in self.files.items()}
        self.search()
        self.assertEqual(before, {doc: path.read_bytes() for doc, (path, _data) in self.files.items()})

    def test_48_findings_de_root_sao_preservados(self):
        self.fallback.mkdir()
        result = self.search(resolver=Mock(return_value=RaizWorkspaceSelecionada(TipoRaizWorkspace.FALLBACK, self.fallback)))
        self.assertIn("ROOT_NOT_READ", {finding.code for finding in result.findings})

    def test_49_roots_da_recuperacao_sao_preservados(self):
        result = self.search()
        self.assertEqual({root.kind for root in result.roots}, {"preferred", "fallback"})

    def test_50_selected_root_kind_e_preservado(self):
        result = self.search()
        self.assertEqual(result.selected_root_kind, "preferred")

    def test_51_nova_consulta_reinvoca_resolver(self):
        self.search()
        self.search(SearchQuery(document_type="blocker"))
        self.assertEqual(self.resolver.call_count, 2)

    def test_52_nova_consulta_observa_novo_documento_sem_cache(self):
        before = len(self.search().matches)
        self.add_document(self.preferred, ANALYSIS_A, DOC_9, "evidence", body="novo")
        after = self.search()
        self.assertEqual(len(after.matches), before + 1)
        self.assertIn(DOC_9, self.ids(after))

    def test_53_consulta_nao_cria_artefato_de_indice_ou_cache(self):
        self.search()
        names = {path.name.lower() for path in self.preferred.rglob("*") if path.is_file()}
        self.assertFalse(names & {"index.json", "manifest.json", "cache.db", "search-index.json"})

    def test_54_consulta_nao_altera_bytes_dos_documentos(self):
        before = {doc: hashlib.sha256(path.read_bytes()).hexdigest() for doc, (path, _data) in self.files.items()}
        self.search()
        after = {doc: hashlib.sha256(path.read_bytes()).hexdigest() for doc, (path, _data) in self.files.items()}
        self.assertEqual(before, after)

    def test_55_consulta_nao_chama_os_link(self):
        with patch("os.link") as link:
            self.search()
        link.assert_not_called()

    def test_56_consulta_nao_cria_anl_ou_doc(self):
        before = sorted(path.relative_to(self.preferred) for path in self.preferred.rglob("*"))
        self.search()
        after = sorted(path.relative_to(self.preferred) for path in self.preferred.rglob("*"))
        self.assertEqual(before, after)

    def test_57_consulta_nao_acessa_rede(self):
        with patch.object(request, "urlopen") as urlopen, patch.object(socket, "create_connection") as connect:
            self.search()
        urlopen.assert_not_called()
        connect.assert_not_called()

    def test_58_consulta_nao_invoca_git_ou_subprocesso(self):
        with patch.object(subprocess, "run") as run, patch.object(subprocess, "Popen") as popen:
            self.search()
        run.assert_not_called()
        popen.assert_not_called()

    def test_59_pesquisa_textual_nao_procura_no_json_de_metadata(self):
        self.assertEqual(self.search(SearchQuery(document_id=DOC_1, text_terms=("Relatório técnico",))).matches, ())

    def test_60_pesquisa_textual_nao_procura_em_ids_ou_paths(self):
        self.assertEqual(self.search(SearchQuery(document_id=DOC_1, text_terms=(DOC_1,))).matches, ())

    def test_61_campo_metadata_ausente_nao_corresponde(self):
        self.assertEqual(self.search(SearchQuery(document_id=DOC_1, metadata_equals={"not_present": "x"})).matches, ())

    def test_62_input_pairs_nao_sao_combinados_entre_objetos(self):
        self.add_document(self.preferred, ANALYSIS_A, DOC_9, "evidence", body="inputs", inputs=[{"kind": "local_file"}, {"locator": "source.py"}])
        self.assertNotIn(DOC_9, self.ids(self.search(SearchQuery(input_equals={"kind": "local_file", "locator": "source.py"}))))

    def test_63_relation_pairs_nao_sao_combinados_entre_objetos(self):
        self.add_document(self.preferred, ANALYSIS_A, DOC_9, "evidence", body="relations", relations=[
            {"relation_type": "supports", "document_id": DOC_2},
            {"relation_type": "related_to", "document_id": DOC_5},
        ])
        self.assertNotIn(DOC_9, self.ids(self.search(SearchQuery(relation_equals={"relation_type": "supports", "document_id": DOC_5}))))

    def test_64_text_terms_vazio_e_rejeitado(self):
        with self.assertRaises(SearchInputError):
            self.search(SearchQuery(text_terms=()))

    def test_65_mapping_com_chave_nao_textual_e_rejeitado(self):
        with self.assertRaises(SearchInputError):
            self.search(SearchQuery(metadata_equals={1: "valor"}))

    def test_66_mapping_com_objeto_executavel_e_rejeitado(self):
        with self.assertRaises(SearchInputError):
            self.search(SearchQuery(metadata_equals={"purpose": lambda: "x"}))

    def test_67_valor_booleano_nao_e_igual_a_inteiro_em_objeto_aninhado(self):
        self.assertEqual(self.search(SearchQuery(document_id=DOC_1, metadata_equals={"quality": {"approved": 1, "score": 2}})).matches, ())

    def test_68_cada_consulta_realiza_uma_recuperacao(self):
        self.search()
        self.assertEqual(self.resolver.call_count, 1)

    def test_69_filtro_document_id_divergente_preserva_zero_e_divergence(self):
        self.add_document(self.preferred, ANALYSIS_A, DOC_10, "evidence", body="A")
        duplicate = self.fallback / ANALYSIS_A / "evidence" / f"{DOC_10}.md"
        duplicate.parent.mkdir(parents=True)
        duplicate.write_bytes(serializar_documento("Divergente", self._metadata(ANALYSIS_A, DOC_10, "evidence", created="2026-10-10T12:00:00Z", purpose="B"), "B"))
        result = self.search(SearchQuery(document_id=DOC_10))
        self.assertEqual(result.matches, ())
        self.assertTrue(any(item.document_id == DOC_10 for item in result.divergences))

    def test_70_catalogo_v1_inteiro_permanece_aceito(self):
        self.assertEqual(DOCUMENT_TYPES, {"context", "analysis", "evidence", "decision", "divergence", "blocker", "result", "handoff"})
        for token in DOCUMENT_TYPES:
            with self.subTest(token=token):
                self.assertTrue(self.search(SearchQuery(document_type=token)).matches)

    def test_71_resultado_expoe_probe_evidence(self):
        result = self.search()
        self.assertEqual(result.probe_evidence, ())

    def test_72_fallback_nao_lido_fica_visivel_no_resultado(self):
        result = self.search()
        fallback = next(root for root in result.roots if root.kind == "fallback")
        self.assertEqual(fallback.status, "MISSING")


if __name__ == "__main__":
    unittest.main()
