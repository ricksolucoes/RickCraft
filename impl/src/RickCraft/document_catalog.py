"""Catálogo fechado v1 e caminhos documentais seguros."""

from __future__ import annotations

import re
import stat
import uuid
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from analysis_lifecycle import AnalysisIdInvalidError, validar_analysis_id


type_catalog_version = 1
TYPE_CATALOG: Mapping[str, str] = MappingProxyType(
    {
        "context": "Contexto, objetivo, origem resumida e restrições da análise.",
        "analysis": "Observações, exame das entradas e interpretação reproduzível.",
        "evidence": "Verificação realizada, método, ambiente e resultados observados.",
        "decision": "Decisão existente, autoridade, justificativa e fonte.",
        "divergence": "Fontes ou observações incompatíveis e impacto pendente.",
        "blocker": "Impedimento verificável, dependência e condição de retomada.",
        "result": "Resultado operacional, evidências, limitações e pendências.",
        "handoff": "Contexto e próximo passo autorizado para outra sessão ou Agent.",
    }
)
DOCUMENT_TYPES = frozenset(TYPE_CATALOG)

_PADRAO_DOCUMENT_ID = re.compile(
    r"DOC-([0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-"
    r"[89ab][0-9a-f]{3}-[0-9a-f]{12})\Z"
)


class DocumentCatalogError(ValueError):
    """Entrada ou localização incompatível com o catálogo documental v1."""


class DocumentTypeInvalidError(DocumentCatalogError):
    """Tipo documental não pertence exatamente ao catálogo fechado v1."""


class DocumentIdInvalidError(DocumentCatalogError):
    """Identificador documental não é DOC-UUIDv4 canônico."""


class DocumentPathError(DocumentCatalogError):
    """Raiz, análise ou destino não atende à contenção esperada."""


def validar_tipo_documento(value: object) -> str:
    """Aceita somente um dos oito tokens literais do catálogo v1."""
    if type(value) is not str or value not in DOCUMENT_TYPES:
        raise DocumentTypeInvalidError(
            "document_type deve ser um token exato do catálogo documental v1."
        )
    return value


def validar_document_id(value: object) -> str:
    """Valida DOC-UUIDv4 canônico em minúsculas, sem normalização implícita."""
    if type(value) is not str:
        raise DocumentIdInvalidError("document_id deve ser texto.")

    correspondencia = _PADRAO_DOCUMENT_ID.fullmatch(value)
    if correspondencia is None:
        raise DocumentIdInvalidError(
            "document_id deve usar DOC-UUIDv4 canônico em minúsculas."
        )

    try:
        identificador_uuid = uuid.UUID(correspondencia.group(1))
    except (ValueError, AttributeError) as exc:
        raise DocumentIdInvalidError("document_id contém UUID inválido.") from exc

    if (
        identificador_uuid.version != 4
        or identificador_uuid.variant != uuid.RFC_4122
        or str(identificador_uuid) != correspondencia.group(1)
    ):
        raise DocumentIdInvalidError(
            "document_id deve conter UUIDv4 canônico em minúsculas."
        )
    return value


def derivar_caminho_documental(
    workspace_root: str | Path,
    analysis_id: str,
    document_type: str,
    document_id: str,
) -> Path:
    """Deriva o destino sem criar diretório ou arquivo operacional."""
    raiz, raiz_fisica, analise, analise_fisica = _validar_diretorio_analise(
        workspace_root, analysis_id
    )
    tipo = validar_tipo_documento(document_type)
    identificador = validar_document_id(document_id)

    pasta_tipo = analise / tipo
    pasta_tipo_esperada = analise_fisica / tipo
    _validar_pasta_tipo_existente(pasta_tipo, pasta_tipo_esperada)

    destino = pasta_tipo / f"{identificador}.md"
    destino_esperado = pasta_tipo_esperada / f"{identificador}.md"
    try:
        destino_fisico = destino.resolve(strict=False)
    except (OSError, RuntimeError, ValueError) as exc:
        raise DocumentPathError(
            "O caminho documental não pôde ser resolvido com segurança."
        ) from exc

    if destino_fisico != destino_esperado or not destino_fisico.is_relative_to(
        analise_fisica
    ):
        raise DocumentPathError(
            "O caminho documental escapa da análise selecionada."
        )

    # A raiz física foi calculada deliberadamente para ancorar a análise;
    # mantê-la no fluxo também confirma que a composição parte da raiz recebida.
    if not analise_fisica.is_relative_to(raiz_fisica) or not analise.is_relative_to(raiz):
        raise DocumentPathError("A análise não está contida na raiz selecionada.")
    return destino


def ensure_document_type_directory(
    workspace_root: str | Path,
    analysis_id: str,
    document_type: str,
) -> Path:
    """Cria idempotentemente somente a pasta do tipo validado solicitado."""
    raiz, _, analise, analise_fisica = _validar_diretorio_analise(
        workspace_root, analysis_id
    )
    tipo = validar_tipo_documento(document_type)
    pasta_tipo = analise / tipo
    try:
        pasta_tipo.mkdir(exist_ok=True)
    except FileExistsError as exc:
        raise DocumentPathError(
            "O destino do tipo documental existe e não é um diretório utilizável."
        ) from exc

    pasta_tipo_esperada = analise_fisica / tipo
    _validar_pasta_tipo_existente(pasta_tipo, pasta_tipo_esperada)
    if not analise.is_relative_to(raiz):
        raise DocumentPathError("A análise não está contida na raiz selecionada.")
    return pasta_tipo


def _validar_diretorio_analise(
    workspace_root: str | Path,
    analysis_id: str,
) -> tuple[Path, Path, Path, Path]:
    try:
        identificador = validar_analysis_id(analysis_id)
    except (AnalysisIdInvalidError, TypeError) as exc:
        raise DocumentPathError("analysis_id não é um ANL-UUIDv4 válido.") from exc

    try:
        raiz = Path(workspace_root)
    except (TypeError, ValueError) as exc:
        raise DocumentPathError("workspace_root deve ser um caminho válido.") from exc
    if not raiz.is_absolute():
        raise DocumentPathError("workspace_root deve ser absoluto.")

    analise = raiz / identificador
    try:
        raiz_fisica = raiz.resolve(strict=True)
        analise_info = analise.lstat()
    except (OSError, RuntimeError, ValueError) as exc:
        raise DocumentPathError(
            "A análise precisa existir dentro da raiz de workspace selecionada."
        ) from exc

    if analise.parent != raiz or analise.name != identificador:
        raise DocumentPathError("analysis_id não identifica um filho direto do workspace.")
    if _e_redirecionamento(analise, analise_info):
        raise DocumentPathError("O diretório da análise não pode ser redirecionado.")
    if not stat.S_ISDIR(analise_info.st_mode):
        raise DocumentPathError("O caminho da análise não aponta para um diretório.")

    try:
        analise_fisica = analise.resolve(strict=True)
    except (OSError, RuntimeError, ValueError) as exc:
        raise DocumentPathError(
            "A localização física da análise não pôde ser confirmada."
        ) from exc

    analise_esperada = raiz_fisica / identificador
    if analise_fisica != analise_esperada or analise_fisica.parent != raiz_fisica:
        raise DocumentPathError(
            "A análise não corresponde ao diretório físico direto esperado."
        )
    return raiz, raiz_fisica, analise, analise_fisica


def _validar_pasta_tipo_existente(pasta: Path, esperada: Path) -> None:
    try:
        informacoes = pasta.lstat()
    except FileNotFoundError:
        return
    except OSError as exc:
        raise DocumentPathError(
            "A pasta de tipo documental não pôde ser verificada."
        ) from exc

    if _e_redirecionamento(pasta, informacoes):
        raise DocumentPathError("A pasta de tipo não pode ser um redirecionamento.")
    if not stat.S_ISDIR(informacoes.st_mode):
        raise DocumentPathError("O destino do tipo documental não é um diretório.")
    try:
        fisica = pasta.resolve(strict=True)
    except (OSError, RuntimeError, ValueError) as exc:
        raise DocumentPathError(
            "A localização física da pasta de tipo não pôde ser confirmada."
        ) from exc
    if fisica != esperada or fisica.parent != esperada.parent:
        raise DocumentPathError("A pasta de tipo escapa da análise selecionada.")


def _e_redirecionamento(caminho: Path, informacoes: object) -> bool:
    if stat.S_ISLNK(informacoes.st_mode):
        return True
    verificar_junction = getattr(caminho, "is_junction", None)
    if callable(verificar_junction) and verificar_junction():
        return True
    atributo_reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    atributos = getattr(informacoes, "st_file_attributes", 0)
    return bool(atributo_reparse and atributos & atributo_reparse)
