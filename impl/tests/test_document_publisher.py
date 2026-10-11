"""Testes controlados de publicação append-only por os.link."""

from __future__ import annotations

from datetime import datetime, timezone
import errno
import hashlib
import os
from pathlib import Path
import threading
import uuid
import sys
import tempfile
import unittest
from unittest.mock import patch

RUNTIME_DIRECTORY = Path(__file__).resolve().parents[1] / "src" / "RickCraft"
sys.path.insert(0, str(RUNTIME_DIRECTORY))

import document_publisher as publisher  # noqa: E402
from document_format import DocumentFormatError, parsear_documento  # noqa: E402
from workspace_resolver import (  # noqa: E402
    RaizWorkspaceSelecionada,
    ResultadoCapacidade,
    ResultadoDesconhecidoError,
    TipoRaizWorkspace,
    resolver_workspace,
)


ANALYSIS_ID = "ANL-12345678-1234-4234-8234-123456789abc"
TIME_UTC = "2026-10-10T12:00:00Z"


def _uuid(numero: int) -> uuid.UUID:
    return uuid.UUID(int=numero, version=4)


def _factory_ids(*numeros: int):
    restantes = list(numeros)
    chamadas: list[int] = []

    def factory() -> uuid.UUID:
        if not restantes:
            raise AssertionError("uuid_factory foi chamado além dos candidatos autorizados")
        numero = restantes.pop(0)
        chamadas.append(numero)
        return _uuid(numero)

    factory.calls = chamadas  # type: ignore[attr-defined]
    return factory


def _metadata(analysis_id: str = ANALYSIS_ID) -> dict[str, object]:
    return {
        "schema_version": 1,
        "type_catalog_version": 1,
        "analysis_id": analysis_id,
        "document_type": "evidence",
        # Valores fornecidos não são autoridades para estes campos.
        "document_id": "DOC-87654321-4321-4321-8432-cba987654321",
        "workspace_root_kind": "fallback",
        "created_at_utc": TIME_UTC,
        "purpose": "Comprovar publicação imutável.",
        "origin": {"kind": "task_execution", "reference": "TASK-008"},
        "inputs": [],
        "relations": [],
    }


class DocumentPublisherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="rickcraft-publisher-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.preferred = self.base / "preferred"
        self.fallback = self.base / "fallback"
        self.preferred.mkdir()
        self._create_analysis(self.preferred)
        self.selections: list[RaizWorkspaceSelecionada] = []
        self.resolver_calls: list[Path] = []

    def _create_analysis(self, root: Path, analysis_id: str = ANALYSIS_ID) -> None:
        root.mkdir(parents=True, exist_ok=True)
        (root / analysis_id).mkdir(exist_ok=True)

    def _actual_layout(self):
        root = self.base / "repository" / "impl" / "src" / "RickCraft"
        root.mkdir(parents=True)
        preferred = root.parent.parent / ".workspace"
        fallback = root / ".workspace"
        self._create_analysis(preferred)
        self._create_analysis(fallback)
        return root, preferred, fallback

    @staticmethod
    def _actual_evaluators(*operations):
        remaining = [list(operation) for operation in operations]

        def factory():
            if not remaining:
                raise AssertionError("A resolução real não tinha resultados controlados restantes")
            results = remaining.pop(0)

            def evaluate(_candidate):
                if not results:
                    raise AssertionError("A resolução consultou uma candidata extra")
                return results.pop(0)

            return evaluate

        return factory

    def _selected(self, kind: TipoRaizWorkspace, root: Path) -> RaizWorkspaceSelecionada:
        selected = RaizWorkspaceSelecionada(kind, root)
        self.selections.append(selected)
        return selected

    def _resolver(self, *selection_pairs):
        remaining = list(selection_pairs)

        def resolve(_rickcraft_root, _evaluator):
            self.resolver_calls.append(_rickcraft_root)
            if not remaining:
                raise AssertionError("A resolução não tinha seleção controlada restante")
            kind, root = remaining.pop(0)
            return self._selected(kind, root)

        return resolve

    def _publish(
        self,
        *,
        ids=(1,),
        selections=None,
        analysis_id=ANALYSIS_ID,
        metadata=None,
        title="Evidência de publicação",
        body="Bytes persistidos e verificados.",
        evaluator_factory=lambda: object(),
        resolver=None,
        temporary_uuid_factory=uuid.uuid4,
        rickcraft_root=None,
    ):
        factory = _factory_ids(*ids)
        if resolver is None:
            pairs = selections or ((TipoRaizWorkspace.PREFERENCIAL, self.preferred),)
            if len(pairs) == 1:
                pairs = pairs * publisher.MAX_TENTATIVAS_PUBLICACAO
            resolver = self._resolver(*pairs)
        result = publisher.publicar_documento(
            rickcraft_root or self.base / "RickCraft",
            analysis_id,
            "evidence",
            title,
            body,
            metadata or _metadata(analysis_id),
            uuid_factory=factory,
            temporary_uuid_factory=temporary_uuid_factory,
            resolver=resolver,
            avaliador_factory=evaluator_factory,
        )
        return result, factory

    def test_doc_gerado_e_uuidv4_canonico(self) -> None:
        result, _ = self._publish()
        self.assertEqual(result.document_id, "DOC-00000000-0000-4000-8000-000000000001")
        valor = uuid.UUID(result.document_id[4:])
        self.assertEqual(valor.version, 4)
        self.assertEqual(str(valor), result.document_id[4:])

    def test_filename_deriva_do_mesmo_id(self) -> None:
        result, _ = self._publish()
        self.assertEqual(result.destination.name, f"{result.document_id}.md")

    def test_publicacao_em_destino_ausente_conclui(self) -> None:
        result, _ = self._publish()
        self.assertTrue(result.destination.is_file())

    def test_temporario_e_criado_com_open_exclusivo_xb(self) -> None:
        original = Path.open
        modos: list[str] = []

        def abrir(path, mode="r", *args, **kwargs):
            modos.append(mode)
            return original(path, mode, *args, **kwargs)

        with patch.object(Path, "open", autospec=True, side_effect=abrir):
            self._publish()
        self.assertIn("xb", modos)

    def test_temporario_termina_em_tmp(self) -> None:
        result, _ = self._publish()
        self.assertEqual(result.destination.suffix, ".md")
        self.assertFalse(any(result.destination.parent.glob("*.tmp")))

    def test_temporario_fica_na_pasta_de_tipo_atual(self) -> None:
        vistos: list[Path] = []
        original = publisher._escrever_temporario_exclusivo

        def gravar(pasta, conteudo, factory):
            caminho = original(pasta, conteudo, factory)
            vistos.append(caminho)
            return caminho

        with patch.object(publisher, "_escrever_temporario_exclusivo", side_effect=gravar):
            result, _ = self._publish()
        self.assertEqual(vistos[0].parent, result.destination.parent)
        self.assertEqual(vistos[0].parent.name, "evidence")

    def test_bytes_completos_sao_escritos(self) -> None:
        escritos: list[bytes] = []
        original = publisher._escrever_temporario_exclusivo

        def gravar(pasta, conteudo, factory):
            escritos.append(conteudo)
            return original(pasta, conteudo, factory)

        with patch.object(publisher, "_escrever_temporario_exclusivo", side_effect=gravar):
            result, _ = self._publish()
        self.assertEqual(result.destination.read_bytes(), escritos[0])

    def test_flush_e_fsync_sao_executados(self) -> None:
        flushes: list[bool] = []
        fsyncs: list[int] = []
        original_open = Path.open
        original_fsync = os.fsync

        class Writer:
            def __init__(self, file):
                self.file = file

            def __enter__(self):
                self.file.__enter__()
                return self

            def __exit__(self, *args):
                return self.file.__exit__(*args)

            def write(self, data):
                return self.file.write(data)

            def flush(self):
                flushes.append(True)
                return self.file.flush()

            def fileno(self):
                return self.file.fileno()

        def open_path(path, mode="r", *args, **kwargs):
            file = original_open(path, mode, *args, **kwargs)
            return Writer(file) if mode == "xb" else file

        def fsync(fd):
            fsyncs.append(fd)
            return original_fsync(fd)

        with patch.object(Path, "open", autospec=True, side_effect=open_path), patch.object(
            publisher.os, "fsync", side_effect=fsync
        ):
            self._publish()
        self.assertEqual(len(flushes), 1)
        self.assertEqual(len(fsyncs), 1)

    def test_temporario_e_relido_byte_a_byte(self) -> None:
        lidos: list[Path] = []
        original = Path.read_bytes

        def ler(path):
            if path.name.endswith(".tmp"):
                lidos.append(path)
            return original(path)

        with patch.object(Path, "read_bytes", autospec=True, side_effect=ler):
            self._publish()
        self.assertEqual(len(lidos), 1)

    def test_parser_task006_valida_temporario(self) -> None:
        parseados: list[bytes] = []
        original = publisher.parsear_documento

        def parsear(conteudo):
            parseados.append(conteudo)
            return original(conteudo)

        with patch.object(publisher, "parsear_documento", side_effect=parsear):
            self._publish()
        self.assertEqual(len(parseados), 2)

    def test_hash_preparado_corresponde_aos_bytes_finais(self) -> None:
        result, _ = self._publish()
        self.assertEqual(result.sha256, hashlib.sha256(result.destination.read_bytes()).hexdigest())

    def test_os_link_e_o_mecanismo_final(self) -> None:
        original = os.link
        chamadas: list[tuple[Path, Path]] = []
        inodes: list[tuple[int, int]] = []

        def link(origem, destino, *args, **kwargs):
            origem = Path(origem)
            destino = Path(destino)
            inode_origem = origem.stat().st_ino
            chamadas.append((origem, destino))
            resultado = original(origem, destino, *args, **kwargs)
            inodes.append((inode_origem, destino.stat().st_ino))
            return resultado

        with patch.object(publisher.os, "link", side_effect=link):
            result, _ = self._publish()
        self.assertEqual(len(chamadas), 1)
        self.assertEqual(chamadas[0][1], result.destination)
        self.assertEqual(chamadas[0][0].parent, result.destination.parent)
        self.assertEqual(inodes[0][0], inodes[0][1])

    def test_destino_final_e_relido_e_validado(self) -> None:
        result, _ = self._publish()
        parsed = parsear_documento(result.destination.read_bytes())
        self.assertEqual(parsed.metadata["document_id"], result.document_id)

    def test_workspace_root_kind_preferred_e_controlado_pelo_publicador(self) -> None:
        result, _ = self._publish()
        metadata = parsear_documento(result.destination.read_bytes()).metadata
        self.assertEqual(metadata["workspace_root_kind"], "preferred")
        self.assertEqual(result.workspace_root_kind, "preferred")

    def test_workspace_root_kind_fallback_e_registrado(self) -> None:
        self._create_analysis(self.fallback)
        result, _ = self._publish(
            selections=((TipoRaizWorkspace.FALLBACK, self.fallback),)
        )
        metadata = parsear_documento(result.destination.read_bytes()).metadata
        self.assertEqual(metadata["workspace_root_kind"], "fallback")
        self.assertEqual(result.destination.parents[1].parent, self.fallback)

    def test_workspace_root_kind_fornecido_pelo_chamador_e_substituido(self) -> None:
        result, _ = self._publish(metadata=_metadata())
        self.assertEqual(
            parsear_documento(result.destination.read_bytes()).metadata[
                "workspace_root_kind"
            ],
            "preferred",
        )

    def test_colisao_nao_substitui_destino_preexistente(self) -> None:
        folder = self.preferred / ANALYSIS_ID / "evidence"
        folder.mkdir()
        existing = folder / f"DOC-{_uuid(1)}.md"
        original_bytes = b"documento anterior imutavel"
        existing.write_bytes(original_bytes)
        result, _ = self._publish(ids=(1, 2))
        self.assertEqual(existing.read_bytes(), original_bytes)
        self.assertEqual(result.document_id, f"DOC-{_uuid(2)}")

    def test_colisao_gera_nova_identidade(self) -> None:
        folder = self.preferred / ANALYSIS_ID / "evidence"
        folder.mkdir()
        (folder / f"DOC-{_uuid(1)}.md").write_bytes(b"ocupado")
        result, factory = self._publish(ids=(1, 2))
        self.assertEqual(factory.calls, [1, 2])
        self.assertEqual(result.document_id, f"DOC-{_uuid(2)}")

    def test_colisao_reserializa_com_nova_identidade(self) -> None:
        folder = self.preferred / ANALYSIS_ID / "evidence"
        folder.mkdir()
        (folder / f"DOC-{_uuid(1)}.md").write_bytes(b"ocupado")
        metadata_ids: list[str] = []
        original = publisher.serializar_documento

        def serializar(titulo, metadata, corpo):
            metadata_ids.append(metadata["document_id"])
            return original(titulo, metadata, corpo)

        with patch.object(publisher, "serializar_documento", side_effect=serializar):
            self._publish(ids=(1, 2))
        self.assertEqual(metadata_ids, [f"DOC-{_uuid(1)}", f"DOC-{_uuid(2)}"])

    def test_colisao_reavalia_raiz_e_pode_troca_la(self) -> None:
        self._create_analysis(self.fallback)
        folder_a = self.preferred / ANALYSIS_ID / "evidence"
        folder_a.mkdir()
        (folder_a / f"DOC-{_uuid(1)}.md").write_bytes(b"ocupado em A")
        result, _ = self._publish(
            ids=(1, 2),
            selections=(
                (TipoRaizWorkspace.PREFERENCIAL, self.preferred),
                (TipoRaizWorkspace.FALLBACK, self.fallback),
            ),
        )
        self.assertEqual(result.workspace_root_kind, "fallback")
        self.assertEqual(result.destination.parents[1].parent, self.fallback)
        self.assertEqual(
            parsear_documento(result.destination.read_bytes()).metadata["document_id"],
            result.destination.stem,
        )
        self.assertEqual(len(self.resolver_calls), 2)

    def test_colisao_recria_temporario_na_nova_raiz(self) -> None:
        self._create_analysis(self.fallback)
        folder = self.preferred / ANALYSIS_ID / "evidence"
        folder.mkdir()
        (folder / f"DOC-{_uuid(1)}.md").write_bytes(b"ocupado")
        temporarios: list[Path] = []
        original = publisher._escrever_temporario_exclusivo

        def escrever(pasta, dados, factory):
            item = original(pasta, dados, factory)
            temporarios.append(item)
            return item

        with patch.object(publisher, "_escrever_temporario_exclusivo", side_effect=escrever):
            result, _ = self._publish(
                ids=(1, 2),
                selections=((TipoRaizWorkspace.PREFERENCIAL, self.preferred), (TipoRaizWorkspace.FALLBACK, self.fallback)),
            )
        self.assertEqual(len(temporarios), 2)
        self.assertEqual(temporarios[0].parent, folder)
        self.assertEqual(temporarios[1].parent, result.destination.parent)
        self.assertFalse(temporarios[0].exists())

    def test_oito_colisoes_bloqueiam(self) -> None:
        folder = self.preferred / ANALYSIS_ID / "evidence"
        folder.mkdir()
        for numero in range(1, 9):
            (folder / f"DOC-{_uuid(numero)}.md").write_bytes(b"ocupado")
        factory = _factory_ids(*range(1, 9))
        resolver = self._resolver(*([(TipoRaizWorkspace.PREFERENCIAL, self.preferred)] * 8))
        with self.assertRaises(publisher.DocumentCollisionLimitError):
            publisher.publicar_documento(
                self.base / "RickCraft", ANALYSIS_ID, "evidence", "Título", "Corpo",
                _metadata(), uuid_factory=factory, resolver=resolver,
                avaliador_factory=lambda: object(),
            )
        self.assertEqual(factory.calls, list(range(1, 9)))

    def test_oito_colisoes_nao_tentam_nono_uuid(self) -> None:
        folder = self.preferred / ANALYSIS_ID / "evidence"
        folder.mkdir()
        for numero in range(1, 9):
            (folder / f"DOC-{_uuid(numero)}.md").write_bytes(b"ocupado")
        factory = _factory_ids(*range(1, 9))
        with self.assertRaises(publisher.DocumentCollisionLimitError):
            publisher.publicar_documento(
                self.base / "RickCraft", ANALYSIS_ID, "evidence", "Título", "Corpo",
                _metadata(), uuid_factory=factory,
                resolver=self._resolver(*([(TipoRaizWorkspace.PREFERENCIAL, self.preferred)] * 8)),
                avaliador_factory=lambda: object(),
            )
        self.assertEqual(len(factory.calls), 8)

    def test_erro_nao_colisao_nao_consumo_retry_de_uuid(self) -> None:
        factory = _factory_ids(1, 2)
        with patch.object(publisher.os, "link", side_effect=OSError(errno.EIO, "falha I/O")):
            with self.assertRaises(publisher.DocumentPublicationError) as contexto:
                publisher.publicar_documento(
                    self.base / "RickCraft", ANALYSIS_ID, "evidence", "Título", "Corpo",
                    _metadata(), uuid_factory=factory,
                    resolver=self._resolver((TipoRaizWorkspace.PREFERENCIAL, self.preferred)),
                    avaliador_factory=lambda: object(),
                )
        self.assertEqual(factory.calls, [1])
        self.assertEqual(contexto.exception.errno, errno.EIO)
        self.assertEqual(
            contexto.exception.resultado_capacidade,
            ResultadoCapacidade.ERRO_DESCONHECIDO,
        )

    def test_falhas_nao_colisao_preservam_classificacao_d03_sem_retry(self) -> None:
        casos = [
            (PermissionError(errno.EACCES, "acesso negado"), ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA),
            (OSError(errno.EIO, "falha de I/O"), ResultadoCapacidade.ERRO_DESCONHECIDO),
            (OSError("falha sem código"), ResultadoCapacidade.ERRO_DESCONHECIDO),
        ]
        codigo_nao_suportado = getattr(errno, "ENOTSUP", None)
        if codigo_nao_suportado is not None:
            casos.append(
                (OSError(codigo_nao_suportado, "operação não suportada"), ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA)
            )

        for erro, esperado in casos:
            with self.subTest(erro=repr(erro)):
                factory = _factory_ids(1, 2)
                resolver = self._resolver((TipoRaizWorkspace.PREFERENCIAL, self.preferred))
                chamadas_antes = len(self.resolver_calls)
                with patch.object(publisher.os, "link", side_effect=erro):
                    with self.assertRaises(publisher.DocumentPublicationError) as contexto:
                        publisher.publicar_documento(
                            self.base / "RickCraft", ANALYSIS_ID, "evidence", "Título", "Corpo",
                            _metadata(), uuid_factory=factory, resolver=resolver,
                            avaliador_factory=lambda: object(),
                        )
                self.assertEqual(contexto.exception.resultado_capacidade, esperado)
                self.assertEqual(factory.calls, [1])
                self.assertEqual(len(self.resolver_calls) - chamadas_antes, 1)

    def test_erro_desconhecido_bloqueia_sem_fallback(self) -> None:
        root, preferred, _fallback = self._actual_layout()
        avaliadas: list[Path] = []

        def avaliar(root: Path):
            avaliadas.append(root)
            return ResultadoCapacidade.ERRO_DESCONHECIDO

        with self.assertRaises(ResultadoDesconhecidoError):
            publisher.publicar_documento(
                root, ANALYSIS_ID, "evidence", "Título", "Corpo",
                _metadata(), resolver=resolver_workspace,
                avaliador_factory=lambda: avaliar,
            )
        self.assertEqual(avaliadas, [preferred])

    def test_erro_desconhecido_posterior_bloqueia_sem_reutilizar_raiz(self) -> None:
        root, preferred, fallback = self._actual_layout()
        avaliadores = self._actual_evaluators(
            (ResultadoCapacidade.UTILIZAVEL,),
            (ResultadoCapacidade.ERRO_DESCONHECIDO,),
        )
        first, _ = self._publish(
            ids=(1,), resolver=resolver_workspace, evaluator_factory=avaliadores,
            rickcraft_root=root,
        )
        novo_uuid = _factory_ids(2)
        before_preferred = set((preferred / ANALYSIS_ID / "evidence").glob("DOC-*.md"))
        with self.assertRaises(ResultadoDesconhecidoError):
            publisher.publicar_documento(
                root, ANALYSIS_ID, "evidence", "Título", "Corpo", _metadata(),
                uuid_factory=novo_uuid, resolver=resolver_workspace,
                avaliador_factory=avaliadores,
            )
        self.assertEqual(first.workspace_root_kind, "preferred")
        self.assertEqual(novo_uuid.calls, [])
        self.assertEqual(
            set((preferred / ANALYSIS_ID / "evidence").glob("DOC-*.md")),
            before_preferred,
        )
        self.assertFalse((fallback / ANALYSIS_ID / "evidence").exists())

    def test_cada_publicacao_resolve_novamente_a_raiz(self) -> None:
        sequencia = self._resolver(
            (TipoRaizWorkspace.PREFERENCIAL, self.preferred),
            (TipoRaizWorkspace.FALLBACK, self.fallback),
        )
        self._create_analysis(self.fallback)
        first, _ = self._publish(ids=(1,), resolver=sequencia)
        second, _ = self._publish(ids=(2,), resolver=sequencia)
        self.assertEqual(first.workspace_root_kind, "preferred")
        self.assertEqual(second.workspace_root_kind, "fallback")
        self.assertEqual(len(self.resolver_calls), 2)

    def test_fallback_retorna_a_preferred_em_nova_publicacao(self) -> None:
        root, preferred, fallback = self._actual_layout()
        avaliadores = self._actual_evaluators(
            (ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA, ResultadoCapacidade.UTILIZAVEL),
            (ResultadoCapacidade.UTILIZAVEL,),
        )
        first, _ = self._publish(ids=(1,), resolver=resolver_workspace, evaluator_factory=avaliadores, rickcraft_root=root)
        second, _ = self._publish(ids=(2,), resolver=resolver_workspace, evaluator_factory=avaliadores, rickcraft_root=root)
        self.assertEqual(first.workspace_root_kind, "fallback")
        self.assertEqual(second.workspace_root_kind, "preferred")
        self.assertEqual(first.destination.parents[1].parent, fallback)
        self.assertEqual(second.destination.parents[1].parent, preferred)

    def test_preferred_para_fallback_somente_por_resolucao_atual(self) -> None:
        root, preferred, fallback = self._actual_layout()
        avaliadores = self._actual_evaluators(
            (ResultadoCapacidade.UTILIZAVEL,),
            (ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA, ResultadoCapacidade.UTILIZAVEL),
        )
        first, _ = self._publish(ids=(1,), resolver=resolver_workspace, evaluator_factory=avaliadores, rickcraft_root=root)
        second, _ = self._publish(ids=(2,), resolver=resolver_workspace, evaluator_factory=avaliadores, rickcraft_root=root)
        self.assertEqual(first.workspace_root_kind, "preferred")
        self.assertEqual(second.workspace_root_kind, "fallback")
        self.assertEqual(first.destination.parents[1].parent, preferred)
        self.assertEqual(second.destination.parents[1].parent, fallback)

    def test_resolvedor_real_nao_avalia_terceira_raiz(self) -> None:
        root = self.base / "repo" / "impl" / "src" / "RickCraft"
        root.mkdir(parents=True)
        local_preferred = root.parent.parent / ".workspace"
        fallback = root / ".workspace"
        self._create_analysis(fallback)
        chamadas: list[Path] = []

        def avaliar(candidate: Path):
            chamadas.append(candidate)
            return (
                ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA
                if candidate == local_preferred
                else ResultadoCapacidade.UTILIZAVEL
            )

        result, _ = self._publish(
            ids=(1,),
            resolver=resolver_workspace,
            evaluator_factory=lambda: avaliar,
            rickcraft_root=root,
        )
        self.assertEqual(result.workspace_root_kind, "fallback")
        self.assertEqual(chamadas, [local_preferred, fallback])

    def test_analise_ausente_na_raiz_selecionada_bloqueia(self) -> None:
        empty_root = self.base / "empty-root"
        empty_root.mkdir()
        with self.assertRaises(publisher.DocumentPublicationError):
            self._publish(
                ids=(1,),
                selections=((TipoRaizWorkspace.PREFERENCIAL, empty_root),),
            )
        self.assertFalse((empty_root / ANALYSIS_ID).exists())
        self.assertFalse((self.fallback / ANALYSIS_ID / "evidence").exists())

    def test_analise_nao_e_migrada_entre_roots(self) -> None:
        self._create_analysis(self.fallback)
        with self.assertRaises(publisher.DocumentPublicationError):
            self._publish(selections=((TipoRaizWorkspace.PREFERENCIAL, self.fallback.parent),))
        self.assertFalse((self.fallback.parent / ANALYSIS_ID).exists())

    def test_append_only_preserva_documento_anterior(self) -> None:
        primeiro, _ = self._publish(ids=(1,))
        bytes_anteriores = primeiro.destination.read_bytes()
        hash_anterior = hashlib.sha256(bytes_anteriores).hexdigest()
        segundo, _ = self._publish(ids=(2,), body="Outro documento.")
        self.assertNotEqual(primeiro.destination, segundo.destination)
        self.assertEqual(primeiro.destination.read_bytes(), bytes_anteriores)
        self.assertEqual(hashlib.sha256(primeiro.destination.read_bytes()).hexdigest(), hash_anterior)

    def test_falha_antes_de_os_link_nao_retorna_sucesso(self) -> None:
        with patch.object(
            publisher,
            "_escrever_temporario_exclusivo",
            side_effect=OSError(errno.EIO, "falha antes de os.link"),
        ):
            with self.assertRaises(publisher.DocumentPublicationError) as contexto:
                self._publish()
        self.assertFalse(contexto.exception.linked)
        self.assertFalse(any((self.preferred / ANALYSIS_ID / "evidence").glob("DOC-*.md")))

    def test_falha_de_validacao_apos_link_nao_retorna_sucesso(self) -> None:
        original = publisher.parsear_documento
        chamadas = 0

        def parsear(conteudo):
            nonlocal chamadas
            chamadas += 1
            if chamadas == 2:
                raise DocumentFormatError("falha final forçada")
            return original(conteudo)

        with patch.object(publisher, "parsear_documento", side_effect=parsear):
            with self.assertRaises(publisher.DocumentPublicationError) as contexto:
                self._publish()
        self.assertTrue(contexto.exception.linked)
        self.assertTrue(contexto.exception.destination.is_file())

    def test_cleanup_bem_sucedido_remove_temporario_proprio(self) -> None:
        temporarios: list[Path] = []
        original = publisher._escrever_temporario_exclusivo

        def gravar(folder, data, factory):
            path = original(folder, data, factory)
            temporarios.append(path)
            return path

        with patch.object(publisher, "_escrever_temporario_exclusivo", side_effect=gravar):
            self._publish()
        self.assertEqual(len(temporarios), 1)
        self.assertFalse(temporarios[0].exists())

    def test_cleanup_falho_e_reportavel_sem_invalidar_sucesso(self) -> None:
        original_unlink = Path.unlink
        temporarios: list[Path] = []
        original_write = publisher._escrever_temporario_exclusivo

        def gravar(folder, data, factory):
            path = original_write(folder, data, factory)
            temporarios.append(path)
            return path

        def unlink(path, *args, **kwargs):
            if path.suffix == ".tmp":
                raise PermissionError("limpeza forçada")
            return original_unlink(path, *args, **kwargs)

        with patch.object(publisher, "_escrever_temporario_exclusivo", side_effect=gravar), patch.object(
            Path, "unlink", autospec=True, side_effect=unlink
        ):
            result, _ = self._publish()
        self.assertTrue(result.destination.is_file())
        self.assertEqual(result.temporary_residues, tuple(temporarios))
        for temp in temporarios:
            original_unlink(temp)

    def test_tmp_nao_e_publicado_com_extensao_md(self) -> None:
        result, _ = self._publish()
        self.assertEqual(result.destination.suffix, ".md")
        self.assertFalse(any(result.destination.parent.glob("*.tmp")))

    def test_resultado_tem_evidencia_do_avaliador_injetado(self) -> None:
        class Evaluator:
            evidencias = ["evidência-controlada"]

        result, _ = self._publish(evaluator_factory=Evaluator)
        self.assertEqual(result.probe_evidence, ("evidência-controlada",))

    def test_metadata_controlado_coincide_com_nome_e_resultado(self) -> None:
        result, _ = self._publish()
        metadata = parsear_documento(result.destination.read_bytes()).metadata
        self.assertEqual(result.destination.stem, metadata["document_id"])
        self.assertEqual(metadata["analysis_id"], ANALYSIS_ID)
        self.assertEqual(metadata["document_type"], "evidence")

    def test_pasta_somente_do_tipo_solicitado_e_criada(self) -> None:
        self._publish()
        analysis = self.preferred / ANALYSIS_ID
        self.assertEqual({item.name for item in analysis.iterdir()}, {"evidence"})

    def test_uuid_factory_default_usa_uuid4(self) -> None:
        result = publisher.publicar_documento(
            self.base / "RickCraft", ANALYSIS_ID, "evidence", "Título", "Corpo",
            _metadata(), resolver=self._resolver((TipoRaizWorkspace.PREFERENCIAL, self.preferred)),
            avaliador_factory=lambda: object(),
        )
        self.assertEqual(uuid.UUID(result.document_id[4:]).version, 4)

    def test_destino_final_rele_hash_parse_e_flags_sao_confirmados(self) -> None:
        result, _ = self._publish()
        data = result.destination.read_bytes()
        parsed = parsear_documento(data)
        self.assertEqual(hashlib.sha256(data).hexdigest(), result.sha256)
        self.assertEqual(parsed.metadata["document_id"], result.destination.stem)

    def test_concorrencia_nao_sobrescreve_e_referencia_filenames_coerentes(self) -> None:
        barrier = threading.Barrier(2)
        real_link = os.link
        failures: list[BaseException] = []
        results: list[publisher.PublicationResult] = []

        def synchronized_link(source, destination, *args, **kwargs):
            if Path(destination).name == f"DOC-{_uuid(100)}.md":
                barrier.wait(timeout=10)
            return real_link(source, destination, *args, **kwargs)

        def worker(next_id: int) -> None:
            try:
                result, _ = self._publish(
                    ids=(100, next_id),
                    selections=((TipoRaizWorkspace.PREFERENCIAL, self.preferred),) * 2,
                )
                results.append(result)
            except BaseException as exc:
                failures.append(exc)

        with patch.object(publisher.os, "link", side_effect=synchronized_link):
            first = threading.Thread(target=worker, args=(101,))
            second = threading.Thread(target=worker, args=(102,))
            first.start()
            second.start()
            first.join(timeout=20)
            second.join(timeout=20)
        self.assertFalse(first.is_alive())
        self.assertFalse(second.is_alive())
        self.assertEqual(failures, [])
        self.assertEqual(len(results), 2)
        self.assertEqual(len({result.destination for result in results}), 2)
        for result in results:
            data = result.destination.read_bytes()
            metadata = parsear_documento(data).metadata
            self.assertEqual(metadata["document_id"], result.destination.stem)
            self.assertEqual(hashlib.sha256(data).hexdigest(), result.sha256)


if __name__ == "__main__":
    unittest.main()
