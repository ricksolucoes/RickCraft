"""Pesquisa somente leitura, sob demanda, sobre documentos recuperados."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import math
from pathlib import Path
from typing import Any

from analysis_lifecycle import AnalysisIdInvalidError, validar_analysis_id
from document_catalog import (
    DocumentIdInvalidError,
    DocumentTypeInvalidError,
    validar_document_id,
    validar_tipo_documento,
)
from document_recovery import (
    DocumentDivergence,
    RecoveredDocument,
    RecoveryFinding,
    RootReadStatus,
    recuperar_documentos,
)


class SearchInputError(ValueError):
    """Consulta contém filtro ou valor incompatível com o contrato local."""


@dataclass(frozen=True)
class SearchQuery:
    """Filtros opcionais combinados sempre com AND."""

    analysis_id: str | None = None
    document_type: str | None = None
    document_id: str | None = None
    metadata_equals: Mapping[str, Any] | None = None
    input_equals: Mapping[str, Any] | None = None
    relation_equals: Mapping[str, Any] | None = None
    text_terms: tuple[str, ...] | list[str] | None = None


@dataclass(frozen=True)
class SearchExclusion:
    """Documento recuperável excluído e todos os filtros que não satisfez."""

    document_id: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class SearchResult:
    """Correspondências e contexto integral relevante da recuperação."""

    matches: tuple[RecoveredDocument, ...]
    exclusions: tuple[SearchExclusion, ...]
    findings: tuple[RecoveryFinding, ...]
    divergences: tuple[DocumentDivergence, ...]
    roots: tuple[RootReadStatus, ...]
    selected_root_kind: str
    probe_evidence: tuple[Any, ...]


def pesquisar_documentos(
    rickcraft_root: str | Path,
    query: SearchQuery | None = None,
    *,
    resolver: Any = None,
    avaliador_factory: Any = None,
    observacoes_atuais: Mapping[str, Mapping[str, Any]] | None = None,
) -> SearchResult:
    """Recupera novamente os documentos e aplica filtros em memória, sem escrita."""
    consulta = query if query is not None else SearchQuery()
    if not isinstance(consulta, SearchQuery):
        raise SearchInputError("query deve ser SearchQuery.")
    normalizada = _validar_consulta(consulta)

    recuperacao = recuperar_documentos(
        rickcraft_root,
        resolver=resolver,
        avaliador_factory=avaliador_factory,
        observacoes_atuais=observacoes_atuais,
    )

    correspondencias: list[RecoveredDocument] = []
    exclusoes: list[SearchExclusion] = []
    for documento in recuperacao.documents:
        motivos = _motivos_exclusao(documento, normalizada)
        if motivos:
            exclusoes.append(SearchExclusion(documento.document_id, motivos))
        else:
            correspondencias.append(documento)

    correspondencias.sort(key=_chave_ordenacao)
    exclusoes.sort(key=lambda item: item.document_id)
    return SearchResult(
        matches=tuple(correspondencias),
        exclusions=tuple(exclusoes),
        findings=recuperacao.findings,
        divergences=recuperacao.divergences,
        roots=recuperacao.roots,
        selected_root_kind=recuperacao.selected_root_kind,
        probe_evidence=recuperacao.probe_evidence,
    )


def _validar_consulta(query: SearchQuery) -> SearchQuery:
    try:
        if query.analysis_id is not None:
            validar_analysis_id(query.analysis_id)
        if query.document_type is not None:
            validar_tipo_documento(query.document_type)
        if query.document_id is not None:
            validar_document_id(query.document_id)
    except (AnalysisIdInvalidError, DocumentIdInvalidError, DocumentTypeInvalidError, TypeError) as exc:
        raise SearchInputError(str(exc)) from exc

    for name in ("metadata_equals", "input_equals", "relation_equals"):
        value = getattr(query, name)
        if value is not None:
            _validar_mapping(name, value)

    terms = query.text_terms
    if terms is not None:
        if not isinstance(terms, (tuple, list)) or not terms:
            raise SearchInputError("text_terms deve ser uma lista ou tupla não vazia.")
        for term in terms:
            if type(term) is not str or not term.strip():
                raise SearchInputError("Cada termo textual deve ser texto não vazio após strip.")

    return query


def _validar_mapping(name: str, value: object) -> None:
    if not isinstance(value, Mapping):
        raise SearchInputError(f"{name} deve ser Mapping.")
    if not value:
        raise SearchInputError(f"{name} não pode ser vazio quando informado.")
    for key, expected in value.items():
        if type(key) is not str:
            raise SearchInputError(f"As chaves de {name} devem ser texto.")
        _validar_valor_json(expected, name)


def _validar_valor_json(value: object, name: str) -> None:
    if value is None or type(value) in {str, bool, int}:
        return
    if type(value) is float:
        if math.isfinite(value):
            return
        raise SearchInputError(f"{name} não aceita número não finito.")
    if type(value) is list:
        for item in value:
            _validar_valor_json(item, name)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise SearchInputError(f"Chaves aninhadas de {name} devem ser texto.")
            _validar_valor_json(item, name)
        return
    raise SearchInputError(f"Valores de {name} devem ser dados JSON, não código ou objetos executáveis.")


def _motivos_exclusao(document: RecoveredDocument, query: SearchQuery) -> tuple[str, ...]:
    metadata = document.parsed.metadata
    reasons: list[str] = []
    if query.analysis_id is not None and document.analysis_id != query.analysis_id:
        reasons.append("analysis_id")
    if query.document_type is not None and document.document_type != query.document_type:
        reasons.append("document_type")
    if query.document_id is not None and document.document_id != query.document_id:
        reasons.append("document_id")
    if query.metadata_equals is not None and not _contém_pares(metadata, query.metadata_equals):
        reasons.append("metadata")
    if query.input_equals is not None and not any(
        _contém_pares(item, query.input_equals)
        for item in metadata["inputs"]
        if isinstance(item, Mapping)
    ):
        reasons.append("input")
    if query.relation_equals is not None and not any(
        _contém_pares(item, query.relation_equals)
        for item in metadata["relations"]
        if isinstance(item, Mapping)
    ):
        reasons.append("relation")
    if query.text_terms is not None:
        body = document.parsed.corpo.casefold()
        if not all(term.strip().casefold() in body for term in query.text_terms):
            reasons.append("text")
    return tuple(reasons)


def _contém_pares(actual: Mapping[str, Any], expected: Mapping[str, Any]) -> bool:
    return all(
        key in actual and _igualdade_json_estrita(actual[key], value)
        for key, value in expected.items()
    )


def _igualdade_json_estrita(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(
            _igualdade_json_estrita(left[key], right[key]) for key in left
        )
    if type(left) is list:
        return len(left) == len(right) and all(
            _igualdade_json_estrita(a, b) for a, b in zip(left, right)
        )
    return left == right


def _chave_ordenacao(document: RecoveredDocument) -> tuple[datetime, str]:
    timestamp = document.created_at_utc
    if timestamp[-1:].lower() == "z":
        timestamp = timestamp[:-1] + "+00:00"
    instante = datetime.fromisoformat(timestamp).astimezone(timezone.utc)
    return instante, document.document_id
