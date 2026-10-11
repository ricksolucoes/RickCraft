from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock


RUNTIME_DIRECTORY = Path(__file__).resolve().parents[1] / "src" / "RickCraft"
sys.path.insert(0, str(RUNTIME_DIRECTORY))

from document_format import serializar_documento
from document_recovery import (
    AnalysisRecoveryNotFoundError,
    DocumentIdentityDivergenceError,
    RecoveryInputError,
    recuperar_analise,
    recuperar_documento,
    recuperar_documentos,
    retomar_analise,
)
from workspace_resolver import RaizWorkspaceSelecionada, TipoRaizWorkspace


ANALYSIS_ID = "ANL-12345678-1234-4234-8234-123456789abc"
OTHER_ANALYSIS_ID = "ANL-87654321-4321-4321-8432-cba987654321"
DOCUMENT_ID = "DOC-12345678-1234-4234-8234-123456789abc"
OTHER_DOCUMENT_ID = "DOC-87654321-4321-4321-8432-cba987654321"
THIRD_DOCUMENT_ID = "DOC-aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"


def metadata(
    analysis_id: str,
    document_id: str,
    document_type: str = "evidence",
    *,
    created: str = "2026-10-10T12:00:00Z",
    inputs: list[dict[str, object]] | None = None,
    relations: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "type_catalog_version": 1,
        "document_id": document_id,
        "analysis_id": analysis_id,
        "document_type": document_type,
        "workspace_root_kind": "preferred",
        "created_at_utc": created,
        "purpose": "Evidência controlada para recuperação.",
        "origin": {"kind": "task_execution", "reference": "TASK-009-test"},
        "inputs": inputs or [],
        "relations": relations or [],
    }


class DocumentRecoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(
            prefix="rickcraft-recovery-", dir=Path(__file__).resolve().parent
        )
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "repository" / "impl" / "src" / "RickCraft"
        self.root.mkdir(parents=True)
        self.preferred = self.root.parent.parent / ".workspace"
        self.fallback = self.root / ".workspace"

    def selected_resolver(self, selected: Path | None = None, kind=None):
        selected = selected or self.preferred
        kind = kind or (
            TipoRaizWorkspace.PREFERENCIAL
            if selected == self.preferred
            else TipoRaizWorkspace.FALLBACK
        )
        calls: list[tuple[Path, object]] = []

        def resolve(_rickcraft_root, evaluator):
            calls.append((selected, evaluator))
            return RaizWorkspaceSelecionada(kind, selected)

        resolve.calls = calls  # type: ignore[attr-defined]
        return resolve

    @staticmethod
    def evaluator_factory():
        class Evaluator:
            evidencias: tuple[object, ...] = ()

            def __call__(self, _path):
                raise AssertionError("resolução controlada não deve executar D-02")

        return Evaluator

    def write_document(
        self,
        workspace: Path,
        analysis_id: str,
        document_id: str,
        *,
        document_type: str = "evidence",
        body: str = "Conteúdo persistido.",
        created: str = "2026-10-10T12:00:00Z",
        inputs: list[dict[str, object]] | None = None,
        relations: list[dict[str, object]] | None = None,
    ) -> tuple[Path, bytes]:
        folder = workspace / analysis_id / document_type
        folder.mkdir(parents=True, exist_ok=True)
        data = serializar_documento(
            "Documento recuperável",
            metadata(
                analysis_id,
                document_id,
                document_type,
                created=created,
                inputs=inputs,
                relations=relations,
            ),
            body,
        )
        path = folder / f"{document_id}.md"
        path.write_bytes(data)
        return path, data

    def recover(self, **kwargs):
        return recuperar_documentos(
            self.root,
            resolver=kwargs.pop("resolver", self.selected_resolver()),
            avaliador_factory=self.evaluator_factory,
            **kwargs,
        )

    def test_recupera_documento_pelo_id_e_confirma_hash_dos_bytes(self) -> None:
        self.preferred.mkdir()
        path, data = self.write_document(self.preferred, ANALYSIS_ID, DOCUMENT_ID)
        result = recuperar_documento(
            self.root,
            DOCUMENT_ID,
            resolver=self.selected_resolver(),
            avaliador_factory=self.evaluator_factory,
        )
        self.assertEqual(result.document_id, DOCUMENT_ID)
        self.assertEqual(result.analysis_id, ANALYSIS_ID)
        self.assertEqual(result.sha256, hashlib.sha256(data).hexdigest())
        self.assertEqual(result.locations[0].path, path)
        self.assertEqual(result.locations[0].workspace_root_kind, "preferred")

    def test_retoma_analysis_id_sem_criar_ou_mudar_diretorio(self) -> None:
        self.preferred.mkdir()
        path, data = self.write_document(self.preferred, ANALYSIS_ID, DOCUMENT_ID)
        before = hashlib.sha256(path.read_bytes()).hexdigest()
        result = retomar_analise(
            self.root,
            ANALYSIS_ID,
            resolver=self.selected_resolver(),
            avaliador_factory=self.evaluator_factory,
        )
        self.assertEqual([item.document_id for item in result.documents], [DOCUMENT_ID])
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before)
        self.assertEqual(path.read_bytes(), data)
        self.assertTrue((self.preferred / ANALYSIS_ID).is_dir())

    def test_ids_invalidos_sao_rejeitados_antes_de_compor_caminho(self) -> None:
        resolver = Mock(side_effect=AssertionError("ID inválido não inicia operação"))
        for analysis_id in ("ANL-../fora", "ANL-invalid", "ANL-12345678-1234-1234-8234-123456789abc"):
            with self.subTest(value=analysis_id), self.assertRaises(RecoveryInputError):
                recuperar_analise(
                    self.root,
                    analysis_id,
                    resolver=resolver,
                    avaliador_factory=self.evaluator_factory,
                )
        for document_id in ("DOC-../fora", "DOC-invalid", "DOC-12345678-1234-1234-8234-123456789abc"):
            with self.subTest(value=document_id), self.assertRaises(RecoveryInputError):
                recuperar_documento(
                    self.root,
                    document_id,
                    resolver=resolver,
                    avaliador_factory=self.evaluator_factory,
                )
        resolver.assert_not_called()

    def test_analise_vazia_pode_ser_retornada_sem_criar_estrutura(self) -> None:
        self.preferred.mkdir()
        (self.preferred / ANALYSIS_ID).mkdir()
        result = recuperar_analise(
            self.root,
            ANALYSIS_ID,
            resolver=self.selected_resolver(),
            avaliador_factory=self.evaluator_factory,
        )
        self.assertEqual(result.documents, ())
        self.assertTrue((self.preferred / ANALYSIS_ID).is_dir())

    def test_analise_ausente_bloqueia_sem_criar_pastas(self) -> None:
        self.preferred.mkdir()
        with self.assertRaises(AnalysisRecoveryNotFoundError):
            recuperar_analise(
                self.root,
                ANALYSIS_ID,
                resolver=self.selected_resolver(),
                avaliador_factory=self.evaluator_factory,
            )
        self.assertEqual(list(self.preferred.iterdir()), [])

    def test_raiz_preferencial_e_lida_e_fallback_existente_apenas_como_historico(self) -> None:
        self.preferred.mkdir()
        self.fallback.mkdir()
        _, preferred_bytes = self.write_document(self.preferred, ANALYSIS_ID, DOCUMENT_ID)
        _, fallback_bytes = self.write_document(self.fallback, ANALYSIS_ID, OTHER_DOCUMENT_ID)
        result = self.recover()
        self.assertEqual({item.document_id for item in result.documents}, {DOCUMENT_ID, OTHER_DOCUMENT_ID})
        self.assertEqual(
            {location.workspace_root_kind for item in result.documents for location in item.locations},
            {"preferred", "fallback"},
        )
        self.assertEqual({root.status for root in result.roots}, {"READ"})
        self.assertEqual(hashlib.sha256((self.preferred / ANALYSIS_ID / "evidence" / f"{DOCUMENT_ID}.md").read_bytes()).hexdigest(), hashlib.sha256(preferred_bytes).hexdigest())
        self.assertEqual(hashlib.sha256((self.fallback / ANALYSIS_ID / "evidence" / f"{OTHER_DOCUMENT_ID}.md").read_bytes()).hexdigest(), hashlib.sha256(fallback_bytes).hexdigest())

    def test_fallback_selecionado_nao_le_preferencial_historico(self) -> None:
        self.preferred.mkdir()
        self.fallback.mkdir(parents=True)
        self.write_document(self.preferred, ANALYSIS_ID, DOCUMENT_ID)
        self.write_document(self.fallback, ANALYSIS_ID, OTHER_DOCUMENT_ID)
        result = self.recover(resolver=self.selected_resolver(self.fallback))
        self.assertEqual({item.document_id for item in result.documents}, {OTHER_DOCUMENT_ID})
        statuses = {(root.kind, root.status) for root in result.roots}
        self.assertIn(("preferred", "NOT_READ_UNAVAILABLE"), statuses)
        self.assertIn(("fallback", "READ"), statuses)
        self.assertIn("ROOT_NOT_READ", {finding.code for finding in result.findings})

    def test_resolvedor_e_reinvocado_em_cada_operacao(self) -> None:
        self.preferred.mkdir()
        self.write_document(self.preferred, ANALYSIS_ID, DOCUMENT_ID)
        resolver = self.selected_resolver()
        for _ in range(2):
            recuperar_analise(
                self.root,
                ANALYSIS_ID,
                resolver=resolver,
                avaliador_factory=self.evaluator_factory,
            )
        self.assertEqual(len(resolver.calls), 2)  # type: ignore[attr-defined]

    def test_mesmo_id_e_mesmos_bytes_em_duas_raizes_deduplicam_preservando_locais(self) -> None:
        self.preferred.mkdir()
        self.fallback.mkdir()
        data = serializar_documento(
            "Documento recuperável", metadata(ANALYSIS_ID, DOCUMENT_ID), "Conteúdo idêntico."
        )
        for workspace in (self.preferred, self.fallback):
            folder = workspace / ANALYSIS_ID / "evidence"
            folder.mkdir(parents=True)
            (folder / f"{DOCUMENT_ID}.md").write_bytes(data)
        result = self.recover()
        self.assertEqual(len(result.documents), 1)
        self.assertEqual(len(result.documents[0].locations), 2)
        self.assertEqual(result.divergences, ())

    def test_mesmo_id_com_conteudo_diferente_registra_divergencia_e_bloqueia_lookup(self) -> None:
        self.preferred.mkdir()
        self.fallback.mkdir()
        self.write_document(self.preferred, ANALYSIS_ID, DOCUMENT_ID, body="Versão preferencial.")
        self.write_document(self.fallback, ANALYSIS_ID, DOCUMENT_ID, body="Versão histórica divergente.")
        result = self.recover()
        self.assertEqual(result.documents, ())
        self.assertEqual(len(result.divergences), 1)
        self.assertIn("DIVERGENCE_DOCUMENT_ID", {finding.code for finding in result.findings})
        with self.assertRaises(DocumentIdentityDivergenceError):
            result.document(DOCUMENT_ID)

    def test_documentos_invalidos_sao_reportados_e_os_independentes_recuperados(self) -> None:
        self.preferred.mkdir()
        good, _ = self.write_document(self.preferred, ANALYSIS_ID, DOCUMENT_ID)
        bad_dir = self.preferred / ANALYSIS_ID / "evidence"
        (bad_dir / f"{OTHER_DOCUMENT_ID}.md").write_bytes(b"not-a-valid-document")
        (bad_dir / "DOC-invalido.md").write_text("inválido", encoding="utf-8")
        result = self.recover()
        self.assertEqual([item.document_id for item in result.documents], [DOCUMENT_ID])
        invalid = [finding for finding in result.findings if finding.code == "INVALID_DOCUMENT"]
        self.assertEqual(len(invalid), 2)
        self.assertTrue(good.is_file())

    def test_temporarios_e_arquivos_que_nao_sao_md_sao_ignorados(self) -> None:
        self.preferred.mkdir()
        self.write_document(self.preferred, ANALYSIS_ID, DOCUMENT_ID)
        folder = self.preferred / ANALYSIS_ID / "evidence"
        (folder / "DOC-aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa.tmp").write_bytes(b"temporary")
        (folder / "anotacao.txt").write_text("não é documento", encoding="utf-8")
        result = self.recover()
        self.assertEqual([item.document_id for item in result.documents], [DOCUMENT_ID])
        self.assertEqual(result.findings, ())

    def test_symlink_de_diretorio_de_tipo_nao_e_seguido(self) -> None:
        self.preferred.mkdir()
        external = self.base / "external"
        external.mkdir()
        self.write_document(external, ANALYSIS_ID, DOCUMENT_ID)
        analysis = self.preferred / ANALYSIS_ID
        analysis.mkdir()
        link = analysis / "evidence"
        try:
            link.symlink_to(external / ANALYSIS_ID / "evidence", target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("O ambiente não permite criar symlink real neste usuário")
        result = self.recover()
        self.assertEqual(result.documents, ())
        self.assertIn("INVALID_TYPE_DIRECTORY", {finding.code for finding in result.findings})

    def test_redirecionamento_simulado_de_tipo_e_rejeitado_sem_link_real(self) -> None:
        self.preferred.mkdir()
        self.write_document(self.preferred, ANALYSIS_ID, DOCUMENT_ID)
        type_path = self.preferred / ANALYSIS_ID / "evidence"
        original = __import__("document_recovery")._is_redirect

        def redirect_only_type(path, info):
            return path == type_path or original(path, info)

        with unittest.mock.patch("document_recovery._is_redirect", side_effect=redirect_only_type):
            result = self.recover()
        self.assertEqual(result.documents, ())
        self.assertIn("INVALID_TYPE_DIRECTORY", {finding.code for finding in result.findings})

    def test_diretorios_e_documentos_sao_ordenados_por_data_utc_e_id(self) -> None:
        self.preferred.mkdir()
        self.write_document(self.preferred, ANALYSIS_ID, OTHER_DOCUMENT_ID, created="2026-10-10T12:00:01Z")
        self.write_document(self.preferred, ANALYSIS_ID, DOCUMENT_ID, created="2026-10-10T12:00:00Z")
        self.write_document(self.preferred, OTHER_ANALYSIS_ID, THIRD_DOCUMENT_ID, created="2026-10-10T11:00:00Z")
        result = self.recover()
        self.assertEqual(
            [(item.created_at_utc, item.document_id) for item in result.documents],
            [
                ("2026-10-10T11:00:00Z", THIRD_DOCUMENT_ID),
                ("2026-10-10T12:00:00Z", DOCUMENT_ID),
                ("2026-10-10T12:00:01Z", OTHER_DOCUMENT_ID),
            ],
        )

    def test_relacoes_sao_reconstruidas_e_targets_ausentes_ou_inconsistentes_reportados(self) -> None:
        self.preferred.mkdir()
        self.write_document(self.preferred, ANALYSIS_ID, DOCUMENT_ID, relations=[
            {"relation_type": "supports", "document_id": OTHER_DOCUMENT_ID, "analysis_id": OTHER_ANALYSIS_ID},
            {"relation_type": "related_to", "document_id": THIRD_DOCUMENT_ID},
        ])
        self.write_document(self.preferred, OTHER_ANALYSIS_ID, OTHER_DOCUMENT_ID)
        result = recuperar_analise(
            self.root,
            ANALYSIS_ID,
            resolver=self.selected_resolver(),
            avaliador_factory=self.evaluator_factory,
        )
        source = result.documents[0]
        self.assertEqual(len(source.relations), 2)
        self.assertTrue(source.relations[0].resolved)
        self.assertFalse(source.relations[1].resolved)
        self.assertIn("BROKEN_RELATION", {finding.code for finding in result.findings})

    def test_relacoes_com_analysis_id_incorreto_sao_inconsistentes(self) -> None:
        self.preferred.mkdir()
        self.write_document(self.preferred, ANALYSIS_ID, DOCUMENT_ID, relations=[
            {"relation_type": "corrects", "document_id": OTHER_DOCUMENT_ID, "analysis_id": ANALYSIS_ID}
        ])
        self.write_document(self.preferred, OTHER_ANALYSIS_ID, OTHER_DOCUMENT_ID)
        result = self.recover()
        self.assertIn("INCONSISTENT_RELATION", {finding.code for finding in result.findings})
        self.assertFalse(result.document(DOCUMENT_ID).relations[0].resolved)

    def test_ciclo_em_relacoes_e_reportado_sem_recursao_infinita(self) -> None:
        self.preferred.mkdir()
        self.write_document(self.preferred, ANALYSIS_ID, DOCUMENT_ID, relations=[
            {"relation_type": "related_to", "document_id": OTHER_DOCUMENT_ID}
        ])
        self.write_document(self.preferred, ANALYSIS_ID, OTHER_DOCUMENT_ID, relations=[
            {"relation_type": "related_to", "document_id": DOCUMENT_ID}
        ])
        result = self.recover()
        self.assertEqual(len(result.documents), 2)
        self.assertIn("RELATION_CYCLE", {finding.code for finding in result.findings})

    def test_inputs_local_documento_e_versionado_sao_revalidados_sem_mutar_historico(self) -> None:
        self.preferred.mkdir()
        local = self.base / "source.bin"
        local.write_bytes(b"source bytes")
        local_history = {
            "kind": "local_file",
            "locator": str(local.resolve()),
            "observed_at_utc": "2026-10-10T12:00:00Z",
            "sha256": hashlib.sha256(b"source bytes").hexdigest(),
            "verification": "UNVERIFIABLE",
        }
        workspace_history = {
            "kind": "workspace_document",
            "locator": OTHER_DOCUMENT_ID,
            "observed_at_utc": "2026-10-10T12:00:00Z",
            "sha256": "0" * 64,
            "verification": "UNVERIFIABLE",
        }
        version_history = {
            "kind": "versioned_source",
            "locator": "https://example.invalid/resource",
            "version_kind": "revision",
            "version": "r1",
            "observed_at_utc": "2026-10-10T12:00:00Z",
            "verification": "UNVERIFIABLE",
        }
        history_before = deepcopy([local_history, workspace_history, version_history])
        self.write_document(self.preferred, ANALYSIS_ID, DOCUMENT_ID, inputs=[
            local_history, workspace_history, version_history
        ])
        _, target_bytes = self.write_document(self.preferred, OTHER_ANALYSIS_ID, OTHER_DOCUMENT_ID)
        result = self.recover()
        doc = result.document(DOCUMENT_ID)
        states = [entry.verification["verification"] for entry in doc.input_verifications]
        self.assertEqual(states, ["MATCHED", "CHANGED_REASSESS", "UNVERIFIABLE"])
        self.assertEqual(doc.input_verifications[1].verification["sha256"], hashlib.sha256(target_bytes).hexdigest())
        self.assertEqual([local_history, workspace_history, version_history], history_before)

    def test_input_local_ausente_fica_unavailable_com_motivo(self) -> None:
        self.preferred.mkdir()
        missing = self.base / "missing-input.bin"
        history = {
            "kind": "local_file",
            "locator": str(missing.resolve()),
            "observed_at_utc": "2026-10-10T12:00:00Z",
            "sha256": "0" * 64,
            "verification": "UNVERIFIABLE",
        }
        self.write_document(self.preferred, ANALYSIS_ID, DOCUMENT_ID, inputs=[history])
        result = self.recover()
        verified = result.document(DOCUMENT_ID).input_verifications[0].verification
        self.assertEqual(verified["verification"], "UNAVAILABLE")
        self.assertTrue(verified["reason"])

    def test_documento_input_divergente_nao_e_escolhido(self) -> None:
        self.preferred.mkdir()
        self.fallback.mkdir()
        history = {
            "kind": "workspace_document",
            "locator": OTHER_DOCUMENT_ID,
            "observed_at_utc": "2026-10-10T12:00:00Z",
            "sha256": "0" * 64,
            "verification": "UNVERIFIABLE",
        }
        self.write_document(self.preferred, ANALYSIS_ID, DOCUMENT_ID, inputs=[history])
        self.write_document(self.preferred, OTHER_ANALYSIS_ID, OTHER_DOCUMENT_ID, body="A")
        self.write_document(self.fallback, OTHER_ANALYSIS_ID, OTHER_DOCUMENT_ID, body="B")
        result = self.recover()
        verification = result.document(DOCUMENT_ID).input_verifications[0].verification
        self.assertEqual(verification["verification"], "UNVERIFIABLE")
        self.assertIn("divergente", verification["reason"])

    def test_observacao_versionada_explicita_pode_comparar_revisao_atual(self) -> None:
        self.preferred.mkdir()
        history = {
            "kind": "versioned_source",
            "locator": "urn:recurso:exemplo",
            "version_kind": "commit",
            "version": "abc123",
            "observed_at_utc": "2026-10-10T12:00:00Z",
            "verification": "UNVERIFIABLE",
        }
        self.write_document(self.preferred, ANALYSIS_ID, DOCUMENT_ID, inputs=[history])
        result = self.recover(observacoes_atuais={"urn:recurso:exemplo": {
            "version_kind": "commit", "version": "abc123"
        }})
        self.assertEqual(
            result.document(DOCUMENT_ID).input_verifications[0].verification["verification"],
            "MATCHED",
        )

    def test_workspace_historico_legivel_e_unido_com_preferred_sem_alteracoes(self) -> None:
        self.preferred.mkdir()
        self.fallback.mkdir()
        legacy, legacy_bytes = self.write_document(self.fallback, ANALYSIS_ID, DOCUMENT_ID)
        before = hashlib.sha256(legacy_bytes).hexdigest()
        result = self.recover()
        self.assertEqual(len(result.documents), 1)
        self.assertEqual(result.documents[0].locations[0].workspace_root_kind, "fallback")
        self.assertEqual(hashlib.sha256(legacy.read_bytes()).hexdigest(), before)

    def test_root_preferencial_inacessivel_gera_finding_sem_dizer_que_foi_lido(self) -> None:
        self.preferred.mkdir()
        self.fallback.mkdir()
        # Preferencial ativa lê seu fallback histórico; a falha de histórico é rastreada.
        resolver = self.selected_resolver(self.preferred)
        original = __import__("document_recovery")._validar_diretorio

        def falha_fallback(path, *, parent, base):
            if path == self.fallback:
                raise PermissionError("acesso controlado")
            return original(path, parent=parent, base=base)

        with unittest.mock.patch("document_recovery._validar_diretorio", side_effect=falha_fallback):
            result = recuperar_documentos(
                self.root, resolver=resolver, avaliador_factory=self.evaluator_factory
            )
        fallback_status = [root.status for root in result.roots if root.kind == "fallback"]
        self.assertEqual(fallback_status, ["INACCESSIBLE"])
        self.assertIn("ROOT_UNAVAILABLE", {finding.code for finding in result.findings})

    def test_integracao_em_processo_independente_le_publicacao_persistida(self) -> None:
        self.preferred.mkdir()
        script_create = r'''
import json, sys, uuid
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from analysis_lifecycle import criar_ou_retomar_analise
from document_publisher import publicar_documento
from workspace_resolver import RaizWorkspaceSelecionada, TipoRaizWorkspace
root, workspace = Path(sys.argv[2]), Path(sys.argv[3])
def resolve(_root, _evaluator):
    return RaizWorkspaceSelecionada(TipoRaizWorkspace.PREFERENCIAL, workspace)
class Evaluator:
    evidencias = ()
analysis = criar_ou_retomar_analise(
    root, uuid_factory=lambda: uuid.UUID("12345678-1234-4234-8234-123456789abc"),
    resolver=resolve, avaliador_factory=Evaluator,
)
metadata = {
    "schema_version": 1, "type_catalog_version": 1,
    "workspace_root_kind": "preferred", "created_at_utc": "2026-10-10T12:00:00Z",
    "purpose": "Persistência entre processos.",
    "origin": {"kind": "test", "reference": "TASK-009"},
    "inputs": [], "relations": [],
}
published = publicar_documento(
    root, analysis.analysis_id, "evidence", "Persistido", "Processo A gravou.", metadata,
    uuid_factory=lambda: uuid.UUID("87654321-4321-4321-8432-cba987654321"),
    resolver=resolve, avaliador_factory=Evaluator,
)
print(json.dumps({"analysis_id": analysis.analysis_id, "document_id": published.document_id,
                  "sha256": published.sha256}))
'''
        creation = subprocess.run(
            [sys.executable, "-B", "-c", script_create, str(RUNTIME_DIRECTORY), str(self.root), str(self.preferred)],
            check=True,
            capture_output=True,
            text=True,
        )
        persisted = json.loads(creation.stdout)
        script_recover = r'''
import json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from document_recovery import recuperar_documento
from workspace_resolver import RaizWorkspaceSelecionada, TipoRaizWorkspace
root, workspace, document_id = Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]
def resolve(_root, _evaluator):
    return RaizWorkspaceSelecionada(TipoRaizWorkspace.PREFERENCIAL, workspace)
class Evaluator:
    evidencias = ()
doc = recuperar_documento(root, document_id, resolver=resolve, avaliador_factory=Evaluator)
print(json.dumps({"analysis_id": doc.analysis_id, "document_id": doc.document_id,
                  "sha256": doc.sha256, "body": doc.parsed.corpo}))
'''
        recovered = subprocess.run(
            [sys.executable, "-B", "-c", script_recover, str(RUNTIME_DIRECTORY), str(self.root),
             str(self.preferred), persisted["document_id"]],
            check=True,
            capture_output=True,
            text=True,
        )
        output = json.loads(recovered.stdout)
        self.assertEqual(output["analysis_id"], persisted["analysis_id"])
        self.assertEqual(output["document_id"], persisted["document_id"])
        self.assertEqual(output["sha256"], persisted["sha256"])
        self.assertEqual(output["body"], "Processo A gravou.")


if __name__ == "__main__":
    unittest.main()
