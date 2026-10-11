from __future__ import annotations

import builtins
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


RUNTIME_DIRECTORY = Path(__file__).resolve().parents[1] / "src" / "RickCraft"
sys.path.insert(0, str(RUNTIME_DIRECTORY))

from document_format import (  # noqa: E402
    DocumentFormatError,
    parsear_documento,
    serializar_documento,
)


DOCUMENT_ID = "DOC-87654321-4321-4321-8432-cba987654321"
ANALYSIS_ID = "ANL-12345678-1234-4234-8234-123456789abc"
RELATION_DOCUMENT_ID = "DOC-12345678-1234-4234-8234-123456789abc"
RELATION_ANALYSIS_ID = "ANL-87654321-4321-4234-8234-cba987654321"


def metadata_valida() -> dict[str, object]:
    return {
        "schema_version": 1,
        "type_catalog_version": 1,
        "document_id": DOCUMENT_ID,
        "analysis_id": ANALYSIS_ID,
        "document_type": "evidence",
        "workspace_root_kind": "preferred",
        "created_at_utc": "2026-10-10T12:00:00Z",
        "purpose": "Registrar uma verificacao explicita.",
        "origin": {"kind": "user_request", "reference": "pedido atual"},
        "inputs": [],
        "relations": [],
    }


def envelope_json(payload: str, titulo: str = "Documento de evidência") -> bytes:
    return f"# {titulo}\n\n```json\n{payload}\n```\n\nCorpo do documento.".encode(
        "utf-8"
    )


def payload_json(metadata: dict[str, object]) -> str:
    return json.dumps(metadata, ensure_ascii=False, allow_nan=False)


class FormatoDocumentalTests(unittest.TestCase):
    def serializar(self, metadata=None, corpo="Corpo explícito.") -> bytes:
        return serializar_documento(
            "Evidência da execução",
            metadata if metadata is not None else metadata_valida(),
            corpo,
        )

    def rejeitar_metadata(self, metadata: dict[str, object]) -> None:
        with self.assertRaises(DocumentFormatError):
            parsear_documento(envelope_json(payload_json(metadata)))

    def test_documento_valido_serializa_em_utf8(self) -> None:
        resultado = self.serializar()
        self.assertIsInstance(resultado, bytes)
        self.assertTrue(resultado.startswith(b"# Evid\xc3\xaancia da execu\xc3\xa7\xc3\xa3o"))
        self.assertEqual(parsear_documento(resultado).metadata["schema_version"], 1)

    def test_documento_valido_faz_round_trip(self) -> None:
        metadata = metadata_valida()
        serializado = self.serializar(metadata, "Corpo mantido.")
        documento = parsear_documento(serializado)
        self.assertEqual(documento.titulo, "Evidência da execução")
        self.assertEqual(documento.metadata, metadata)
        self.assertEqual(documento.corpo, "Corpo mantido.")

    def test_caracteres_pt_br_sobrevivem_ao_round_trip(self) -> None:
        metadata = metadata_valida()
        metadata["purpose"] = "Revisão de informações e ações"
        corpo = "Conclusão: a evidência está íntegra; não houve alteração."
        documento = parsear_documento(self.serializar(metadata, corpo))
        self.assertEqual(documento.metadata["purpose"], metadata["purpose"])
        self.assertEqual(documento.corpo, corpo)

    def test_bytes_utf8_invalidos_sao_rejeitados(self) -> None:
        with self.assertRaises(DocumentFormatError):
            parsear_documento(b"# titulo\n\n```json\n\xff\n```\n\ncorpo")

    def test_json_sintaticamente_invalido_e_rejeitado(self) -> None:
        with self.assertRaises(DocumentFormatError):
            parsear_documento(envelope_json('{"schema_version":'))

    def test_raiz_json_que_nao_e_objeto_e_rejeitada(self) -> None:
        with self.assertRaises(DocumentFormatError):
            parsear_documento(envelope_json("[]"))

    def test_chave_duplicada_na_raiz_e_rejeitada(self) -> None:
        raw = '{"schema_version":1,"schema_version":1}'
        with self.assertRaises(DocumentFormatError):
            parsear_documento(envelope_json(raw))

    def test_chave_duplicada_em_objeto_aninhado_e_rejeitada(self) -> None:
        raw = payload_json(metadata_valida()).replace(
            '"origin": {"kind": "user_request", "reference": "pedido atual"}',
            '"origin": {"kind": "user_request", "kind": "other", "reference": "pedido atual"}',
        )
        with self.assertRaises(DocumentFormatError):
            parsear_documento(envelope_json(raw))

    def test_nan_e_rejeitado(self) -> None:
        metadata = metadata_valida()
        raw = payload_json(metadata).replace('"schema_version": 1', '"extra": NaN, "schema_version": 1')
        with self.assertRaises(DocumentFormatError):
            parsear_documento(envelope_json(raw))

    def test_infinity_e_rejeitado(self) -> None:
        raw = payload_json(metadata_valida()).replace(
            '"schema_version": 1', '"extra": Infinity, "schema_version": 1'
        )
        with self.assertRaises(DocumentFormatError):
            parsear_documento(envelope_json(raw))

    def test_menos_infinity_e_rejeitado(self) -> None:
        raw = payload_json(metadata_valida()).replace(
            '"schema_version": 1', '"extra": -Infinity, "schema_version": 1'
        )
        with self.assertRaises(DocumentFormatError):
            parsear_documento(envelope_json(raw))

    def test_serializador_nao_permite_nan_ou_infinity(self) -> None:
        metadata = metadata_valida()
        metadata["extra"] = float("nan")
        with self.assertRaises(DocumentFormatError):
            self.serializar(metadata)

    def test_schema_version_ausente_e_rejeitado(self) -> None:
        metadata = metadata_valida()
        del metadata["schema_version"]
        self.rejeitar_metadata(metadata)

    def test_schema_version_diferente_de_um_e_rejeitado(self) -> None:
        metadata = metadata_valida()
        metadata["schema_version"] = 2
        self.rejeitar_metadata(metadata)

    def test_type_catalog_version_ausente_e_rejeitado(self) -> None:
        metadata = metadata_valida()
        del metadata["type_catalog_version"]
        self.rejeitar_metadata(metadata)

    def test_type_catalog_version_diferente_de_um_e_rejeitado(self) -> None:
        metadata = metadata_valida()
        metadata["type_catalog_version"] = 2
        self.rejeitar_metadata(metadata)

    def test_document_id_invalido_e_rejeitado(self) -> None:
        metadata = metadata_valida()
        metadata["document_id"] = "DOC-invalido"
        self.rejeitar_metadata(metadata)

    def test_analysis_id_invalido_e_rejeitado(self) -> None:
        metadata = metadata_valida()
        metadata["analysis_id"] = "ANL-invalido"
        self.rejeitar_metadata(metadata)

    def test_document_type_desconhecido_e_rejeitado(self) -> None:
        metadata = metadata_valida()
        metadata["document_type"] = "Evidence"
        self.rejeitar_metadata(metadata)

    def test_workspace_root_kind_invalido_e_rejeitado(self) -> None:
        metadata = metadata_valida()
        metadata["workspace_root_kind"] = "other"
        self.rejeitar_metadata(metadata)

    def test_created_at_utc_sintaticamente_invalido_e_rejeitado(self) -> None:
        metadata = metadata_valida()
        metadata["created_at_utc"] = "2026-99-10T12:00:00Z"
        self.rejeitar_metadata(metadata)

    def test_created_at_utc_sem_timezone_e_rejeitado(self) -> None:
        metadata = metadata_valida()
        metadata["created_at_utc"] = "2026-10-10T12:00:00"
        self.rejeitar_metadata(metadata)

    def test_created_at_utc_com_fuso_nao_utc_e_rejeitado(self) -> None:
        metadata = metadata_valida()
        metadata["created_at_utc"] = "2026-10-10T12:00:00-03:00"
        self.rejeitar_metadata(metadata)

    def test_created_at_utc_normaliza_fracao_e_fuso_zero(self) -> None:
        metadata = metadata_valida()
        metadata["created_at_utc"] = "2026-10-10T12:00:00.1200+00:00"
        parsed = parsear_documento(self.serializar(metadata))
        self.assertEqual(parsed.metadata["created_at_utc"], "2026-10-10T12:00:00.12Z")

    def test_created_at_utc_normaliza_t_e_z_minusculos(self) -> None:
        metadata = metadata_valida()
        metadata["created_at_utc"] = "2026-10-10t12:00:00z"
        parsed = parsear_documento(self.serializar(metadata))
        self.assertEqual(parsed.metadata["created_at_utc"], "2026-10-10T12:00:00Z")

    def test_purpose_ausente_ou_vazio_e_rejeitado(self) -> None:
        for value in (None, "", "   "):
            metadata = metadata_valida()
            if value is None:
                del metadata["purpose"]
            else:
                metadata["purpose"] = value
            with self.subTest(value=value):
                self.rejeitar_metadata(metadata)

    def test_origin_ausente_ou_malformado_e_rejeitado(self) -> None:
        metadata = metadata_valida()
        del metadata["origin"]
        self.rejeitar_metadata(metadata)
        for origin in (
            [],
            {},
            {"kind": "user_request"},
            {"kind": "", "reference": "x"},
            {"kind": "user_request", "reference": 7, "summary": "resumo"},
        ):
            metadata = metadata_valida()
            metadata["origin"] = origin
            with self.subTest(origin=origin):
                self.rejeitar_metadata(metadata)

    def test_origin_pode_usar_resumo_minimo_explicito(self) -> None:
        metadata = metadata_valida()
        metadata["origin"] = {"kind": "user_request", "summary": "Pedido resumido."}
        self.assertEqual(parsear_documento(self.serializar(metadata)).metadata["origin"], metadata["origin"])

    def test_inputs_ausente_e_rejeitado(self) -> None:
        metadata = metadata_valida()
        del metadata["inputs"]
        self.rejeitar_metadata(metadata)

    def test_inputs_nao_array_e_rejeitado(self) -> None:
        metadata = metadata_valida()
        metadata["inputs"] = {}
        self.rejeitar_metadata(metadata)

    def test_cada_input_presente_deve_ser_objeto(self) -> None:
        metadata = metadata_valida()
        metadata["inputs"] = ["texto livre"]
        self.rejeitar_metadata(metadata)

    def test_inputs_vazios_e_campos_fornecidos_sao_preservados_sem_proveniencia(self) -> None:
        metadata = metadata_valida()
        metadata["inputs"] = [{"kind": "local_file", "locator": "fonte.txt"}]
        parsed = parsear_documento(self.serializar(metadata))
        self.assertEqual(parsed.metadata["inputs"], metadata["inputs"])

    def test_relations_ausente_e_rejeitado(self) -> None:
        metadata = metadata_valida()
        del metadata["relations"]
        self.rejeitar_metadata(metadata)

    def test_relations_nao_array_e_rejeitado(self) -> None:
        metadata = metadata_valida()
        metadata["relations"] = {}
        self.rejeitar_metadata(metadata)

    def test_token_de_relacao_invalido_e_rejeitado(self) -> None:
        metadata = metadata_valida()
        metadata["relations"] = [{"relation_type": "Corrects", "document_id": RELATION_DOCUMENT_ID}]
        self.rejeitar_metadata(metadata)

    def test_document_id_de_relacao_invalido_e_rejeitado(self) -> None:
        metadata = metadata_valida()
        metadata["relations"] = [{"relation_type": "corrects", "document_id": "DOC-invalid"}]
        self.rejeitar_metadata(metadata)

    def test_analysis_id_de_relacao_invalido_e_rejeitado(self) -> None:
        metadata = metadata_valida()
        metadata["relations"] = [
            {"relation_type": "related_to", "document_id": RELATION_DOCUMENT_ID, "analysis_id": "ANL-invalid"}
        ]
        self.rejeitar_metadata(metadata)

    def test_relacao_estruturada_valida_e_preservada(self) -> None:
        metadata = metadata_valida()
        metadata["relations"] = [
            {
                "relation_type": "supports",
                "document_id": RELATION_DOCUMENT_ID,
                "analysis_id": RELATION_ANALYSIS_ID,
            }
        ]
        self.assertEqual(parsear_documento(self.serializar(metadata)).metadata["relations"], metadata["relations"])

    def test_seis_tokens_de_relacao_sao_aceitos(self) -> None:
        for token in ("corrects", "complements", "supersedes", "invalidates", "supports", "related_to"):
            metadata = metadata_valida()
            metadata["relations"] = [
                {"relation_type": token, "document_id": RELATION_DOCUMENT_ID}
            ]
            with self.subTest(token=token):
                self.assertEqual(
                    parsear_documento(self.serializar(metadata)).metadata["relations"][0]["relation_type"],
                    token,
                )

    def test_relacao_com_valor_textual_e_rejeitada(self) -> None:
        metadata = metadata_valida()
        metadata["relations"] = ["corrects"]
        self.rejeitar_metadata(metadata)

    def test_titulo_ausente_e_rejeitado(self) -> None:
        content = self.serializar().decode("utf-8").replace("# Evidência da execução\n", "", 1)
        with self.assertRaises(DocumentFormatError):
            parsear_documento(content)

    def test_titulo_vazio_e_rejeitado(self) -> None:
        content = self.serializar().decode("utf-8").replace("# Evidência da execução", "#   ", 1)
        with self.assertRaises(DocumentFormatError):
            parsear_documento(content)

    def test_ausencia_do_bloco_json_e_rejeitada(self) -> None:
        with self.assertRaises(DocumentFormatError):
            parsear_documento("# Titulo\n\nCorpo sem metadados")

    def test_bloco_json_nao_fechado_e_rejeitado(self) -> None:
        content = self.serializar().decode("utf-8").replace("\n```\n\n", "\n", 1)
        with self.assertRaises(DocumentFormatError):
            parsear_documento(content)

    def test_mais_de_um_bloco_json_e_rejeitado(self) -> None:
        content = self.serializar().decode("utf-8") + "\n```json\n{}\n```\n"
        with self.assertRaises(DocumentFormatError):
            parsear_documento(content)

    def test_corpo_markdown_e_preservado_no_round_trip(self) -> None:
        corpo = "## Observação\n\n- primeiro item\n- segundo item\n"
        documento = parsear_documento(self.serializar(corpo=corpo))
        self.assertEqual(documento.corpo, corpo)

    def test_campos_obrigatorios_nao_sao_inferidos(self) -> None:
        metadata = metadata_valida()
        del metadata["purpose"]
        with self.assertRaises(DocumentFormatError):
            serializar_documento("Titulo", metadata, "Corpo")

    def test_serializacao_nao_cria_arquivo(self) -> None:
        with (
            patch.object(builtins, "open", side_effect=AssertionError("sem escrita")),
            patch.object(Path, "open", side_effect=AssertionError("sem escrita")),
            patch.object(Path, "write_bytes", side_effect=AssertionError("sem escrita")),
            patch.object(os, "open", side_effect=AssertionError("sem escrita")),
        ):
            self.serializar()

    def test_metadata_adicional_json_e_preservada_sem_reinterpretacao(self) -> None:
        metadata = metadata_valida()
        metadata["specific_v1"] = {"informacao": "explícita"}
        self.assertEqual(parsear_documento(self.serializar(metadata)).metadata, metadata)


if __name__ == "__main__":
    unittest.main()
