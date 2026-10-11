"""Integrações cross-component da SPEC-0000000001 em fixtures isoladas."""

from __future__ import annotations

import errno
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
import urllib.request
import uuid
from unittest.mock import patch


RUNTIME_DIRECTORY = Path(__file__).resolve().parents[1] / "src" / "RickCraft"
sys.path.insert(0, str(RUNTIME_DIRECTORY))

import workspace_probe
from analysis_lifecycle import criar_ou_retomar_analise
from document_format import parsear_documento
from document_publisher import publicar_documento
from document_recovery import recuperar_documento, recuperar_documentos
from document_search import SearchQuery, pesquisar_documentos
from provenance import observar_arquivo_local, verificar_arquivo_local
from workspace_probe import AvaliadorWorkspace, EvidenciaSonda
from workspace_resolver import (
    ResultadoCapacidade,
    ResultadoDesconhecidoError,
    TipoRaizWorkspace,
    derivar_caminhos_workspace,
    resolver_workspace,
)
import gap_handling as gaps


ANALYSIS_UUID = "12345678-1234-4234-8234-123456789abc"
DOC_UUIDS = (
    "87654321-4321-4321-8432-cba987654321",
    "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
    "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
)
UTC = "2026-10-11T12:00:00Z"


class WorkspaceIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(
            prefix="rickcraft-integration-", dir=Path(__file__).resolve().parent
        )
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.rickcraft_root = self.base / "repo" / "impl" / "src" / "RickCraft"
        self.rickcraft_root.mkdir(parents=True)
        self.paths = derivar_caminhos_workspace(self.rickcraft_root)

    def create_analysis(self) -> str:
        created = criar_ou_retomar_analise(
            self.rickcraft_root,
            uuid_factory=lambda: uuid.UUID(ANALYSIS_UUID),
        )
        self.assertEqual(created.workspace.tipo, TipoRaizWorkspace.PREFERENCIAL)
        self.assertEqual(created.directory.parent, self.paths.preferencial)
        self.assertEqual(created.analysis_id, f"ANL-{ANALYSIS_UUID}")
        return created.analysis_id

    def metadata(self, inputs=(), relations=(), purpose="Evidência integrada"):
        return {
            "schema_version": 1,
            "type_catalog_version": 1,
            "created_at_utc": UTC,
            "purpose": purpose,
            "origin": {"kind": "task_execution", "reference": "TASK-013 fixture"},
            "inputs": list(inputs),
            "relations": list(relations),
        }

    def publish(self, analysis_id, sequence, *, inputs=(), relations=(), body="Evidência íntegra.", purpose="Evidência integrada"):
        return publicar_documento(
            self.rickcraft_root,
            analysis_id,
            "evidence",
            "Evidência integrada",
            body,
            self.metadata(inputs, relations, purpose),
            uuid_factory=lambda: uuid.UUID(DOC_UUIDS[sequence]),
        )

    def test_sonda_real_em_fixture_prova_precedencia_fallback_e_bloqueio(self) -> None:
        # CA-001/002: a raiz preferencial ausente é criada e testada pelas
        # operações concretas D-02 antes de qualquer análise/documento.
        avaliador = AvaliadorWorkspace()
        selecionada = resolver_workspace(self.rickcraft_root, avaliador)
        self.assertEqual(selecionada.tipo, TipoRaizWorkspace.PREFERENCIAL)
        self.assertEqual(selecionada.caminho, self.paths.preferencial)
        self.assertEqual([item.raiz for item in avaliador.evidencias], [self.paths.preferencial])
        evidencia = avaliador.evidencias[0]
        self.assertIs(evidencia.resultado, ResultadoCapacidade.UTILIZAVEL)
        for capacidade in (
            "raiz criada ou já existente como diretório",
            "open xb exclusivo",
            "escrita",
            "flush",
            "releitura da origem conferida byte a byte",
            "os.link para destino ausente",
            "releitura do destino publicada conferida",
            "destino existente rejeitado sem substituir bytes sentinela",
        ):
            self.assertIn(capacidade, evidencia.capacidades)
        self.assertEqual(evidencia.residuos, ())
        self.assertEqual(list(self.paths.preferencial.iterdir()), [])

        # CA-003: arquivo no lugar da raiz preferred causa impossibilidade
        # concreta D-03; então e somente então o fallback recebe sonda D-02.
        self.paths.preferencial.rmdir()
        self.paths.preferencial.write_text("componente não é diretório", encoding="utf-8")
        avaliador_fallback = AvaliadorWorkspace()
        fallback = resolver_workspace(self.rickcraft_root, avaliador_fallback)
        self.assertEqual(fallback.tipo, TipoRaizWorkspace.FALLBACK)
        self.assertEqual(fallback.caminho, self.paths.fallback)
        self.assertEqual(
            [item.raiz for item in avaliador_fallback.evidencias],
            [self.paths.preferencial, self.paths.fallback],
        )
        self.assertIs(
            avaliador_fallback.evidencias[0].resultado,
            ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA,
        )
        self.assertIs(
            avaliador_fallback.evidencias[1].resultado,
            ResultadoCapacidade.UTILIZAVEL,
        )
        self.assertEqual(avaliador_fallback.evidencias[1].residuos, ())
        self.assertEqual(list(self.paths.fallback.iterdir()), [])

        # Erro desconhecido é distinto de impossibilidade e bloqueia antes
        # de sondar ou materializar o fallback.
        self.paths.fallback.rmdir()
        self.paths.preferencial.unlink()
        original_link = os.link

        def falhar_preferencial(origem, destino, *args, **kwargs):
            if Path(origem).is_relative_to(self.paths.preferencial):
                raise OSError(errno.EIO, "falha desconhecida integrada")
            return original_link(origem, destino, *args, **kwargs)

        avaliador_desconhecido = AvaliadorWorkspace()
        with patch.object(workspace_probe.os, "link", side_effect=falhar_preferencial):
            with self.assertRaises(ResultadoDesconhecidoError):
                resolver_workspace(self.rickcraft_root, avaliador_desconhecido)
        self.assertEqual(
            [item.raiz for item in avaliador_desconhecido.evidencias],
            [self.paths.preferencial],
        )
        self.assertIs(
            avaliador_desconhecido.evidencias[0].resultado,
            ResultadoCapacidade.ERRO_DESCONHECIDO,
        )
        self.assertFalse(self.paths.fallback.exists())

    def test_publicacao_recuperacao_processo_novo_proveniencia_e_append_only(self) -> None:
        # Contexto A: análise, proveniência inicial e primeiro documento.
        analysis_id = self.create_analysis()
        source = self.base / "entrada local.txt"
        source.write_bytes("versão inicial: ação e evidência\r\n".encode("utf-8"))
        observacao = observar_arquivo_local(source)
        self.assertEqual(observacao["verification"], "UNVERIFIABLE")
        self.assertEqual(observacao["sha256"], hashlib.sha256(source.read_bytes()).hexdigest())

        primeiro = self.publish(
            analysis_id,
            0,
            inputs=(observacao,),
            body="A evidência inicial está íntegra e contém ação em pt-BR.",
            purpose="Registrar observação inicial",
        )
        bytes_anteriores = primeiro.destination.read_bytes()
        hash_anterior = hashlib.sha256(bytes_anteriores).hexdigest()
        metadata_primeira = parsear_documento(bytes_anteriores).metadata
        self.assertEqual(primeiro.workspace_root_kind, "preferred")
        self.assertEqual(primeiro.destination.name, f"{primeiro.document_id}.md")
        self.assertEqual(primeiro.destination.parent, self.paths.preferencial / analysis_id / "evidence")
        self.assertEqual(metadata_primeira["inputs"], [observacao])
        self.assertIn("ação", parsear_documento(bytes_anteriores).corpo)

        # Contexto B é um processo Python independente. Seus únicos dados
        # funcionais de retomada são RickCraftRoot, analysis_id e document_id;
        # não recebe objetos ou metadados do processo A.
        child = r'''
import json, sys
from pathlib import Path
from document_recovery import recuperar_documento
from document_search import SearchQuery, pesquisar_documentos
root = Path(sys.argv[1])
analysis_id, document_id = sys.argv[2], sys.argv[3]
doc = recuperar_documento(root, document_id)
search = pesquisar_documentos(root, SearchQuery(
    analysis_id=analysis_id, document_type="evidence", document_id=document_id,
    text_terms=("EVIDÊNCIA", "pt-BR")))
print(json.dumps({"analysis_id": doc.analysis_id, "document_id": doc.document_id,
    "sha256": doc.sha256, "body": doc.parsed.corpo,
    "search_ids": [item.document_id for item in search.matches]}, ensure_ascii=False))
'''
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(RUNTIME_DIRECTORY)
        environment["PYTHONIOENCODING"] = "utf-8"
        recovered_process = subprocess.run(
            [sys.executable, "-B", "-c", child, str(self.rickcraft_root), analysis_id, primeiro.document_id],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=environment,
        )
        recovered_child = json.loads(recovered_process.stdout)
        self.assertEqual(recovered_child["analysis_id"], analysis_id)
        self.assertEqual(recovered_child["document_id"], primeiro.document_id)
        self.assertEqual(recovered_child["sha256"], hash_anterior)
        self.assertEqual(recovered_child["search_ids"], [primeiro.document_id])

        # A entrada muda depois do primeiro registro. A recuperação compara
        # com o histórico sem reescrevê-lo; uma nova evidência é append-only.
        source.write_bytes("versão atualizada: ação revisada\r\n".encode("utf-8"))
        comparacao = verificar_arquivo_local(observacao, source)
        self.assertEqual(comparacao["verification"], "CHANGED_REASSESS")
        self.assertEqual(comparacao["historical"]["sha256"], observacao["sha256"])
        verificado_na_recuperacao = recuperar_documento(self.rickcraft_root, primeiro.document_id)
        self.assertEqual(
            verificado_na_recuperacao.input_verifications[0].verification["verification"],
            "CHANGED_REASSESS",
        )

        segundo = self.publish(
            analysis_id,
            1,
            inputs=(comparacao,),
            relations=({
                "relation_type": "complements",
                "document_id": primeiro.document_id,
            },),
            body="A nova validação complementa a evidência anterior após mudança da entrada.",
            purpose="Reavaliar a entrada alterada",
        )
        self.assertNotEqual(segundo.document_id, primeiro.document_id)
        self.assertEqual(primeiro.destination.read_bytes(), bytes_anteriores)
        self.assertEqual(hashlib.sha256(primeiro.destination.read_bytes()).hexdigest(), hash_anterior)
        self.assertFalse(any(primeiro.destination.parent.glob("*.tmp")))

        historico = recuperar_documentos(self.rickcraft_root)
        anterior_recuperado = historico.document(primeiro.document_id)
        novo_recuperado = historico.document(segundo.document_id)
        self.assertEqual(anterior_recuperado.sha256, hash_anterior)
        self.assertEqual(anterior_recuperado.parsed.metadata, metadata_primeira)
        self.assertEqual(novo_recuperado.relations[0].relation_type, "complements")
        self.assertEqual(novo_recuperado.relations[0].document_id, primeiro.document_id)
        self.assertTrue(novo_recuperado.relations[0].resolved)
        self.assertEqual(
            [item.document_id for item in pesquisar_documentos(
                self.rickcraft_root,
                SearchQuery(
                    analysis_id=analysis_id,
                    document_type="evidence",
                    relation_equals={"relation_type": "complements", "document_id": primeiro.document_id},
                    input_equals={"verification": "CHANGED_REASSESS"},
                    text_terms=("NOVA", "ação"),
                ),
            ).matches],
            [segundo.document_id],
        )

    def test_lacuna_autoridade_normativa_e_continuidade_sao_persistidas(self) -> None:
        analysis_id = self.create_analysis()
        normativa = gaps.SourceReference(
            "normative", "POL-0000000001 §4", "A fonte vigente mantém autoridade.",
            "Responsável pelo projeto",
        )
        workspace = gaps.SourceReference(
            "workspace", "DOC-operacional", "Texto operacional incompatível."
        )
        conflito_workspace = gaps.avaliar_conflito_fontes(
            normativa,
            workspace,
            affected_scope="parte dependente",
            impact="o documento operacional diverge da fonte normativa",
            resume_condition="registrar a referência normativa aplicável",
            materially_incompatible=True,
        )
        self.assertEqual(conflito_workspace.authoritative_reference, normativa.reference)
        self.assertIsNone(conflito_workspace.required_authority)
        divergence = gaps.registrar_divergencia(
            self.rickcraft_root,
            analysis_id,
            conflito_workspace.divergence,
            purpose="Registrar precedência normativa",
        )

        conflito_normativo = gaps.avaliar_conflito_fontes(
            normativa,
            gaps.SourceReference("normative", "POL-0000000002 §3", "Regra conflitante.", "Responsável pelo projeto"),
            affected_scope="escopo A",
            impact="duas regras normativas são incompatíveis",
            resume_condition="identificar autoridade e obter decisão formal",
            materially_incompatible=True,
        )
        self.assertIsNone(conflito_normativo.authoritative_reference)
        self.assertTrue(conflito_normativo.blocker_required)
        self.assertIsNone(conflito_normativo.required_authority)
        self.assertIsNone(conflito_normativo.divergence.required_authority)
        self.assertTrue(conflito_normativo.divergence.required_information)

        blocker_case = gaps.BlockerCase(
            affected_scope="escopo A",
            cause="conflito normativo sem precedência fornecida",
            dependency="identificação da autoridade competente",
            resume_condition="decisão formal registrada",
            required_information=conflito_normativo.divergence.required_information,
        )
        blocker = gaps.registrar_blocker(
            self.rickcraft_root,
            analysis_id,
            blocker_case,
            purpose="Suspender somente o escopo dependente",
        )

        requests = (
            gaps.ScopeRequest("escopo A", (), True, True, True, True, True),
            gaps.ScopeRequest("escopo B", (), True, True, True, True, True),
            gaps.ScopeRequest("escopo C", ("escopo B",), True, True, True, True, True),
            gaps.ScopeRequest("escopo D", ("escopo A",), True, True, True, True, True),
            gaps.ScopeRequest("escopo E", ("escopo D",), True, True, True, True, True),
            gaps.ScopeRequest("escopo sem autorização", (), False, True, True, True, True),
            gaps.ScopeRequest("escopo sem evidência", (), True, True, False, True, True),
            gaps.ScopeRequest("escopo em conflito", (), True, True, True, True, False),
        )
        continuidade = gaps.avaliar_continuidade_localizada(("escopo A",), requests)
        self.assertEqual(continuidade.continuable_scopes, ("escopo B", "escopo C"))
        for scope in (
            "escopo D",
            "escopo E",
            "escopo sem autorização",
            "escopo sem evidência",
            "escopo em conflito",
        ):
            self.assertFalse(next(item for item in continuidade.scopes if item.scope == scope).continuable)
        for scope in ("escopo D", "escopo E"):
            self.assertTrue(any("depende de escopo bloqueado" in reason for reason in next(
                item for item in continuidade.scopes if item.scope == scope
            ).reasons))
        resultado = gaps.registrar_resultado(
            self.rickcraft_root,
            analysis_id,
            gaps.OperationalResultCase(
                operation="avaliar continuidade localizada",
                outcome="somente escopos autorizados e independentes continuam",
                evidence_references=(f"DOC:{blocker.persisted_document_id}",),
                blocked_scopes=("escopo A",),
                scope_requests=requests,
            ),
            purpose="Registrar resultado de continuidade",
        )

        recovered = recuperar_documentos(self.rickcraft_root)
        self.assertEqual(
            {item.document_type for item in recovered.documents},
            {"divergence", "blocker", "result"},
        )
        self.assertIn("fonte normativa", recovered.document(divergence.persisted_document_id).parsed.corpo)
        body_blocker = recovered.document(blocker.persisted_document_id).parsed.corpo
        self.assertIn(conflito_normativo.divergence.required_information, body_blocker)
        self.assertNotIn("Decision Owner competente", body_blocker)
        body_result = recovered.document(resultado.persisted_document_id).parsed.corpo
        self.assertIn("escopo B", body_result)
        self.assertIn("escopo C", body_result)
        self.assertIn("escopo D", body_result)
        self.assertFalse((self.base / "status.md").exists())

    def test_persistencia_local_ptbr_sem_chamadas_externas_ou_release(self) -> None:
        analysis_id = self.create_analysis()
        with (
            patch.object(subprocess, "Popen", side_effect=AssertionError("runtime não inicia subprocesso")) as popen,
            patch.object(subprocess, "run", side_effect=AssertionError("runtime não inicia subprocesso")) as run,
            patch.object(subprocess, "call", side_effect=AssertionError("runtime não inicia subprocesso")) as call,
            patch.object(os, "system", side_effect=AssertionError("runtime não chama shell")) as system,
            patch.object(socket, "create_connection", side_effect=AssertionError("runtime não acessa rede")) as connection,
            patch.object(socket.socket, "connect", side_effect=AssertionError("runtime não acessa rede")) as connect,
            patch.object(urllib.request, "urlopen", side_effect=AssertionError("runtime não acessa rede")) as urlopen,
        ):
            published = self.publish(
                analysis_id,
                2,
                body="Ação, evidência e conclusão permanecem em português.",
                purpose="Persistência local em pt-BR",
            )
            document = recuperar_documento(self.rickcraft_root, published.document_id)
            search = pesquisar_documentos(
                self.rickcraft_root,
                SearchQuery(document_id=published.document_id, text_terms=("AÇÃO", "português")),
            )
        for spy in (popen, run, call, system, connection, connect, urlopen):
            spy.assert_not_called()
        self.assertEqual(document.document_type, "evidence")
        self.assertIn("Ação", document.parsed.corpo)
        self.assertEqual(len(search.matches), 1)
        self.assertEqual(search.matches[0].document_id, published.document_id)
        self.assertIn(b"A\xc3\xa7\xc3\xa3o", published.destination.read_bytes())
        analysis_entries = {item.name for item in (self.paths.preferencial / analysis_id).iterdir()}
        self.assertEqual(analysis_entries, {"evidence"})
        self.assertFalse(any("_en" in item.name for item in (self.paths.preferencial / analysis_id).rglob("*")))
        self.assertFalse(any(path.name.lower() in {"dist", "build", "release", "package"}
                             for path in self.base.iterdir()))


if __name__ == "__main__":
    unittest.main()
