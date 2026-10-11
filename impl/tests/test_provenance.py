"""Testes de proveniência e comparação de identidade de entradas."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib import request

RUNTIME_DIRECTORY = Path(__file__).resolve().parents[1] / "src" / "RickCraft"
sys.path.insert(0, str(RUNTIME_DIRECTORY))

from document_format import parsear_documento, serializar_documento  # noqa: E402
from provenance import (  # noqa: E402
    ESTADOS_VERIFICACAO,
    KIND_LOCAL_FILE,
    KIND_VERSIONED_SOURCE,
    KIND_WORKSPACE_DOCUMENT,
    ProvenanceError,
    calcular_sha256,
    observar_arquivo_local,
    observar_documento_workspace,
    observar_fonte_versionada,
    verificar_arquivo_local,
    verificar_documento_workspace,
    verificar_fonte_versionada,
)


DOCUMENT_ID = "DOC-87654321-4321-4321-8432-cba987654321"
ANALYSIS_ID = "ANL-12345678-1234-4234-8234-123456789abc"
AGORA = datetime(2026, 10, 10, 12, 34, 56, 123000, tzinfo=timezone.utc)


def metadata_valida(inputs: list[dict[str, object]]) -> dict[str, object]:
    return {
        "schema_version": 1,
        "type_catalog_version": 1,
        "document_id": DOCUMENT_ID,
        "analysis_id": ANALYSIS_ID,
        "document_type": "evidence",
        "workspace_root_kind": "preferred",
        "created_at_utc": "2026-10-10T12:00:00Z",
        "purpose": "Registrar proveniência de uma entrada.",
        "origin": {"kind": "user_request", "reference": "pedido atual"},
        "inputs": inputs,
        "relations": [],
    }


class ProvenanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="rickcraft-provenance-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.clock = lambda: AGORA

    def test_sha256_vetor_padrao_abc(self) -> None:
        self.assertEqual(
            calcular_sha256(b"abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        )

    def test_sha256_tem_64_caracteres(self) -> None:
        self.assertEqual(len(calcular_sha256(b"abc")), 64)

    def test_sha256_hexadecimal_minusculo(self) -> None:
        self.assertRegex(calcular_sha256(b"abc"), r"^[0-9a-f]{64}$")

    def test_sha256_rejeita_texto_em_vez_de_bytes(self) -> None:
        with self.assertRaises(TypeError):
            calcular_sha256("abc")  # type: ignore[arg-type]

    def test_bytes_diferentes_produzem_digests_diferentes(self) -> None:
        self.assertNotEqual(calcular_sha256(b"abc"), calcular_sha256(b"abd"))

    def test_newline_diferente_altera_digest(self) -> None:
        self.assertNotEqual(calcular_sha256(b"a\nb"), calcular_sha256(b"a\r\nb"))

    def test_bytes_de_encoding_diferente_alteram_digest(self) -> None:
        self.assertNotEqual("é".encode("utf-8"), "é".encode("utf-16-le"))
        self.assertNotEqual(
            calcular_sha256("é".encode("utf-8")),
            calcular_sha256("é".encode("utf-16-le")),
        )

    def test_arquivo_local_registra_hash_dos_bytes_exatos(self) -> None:
        caminho = self.root / "entrada.bin"
        caminho.write_bytes(b"abc\r\n")
        registro = observar_arquivo_local(caminho, clock=self.clock)
        self.assertEqual(registro["sha256"], calcular_sha256(b"abc\r\n"))
        self.assertEqual(registro["kind"], KIND_LOCAL_FILE)

    def test_locator_local_e_absoluto_normalizado(self) -> None:
        caminho = self.root / "sub" / ".." / "entrada.bin"
        caminho.parent.parent.mkdir(exist_ok=True)
        caminho.resolve().write_bytes(b"x")
        registro = observar_arquivo_local(caminho, clock=self.clock)
        self.assertTrue(Path(registro["locator"]).is_absolute())
        self.assertEqual(registro["locator"], os.path.abspath(os.fspath(caminho)))

    def test_observacao_inicial_nao_afirma_matched(self) -> None:
        caminho = self.root / "entrada"
        caminho.write_bytes(b"conteudo")
        registro = observar_arquivo_local(caminho, clock=self.clock)
        self.assertEqual(registro["verification"], "UNVERIFIABLE")
        self.assertTrue(registro["reason"])

    def test_mesmo_arquivo_retorna_matched_somente_apos_comparacao(self) -> None:
        caminho = self.root / "entrada"
        caminho.write_bytes(b"conteudo")
        historico = observar_arquivo_local(caminho, clock=self.clock)
        atual = verificar_arquivo_local(historico, caminho, clock=self.clock)
        self.assertEqual(atual["verification"], "MATCHED")

    def test_arquivo_alterado_retorna_changed_reassess(self) -> None:
        caminho = self.root / "entrada"
        caminho.write_bytes(b"antes")
        historico = observar_arquivo_local(caminho, clock=self.clock)
        caminho.write_bytes(b"depois")
        atual = verificar_arquivo_local(historico, caminho, clock=self.clock)
        self.assertEqual(atual["verification"], "CHANGED_REASSESS")

    def test_arquivo_removido_retorna_unavailable(self) -> None:
        caminho = self.root / "entrada"
        caminho.write_bytes(b"conteudo")
        historico = observar_arquivo_local(caminho, clock=self.clock)
        caminho.unlink()
        atual = verificar_arquivo_local(historico, caminho, clock=self.clock)
        self.assertEqual(atual["verification"], "UNAVAILABLE")

    def test_unavailable_tem_motivo_explicito(self) -> None:
        atual = observar_arquivo_local(self.root / "ausente", clock=self.clock)
        self.assertTrue(atual["reason"])

    def test_unavailable_nao_fabrica_sha256(self) -> None:
        atual = observar_arquivo_local(self.root / "ausente", clock=self.clock)
        self.assertNotIn("sha256", atual)

    def test_unavailable_preserva_referencia_historica_sem_mutar(self) -> None:
        caminho = self.root / "entrada"
        caminho.write_bytes("histórico".encode("utf-8"))
        historico = observar_arquivo_local(caminho, clock=self.clock)
        antes = deepcopy(historico)
        caminho.unlink()
        atual = verificar_arquivo_local(historico, caminho, clock=self.clock)
        self.assertEqual(atual["historical"]["sha256"], historico["sha256"])
        self.assertEqual(historico, antes)

    def test_documento_workspace_aceita_document_id_valido(self) -> None:
        registro = observar_documento_workspace(DOCUMENT_ID, b"documento", clock=self.clock)
        self.assertEqual(registro["locator"], DOCUMENT_ID)

    def test_documento_workspace_rejeita_document_id_invalido(self) -> None:
        with self.assertRaises(ProvenanceError):
            observar_documento_workspace("DOC-../../fora", b"x", clock=self.clock)

    def test_documento_workspace_hash_reproduzivel(self) -> None:
        registro = observar_documento_workspace(DOCUMENT_ID, b"bytes", clock=self.clock)
        self.assertEqual(registro["sha256"], calcular_sha256(b"bytes"))

    def test_documento_workspace_mesmos_bytes_retorna_matched(self) -> None:
        historico = observar_documento_workspace(DOCUMENT_ID, b"bytes", clock=self.clock)
        atual = verificar_documento_workspace(historico, DOCUMENT_ID, b"bytes", clock=self.clock)
        self.assertEqual(atual["verification"], "MATCHED")

    def test_documento_workspace_bytes_alterados_retorna_changed(self) -> None:
        historico = observar_documento_workspace(DOCUMENT_ID, b"antes", clock=self.clock)
        atual = verificar_documento_workspace(historico, DOCUMENT_ID, b"depois", clock=self.clock)
        self.assertEqual(atual["verification"], "CHANGED_REASSESS")

    def test_documento_workspace_id_diferente_requer_reavaliacao(self) -> None:
        historico = observar_documento_workspace(DOCUMENT_ID, b"bytes", clock=self.clock)
        outro = "DOC-12345678-1234-4234-8234-123456789abc"
        atual = verificar_documento_workspace(historico, outro, b"bytes", clock=self.clock)
        self.assertEqual(atual["verification"], "CHANGED_REASSESS")

    def test_fonte_versionada_mesma_revisao_retorna_matched(self) -> None:
        historico = observar_fonte_versionada(
            "https://exemplo.invalid/item", version_kind="commit", version="abc123", clock=self.clock
        )
        atual = verificar_fonte_versionada(
            historico,
            "https://exemplo.invalid/item",
            version_kind="commit",
            version="abc123",
            clock=self.clock,
        )
        self.assertEqual(atual["verification"], "MATCHED")

    def test_fonte_versionada_revisao_divergente_retorna_changed(self) -> None:
        historico = observar_fonte_versionada(
            "fonte:registro", version_kind="revision", version="r1", clock=self.clock
        )
        atual = verificar_fonte_versionada(
            historico, "fonte:registro", version_kind="revision", version="r2", clock=self.clock
        )
        self.assertEqual(atual["verification"], "CHANGED_REASSESS")

    def test_fonte_versionada_sem_versao_ou_hash_retorna_unverifiable(self) -> None:
        historico = observar_fonte_versionada("fonte:sem-versao", clock=self.clock)
        atual = verificar_fonte_versionada(historico, "fonte:sem-versao", clock=self.clock)
        self.assertEqual(atual["verification"], "UNVERIFIABLE")
        self.assertTrue(atual["reason"])

    def test_fonte_versionada_com_bytes_compara_hash_sem_rede(self) -> None:
        historico = observar_fonte_versionada("id:local", conteudo=b"abc", clock=self.clock)
        atual = verificar_fonte_versionada(
            historico, "id:local", conteudo=b"abc", clock=self.clock
        )
        self.assertEqual(atual["verification"], "MATCHED")

    def test_fonte_versionada_locator_divergente_requer_reavaliacao(self) -> None:
        historico = observar_fonte_versionada("ref-a", version_kind="etag", version="1", clock=self.clock)
        atual = verificar_fonte_versionada(
            historico, "ref-b", version_kind="etag", version="1", clock=self.clock
        )
        self.assertEqual(atual["verification"], "CHANGED_REASSESS")

    def test_estados_sao_exatamente_os_quatro_tokens_aprovados(self) -> None:
        self.assertEqual(
            ESTADOS_VERIFICACAO,
            {"MATCHED", "CHANGED_REASSESS", "UNAVAILABLE", "UNVERIFIABLE"},
        )

    def test_sha_novo_sem_referencia_nao_resulta_em_matched(self) -> None:
        caminho = self.root / "entrada"
        caminho.write_bytes(b"x")
        self.assertNotEqual(observar_arquivo_local(caminho, clock=self.clock)["verification"], "MATCHED")

    def test_instante_observado_e_utc_canonico(self) -> None:
        caminho = self.root / "entrada"
        caminho.write_bytes(b"x")
        registro = observar_arquivo_local(caminho, clock=self.clock)
        self.assertEqual(registro["observed_at_utc"], "2026-10-10T12:34:56.123Z")
        parsed = datetime.fromisoformat(registro["observed_at_utc"].replace("Z", "+00:00"))
        self.assertEqual(parsed.utcoffset().total_seconds(), 0)

    def test_clock_pode_ser_injetado(self) -> None:
        caminho = self.root / "entrada"
        caminho.write_bytes(b"x")
        outro = datetime(2020, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
        registro = observar_arquivo_local(caminho, clock=lambda: outro)
        self.assertEqual(registro["observed_at_utc"], "2020-01-02T03:04:05Z")

    def test_clock_sem_fuso_e_rejeitado(self) -> None:
        caminho = self.root / "entrada"
        caminho.write_bytes(b"x")
        with self.assertRaises(ProvenanceError):
            observar_arquivo_local(caminho, clock=lambda: datetime(2026, 1, 1))

    def test_verificacao_nao_altera_historico(self) -> None:
        caminho = self.root / "entrada"
        caminho.write_bytes(b"antes")
        historico = observar_arquivo_local(caminho, clock=self.clock)
        antes = deepcopy(historico)
        caminho.write_bytes(b"depois")
        verificar_arquivo_local(historico, caminho, clock=self.clock)
        self.assertEqual(historico, antes)

    def test_verificacao_produz_novo_objeto(self) -> None:
        caminho = self.root / "entrada"
        caminho.write_bytes(b"bytes")
        historico = observar_arquivo_local(caminho, clock=self.clock)
        atual = verificar_arquivo_local(historico, caminho, clock=self.clock)
        self.assertIsNot(atual, historico)

    def test_resultado_preserva_referencia_historica(self) -> None:
        caminho = self.root / "entrada"
        caminho.write_bytes(b"bytes")
        historico = observar_arquivo_local(caminho, clock=self.clock)
        atual = verificar_arquivo_local(historico, caminho, clock=self.clock)
        self.assertEqual(atual["historical"]["sha256"], historico["sha256"])

    def test_registro_encaixa_em_inputs_task006_e_faz_round_trip(self) -> None:
        caminho = self.root / "entrada"
        caminho.write_bytes(b"bytes")
        registro = observar_arquivo_local(caminho, clock=self.clock)
        documento = serializar_documento("Evidência", metadata_valida([registro]), "Corpo.")
        recuperado = parsear_documento(documento)
        self.assertEqual(recuperado.metadata["inputs"], [registro])

    def test_serializacao_preserva_campos_historicos_do_input(self) -> None:
        entrada = observar_fonte_versionada(
            "id:fonte", version_kind="etag", version="v1", clock=self.clock
        )
        atual = verificar_fonte_versionada(
            entrada, "id:fonte", version_kind="etag", version="v2", clock=self.clock
        )
        documento = serializar_documento("Evidência", metadata_valida([atual]), "Corpo.")
        self.assertEqual(parsear_documento(documento).metadata["inputs"][0], atual)

    def test_execucao_nao_acessa_rede_git_ou_publicacao(self) -> None:
        with (
            patch.object(request, "urlopen", side_effect=AssertionError("rede inesperada")) as urlopen,
            patch.object(subprocess, "run", side_effect=AssertionError("Git/processo inesperado")) as run,
            patch("os.link", side_effect=AssertionError("publicação inesperada")) as link,
        ):
            registro = observar_fonte_versionada("id:fonte", version_kind="etag", version="1", clock=self.clock)
            self.assertEqual(registro["verification"], "UNVERIFIABLE")
            self.assertFalse(urlopen.called)
            self.assertFalse(run.called)
            self.assertFalse(link.called)

    def test_falha_filesystem_e_indisponivel_sem_capturar_erro_programacao(self) -> None:
        caminho = self.root / "entrada"
        historico = observar_arquivo_local(self.root / "inexistente", clock=self.clock)
        with patch("pathlib.Path.read_bytes", side_effect=PermissionError("negado")):
            atual = verificar_arquivo_local(historico, caminho, clock=self.clock)
        self.assertEqual(atual["verification"], "UNAVAILABLE")
        with patch("pathlib.Path.read_bytes", side_effect=RuntimeError("defeito")):
            with self.assertRaises(RuntimeError):
                verificar_arquivo_local(historico, caminho, clock=self.clock)


if __name__ == "__main__":
    unittest.main()
