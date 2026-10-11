"""Serialização e validação estrutural do envelope Markdown/JSON v1."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import math
import re
from typing import Any, Mapping

from analysis_lifecycle import AnalysisIdInvalidError, validar_analysis_id
from document_catalog import (
    DocumentIdInvalidError,
    DocumentTypeInvalidError,
    type_catalog_version,
    validar_document_id,
    validar_tipo_documento,
)


TOKENS_RELACAO = frozenset(
    {"corrects", "complements", "supersedes", "invalidates", "supports", "related_to"}
)
_CAMPOS_OBRIGATORIOS = frozenset(
    {
        "schema_version",
        "type_catalog_version",
        "document_id",
        "analysis_id",
        "document_type",
        "workspace_root_kind",
        "created_at_utc",
        "purpose",
        "origin",
        "inputs",
        "relations",
    }
)
_PADRAO_DATA_UTC = re.compile(
    r"(?P<data>\d{4}-\d{2}-\d{2})[Tt]"
    r"(?P<hora>\d{2}:\d{2}:\d{2})"
    r"(?P<fracao>\.\d+)?"
    r"(?P<zona>[Zz]|[+-]\d{2}:\d{2})\Z"
)


class DocumentFormatError(ValueError):
    """Documento não atende ao formato Markdown/JSON v1."""


@dataclass(frozen=True)
class DocumentoMarkdown:
    """Conteudo validado de um documento operacional, sem persistencia."""

    titulo: str
    metadata: dict[str, Any]
    corpo: str


def serializar_documento(
    titulo: str,
    metadata: Mapping[str, Any],
    corpo: str,
) -> bytes:
    """Produz bytes UTF-8 deterministas sem criar arquivo ou diretório."""
    if type(titulo) is not str or not titulo.strip() or "\n" in titulo or "\r" in titulo:
        raise DocumentFormatError("O título Markdown deve ser uma linha de texto não vazia.")
    if type(corpo) is not str:
        raise DocumentFormatError("O corpo Markdown deve ser texto explicito.")
    if not isinstance(metadata, Mapping):
        raise DocumentFormatError("Os metadados devem ser um objeto JSON.")

    dados = dict(metadata)
    validar_metadados(dados)
    dados["created_at_utc"] = _normalizar_data_utc(dados["created_at_utc"])
    _validar_valores_json(dados)
    try:
        json_texto = json.dumps(
            dados,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            indent=2,
        )
        documento = f"# {titulo}\n\n```json\n{json_texto}\n```\n\n{corpo}"
        return documento.encode("utf-8", errors="strict")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise DocumentFormatError(
            "Os metadados ou o documento não podem ser serializados como JSON/UTF-8 estritos."
        ) from exc


def parsear_documento(conteudo: bytes | str) -> DocumentoMarkdown:
    """Valida e interpreta o envelope em bytes UTF-8 ou texto Unicode."""
    if isinstance(conteudo, bytes):
        try:
            texto = conteudo.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise DocumentFormatError("O documento não é UTF-8 válido.") from exc
    elif type(conteudo) is str:
        texto = conteudo
        try:
            texto.encode("utf-8", errors="strict")
        except UnicodeEncodeError as exc:
            raise DocumentFormatError("O documento contém texto fora de UTF-8 válido.") from exc
    else:
        raise DocumentFormatError("O documento deve ser informado como bytes UTF-8 ou texto.")

    linhas = texto.splitlines(keepends=True)
    if len(linhas) < 5:
        raise DocumentFormatError("O envelope Markdown/JSON esta incompleto.")

    titulo_linha = _sem_quebra_final(linhas[0])
    if not titulo_linha.startswith("# ") or not titulo_linha[2:].strip():
        raise DocumentFormatError("O documento deve começar com um título Markdown não vazio.")
    if _sem_quebra_final(linhas[1]).strip() or _sem_quebra_final(linhas[2]).strip() != "```json":
        raise DocumentFormatError("O título deve ser seguido por um único bloco cercado json.")

    aberturas = [
        indice
        for indice, linha in enumerate(linhas)
        if _sem_quebra_final(linha).strip() == "```json"
    ]
    if aberturas != [2]:
        raise DocumentFormatError("O documento deve conter exatamente um bloco de metadados json.")

    fechamento = next(
        (
            indice
            for indice in range(3, len(linhas))
            if _sem_quebra_final(linhas[indice]).strip() == "```"
        ),
        None,
    )
    if fechamento is None:
        raise DocumentFormatError("O bloco json não foi fechado.")
    if fechamento + 1 >= len(linhas) or _sem_quebra_final(linhas[fechamento + 1]).strip():
        raise DocumentFormatError("O bloco json deve ser separado do corpo Markdown por uma linha vazia.")
    if fechamento + 2 >= len(linhas) and not texto.endswith(("\n\n", "\r\n\r\n")):
        raise DocumentFormatError("O corpo Markdown deve ser explicitamente separado do bloco json.")

    json_texto = "".join(linhas[3:fechamento])
    try:
        metadata = json.loads(
            json_texto,
            object_pairs_hook=_objeto_sem_chaves_duplicadas,
            parse_constant=_rejeitar_constante_json,
        )
    except DocumentFormatError:
        raise
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise DocumentFormatError("O bloco de metadados não contém JSON estrito válido.") from exc
    if type(metadata) is not dict:
        raise DocumentFormatError("A raiz dos metadados JSON deve ser um objeto.")

    validar_metadados(metadata)
    corpo = "".join(linhas[fechamento + 2 :]) if fechamento + 2 < len(linhas) else ""
    return DocumentoMarkdown(titulo_linha[2:], metadata, corpo)


def validar_metadados(metadata: Mapping[str, Any]) -> None:
    """Valida estrutura e tokens v1, sem verificar proveniência ou filesystem."""
    if not isinstance(metadata, Mapping):
        raise DocumentFormatError("Os metadados devem ser um objeto JSON.")
    ausentes = _CAMPOS_OBRIGATORIOS.difference(metadata)
    if ausentes:
        raise DocumentFormatError(
            "Campos obrigatórios ausentes: " + ", ".join(sorted(ausentes)) + "."
        )

    if type(metadata["schema_version"]) is not int or metadata["schema_version"] != 1:
        raise DocumentFormatError("schema_version deve ser o inteiro 1.")
    if (
        type(metadata["type_catalog_version"]) is not int
        or metadata["type_catalog_version"] != type_catalog_version
    ):
        raise DocumentFormatError("type_catalog_version deve ser o inteiro 1.")

    try:
        validar_document_id(metadata["document_id"])
        validar_analysis_id(metadata["analysis_id"])
        validar_tipo_documento(metadata["document_type"])
    except (AnalysisIdInvalidError, DocumentIdInvalidError, DocumentTypeInvalidError, TypeError) as exc:
        raise DocumentFormatError(str(exc)) from exc

    if type(metadata["workspace_root_kind"]) is not str or metadata[
        "workspace_root_kind"
    ] not in {"preferred", "fallback"}:
        raise DocumentFormatError("workspace_root_kind deve ser preferred ou fallback.")
    _normalizar_data_utc(metadata["created_at_utc"])
    if type(metadata["purpose"]) is not str or not metadata["purpose"].strip():
        raise DocumentFormatError("purpose deve ser texto explícito não vazio.")

    origin = metadata["origin"]
    if type(origin) is not dict:
        raise DocumentFormatError("origin deve ser um objeto JSON.")
    if type(origin.get("kind")) is not str or not origin["kind"].strip():
        raise DocumentFormatError("origin.kind deve identificar explicitamente a origem.")
    for campo in ("reference", "summary"):
        if campo in origin and (
            type(origin[campo]) is not str or not origin[campo].strip()
        ):
            raise DocumentFormatError(f"origin.{campo} deve ser texto não vazio quando informado.")
    possui_referencia = "reference" in origin
    possui_resumo = "summary" in origin
    if not (possui_referencia or possui_resumo):
        raise DocumentFormatError("origin requer reference ou summary explícito não vazio.")

    inputs = metadata["inputs"]
    if type(inputs) is not list:
        raise DocumentFormatError("inputs deve ser um array JSON explicito.")
    for item in inputs:
        if type(item) is not dict:
            raise DocumentFormatError("Cada entrada de inputs deve ser um objeto JSON.")
        for campo in ("kind", "locator", "version_kind", "version", "sha256", "verification"):
            if campo in item and type(item[campo]) is not str:
                raise DocumentFormatError(f"inputs.{campo} deve ser texto quando informado.")
        if "observed_at_utc" in item:
            _normalizar_data_utc(item["observed_at_utc"])

    relations = metadata["relations"]
    if type(relations) is not list:
        raise DocumentFormatError("relations deve ser um array JSON explicito.")
    for item in relations:
        if type(item) is not dict:
            raise DocumentFormatError("Cada relation deve ser um objeto JSON.")
        token = item.get("relation_type")
        if type(token) is not str or token not in TOKENS_RELACAO:
            raise DocumentFormatError("relation_type deve ser um token exato definido pelo PLAN.")
        try:
            validar_document_id(item.get("document_id"))
        except (DocumentIdInvalidError, TypeError) as exc:
            raise DocumentFormatError("Toda relation requer document_id válido.") from exc
        if "analysis_id" in item:
            try:
                validar_analysis_id(item["analysis_id"])
            except (AnalysisIdInvalidError, TypeError) as exc:
                raise DocumentFormatError("analysis_id da relation deve ser ANL-UUIDv4 válido.") from exc

    _validar_valores_json(metadata)


def _objeto_sem_chaves_duplicadas(pares: list[tuple[str, Any]]) -> dict[str, Any]:
    resultado: dict[str, Any] = {}
    for chave, valor in pares:
        if chave in resultado:
            raise DocumentFormatError(f"Chave JSON duplicada: {chave}.")
        resultado[chave] = valor
    return resultado


def _rejeitar_constante_json(valor: str) -> None:
    raise DocumentFormatError(f"Constante JSON nao permitida: {valor}.")


def _normalizar_data_utc(valor: object) -> str:
    if type(valor) is not str:
        raise DocumentFormatError("created_at_utc deve ser texto RFC3339 em UTC.")
    correspondencia = _PADRAO_DATA_UTC.fullmatch(valor)
    if correspondencia is None:
        raise DocumentFormatError("created_at_utc deve ser um instante RFC3339 em UTC.")

    zona = correspondencia.group("zona")
    if zona not in {"Z", "z", "+00:00"}:
        raise DocumentFormatError("created_at_utc deve usar fuso UTC, sem deslocamento local.")
    base = f"{correspondencia.group('data')}T{correspondencia.group('hora')}"
    try:
        datetime.fromisoformat(base).replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise DocumentFormatError("created_at_utc contém data ou horário inválido.") from exc

    fracao = correspondencia.group("fracao")
    fracao_canonica = ""
    if fracao:
        digitos = fracao[1:].rstrip("0")
        if digitos:
            fracao_canonica = "." + digitos
    return base + fracao_canonica + "Z"


def _validar_valores_json(valor: Any, caminho: str = "metadata") -> None:
    if valor is None or type(valor) in {bool, int}:
        return
    if type(valor) is str:
        try:
            valor.encode("utf-8", errors="strict")
        except UnicodeEncodeError as exc:
            raise DocumentFormatError(f"Texto fora de UTF-8 válido em {caminho}.") from exc
        return
    if type(valor) is float:
        if not math.isfinite(valor):
            raise DocumentFormatError(f"Valor numerico nao finito em {caminho}.")
        return
    if type(valor) is list:
        for indice, item in enumerate(valor):
            _validar_valores_json(item, f"{caminho}[{indice}]")
        return
    if type(valor) is dict:
        for chave, item in valor.items():
            if type(chave) is not str:
                raise DocumentFormatError(f"Chave não textual em {caminho}.")
            try:
                chave.encode("utf-8", errors="strict")
            except UnicodeEncodeError as exc:
                raise DocumentFormatError(f"Chave fora de UTF-8 válido em {caminho}.") from exc
            _validar_valores_json(item, f"{caminho}.{chave}")
        return
    raise DocumentFormatError(f"Valor fora do modelo JSON em {caminho}.")


def _sem_quebra_final(linha: str) -> str:
    if linha.endswith("\n"):
        linha = linha[:-1]
    if linha.endswith("\r"):
        linha = linha[:-1]
    return linha
