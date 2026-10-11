"""Recuperação somente leitura do histórico documental v1 do RickCraft."""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import stat
from typing import Any, Callable, Mapping

from analysis_lifecycle import AnalysisIdInvalidError, validar_analysis_id
from document_catalog import (
    DOCUMENT_TYPES,
    DocumentIdInvalidError,
    DocumentTypeInvalidError,
    validar_document_id,
)
from document_format import DocumentFormatError, DocumentoMarkdown, parsear_documento
from provenance import (
    KIND_LOCAL_FILE,
    KIND_VERSIONED_SOURCE,
    KIND_WORKSPACE_DOCUMENT,
    ProvenanceError,
    verificar_arquivo_local,
    verificar_documento_workspace,
    verificar_fonte_versionada,
)
from workspace_probe import AvaliadorWorkspace
from rickcraft_root import RickCraftRootError
from workspace_resolver import (
    RaizWorkspaceSelecionada,
    ResultadoDesconhecidoError,
    TipoRaizWorkspace,
    derivar_caminhos_workspace,
    resolver_workspace,
)


class DocumentRecoveryError(RuntimeError):
    """Erro de entrada ou de recuperação documental."""


class AnalysisRecoveryNotFoundError(DocumentRecoveryError):
    """A análise solicitada não está entre as raízes que puderam ser lidas."""


class DocumentRecoveryNotFoundError(DocumentRecoveryError):
    """O documento solicitado não foi encontrado nas raízes legíveis."""


class DocumentIdentityDivergenceError(DocumentRecoveryError):
    """O mesmo document_id possui conteúdos diferentes; uso bloqueado."""

    def __init__(self, divergence: "DocumentDivergence") -> None:
        self.divergence = divergence
        super().__init__(
            f"DIVERGENCE_DOCUMENT_ID: {divergence.document_id} possui conteúdo divergente."
        )


class RecoveryInputError(DocumentRecoveryError):
    """Uma identidade de recuperação não atende ao contrato estrito."""


@dataclass(frozen=True)
class RecoveryFinding:
    code: str
    message: str
    path: str | None = None
    document_id: str | None = None
    analysis_id: str | None = None
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class RootReadStatus:
    kind: str
    path: Path
    status: str
    detail: str | None = None


@dataclass(frozen=True)
class DocumentLocation:
    path: Path
    workspace_root_kind: str
    sha256: str


@dataclass(frozen=True)
class RecoveredRelation:
    relation_type: str
    document_id: str
    analysis_id: str | None
    resolved: bool


@dataclass(frozen=True)
class RecoveredInput:
    document_id: str
    index: int
    verification: Mapping[str, Any]


@dataclass(frozen=True)
class RecoveredDocument:
    document_id: str
    analysis_id: str
    document_type: str
    created_at_utc: str
    sha256: str
    parsed: DocumentoMarkdown
    locations: tuple[DocumentLocation, ...]
    relations: tuple[RecoveredRelation, ...]
    input_verifications: tuple[RecoveredInput, ...]


@dataclass(frozen=True)
class DocumentDivergence:
    document_id: str
    locations: tuple[DocumentLocation, ...]
    hashes: tuple[str, ...]
    analysis_ids: tuple[str, ...]


@dataclass(frozen=True)
class RecoveryResult:
    documents: tuple[RecoveredDocument, ...]
    findings: tuple[RecoveryFinding, ...]
    divergences: tuple[DocumentDivergence, ...]
    roots: tuple[RootReadStatus, ...]
    selected_root_kind: str
    probe_evidence: tuple[Any, ...]

    def document(self, document_id: str) -> RecoveredDocument:
        try:
            validar_document_id(document_id)
        except DocumentIdInvalidError as exc:
            raise RecoveryInputError(str(exc)) from exc
        for item in self.documents:
            if item.document_id == document_id:
                return item
        for item in self.divergences:
            if item.document_id == document_id:
                raise DocumentIdentityDivergenceError(item)
        raise DocumentRecoveryNotFoundError(
            f"O documento {document_id} não foi encontrado nas raízes legíveis."
        )


@dataclass(frozen=True)
class _Root:
    path: Path
    kind: str
    active: bool
    inspect: bool = True


@dataclass(frozen=True)
class _Candidate:
    parsed: DocumentoMarkdown
    data: bytes
    path: Path
    root_kind: str
    digest: str


Resolver = Callable[[str | Path, Callable[[Path], object]], RaizWorkspaceSelecionada]
EvaluatorFactory = Callable[[], Callable[[Path], object]]


def recuperar_analise(
    rickcraft_root: str | Path,
    analysis_id: str,
    *,
    resolver: Resolver | None = None,
    avaliador_factory: EvaluatorFactory | None = None,
    observacoes_atuais: Mapping[str, Mapping[str, Any]] | None = None,
) -> RecoveryResult:
    """Recupera uma análise e suas relações das raízes permitidas, sem escrita."""
    identificador = _validar_analysis_id(analysis_id)
    estado = _iniciar_operacao(rickcraft_root, resolver, avaliador_factory)
    resultado = _recuperar_todas(estado, observacoes_atuais or {})
    documentos = tuple(
        documento
        for documento in resultado.documents
        if documento.analysis_id == identificador
    )
    if not documentos and not any(
        identificador in divergencia.analysis_ids
        for divergencia in resultado.divergences
    ):
        analisada = any(
            root.status == "READ"
            and _analysis_directory_present(root.path, identificador)
            for root in resultado.roots
        )
        if not analisada:
            raise AnalysisRecoveryNotFoundError(
                f"A análise {identificador} não foi encontrada nas raízes legíveis."
            )
    return RecoveryResult(
        documents=documentos,
        findings=resultado.findings,
        divergences=resultado.divergences,
        roots=resultado.roots,
        selected_root_kind=resultado.selected_root_kind,
        probe_evidence=resultado.probe_evidence,
    )


def retomar_analise(
    rickcraft_root: str | Path,
    resume_analysis_id: str,
    **kwargs: Any,
) -> RecoveryResult:
    """Retoma somente a identidade explícita, sem gerar ou criar IDs."""
    return recuperar_analise(rickcraft_root, resume_analysis_id, **kwargs)


def recuperar_documento(
    rickcraft_root: str | Path,
    document_id: str,
    *,
    resolver: Resolver | None = None,
    avaliador_factory: EvaluatorFactory | None = None,
    observacoes_atuais: Mapping[str, Mapping[str, Any]] | None = None,
) -> RecoveredDocument:
    """Localiza um DOC-UUIDv4 exato na união somente leitura permitida."""
    try:
        validar_document_id(document_id)
    except DocumentIdInvalidError as exc:
        raise RecoveryInputError(str(exc)) from exc
    estado = _iniciar_operacao(rickcraft_root, resolver, avaliador_factory)
    resultado = _recuperar_todas(estado, observacoes_atuais or {})
    return resultado.document(document_id)


def recuperar_documentos(
    rickcraft_root: str | Path,
    *,
    resolver: Resolver | None = None,
    avaliador_factory: EvaluatorFactory | None = None,
    observacoes_atuais: Mapping[str, Mapping[str, Any]] | None = None,
) -> RecoveryResult:
    """Reconstrói a união determinística dos documentos legíveis v1."""
    estado = _iniciar_operacao(rickcraft_root, resolver, avaliador_factory)
    return _recuperar_todas(estado, observacoes_atuais or {})


def _iniciar_operacao(
    rickcraft_root: str | Path,
    resolver: Resolver | None,
    avaliador_factory: EvaluatorFactory | None,
) -> tuple[RaizWorkspaceSelecionada, tuple[Any, ...], tuple[_Root, ...]]:
    avaliador = (avaliador_factory or AvaliadorWorkspace)()
    workspace = (resolver or resolver_workspace)(rickcraft_root, avaliador)
    try:
        paths = derivar_caminhos_workspace(rickcraft_root)
    except (RickCraftRootError, TypeError, ValueError) as exc:
        raise DocumentRecoveryError("RickCraftRoot não pôde ser validado.") from exc

    selected_kind = workspace.tipo.value
    if workspace.caminho == paths.preferencial and selected_kind == "preferred":
        roots = (
            _Root(paths.preferencial, "preferred", True),
            _Root(paths.fallback, "fallback", False),
        )
    elif workspace.caminho == paths.fallback and selected_kind == "fallback":
        roots = (
            _Root(paths.preferencial, "preferred", False, False),
            _Root(paths.fallback, "fallback", True),
        )
    else:
        raise DocumentRecoveryError(
            "O resolvedor retornou uma raiz diferente das duas localizações permitidas."
        )
    evidence = tuple(getattr(avaliador, "evidencias", ()))
    return workspace, evidence, roots


def _recuperar_todas(
    estado: tuple[RaizWorkspaceSelecionada, tuple[Any, ...], tuple[_Root, ...]],
    observacoes_atuais: Mapping[str, Mapping[str, Any]],
) -> RecoveryResult:
    workspace, evidence, roots = estado
    root_status: list[RootReadStatus] = []
    findings: list[RecoveryFinding] = []
    candidates: list[_Candidate] = []

    for root in roots:
        if not root.inspect:
            detail = _probe_failure_detail(evidence, root.path)
            root_status.append(
                RootReadStatus(
                    root.kind,
                    root.path,
                    "NOT_READ_UNAVAILABLE",
                    detail or "A sonda atual não selecionou esta raiz; nenhum histórico foi lido nela.",
                )
            )
            findings.append(
                RecoveryFinding(
                    "ROOT_NOT_READ",
                    "A raiz preferencial está indisponível na resolução atual; seu histórico não foi examinado.",
                    str(root.path),
                    details=((detail,) if detail else ()),
                )
            )
            continue
        if not root.active and not _lexists(root.path):
            root_status.append(RootReadStatus(root.kind, root.path, "MISSING"))
            continue
        try:
            _validar_diretorio(root.path, parent=None, base=None)
        except (OSError, DocumentRecoveryError) as exc:
            status = "INACCESSIBLE" if not root.active else "INVALID_ROOT"
            root_status.append(RootReadStatus(root.kind, root.path, status, str(exc)))
            findings.append(
                RecoveryFinding(
                    "ROOT_UNAVAILABLE" if not root.active else "INVALID_ROOT",
                    "A raiz histórica não foi lida." if not root.active else "A raiz selecionada não é segura para leitura.",
                    str(root.path),
                    details=(str(exc),),
                )
            )
            if root.active:
                raise DocumentRecoveryError(
                    "A raiz atualmente selecionada não pode ser lida com segurança."
                ) from exc
            continue
        scanned = _coletar_raiz(root, candidates, findings)
        root_status.append(
            RootReadStatus(
                root.kind,
                root.path,
                "READ" if scanned else "INACCESSIBLE",
                None if scanned else "A raiz não pôde ser enumerada por completo.",
            )
        )

    agrupados: dict[str, list[_Candidate]] = defaultdict(list)
    for candidate in candidates:
        metadata = candidate.parsed.metadata
        agrupados[metadata["document_id"]].append(candidate)

    divergences: list[DocumentDivergence] = []
    consolidados: dict[str, tuple[_Candidate, tuple[DocumentLocation, ...]]] = {}
    for document_id, itens in agrupados.items():
        hashes = sorted({item.digest for item in itens})
        locations = tuple(
            sorted(
                (DocumentLocation(item.path, item.root_kind, item.digest) for item in itens),
                key=lambda location: (location.workspace_root_kind, str(location.path)),
            )
        )
        if len(hashes) != 1:
            analysis_ids = tuple(
                sorted({item.parsed.metadata["analysis_id"] for item in itens})
            )
            divergences.append(
                DocumentDivergence(document_id, locations, tuple(hashes), analysis_ids)
            )
            findings.append(
                RecoveryFinding(
                    "DIVERGENCE_DOCUMENT_ID",
                    "O mesmo document_id possui bytes diferentes; seu uso está bloqueado.",
                    document_id=document_id,
                    details=tuple(
                        f"{location.workspace_root_kind}:{location.path} sha256={location.sha256}"
                        for location in locations
                    ),
                )
            )
            continue
        consolidados[document_id] = (itens[0], locations)

    relation_map: dict[str, tuple[RecoveredRelation, ...]] = {}
    for document_id, (candidate, _locations) in consolidados.items():
        relation_map[document_id] = _resolver_relacoes(
            candidate.parsed.metadata, consolidados, findings
        )

    _detectar_ciclos(relation_map, findings)
    documentos: list[RecoveredDocument] = []
    for document_id, (candidate, locations) in consolidados.items():
        metadata = candidate.parsed.metadata
        documentos.append(
            RecoveredDocument(
                document_id=document_id,
                analysis_id=metadata["analysis_id"],
                document_type=metadata["document_type"],
                created_at_utc=metadata["created_at_utc"],
                sha256=candidate.digest,
                parsed=candidate.parsed,
                locations=locations,
                relations=relation_map[document_id],
                input_verifications=_verificar_inputs(
                    document_id,
                    metadata.get("inputs", []),
                    consolidados,
                    {item.document_id for item in divergences},
                    observacoes_atuais,
                    findings,
                ),
            )
        )
    documentos.sort(key=_ordem_documento)
    divergences.sort(key=lambda item: item.document_id)
    return RecoveryResult(
        tuple(documentos),
        tuple(findings),
        tuple(divergences),
        tuple(root_status),
        workspace.tipo.value,
        evidence,
    )


def _coletar_raiz(
    root: _Root,
    candidates: list[_Candidate],
    findings: list[RecoveryFinding],
) -> bool:
    try:
        analysis_dirs = sorted(root.path.iterdir(), key=lambda path: path.name)
    except OSError as exc:
        findings.append(
            RecoveryFinding("ROOT_UNAVAILABLE", "A raiz não pôde ser enumerada.", str(root.path), details=(repr(exc),))
        )
        return False

    for analysis_path in analysis_dirs:
        if not analysis_path.name.startswith("ANL-"):
            continue
        try:
            analysis_id = validar_analysis_id(analysis_path.name)
        except AnalysisIdInvalidError:
            if analysis_path.suffix.lower() == ".md":
                findings.append(
                    RecoveryFinding("INVALID_DOCUMENT", "Nome de análise inválido.", str(analysis_path))
                )
            continue
        try:
            _validar_diretorio(analysis_path, parent=root.path, base=root.path)
        except (OSError, DocumentRecoveryError) as exc:
            findings.append(
                RecoveryFinding(
                    "INVALID_ANALYSIS_DIRECTORY",
                    "O diretório da análise foi ignorado por não ser um filho real e seguro da raiz.",
                    str(analysis_path),
                    analysis_id=analysis_id,
                    details=(str(exc),),
                )
            )
            continue
        try:
            type_dirs = sorted(analysis_path.iterdir(), key=lambda path: path.name)
        except OSError as exc:
            findings.append(
                RecoveryFinding(
                    "ANALYSIS_UNAVAILABLE",
                    "O diretório da análise não pôde ser enumerado.",
                    str(analysis_path),
                    analysis_id=analysis_id,
                    details=(repr(exc),),
                )
            )
            continue
        for type_path in type_dirs:
            if type_path.name not in DOCUMENT_TYPES:
                continue
            try:
                _validar_diretorio(type_path, parent=analysis_path, base=root.path)
            except (OSError, DocumentRecoveryError) as exc:
                findings.append(
                    RecoveryFinding(
                        "INVALID_TYPE_DIRECTORY",
                        "A pasta de tipo foi ignorada por redirecionamento ou falta de contenção.",
                        str(type_path),
                        analysis_id=analysis_id,
                        details=(str(exc),),
                    )
                )
                continue
            try:
                files = sorted(type_path.iterdir(), key=lambda path: path.name)
            except OSError as exc:
                findings.append(
                    RecoveryFinding(
                        "TYPE_DIRECTORY_UNAVAILABLE",
                        "A pasta de tipo não pôde ser enumerada.",
                        str(type_path),
                        analysis_id=analysis_id,
                        details=(repr(exc),),
                    )
                )
                continue
            for path in files:
                if path.suffix != ".md":
                    continue
                try:
                    document_id = validar_document_id(path.stem)
                except DocumentIdInvalidError as exc:
                    findings.append(
                        RecoveryFinding(
                            "INVALID_DOCUMENT",
                            "Arquivo Markdown ignorado: filename não é DOC-UUIDv4 canônico.",
                            str(path),
                            analysis_id=analysis_id,
                            details=(str(exc),),
                        )
                    )
                    continue
                try:
                    _validar_arquivo(path, parent=type_path, base=root.path)
                    data = path.read_bytes()
                    parsed = parsear_documento(data)
                    metadata = parsed.metadata
                    if (
                        metadata["analysis_id"] != analysis_id
                        or metadata["document_id"] != document_id
                        or metadata["document_type"] != type_path.name
                    ):
                        raise DocumentFormatError(
                            "Metadados não correspondem ao caminho e ao filename recuperados."
                        )
                except (OSError, DocumentFormatError, DocumentRecoveryError) as exc:
                    findings.append(
                        RecoveryFinding(
                            "INVALID_DOCUMENT",
                            "Documento não pôde ser validado e não será usado como evidência.",
                            str(path),
                            document_id=document_id,
                            analysis_id=analysis_id,
                            details=(f"{type(exc).__name__}: {exc}",),
                        )
                    )
                    continue
                candidates.append(
                    _Candidate(parsed, data, path, root.kind, hashlib.sha256(data).hexdigest())
                )
    return True


def _resolver_relacoes(
    metadata: Mapping[str, Any],
    documentos: Mapping[str, tuple[_Candidate, tuple[DocumentLocation, ...]]],
    findings: list[RecoveryFinding],
) -> tuple[RecoveredRelation, ...]:
    source_id = metadata["document_id"]
    source_analysis = metadata["analysis_id"]
    result: list[RecoveredRelation] = []
    for relation in metadata["relations"]:
        target_id = relation["document_id"]
        target = documentos.get(target_id)
        expected_analysis = relation.get("analysis_id")
        if target is None:
            findings.append(
                RecoveryFinding(
                    "BROKEN_RELATION",
                    "A relação aponta para documento ausente ou divergente.",
                    document_id=source_id,
                    details=(f"{relation['relation_type']} -> {target_id}",),
                )
            )
            result.append(
                RecoveredRelation(relation["relation_type"], target_id, expected_analysis, False)
            )
            continue
        actual_analysis = target[0].parsed.metadata["analysis_id"]
        if expected_analysis is None and actual_analysis != source_analysis:
            findings.append(
                RecoveryFinding(
                    "INCONSISTENT_RELATION",
                    "Relação entre análises exige analysis_id explícito.",
                    document_id=source_id,
                    analysis_id=actual_analysis,
                    details=(
                        f"fonte={source_id}; analysis_id_fonte={source_analysis}; "
                        f"alvo={target_id}; analysis_id_real_alvo={actual_analysis}; "
                        "analysis_id_declarado=ausente; relação entre análises exige analysis_id explícito",
                    ),
                )
            )
            result.append(
                RecoveredRelation(relation["relation_type"], target_id, None, False)
            )
            continue
        if expected_analysis is not None and expected_analysis != actual_analysis:
            findings.append(
                RecoveryFinding(
                    "INCONSISTENT_RELATION",
                    "analysis_id da relação não corresponde ao documento alvo.",
                    document_id=source_id,
                    analysis_id=actual_analysis,
                    details=(f"declarado={expected_analysis}; real={actual_analysis}; alvo={target_id}",),
                )
            )
            result.append(
                RecoveredRelation(relation["relation_type"], target_id, expected_analysis, False)
            )
            continue
        result.append(
            RecoveredRelation(relation["relation_type"], target_id, expected_analysis, True)
        )
    return tuple(result)


def _detectar_ciclos(
    relations: Mapping[str, tuple[RecoveredRelation, ...]],
    findings: list[RecoveryFinding],
) -> None:
    concluido: set[str] = set()
    pilha: list[str] = []
    posicoes: dict[str, int] = {}
    ciclos: set[tuple[str, ...]] = set()

    def visitar(document_id: str) -> None:
        if document_id in concluido:
            return
        if document_id in posicoes:
            ciclo = tuple(sorted(pilha[posicoes[document_id] :]))
            if ciclo and ciclo not in ciclos:
                ciclos.add(ciclo)
                findings.append(
                    RecoveryFinding(
                        "RELATION_CYCLE",
                        "Ciclo entre relações recuperadas; os documentos foram mantidos sem recursão.",
                        document_id=document_id,
                        details=ciclo,
                    )
                )
            return
        posicoes[document_id] = len(pilha)
        pilha.append(document_id)
        for relation in relations.get(document_id, ()):
            if relation.resolved and relation.document_id in relations:
                visitar(relation.document_id)
        pilha.pop()
        posicoes.pop(document_id, None)
        concluido.add(document_id)

    for identifier in sorted(relations):
        visitar(identifier)


def _verificar_inputs(
    document_id: str,
    inputs: object,
    documentos: Mapping[str, tuple[_Candidate, tuple[DocumentLocation, ...]]],
    divergent_ids: set[str],
    observacoes_atuais: Mapping[str, Mapping[str, Any]],
    findings: list[RecoveryFinding],
) -> tuple[RecoveredInput, ...]:
    result: list[RecoveredInput] = []
    if type(inputs) is not list:
        return ()
    for index, historical in enumerate(inputs):
        if not isinstance(historical, Mapping):
            continue
        kind = historical.get("kind")
        locator = historical.get("locator")
        current = observacoes_atuais.get(str(locator), {})
        try:
            if kind == KIND_LOCAL_FILE:
                verification = verificar_arquivo_local(historical, locator)
            elif kind == KIND_WORKSPACE_DOCUMENT:
                try:
                    target_id = validar_document_id(locator)
                except (DocumentIdInvalidError, TypeError):
                    verification = _verification_without_read(
                        kind, locator, historical, "UNVERIFIABLE", "O locator histórico não é document_id verificável."
                    )
                else:
                    alvo = documentos.get(target_id)
                    if alvo is None:
                        divergente = target_id in divergent_ids
                        reason = (
                            "O documento de entrada possui identidade divergente."
                            if divergente
                            else "O documento de entrada está ausente ou indisponível nas raízes legíveis."
                        )
                        verification = _verification_without_read(
                            kind,
                            target_id,
                            historical,
                            "UNVERIFIABLE" if divergente else "UNAVAILABLE",
                            reason,
                        )
                    else:
                        verification = verificar_documento_workspace(
                            historical, target_id, alvo[0].data
                        )
            elif kind == KIND_VERSIONED_SOURCE:
                verification = verificar_fonte_versionada(
                    historical,
                    locator,
                    version_kind=current.get("version_kind"),
                    version=current.get("version"),
                    conteudo=current.get("bytes"),
                )
            else:
                verification = _verification_without_read(
                    str(kind), locator, historical, "UNVERIFIABLE", "kind de provenance não reconhecido."
                )
        except (ProvenanceError, TypeError, ValueError) as exc:
            verification = _verification_without_read(
                str(kind), locator, historical, "UNVERIFIABLE", f"Referência de entrada inválida ({type(exc).__name__})."
            )
            findings.append(
                RecoveryFinding(
                    "INPUT_UNVERIFIABLE",
                    "A entrada histórica não pôde ser revalidada.",
                    document_id=document_id,
                    details=(f"índice={index}; {exc}",),
                )
            )
        result.append(RecoveredInput(document_id, index, deepcopy(verification)))
    return tuple(result)


def _verification_without_read(
    kind: object,
    locator: object,
    historical: Mapping[str, Any],
    state: str,
    reason: str,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
    record: dict[str, Any] = {
        "kind": kind,
        "locator": locator,
        "observed_at_utc": now,
        "verification": state,
        "reason": reason,
        "historical": deepcopy(dict(historical)),
    }
    return record


def _validar_analysis_id(value: object) -> str:
    try:
        return validar_analysis_id(value)
    except (AnalysisIdInvalidError, TypeError) as exc:
        raise RecoveryInputError(str(exc)) from exc


def _validar_diretorio(path: Path, *, parent: Path | None, base: Path | None) -> None:
    info = path.lstat()
    if _is_redirect(path, info) or not stat.S_ISDIR(info.st_mode):
        raise DocumentRecoveryError(f"Diretório inválido ou redirecionado: {path}")
    physical = path.resolve(strict=True)
    if parent is not None:
        expected_parent = parent.resolve(strict=True)
        if path.parent != parent or physical.parent != expected_parent:
            raise DocumentRecoveryError(f"Diretório não é filho físico direto esperado: {path}")
    if base is not None:
        physical_base = base.resolve(strict=True)
        if not physical.is_relative_to(physical_base):
            raise DocumentRecoveryError(f"Diretório escapa da raiz permitida: {path}")


def _validar_arquivo(path: Path, *, parent: Path, base: Path) -> None:
    info = path.lstat()
    if _is_redirect(path, info) or not stat.S_ISREG(info.st_mode):
        raise DocumentRecoveryError(f"Arquivo não regular ou redirecionado: {path}")
    physical = path.resolve(strict=True)
    expected_parent = parent.resolve(strict=True)
    physical_base = base.resolve(strict=True)
    if path.parent != parent or physical.parent != expected_parent:
        raise DocumentRecoveryError(f"Arquivo não é filho físico direto da pasta de tipo: {path}")
    if not physical.is_relative_to(physical_base):
        raise DocumentRecoveryError(f"Arquivo escapa da raiz permitida: {path}")


def _is_redirect(path: Path, info: Any) -> bool:
    if stat.S_ISLNK(info.st_mode):
        return True
    is_junction = getattr(path, "is_junction", None)
    if callable(is_junction) and is_junction():
        return True
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(flag and getattr(info, "st_file_attributes", 0) & flag)


def _lexists(path: Path) -> bool:
    try:
        path.lstat()
        return True
    except FileNotFoundError:
        return False
    except OSError:
        return True


def _analysis_directory_present(root: Path, analysis_id: str) -> bool:
    path = root / analysis_id
    try:
        _validar_diretorio(path, parent=root, base=root)
    except (OSError, DocumentRecoveryError):
        return False
    return True


def _probe_failure_detail(evidence: tuple[Any, ...], root: Path) -> str | None:
    for item in evidence:
        if getattr(item, "raiz", None) == root:
            resultado = getattr(getattr(item, "resultado", None), "value", None)
            causa = getattr(item, "causa", None)
            operacao = getattr(item, "operacao_falha", None)
            parts = [part for part in (resultado, operacao, causa) if part]
            return "; ".join(parts) if parts else "A sonda não classificou esta raiz como utilizável."
    return None


def _ordem_documento(document: RecoveredDocument) -> tuple[datetime, str]:
    timestamp = datetime.fromisoformat(document.created_at_utc.replace("Z", "+00:00"))
    return timestamp.astimezone(timezone.utc), document.document_id
