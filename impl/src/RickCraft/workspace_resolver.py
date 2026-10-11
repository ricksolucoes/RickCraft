"""Derivação e seleção determinística das raízes de workspace."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable

from rickcraft_root import validate_rickcraft_root


class ResultadoCapacidade(Enum):
    """Resultado semântico fornecido pela capacidade avaliadora da raiz."""

    UTILIZAVEL = "utilizavel"
    IMPOSSIBILIDADE_CONCRETA = "impossibilidade_concreta"
    ERRO_DESCONHECIDO = "erro_desconhecido"


class TipoRaizWorkspace(Enum):
    """Identifica uma das duas localizações normativas do workspace."""

    PREFERENCIAL = "preferred"
    FALLBACK = "fallback"


@dataclass(frozen=True)
class CaminhosWorkspace:
    """Caminhos derivados sem criar ou sondar diretórios."""

    local_definido_usuario: Path
    preferencial: Path
    fallback: Path


@dataclass(frozen=True)
class RaizWorkspaceSelecionada:
    """Raiz selecionada pela resolução atual, sem persistir seleção."""

    tipo: TipoRaizWorkspace
    caminho: Path


class ResolucaoWorkspaceError(RuntimeError):
    """Erro-base para uma resolução sem raiz utilizável."""


class WorkspaceIndisponivelError(ResolucaoWorkspaceError):
    """As duas localizações tiveram impossibilidade concreta."""


class ResultadoDesconhecidoError(ResolucaoWorkspaceError):
    """A avaliação não forneceu um resultado semântico reconhecido."""


def derivar_caminhos_workspace(
    rickcraft_root: str | Path,
) -> CaminhosWorkspace:
    """Deriva as localizações autorizadas a partir da raiz explícita validada."""
    raiz = validate_rickcraft_root(rickcraft_root)
    local_definido_usuario = raiz.parent
    pai_do_local = local_definido_usuario.parent

    return CaminhosWorkspace(
        local_definido_usuario=local_definido_usuario,
        preferencial=pai_do_local / ".workspace",
        fallback=raiz / ".workspace",
    )


def resolver_workspace(
    rickcraft_root: str | Path,
    avaliar: Callable[[Path], ResultadoCapacidade],
) -> RaizWorkspaceSelecionada:
    """Reavalia preferencial e, se autorizado, fallback em cada chamada."""
    caminhos = derivar_caminhos_workspace(rickcraft_root)

    resultado_preferencial = avaliar(caminhos.preferencial)
    if resultado_preferencial is ResultadoCapacidade.UTILIZAVEL:
        return RaizWorkspaceSelecionada(
            TipoRaizWorkspace.PREFERENCIAL,
            caminhos.preferencial,
        )
    if resultado_preferencial is ResultadoCapacidade.ERRO_DESCONHECIDO:
        raise ResultadoDesconhecidoError(
            "A avaliação do workspace preferencial retornou erro desconhecido."
        )
    if resultado_preferencial is not ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA:
        raise ResultadoDesconhecidoError(
            "A avaliação do workspace preferencial retornou resultado inválido."
        )

    resultado_fallback = avaliar(caminhos.fallback)
    if resultado_fallback is ResultadoCapacidade.UTILIZAVEL:
        return RaizWorkspaceSelecionada(
            TipoRaizWorkspace.FALLBACK,
            caminhos.fallback,
        )
    if resultado_fallback is ResultadoCapacidade.ERRO_DESCONHECIDO:
        raise ResultadoDesconhecidoError(
            "A avaliação do workspace fallback retornou erro desconhecido."
        )
    if resultado_fallback is ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA:
        raise WorkspaceIndisponivelError(
            "Workspace preferencial e fallback estão indisponíveis."
        )

    raise ResultadoDesconhecidoError(
        "A avaliação do workspace fallback retornou resultado inválido."
    )
