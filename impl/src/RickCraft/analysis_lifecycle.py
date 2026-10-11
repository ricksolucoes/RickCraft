"""Cria e retoma diretórios de análise com identidade ANL-UUIDv4."""

from __future__ import annotations

import errno
import re
import stat
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from workspace_probe import AvaliadorWorkspace
from workspace_resolver import RaizWorkspaceSelecionada, resolver_workspace


MAX_TENTATIVAS_ANALISE = 8
_PADRAO_ANALYSIS_ID = re.compile(
    r"ANL-([0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-"
    r"[89ab][0-9a-f]{3}-[0-9a-f]{12})\Z"
)


class AnalysisLifecycleError(RuntimeError):
    """Erro operacional ao criar ou retomar uma análise."""


class AnalysisIdInvalidError(AnalysisLifecycleError):
    """O identificador fornecido não é um ANL-UUIDv4 canônico."""


class AnalysisNotFoundError(AnalysisLifecycleError):
    """A identidade solicitada não existe como diretório de análise."""


class AnalysisCollisionLimitError(AnalysisLifecycleError):
    """O limite de oito criações exclusivas colidiu."""


@dataclass(frozen=True)
class AnalysisDirectory:
    """Identidade e localização efetiva da operação atual."""

    analysis_id: str
    directory: Path
    workspace: RaizWorkspaceSelecionada


def validar_analysis_id(value: object) -> str:
    """Valida estritamente um identificador ANL-UUIDv4 canônico."""
    if type(value) is not str:
        raise AnalysisIdInvalidError("resume_analysis_id deve ser texto.")

    correspondencia = _PADRAO_ANALYSIS_ID.fullmatch(value)
    if correspondencia is None:
        raise AnalysisIdInvalidError(
            "resume_analysis_id deve usar ANL-UUIDv4 canônico em minúsculas."
        )

    try:
        identificador_uuid = uuid.UUID(correspondencia.group(1))
    except (ValueError, AttributeError) as exc:
        raise AnalysisIdInvalidError("resume_analysis_id contém UUID inválido.") from exc

    if (
        identificador_uuid.version != 4
        or identificador_uuid.variant != uuid.RFC_4122
        or str(identificador_uuid) != correspondencia.group(1)
    ):
        raise AnalysisIdInvalidError(
            "resume_analysis_id deve conter UUIDv4 canônico em minúsculas."
        )
    return value


def criar_ou_retomar_analise(
    rickcraft_root: str | Path,
    resume_analysis_id: str | None = None,
    *,
    uuid_factory: Callable[[], uuid.UUID] = uuid.uuid4,
    resolver: Callable[..., RaizWorkspaceSelecionada] | None = None,
    avaliador_factory: Callable[[], Callable[[Path], object]] | None = None,
) -> AnalysisDirectory:
    """Cria análise nova ou retoma exatamente a identidade solicitada.

    Cada chamada válida resolve e sonda novamente o workspace. Os pontos de
    substituição existem para testes controlados; em produção são usados o
    resolvedor e o avaliador concretos das TASK-002/TASK-003.
    """
    if resume_analysis_id is not None:
        resume_analysis_id = validar_analysis_id(resume_analysis_id)

    resolver_atual = resolver or resolver_workspace
    criar_avaliador = avaliador_factory or AvaliadorWorkspace
    workspace = resolver_atual(rickcraft_root, criar_avaliador())

    if resume_analysis_id is not None:
        return _retomar(workspace, resume_analysis_id)

    return _criar(workspace, uuid_factory)


def _retomar(
    workspace: RaizWorkspaceSelecionada,
    analysis_id: str,
) -> AnalysisDirectory:
    diretorio = workspace.caminho / analysis_id
    try:
        informacoes = diretorio.stat()
    except FileNotFoundError as exc:
        raise AnalysisNotFoundError(
            f"A análise solicitada não existe: {analysis_id}."
        ) from exc

    if not stat.S_ISDIR(informacoes.st_mode):
        raise AnalysisNotFoundError(
            f"A identidade solicitada não aponta para um diretório: {analysis_id}."
        )
    return AnalysisDirectory(analysis_id, diretorio, workspace)


def _criar(
    workspace: RaizWorkspaceSelecionada,
    uuid_factory: Callable[[], uuid.UUID],
) -> AnalysisDirectory:
    for _ in range(MAX_TENTATIVAS_ANALISE):
        candidato = uuid_factory()
        if (
            not isinstance(candidato, uuid.UUID)
            or candidato.version != 4
            or candidato.variant != uuid.RFC_4122
        ):
            raise AnalysisLifecycleError(
                "A fonte de identidade não forneceu um UUIDv4 válido."
            )
        analysis_id = f"ANL-{str(candidato)}"
        diretorio = workspace.caminho / analysis_id
        try:
            diretorio.mkdir()
        except FileExistsError as exc:
            if not _e_colisao_de_criacao(exc):
                raise
            continue
        return AnalysisDirectory(analysis_id, diretorio, workspace)

    raise AnalysisCollisionLimitError(
        "Oito candidatos ANL-UUIDv4 colidiram; nenhuma análise foi criada."
    )


def _e_colisao_de_criacao(exc: FileExistsError) -> bool:
    """Reconhece somente EEXIST e códigos Windows equivalentes."""
    return exc.errno == errno.EEXIST or getattr(exc, "winerror", None) in {80, 183}
