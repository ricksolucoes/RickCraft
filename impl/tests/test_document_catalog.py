from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


RUNTIME_DIRECTORY = Path(__file__).resolve().parents[1] / "src" / "RickCraft"
sys.path.insert(0, str(RUNTIME_DIRECTORY))

from document_catalog import (  # noqa: E402
    DOCUMENT_TYPES,
    TYPE_CATALOG,
    DocumentIdInvalidError,
    DocumentPathError,
    DocumentTypeInvalidError,
    derivar_caminho_documental,
    ensure_document_type_directory,
    type_catalog_version,
    validar_document_id,
    validar_tipo_documento,
)


ANALYSIS_ID = "ANL-12345678-1234-4234-8234-123456789abc"
DOCUMENT_ID = "DOC-87654321-4321-4321-8432-cba987654321"
CATALOG_TOKENS = (
    "context",
    "analysis",
    "evidence",
    "decision",
    "divergence",
    "blocker",
    "result",
    "handoff",
)


class CatalogoDocumentalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory(
            dir=Path(__file__).resolve().parent
        )
        self.addCleanup(self.temporary_directory.cleanup)
        self.base = Path(self.temporary_directory.name)
        self.workspace = self.base / ".workspace"
        self.workspace.mkdir()
        self.analysis = self.workspace / ANALYSIS_ID
        self.analysis.mkdir()

    def test_versao_um_e_catalogo_fechado_com_oito_tokens(self) -> None:
        self.assertEqual(type_catalog_version, 1)
        self.assertEqual(len(TYPE_CATALOG), 8)
        self.assertEqual(DOCUMENT_TYPES, frozenset(CATALOG_TOKENS))
        with self.assertRaises(TypeError):
            TYPE_CATALOG["extra"] = "não autorizado"  # type: ignore[index]

    def test_oito_tokens_sao_aceitos_e_derivam_o_layout_correto(self) -> None:
        for token in CATALOG_TOKENS:
            with self.subTest(document_type=token):
                tipo = validar_tipo_documento(token)
                caminho = derivar_caminho_documental(
                    self.workspace, ANALYSIS_ID, tipo, DOCUMENT_ID
                )
                self.assertEqual(caminho.parent, self.analysis / token)
                self.assertEqual(caminho.parent.name, token)
                self.assertEqual(caminho.name, f"{DOCUMENT_ID}.md")
                self.assertTrue(caminho.is_relative_to(self.analysis))

    def test_tipo_desconhecido_maiusculo_ou_com_whitespace_e_rejeitado(self) -> None:
        for value in (
            "unknown",
            "Evidence",
            "evidence ",
            " evidence",
            "evidence\n",
            "contexts",
            "",
        ):
            with self.subTest(document_type=value):
                with self.assertRaises(DocumentTypeInvalidError):
                    validar_tipo_documento(value)

    def test_path_absoluto_e_texto_livre_nao_sao_tokens(self) -> None:
        values = (
            str(self.base),
            "../evidence",
            "..\\evidence",
            "/evidence",
            "C:\\evidence",
            "\\\\servidor\\evidence",
            "evidence/extra",
            "evidence\\extra",
        )
        for value in values:
            with self.subTest(document_type=value):
                with self.assertRaises(DocumentTypeInvalidError):
                    derivar_caminho_documental(
                        self.workspace, ANALYSIS_ID, value, DOCUMENT_ID
                    )
        self.assertEqual(list(self.analysis.iterdir()), [])

    def test_analysis_id_invalido_bloqueia_derivacao(self) -> None:
        for value in (
            "ANL-invalid",
            "DOC-12345678-1234-4234-8234-123456789abc",
            "ANL-12345678-1234-1234-8234-123456789abc",
            "ANL-12345678-1234-4234-8234-123456789ABC",
            "ANL-../escape",
        ):
            with self.subTest(analysis_id=value):
                with self.assertRaises(DocumentPathError):
                    derivar_caminho_documental(
                        self.workspace, value, "evidence", DOCUMENT_ID
                    )
        self.assertEqual(list(self.analysis.iterdir()), [])

    def test_document_id_exige_uuidv4_canonico_e_sem_path(self) -> None:
        self.assertEqual(validar_document_id(DOCUMENT_ID), DOCUMENT_ID)
        for value in (
            42,
            "ANL-87654321-4321-4321-8432-cba987654321",
            "DOC-87654321-4321-1234-8432-cba987654321",
            "DOC-87654321-4321-4321-8432-CBA987654321",
            "DOC-../escape",
            "DOC-87654321-4321-4321-8432-cba987654321/../../outside",
            "DOC-87654321-4321-4321-8432-cba987654321\\..\\outside",
        ):
            with self.subTest(document_id=value):
                with self.assertRaises(DocumentIdInvalidError):
                    derivar_caminho_documental(
                        self.workspace, ANALYSIS_ID, "evidence", value
                    )
        self.assertEqual(list(self.analysis.iterdir()), [])

    def test_raiz_de_workspace_precisa_ser_absoluta(self) -> None:
        with self.assertRaises(DocumentPathError):
            derivar_caminho_documental(
                Path("relative-workspace"), ANALYSIS_ID, "evidence", DOCUMENT_ID
            )

    def test_derivacao_nao_cria_pasta_de_tipo_ou_documento(self) -> None:
        caminho = derivar_caminho_documental(
            self.workspace, ANALYSIS_ID, "evidence", DOCUMENT_ID
        )
        self.assertEqual(
            caminho,
            self.workspace / ANALYSIS_ID / "evidence" / f"{DOCUMENT_ID}.md",
        )
        self.assertFalse(caminho.parent.exists())
        self.assertFalse(caminho.exists())
        self.assertEqual(list(self.analysis.iterdir()), [])

    def test_criacao_idempotente_preserva_conteudo_e_cria_somente_tipo_pedido(self) -> None:
        pasta = ensure_document_type_directory(
            self.workspace, ANALYSIS_ID, "evidence"
        )
        sentinela = pasta / ".sentinela-fixture"
        sentinela.write_text("preservar", encoding="utf-8")

        segunda = ensure_document_type_directory(
            self.workspace, ANALYSIS_ID, "evidence"
        )

        self.assertEqual(segunda, pasta)
        self.assertEqual(sentinela.read_text(encoding="utf-8"), "preservar")
        self.assertEqual(
            [item.name for item in self.analysis.iterdir()], ["evidence"]
        )
        self.assertFalse((self.analysis / "context").exists())
        self.assertEqual(list(pasta.glob("DOC-*.md")), [])

    def test_tipo_invalido_nao_cria_pasta(self) -> None:
        with self.assertRaises(DocumentTypeInvalidError):
            ensure_document_type_directory(
                self.workspace, ANALYSIS_ID, "Evidence"
            )
        self.assertEqual(list(self.analysis.iterdir()), [])

    def test_analise_redirecionada_e_rejeitada(self) -> None:
        with patch("document_catalog._e_redirecionamento", return_value=True):
            with self.assertRaises(DocumentPathError):
                derivar_caminho_documental(
                    self.workspace, ANALYSIS_ID, "evidence", DOCUMENT_ID
                )
        self.assertEqual(list(self.analysis.iterdir()), [])

    def test_detector_junction_da_stdlib_bloqueia_analise(self) -> None:
        if not callable(getattr(self.analysis, "is_junction", None)):
            self.skipTest("Path.is_junction não está disponível neste runtime")
        with patch.object(type(self.analysis), "is_junction", return_value=True):
            with self.assertRaises(DocumentPathError):
                derivar_caminho_documental(
                    self.workspace, ANALYSIS_ID, "evidence", DOCUMENT_ID
                )
        self.assertEqual(list(self.analysis.iterdir()), [])

    def test_analise_resolvida_fora_da_raiz_e_rejeitada(self) -> None:
        outro = self.base / "outro" / ANALYSIS_ID
        resolver_original = Path.resolve

        def resolver_controlado(path, *, strict=False):
            if path == self.analysis:
                return outro
            return resolver_original(path, strict=strict)

        with patch.object(Path, "resolve", resolver_controlado):
            with self.assertRaises(DocumentPathError):
                derivar_caminho_documental(
                    self.workspace, ANALYSIS_ID, "evidence", DOCUMENT_ID
                )
        self.assertEqual(list(self.analysis.iterdir()), [])

    def test_pasta_de_tipo_redirecionada_e_rejeitada(self) -> None:
        pasta = self.analysis / "evidence"
        pasta.mkdir()
        with patch(
            "document_catalog._e_redirecionamento",
            side_effect=lambda path, info: path == pasta,
        ):
            with self.assertRaises(DocumentPathError):
                derivar_caminho_documental(
                    self.workspace, ANALYSIS_ID, "evidence", DOCUMENT_ID
                )

    def test_documento_existente_com_resolucao_externa_e_rejeitado(self) -> None:
        pasta = self.analysis / "evidence"
        pasta.mkdir()
        destino = pasta / f"{DOCUMENT_ID}.md"
        destino.write_text("fixture", encoding="utf-8")
        externo = self.base / "fora.md"
        resolver_original = Path.resolve

        def resolver_controlado(path, *, strict=False):
            if path == destino:
                return externo
            return resolver_original(path, strict=strict)

        with patch.object(Path, "resolve", resolver_controlado):
            with self.assertRaises(DocumentPathError):
                derivar_caminho_documental(
                    self.workspace, ANALYSIS_ID, "evidence", DOCUMENT_ID
                )


if __name__ == "__main__":
    unittest.main()
