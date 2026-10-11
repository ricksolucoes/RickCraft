"""Registro e verificação de proveniência de entradas por identidade observável."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
from typing import Any

from document_catalog import DocumentIdInvalidError, validar_document_id


KIND_LOCAL_FILE = "local_file"
KIND_WORKSPACE_DOCUMENT = "workspace_document"
KIND_VERSIONED_SOURCE = "versioned_source"
ESTADOS_VERIFICACAO = frozenset(
    {"MATCHED", "CHANGED_REASSESS", "UNAVAILABLE", "UNVERIFIABLE"}
)


class ProvenanceError(ValueError):
    """Entrada de proveniência inválida para as operações suportadas."""


Clock = Callable[[], datetime]


def calcular_sha256(conteudo: bytes) -> str:
    """Calcula SHA-256 diretamente sobre os bytes recebidos, sem conversão."""
    if type(conteudo) is not bytes:
        raise TypeError("O conteúdo para SHA-256 deve ser informado como bytes.")
    return hashlib.sha256(conteudo).hexdigest()


def observar_arquivo_local(caminho: str | os.PathLike[str], *, clock: Clock | None = None) -> dict[str, Any]:
    """Lê arquivo local em binário e registra uma observação, sem publicá-la."""
    locator = _normalizar_locator_local(caminho)
    instante = _instante_utc(clock)
    try:
        conteudo = Path(locator).read_bytes()
    except OSError as exc:
        return _registro(
            KIND_LOCAL_FILE,
            locator,
            instante,
            verification="UNAVAILABLE",
            reason=f"A entrada local não pôde ser lida ({type(exc).__name__}).",
        )
    return _registro(
        KIND_LOCAL_FILE,
        locator,
        instante,
        sha256=calcular_sha256(conteudo),
        verification="UNVERIFIABLE",
        reason="Observação inicial sem referência histórica para comparação.",
    )


def verificar_arquivo_local(
    historico: Mapping[str, Any],
    caminho: str | os.PathLike[str],
    *,
    clock: Clock | None = None,
) -> dict[str, Any]:
    """Compara os bytes atuais do arquivo com a observação histórica fornecida."""
    registro_historico = _validar_historico(historico, KIND_LOCAL_FILE)
    locator = _normalizar_locator_local(caminho)
    instante = _instante_utc(clock)
    locator_historico = _normalizar_locator_historico_local(
        registro_historico.get("locator")
    )
    if locator_historico is None:
        return _registro(
            KIND_LOCAL_FILE,
            locator,
            instante,
            verification="UNVERIFIABLE",
            reason="A referência histórica não contém locator local absoluto verificável.",
            historical=_referencia_historica(registro_historico),
        )
    if os.path.normcase(locator_historico) != os.path.normcase(locator):
        return _registro(
            KIND_LOCAL_FILE,
            locator,
            instante,
            verification="CHANGED_REASSESS",
            historical=_referencia_historica(registro_historico),
        )

    try:
        conteudo = Path(locator).read_bytes()
    except OSError as exc:
        return _registro(
            KIND_LOCAL_FILE,
            locator,
            instante,
            verification="UNAVAILABLE",
            reason=f"A entrada local não pôde ser lida ({type(exc).__name__}).",
            historical=_referencia_historica(registro_historico),
        )

    digest = calcular_sha256(conteudo)
    digest_historico = registro_historico.get("sha256")
    if not _sha256_valido(digest_historico):
        return _registro(
            KIND_LOCAL_FILE,
            locator,
            instante,
            sha256=digest,
            verification="UNVERIFIABLE",
            reason="A referência histórica não contém SHA-256 verificável.",
            historical=_referencia_historica(registro_historico),
        )
    estado = "MATCHED" if digest == digest_historico else "CHANGED_REASSESS"
    return _registro(
        KIND_LOCAL_FILE,
        locator,
        instante,
        sha256=digest,
        verification=estado,
        historical=_referencia_historica(registro_historico),
    )


def observar_documento_workspace(
    document_id: object,
    conteudo: bytes,
    *,
    clock: Clock | None = None,
) -> dict[str, Any]:
    """Registra bytes fornecidos pelo chamador sob identidade DOC validada."""
    identificador = _validar_document_id(document_id)
    digest = calcular_sha256(conteudo)
    return _registro(
        KIND_WORKSPACE_DOCUMENT,
        identificador,
        _instante_utc(clock),
        sha256=digest,
        verification="UNVERIFIABLE",
        reason="Observação inicial sem referência histórica para comparação.",
    )


def verificar_documento_workspace(
    historico: Mapping[str, Any],
    document_id: object,
    conteudo: bytes,
    *,
    clock: Clock | None = None,
) -> dict[str, Any]:
    """Compara bytes fornecidos explicitamente, sem buscar o documento no disco."""
    registro_historico = _validar_historico(historico, KIND_WORKSPACE_DOCUMENT)
    identificador = _validar_document_id(document_id)
    digest = calcular_sha256(conteudo)
    locator_historico = registro_historico.get("locator")
    digest_historico = registro_historico.get("sha256")
    if locator_historico != identificador or not _sha256_valido(digest_historico):
        return _registro(
            KIND_WORKSPACE_DOCUMENT,
            identificador,
            _instante_utc(clock),
            sha256=digest,
            verification=(
                "CHANGED_REASSESS"
                if locator_historico != identificador
                else "UNVERIFIABLE"
            ),
            reason=(
                None
                if locator_historico != identificador
                else "A referência histórica não contém SHA-256 verificável."
            ),
            historical=_referencia_historica(registro_historico),
        )
    estado = "MATCHED" if digest == digest_historico else "CHANGED_REASSESS"
    return _registro(
        KIND_WORKSPACE_DOCUMENT,
        identificador,
        _instante_utc(clock),
        sha256=digest,
        verification=estado,
        historical=_referencia_historica(registro_historico),
    )


def observar_fonte_versionada(
    referencia: str,
    *,
    version_kind: str | None = None,
    version: str | None = None,
    conteudo: bytes | None = None,
    clock: Clock | None = None,
) -> dict[str, Any]:
    """Registra identificadores explicitamente fornecidos, sem acessar a fonte."""
    locator = _texto_nao_vazio(referencia, "A referência da fonte versionada")
    tipo_versao = _opcional_nao_vazio(version_kind, "version_kind")
    versao = _opcional_nao_vazio(version, "version")
    digest = calcular_sha256(conteudo) if conteudo is not None else None
    verificavel = (tipo_versao is not None and versao is not None) or digest is not None
    return _registro(
        KIND_VERSIONED_SOURCE,
        locator,
        _instante_utc(clock),
        version_kind=tipo_versao,
        version=versao,
        sha256=digest,
        verification="UNVERIFIABLE",
        reason=(
            "Observação inicial sem referência histórica para comparação."
            if verificavel
            else "A fonte não forneceu versão nem bytes verificáveis."
        ),
    )


def verificar_fonte_versionada(
    historico: Mapping[str, Any],
    referencia: str,
    *,
    version_kind: str | None = None,
    version: str | None = None,
    conteudo: bytes | None = None,
    clock: Clock | None = None,
) -> dict[str, Any]:
    """Compara apenas versões/bytes recebidos explicitamente pelo chamador."""
    registro_historico = _validar_historico(historico, KIND_VERSIONED_SOURCE)
    locator = _texto_nao_vazio(referencia, "A referência da fonte versionada")
    tipo_versao = _opcional_nao_vazio(version_kind, "version_kind")
    versao = _opcional_nao_vazio(version, "version")
    digest = calcular_sha256(conteudo) if conteudo is not None else None
    instante = _instante_utc(clock)

    if registro_historico.get("locator") != locator:
        return _registro(
            KIND_VERSIONED_SOURCE,
            locator,
            instante,
            version_kind=tipo_versao,
            version=versao,
            sha256=digest,
            verification="CHANGED_REASSESS",
            historical=_referencia_historica(registro_historico),
        )

    comparacoes: list[bool] = []
    antigo_tipo = registro_historico.get("version_kind")
    antiga_versao = registro_historico.get("version")
    if (
        type(antigo_tipo) is str
        and type(antiga_versao) is str
        and tipo_versao is not None
        and versao is not None
    ):
        comparacoes.append((antigo_tipo, antiga_versao) == (tipo_versao, versao))
    antigo_digest = registro_historico.get("sha256")
    if _sha256_valido(antigo_digest) and digest is not None:
        comparacoes.append(antigo_digest == digest)

    if not comparacoes:
        return _registro(
            KIND_VERSIONED_SOURCE,
            locator,
            instante,
            version_kind=tipo_versao,
            version=versao,
            sha256=digest,
            verification="UNVERIFIABLE",
            reason="Não há versão ou hash histórico e atual comparáveis.",
            historical=_referencia_historica(registro_historico),
        )
    estado = "CHANGED_REASSESS" if not all(comparacoes) else "MATCHED"
    return _registro(
        KIND_VERSIONED_SOURCE,
        locator,
        instante,
        version_kind=tipo_versao,
        version=versao,
        sha256=digest,
        verification=estado,
        historical=_referencia_historica(registro_historico),
    )


def _registro(
    kind: str,
    locator: str,
    observed_at_utc: str,
    *,
    sha256: str | None = None,
    verification: str,
    reason: str | None = None,
    version_kind: str | None = None,
    version: str | None = None,
    historical: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if verification not in ESTADOS_VERIFICACAO:
        raise AssertionError("Estado de verificação interno inválido.")
    resultado: dict[str, Any] = {
        "kind": kind,
        "locator": locator,
        "observed_at_utc": observed_at_utc,
        "verification": verification,
    }
    if version_kind is not None:
        resultado["version_kind"] = version_kind
    if version is not None:
        resultado["version"] = version
    if sha256 is not None:
        resultado["sha256"] = sha256
    if reason is not None:
        resultado["reason"] = reason
    if historical is not None:
        resultado["historical"] = historical
    return resultado


def _normalizar_locator_local(caminho: str | os.PathLike[str]) -> str:
    try:
        valor = os.fspath(caminho)
    except TypeError as exc:
        raise ProvenanceError("O caminho local deve ser informado explicitamente.") from exc
    if type(valor) is not str or not valor:
        raise ProvenanceError("O caminho local deve ser texto não vazio.")
    try:
        return os.path.abspath(valor)
    except (OSError, ValueError) as exc:
        raise ProvenanceError("O caminho local não pôde ser normalizado.") from exc


def _normalizar_locator_historico_local(valor: object) -> str | None:
    """Aceita somente locator histórico absoluto e normaliza sua forma lexical."""
    if type(valor) is not str or not valor or not os.path.isabs(valor):
        return None
    try:
        return os.path.abspath(valor)
    except (OSError, ValueError):
        return None


def _instante_utc(clock: Clock | None) -> str:
    instante = (clock or (lambda: datetime.now(timezone.utc)))()
    if not isinstance(instante, datetime) or instante.tzinfo is None:
        raise ProvenanceError("O relógio deve fornecer instante com fuso horário.")
    instante = instante.astimezone(timezone.utc)
    texto = instante.isoformat(timespec="microseconds")
    texto = texto.removesuffix("+00:00").rstrip("0").rstrip(".") + "Z"
    return texto


def _validar_document_id(valor: object) -> str:
    try:
        return validar_document_id(valor)
    except (DocumentIdInvalidError, TypeError) as exc:
        raise ProvenanceError("document_id deve ser DOC-UUIDv4 canônico válido.") from exc


def _validar_historico(historico: Mapping[str, Any], kind: str) -> dict[str, Any]:
    if not isinstance(historico, Mapping):
        raise ProvenanceError("A observação histórica deve ser um objeto de proveniência.")
    copia = dict(historico)
    if copia.get("kind") != kind:
        raise ProvenanceError("A família da observação histórica não corresponde à verificação.")
    return copia


def _referencia_historica(historico: Mapping[str, Any]) -> dict[str, Any]:
    campos = ("kind", "locator", "observed_at_utc", "version_kind", "version", "sha256")
    return {campo: historico[campo] for campo in campos if campo in historico}


def _sha256_valido(valor: object) -> bool:
    return (
        type(valor) is str
        and len(valor) == 64
        and all(caractere in "0123456789abcdef" for caractere in valor)
    )


def _texto_nao_vazio(valor: object, nome: str) -> str:
    if type(valor) is not str or not valor.strip():
        raise ProvenanceError(f"{nome} deve ser texto explícito não vazio.")
    return valor


def _opcional_nao_vazio(valor: object, nome: str) -> str | None:
    if valor is None:
        return None
    return _texto_nao_vazio(valor, nome)
