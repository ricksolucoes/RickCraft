"""Publicação append-only de documentos operacionais por hard link."""

from __future__ import annotations

import errno
import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
import uuid
from typing import Any, Callable, Mapping

from document_catalog import (
    derivar_caminho_documental,
    ensure_document_type_directory,
    validar_document_id,
)
from document_format import parsear_documento, serializar_documento
from workspace_probe import AvaliadorWorkspace, classificar_falha
from workspace_resolver import RaizWorkspaceSelecionada, resolver_workspace


MAX_TENTATIVAS_PUBLICACAO = 8
MAX_TENTATIVAS_TEMPORARIO = 8


class DocumentPublicationError(RuntimeError):
    """Publicação não confirmada, com diagnóstico e resíduos próprios."""

    def __init__(
        self,
        message: str,
        *,
        cause: BaseException | None = None,
        temporary_residues: tuple[Path, ...] = (),
        destination: Path | None = None,
        linked: bool = False,
    ) -> None:
        super().__init__(message)
        self.cause = cause
        self.errno = getattr(cause, "errno", None)
        self.winerror = getattr(cause, "winerror", None)
        self.temporary_residues = temporary_residues
        self.destination = destination
        self.linked = linked
        causa_arquivo = cause
        while isinstance(causa_arquivo, DocumentPublicationError):
            causa_arquivo = causa_arquivo.cause
        self.resultado_capacidade = (
            classificar_falha(causa_arquivo, "publicacao")
            if isinstance(causa_arquivo, OSError)
            else None
        )


class DocumentCollisionLimitError(DocumentPublicationError):
    """Oito identidades DOC-UUIDv4 colidiram sem sobrescrever destinos."""


@dataclass(frozen=True)
class PublicationResult:
    """Documento cuja publicação e leitura final foram confirmadas."""

    document_id: str
    destination: Path
    sha256: str
    workspace_root_kind: str
    analysis_id: str
    document_type: str
    attempts: int
    temporary_residues: tuple[Path, ...]
    probe_evidence: tuple[object, ...]


Resolver = Callable[..., RaizWorkspaceSelecionada]
EvaluatorFactory = Callable[[], Callable[[Path], object]]
UuidFactory = Callable[[], uuid.UUID]


def publicar_documento(
    rickcraft_root: str | Path,
    analysis_id: str,
    document_type: str,
    titulo: str,
    corpo: str,
    metadados_base: Mapping[str, Any],
    *,
    uuid_factory: UuidFactory = uuid.uuid4,
    temporary_uuid_factory: UuidFactory = uuid.uuid4,
    resolver: Resolver | None = None,
    avaliador_factory: EvaluatorFactory | None = None,
) -> PublicationResult:
    """Serializa e publica um documento sem substituir destinos existentes.

    A raiz é resolvida novamente para cada candidato, inclusive após colisão.
    Os parâmetros injetáveis são pontos mínimos para testes controlados; o
    caminho de produção usa `resolver_workspace` e `AvaliadorWorkspace`.
    """
    if not isinstance(metadados_base, Mapping):
        raise DocumentPublicationError("Os metadados-base devem ser um objeto.")
    if type(analysis_id) is not str or not analysis_id:
        raise DocumentPublicationError("analysis_id deve ser informado explicitamente.")
    if type(document_type) is not str or not document_type:
        raise DocumentPublicationError("document_type deve ser informado explicitamente.")

    resolver_atual = resolver or resolver_workspace
    criar_avaliador = avaliador_factory or AvaliadorWorkspace
    residuos_acumulados: list[Path] = []

    for tentativa in range(1, MAX_TENTATIVAS_PUBLICACAO + 1):
        avaliador = criar_avaliador()
        workspace = resolver_atual(rickcraft_root, avaliador)
        raiz = workspace.caminho
        workspace_root_kind = getattr(getattr(workspace, "tipo", None), "value", None)
        if workspace_root_kind not in {"preferred", "fallback"}:
            raise DocumentPublicationError(
                "O resolvedor não identificou preferred ou fallback como raiz atual."
            )

        try:
            document_id = _novo_document_id(uuid_factory)
            pasta_tipo = ensure_document_type_directory(
                raiz, analysis_id, document_type
            )
            destination = derivar_caminho_documental(
                raiz, analysis_id, document_type, document_id
            )
            if destination.parent != pasta_tipo:
                raise DocumentPublicationError(
                    "O destino documental não corresponde à pasta de tipo selecionada."
                )

            metadados = dict(metadados_base)
            metadados["analysis_id"] = analysis_id
            metadados["document_type"] = document_type
            metadados["document_id"] = document_id
            metadados["workspace_root_kind"] = workspace_root_kind
            bytes_preparados = serializar_documento(titulo, metadados, corpo)
            digest_preparado = hashlib.sha256(bytes_preparados).hexdigest()
            temporario: Path | None = None
            publicado = False

            try:
                temporario = _escrever_temporario_exclusivo(
                    pasta_tipo, bytes_preparados, temporary_uuid_factory
                )
                bytes_releitura = temporario.read_bytes()
                if bytes_releitura != bytes_preparados:
                    raise DocumentPublicationError(
                        "A releitura do temporário divergiu dos bytes preparados."
                    )
                documento_temporario = parsear_documento(bytes_releitura)
                _validar_identidade_documento(
                    documento_temporario.metadata,
                    document_id,
                    analysis_id,
                    document_type,
                    workspace_root_kind,
                )
                if hashlib.sha256(bytes_releitura).hexdigest() != digest_preparado:
                    raise DocumentPublicationError(
                        "O hash do temporário divergiu dos bytes preparados."
                    )

                try:
                    os.link(temporario, destination)
                except OSError as exc:
                    if _e_colisao_destino(exc):
                        residuos_acumulados.extend(_limpar_temporario(temporario))
                        # O próximo loop resolve D-04 novamente e reconstrói
                        # identidade, metadados, bytes, temporário e destino.
                        continue
                    raise
                publicado = True

                bytes_finais = destination.read_bytes()
                if hashlib.sha256(bytes_finais).hexdigest() != digest_preparado:
                    raise DocumentPublicationError(
                        "O hash do destino final divergiu dos bytes publicados.",
                        destination=destination,
                        linked=True,
                    )
                documento_final = parsear_documento(bytes_finais)
                _validar_identidade_documento(
                    documento_final.metadata,
                    document_id,
                    analysis_id,
                    document_type,
                    workspace_root_kind,
                )
                residuos_acumulados.extend(_limpar_temporario(temporario))
                return PublicationResult(
                    document_id=document_id,
                    destination=destination,
                    sha256=digest_preparado,
                    workspace_root_kind=workspace_root_kind,
                    analysis_id=analysis_id,
                    document_type=document_type,
                    attempts=tentativa,
                    temporary_residues=tuple(residuos_acumulados),
                    probe_evidence=tuple(getattr(avaliador, "evidencias", ())),
                )
            except DocumentPublicationError as exc:
                if temporario is not None:
                    residuos_acumulados.extend(_limpar_temporario(temporario))
                residuos = tuple(
                    dict.fromkeys((*exc.temporary_residues, *residuos_acumulados))
                )
                destino = destination if publicado else exc.destination
                linked = publicado or exc.linked
                if (
                    residuos != exc.temporary_residues
                    or destino != exc.destination
                    or linked != exc.linked
                ):
                    erro_enriquecido = DocumentPublicationError(
                        str(exc),
                        cause=exc.cause,
                        temporary_residues=residuos,
                        destination=destino,
                        linked=linked,
                    )
                    # Copiar os campos explícitos preserva também diagnósticos
                    # que não possam ser reconstruídos apenas a partir de cause.
                    erro_enriquecido.errno = exc.errno
                    erro_enriquecido.winerror = exc.winerror
                    erro_enriquecido.resultado_capacidade = exc.resultado_capacidade
                    raise erro_enriquecido from exc
                raise
            except Exception as exc:
                if temporario is not None:
                    residuos_acumulados.extend(_limpar_temporario(temporario))
                raise DocumentPublicationError(
                    "A publicação não pôde ser confirmada.",
                    cause=exc,
                    temporary_residues=tuple(residuos_acumulados),
                    destination=destination if publicado else None,
                    linked=publicado,
                ) from exc

        except DocumentPublicationError:
            raise
        except Exception as exc:
            raise DocumentPublicationError(
                "A preparação da publicação foi bloqueada.",
                cause=exc,
                temporary_residues=tuple(residuos_acumulados),
            ) from exc

    raise DocumentCollisionLimitError(
        "Oito identidades DOC-UUIDv4 colidiram; nenhum destino foi substituído.",
        temporary_residues=tuple(residuos_acumulados),
    )


def _novo_document_id(uuid_factory: UuidFactory) -> str:
    candidato = uuid_factory()
    if (
        not isinstance(candidato, uuid.UUID)
        or candidato.version != 4
        or candidato.variant != uuid.RFC_4122
    ):
        raise DocumentPublicationError("A fonte de identidade não forneceu UUIDv4 válido.")
    document_id = f"DOC-{candidato}"
    try:
        return validar_document_id(document_id)
    except (ValueError, TypeError) as exc:
        raise DocumentPublicationError("DOC-UUIDv4 gerado não é canônico.", cause=exc) from exc


def _escrever_temporario_exclusivo(
    pasta_tipo: Path,
    conteudo: bytes,
    uuid_factory: UuidFactory,
) -> Path:
    for _ in range(MAX_TENTATIVAS_TEMPORARIO):
        candidato_uuid = uuid_factory()
        if (
            not isinstance(candidato_uuid, uuid.UUID)
            or candidato_uuid.version != 4
            or candidato_uuid.variant != uuid.RFC_4122
        ):
            raise DocumentPublicationError(
                "A fonte de nome temporário não forneceu UUIDv4 válido."
            )
        caminho = pasta_tipo / f".rickcraft-publish-{candidato_uuid.hex}.tmp"
        try:
            with caminho.open("xb") as arquivo:
                escritos = arquivo.write(conteudo)
                if escritos != len(conteudo):
                    raise OSError("A escrita do temporário foi incompleta.")
                arquivo.flush()
                fsync = getattr(os, "fsync", None)
                if callable(fsync):
                    fsync(arquivo.fileno())
            return caminho
        except FileExistsError as exc:
            if not _e_colisao_destino(exc):
                raise
    raise FileExistsError(errno.EEXIST, "Colisões no nome temporário excederam o limite", str(pasta_tipo))


def _e_colisao_destino(exc: OSError) -> bool:
    return exc.errno == errno.EEXIST or getattr(exc, "winerror", None) in {80, 183}


def _validar_identidade_documento(
    metadata: Mapping[str, Any],
    document_id: str,
    analysis_id: str,
    document_type: str,
    workspace_root_kind: str,
) -> None:
    esperados = {
        "document_id": document_id,
        "analysis_id": analysis_id,
        "document_type": document_type,
        "workspace_root_kind": workspace_root_kind,
    }
    for campo, esperado in esperados.items():
        if metadata.get(campo) != esperado:
            raise DocumentPublicationError(
                f"O campo documental controlado {campo} não corresponde à tentativa."
            )


def _limpar_temporario(caminho: Path) -> tuple[Path, ...]:
    try:
        caminho.unlink()
    except FileNotFoundError:
        return ()
    except OSError:
        return (caminho,)
    return ()
