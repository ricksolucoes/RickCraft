"""Registro operacional de lacunas e autoridade, sem motor de workflow."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from analysis_lifecycle import AnalysisLifecycleError, validar_analysis_id
from document_publisher import PublicationResult, publicar_documento


class GapHandlingError(ValueError):
    """Entrada operacional incompleta, inválida ou não autorizada."""


@dataclass(frozen=True)
class SourceReference:
    """Referência fornecida pelo chamador para uma observação ou autoridade."""

    category: str
    reference: str
    statement: str
    authority: str | None = None


@dataclass(frozen=True)
class DivergenceCase:
    occurrence: str
    references: tuple[SourceReference, ...]
    affected_scope: str
    impact: str
    unresolved_reason: str
    resume_condition: str
    required_authority: str | None = None
    required_information: str | None = None
    required_evidence: str | None = None


@dataclass(frozen=True)
class BlockerCase:
    affected_scope: str
    cause: str
    dependency: str
    resume_condition: str
    required_authority: str | None = None
    required_information: str | None = None
    required_evidence: str | None = None


@dataclass(frozen=True)
class ExistingDecisionCase:
    decision: str
    decision_owner: str
    owner_authority_reference: str
    source_reference: str
    scope: str
    justification: str
    explicitly_existing: bool


@dataclass(frozen=True)
class OperationalResultCase:
    operation: str
    outcome: str
    evidence_references: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    blocked_scopes: tuple[str, ...] = ()
    scope_requests: tuple[ScopeRequest, ...] = ()


@dataclass(frozen=True)
class ScopeRequest:
    """Fatos de autorização e dependência fornecidos pelo chamador."""

    scope: str
    depends_on: tuple[str, ...] = ()
    explicitly_authorized: bool = False
    information_sufficient: bool = False
    evidence_sufficient: bool = False
    authority_sufficient: bool = False
    conflict_free: bool = False


@dataclass(frozen=True)
class ScopeContinuity:
    scope: str
    continuable: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ContinuityAssessment:
    affected_scopes: tuple[str, ...]
    scopes: tuple[ScopeContinuity, ...]

    @property
    def continuable_scopes(self) -> tuple[str, ...]:
        return tuple(item.scope for item in self.scopes if item.continuable)


@dataclass(frozen=True)
class ConflictAssessment:
    divergence: DivergenceCase
    authoritative_reference: str | None
    blocker_required: bool
    required_authority: str | None


@dataclass(frozen=True)
class PersistedOperationalRecord:
    document_type: str
    publication: PublicationResult
    record: object

    @property
    def persisted_document_id(self) -> str:
        return self.publication.document_id


Clock = Callable[[], datetime]

_CATEGORIES = {"normative", "workspace", "evidence", "operational"}
_INVALID_RESULT_CLAIMS = re.compile(
    r"(?<!\w)(?:ANALYZE(?:\s+|[:=\-–]\s*)(?:[:=\-–]\s*)?PASS|"
    r"CONVERGED|CONVERGE(?:\s+|[:=\-–]\s*)(?:[:=\-–]\s*)?CONVERGED)(?!\w)",
    re.IGNORECASE,
)


def avaliar_conflito_fontes(
    source_a: SourceReference,
    source_b: SourceReference,
    *,
    affected_scope: str,
    impact: str,
    resume_condition: str,
    materially_incompatible: bool,
    required_authority: str | None = None,
) -> ConflictAssessment | None:
    """Classifica conflito informado; não interpreta textos nem ranqueia fontes."""
    _validate_source(source_a, "source_a")
    _validate_source(source_b, "source_b")
    _require_text(affected_scope, "affected_scope")
    _require_text(impact, "impact")
    _require_text(resume_condition, "resume_condition")
    if required_authority is not None:
        _require_text(required_authority, "required_authority")
    if type(materially_incompatible) is not bool:
        raise GapHandlingError("materially_incompatible deve ser booleano explícito.")
    if not materially_incompatible:
        return None

    normative = [item for item in (source_a, source_b) if item.category == "normative"]
    workspace = [item for item in (source_a, source_b) if item.category == "workspace"]
    authoritative_reference = None
    blocker_required = False
    authority_needed = required_authority
    if len(normative) == 1 and len(workspace) == 1:
        authoritative_reference = normative[0].reference
    elif len(normative) == 2:
        blocker_required = True
    else:
        blocker_required = True

    if authoritative_reference is not None:
        reason = (
            "A referência normativa fornecida continua aplicável; o workspace é evidência operacional e não a substitui. "
            "Esta avaliação não altera a fonte normativa nem o estado do SDD."
        )
    elif len(normative) == 2:
        reason = (
            "As fontes normativas foram informadas como materialmente incompatíveis. "
            "Não foi fornecida precedência normativa formal; nenhuma vencedora é escolhida e a parte afetada permanece bloqueada."
        )
    else:
        reason = (
            "As fontes foram informadas como materialmente incompatíveis; não há autoridade fornecida para escolher uma vencedora."
        )

    required_information = None
    if len(normative) == 2 and authority_needed is None:
        required_information = "identificar a autoridade competente para resolver o conflito normativo"
    case = DivergenceCase(
        occurrence="Conflito material entre as referências fornecidas.",
        references=(source_a, source_b),
        affected_scope=affected_scope,
        impact=impact,
        unresolved_reason=reason,
        resume_condition=resume_condition,
        required_authority=authority_needed,
        required_information=required_information,
    )
    return ConflictAssessment(case, authoritative_reference, blocker_required, authority_needed)


def avaliar_continuidade_localizada(
    affected_scopes: Sequence[str],
    requests: Sequence[ScopeRequest],
) -> ContinuityAssessment:
    """Marca apenas escopos independentes e explicitamente aptos como continuáveis."""
    if isinstance(affected_scopes, (str, bytes)) or not isinstance(affected_scopes, Sequence):
        raise GapHandlingError("affected_scopes deve ser uma sequência explícita de escopos.")
    if isinstance(requests, (str, bytes)) or not isinstance(requests, Sequence):
        raise GapHandlingError("requests deve ser uma sequência de ScopeRequest.")
    affected = tuple(_require_text(scope, "affected_scope") for scope in affected_scopes)
    if not affected:
        raise GapHandlingError("Ao menos um affected_scope deve ser informado.")
    validated: list[ScopeRequest] = []
    seen: set[str] = set()
    for request in requests:
        if not isinstance(request, ScopeRequest):
            raise GapHandlingError("requests deve conter somente ScopeRequest.")
        scope = _require_text(request.scope, "scope")
        if scope in seen:
            raise GapHandlingError("Cada scope deve aparecer uma única vez.")
        seen.add(scope)
        if not isinstance(request.depends_on, tuple):
            raise GapHandlingError("depends_on deve ser uma tupla explícita de escopos.")
        dependencies = tuple(_require_text(dep, "depends_on") for dep in request.depends_on)
        validated.append(ScopeRequest(
            scope=scope,
            depends_on=dependencies,
            explicitly_authorized=_explicit_bool(request.explicitly_authorized, "explicitly_authorized"),
            information_sufficient=_explicit_bool(request.information_sufficient, "information_sufficient"),
            evidence_sufficient=_explicit_bool(request.evidence_sufficient, "evidence_sufficient"),
            authority_sufficient=_explicit_bool(request.authority_sufficient, "authority_sufficient"),
            conflict_free=_explicit_bool(request.conflict_free, "conflict_free"),
        ))

    local_reasons: dict[str, list[str]] = {}
    for request in validated:
        reasons: list[str] = []
        if request.scope in affected:
            reasons.append("escopo diretamente afetado pela lacuna")
        for dependency in sorted(set(request.depends_on)):
            if dependency not in affected and dependency not in seen:
                reasons.append(f"depende de escopo não avaliado: {dependency}")
        if not request.explicitly_authorized:
            reasons.append("não há autorização explícita para este escopo")
        if not request.information_sufficient:
            reasons.append("informação necessária insuficiente")
        if not request.evidence_sufficient:
            reasons.append("evidência necessária insuficiente")
        if not request.authority_sufficient:
            reasons.append("autoridade necessária insuficiente")
        if not request.conflict_free:
            reasons.append("há conflito material não resolvido")

        local_reasons[request.scope] = reasons

    blocked = set(affected)
    blocked.update(scope for scope, reasons in local_reasons.items() if reasons)
    propagated: dict[str, set[str]] = {request.scope: set() for request in validated}
    changed = True
    while changed:
        changed = False
        for request in validated:
            if request.scope in blocked:
                continue
            blocked_dependencies = sorted(
                dependency for dependency in set(request.depends_on)
                if dependency in blocked
            )
            if blocked_dependencies:
                blocked.add(request.scope)
                propagated[request.scope].update(blocked_dependencies)
                changed = True

    results: list[ScopeContinuity] = []
    for request in validated:
        reasons = list(local_reasons[request.scope])
        if propagated[request.scope]:
            reasons.append(
                "depende de escopo bloqueado: "
                + ", ".join(sorted(propagated[request.scope]))
            )
        results.append(ScopeContinuity(request.scope, not reasons, tuple(reasons)))
    return ContinuityAssessment(affected, tuple(results))


def registrar_divergencia(
    rickcraft_root: str | Path,
    analysis_id: str,
    case: DivergenceCase,
    *,
    purpose: str,
    origin_reference: str = "SPEC-0000000001 TASK-011",
    inputs: Sequence[Mapping[str, Any]] = (),
    relations: Sequence[Mapping[str, Any]] = (),
    clock: Clock | None = None,
    resolver: Any = None,
    avaliador_factory: Any = None,
) -> PersistedOperationalRecord:
    _validate_divergence(case)
    body = _body("Divergência operacional", (
        ("Ocorrência", case.occurrence),
        ("Referências envolvidas", tuple(case.references)),
        ("Escopo afetado", case.affected_scope),
        ("Impacto", case.impact),
        ("Razão para não resolver silenciosamente", case.unresolved_reason),
        ("Autoridade necessária", case.required_authority),
        ("Informação necessária", case.required_information),
        ("Evidência necessária", case.required_evidence),
        ("Condição de retomada", case.resume_condition),
    ))
    return _publish(
        rickcraft_root, analysis_id, "divergence", purpose, origin_reference, body, case,
        inputs, relations, clock, resolver, avaliador_factory,
    )


def registrar_blocker(
    rickcraft_root: str | Path,
    analysis_id: str,
    case: BlockerCase,
    *,
    purpose: str,
    origin_reference: str = "SPEC-0000000001 TASK-011",
    inputs: Sequence[Mapping[str, Any]] = (),
    relations: Sequence[Mapping[str, Any]] = (),
    clock: Clock | None = None,
    resolver: Any = None,
    avaliador_factory: Any = None,
) -> PersistedOperationalRecord:
    _validate_blocker(case)
    body = _body("Bloqueio operacional", (
        ("Parte afetada", case.affected_scope),
        ("Causa verificável", case.cause),
        ("Dependência", case.dependency),
        ("Autoridade necessária", case.required_authority),
        ("Informação necessária", case.required_information),
        ("Evidência necessária", case.required_evidence),
        ("Condição objetiva de retomada", case.resume_condition),
    ))
    return _publish(
        rickcraft_root, analysis_id, "blocker", purpose, origin_reference, body, case,
        inputs, relations, clock, resolver, avaliador_factory,
    )


def registrar_decisao_existente(
    rickcraft_root: str | Path,
    analysis_id: str,
    case: ExistingDecisionCase,
    *,
    purpose: str,
    origin_reference: str = "SPEC-0000000001 TASK-011",
    inputs: Sequence[Mapping[str, Any]] = (),
    relations: Sequence[Mapping[str, Any]] = (),
    clock: Clock | None = None,
    resolver: Any = None,
    avaliador_factory: Any = None,
) -> PersistedOperationalRecord:
    _validate_decision(case)
    body = _body("Decisão existente", (
        ("Decisão registrada", case.decision),
        ("Decision Owner informado", case.decision_owner),
        ("Referência que demonstra a autoridade do owner", case.owner_authority_reference),
        ("Fonte da decisão", case.source_reference),
        ("Escopo", case.scope),
        ("Justificativa", case.justification),
        ("Atribuição", "Registro de decisão previamente existente; não transfere autoridade."),
    ))
    return _publish(
        rickcraft_root, analysis_id, "decision", purpose, origin_reference, body, case,
        inputs, relations, clock, resolver, avaliador_factory,
    )


def registrar_resultado(
    rickcraft_root: str | Path,
    analysis_id: str,
    case: OperationalResultCase,
    *,
    purpose: str,
    origin_reference: str = "SPEC-0000000001 TASK-011",
    inputs: Sequence[Mapping[str, Any]] = (),
    relations: Sequence[Mapping[str, Any]] = (),
    clock: Clock | None = None,
    resolver: Any = None,
    avaliador_factory: Any = None,
) -> PersistedOperationalRecord:
    continuity = _validate_result(case)
    body = _body("Resultado operacional", (
        ("Operação", case.operation),
        ("Resultado observado", case.outcome),
        ("Referências de evidência", case.evidence_references),
        ("Limitações", case.limitations),
        ("Escopos bloqueados", case.blocked_scopes),
        ("Avaliação de continuidade localizada", continuity),
        (
            "Escopos que podem continuar sob autorização existente",
            continuity.continuable_scopes if continuity else (),
        ),
        ("Limite", "Este resultado operacional não declara gate SDD nem substitui status.md."),
    ))
    return _publish(
        rickcraft_root, analysis_id, "result", purpose, origin_reference, body, case,
        inputs, relations, clock, resolver, avaliador_factory,
    )


def _publish(
    rickcraft_root: str | Path,
    analysis_id: str,
    document_type: str,
    purpose: str,
    origin_reference: str,
    body: str,
    record: object,
    inputs: Sequence[Mapping[str, Any]],
    relations: Sequence[Mapping[str, Any]],
    clock: Clock | None,
    resolver: Any,
    avaliador_factory: Any,
) -> PersistedOperationalRecord:
    try:
        validar_analysis_id(analysis_id)
    except (AnalysisLifecycleError, TypeError) as exc:
        raise GapHandlingError("analysis_id deve ser ANL-UUIDv4 canônico válido.") from exc
    _require_text(purpose, "purpose")
    _require_text(origin_reference, "origin_reference")
    if isinstance(inputs, (str, bytes)) or not isinstance(inputs, Sequence):
        raise GapHandlingError("inputs deve ser uma sequência de objetos JSON.")
    if isinstance(relations, (str, bytes)) or not isinstance(relations, Sequence):
        raise GapHandlingError("relations deve ser uma sequência de objetos JSON.")
    instant = (clock or (lambda: datetime.now(timezone.utc)))()
    if not isinstance(instant, datetime) or instant.tzinfo is None or instant.utcoffset() is None:
        raise GapHandlingError("O clock deve fornecer datetime com fuso explícito.")
    created_at = instant.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
    metadata = {
        "schema_version": 1,
        "type_catalog_version": 1,
        "created_at_utc": created_at,
        "purpose": purpose,
        "origin": {"kind": "rickcraft_task_011", "reference": origin_reference},
        "inputs": [dict(item) for item in inputs],
        "relations": [dict(item) for item in relations],
    }
    kwargs: dict[str, Any] = {}
    if resolver is not None:
        kwargs["resolver"] = resolver
    if avaliador_factory is not None:
        kwargs["avaliador_factory"] = avaliador_factory
    # O publicador é a única fronteira de persistência; falhas propagam e não
    # produzem receipt/document_id em memória como se houvesse sucesso.
    publication = publicar_documento(
        rickcraft_root,
        analysis_id,
        document_type,
        _title_for(document_type),
        body,
        metadata,
        **kwargs,
    )
    if not isinstance(publication, PublicationResult):
        raise GapHandlingError("A persistência não foi confirmada pelo publicador TASK-008.")
    return PersistedOperationalRecord(document_type, publication, record)


def _title_for(document_type: str) -> str:
    titles = {
        "divergence": "Divergência operacional registrada",
        "blocker": "Bloqueio operacional registrado",
        "decision": "Decisão existente registrada",
        "result": "Resultado operacional registrado",
    }
    try:
        return titles[document_type]
    except (KeyError, TypeError) as exc:
        raise GapHandlingError("TASK-011 aceita somente divergence, blocker, decision ou result.") from exc


def _body(title: str, sections: Sequence[tuple[str, object]]) -> str:
    parts = [f"## {title}"]
    for heading, value in sections:
        if value is None:
            continue
        encoded = json.dumps(_jsonable(value), ensure_ascii=False, sort_keys=True, indent=2)
        # O envelope JSON único pertence ao serializador TASK-006; o corpo
        # mantém os valores legíveis sem adicionar outro bloco cercado.
        encoded = encoded.replace("`", "\\u0060")
        parts.extend((f"### {heading}", encoded))
    return "\n\n".join(parts) + "\n"


def _jsonable(value: object) -> object:
    if isinstance(value, SourceReference):
        return {
            "category": value.category,
            "reference": value.reference,
            "statement": value.statement,
            "authority": value.authority,
        }
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, ContinuityAssessment):
        return {
            "affected_scopes": list(value.affected_scopes),
            "scopes": [
                {"scope": item.scope, "continuable": item.continuable, "reasons": list(item.reasons)}
                for item in value.scopes
            ],
        }
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def _validate_source(source: SourceReference, name: str) -> None:
    if not isinstance(source, SourceReference):
        raise GapHandlingError(f"{name} deve ser SourceReference explícita.")
    if type(source.category) is not str or source.category not in _CATEGORIES:
        raise GapHandlingError(f"{name}.category deve identificar uma classe de fonte conhecida.")
    _require_text(source.reference, f"{name}.reference")
    _require_text(source.statement, f"{name}.statement")
    if source.authority is not None:
        _require_text(source.authority, f"{name}.authority")
    elif source.category == "normative":
        raise GapHandlingError(f"{name} requer referência explícita da autoridade normativa.")


def _validate_divergence(case: DivergenceCase) -> None:
    if not isinstance(case, DivergenceCase):
        raise GapHandlingError("case deve ser DivergenceCase.")
    for name in ("occurrence", "affected_scope", "impact", "unresolved_reason", "resume_condition"):
        _require_text(getattr(case, name), name)
    if len(case.references) < 2:
        raise GapHandlingError("Divergence requer ao menos duas referências envolvidas.")
    for index, source in enumerate(case.references):
        _validate_source(source, f"references[{index}]")
    for name in ("required_authority", "required_information", "required_evidence"):
        value = getattr(case, name)
        if value is not None:
            _require_text(value, name)


def _validate_blocker(case: BlockerCase) -> None:
    if not isinstance(case, BlockerCase):
        raise GapHandlingError("case deve ser BlockerCase.")
    for name in ("affected_scope", "cause", "dependency", "resume_condition"):
        _require_text(getattr(case, name), name)
    requirements = (case.required_authority, case.required_information, case.required_evidence)
    if not any(value is not None and type(value) is str and value.strip() for value in requirements):
        raise GapHandlingError("Blocker deve declarar autoridade, informação ou evidência necessária.")
    for name in ("required_authority", "required_information", "required_evidence"):
        value = getattr(case, name)
        if value is not None:
            _require_text(value, name)


def _validate_decision(case: ExistingDecisionCase) -> None:
    if not isinstance(case, ExistingDecisionCase):
        raise GapHandlingError("case deve ser ExistingDecisionCase.")
    if case.explicitly_existing is not True:
        raise GapHandlingError("Somente decisão explicitamente existente pode ser registrada como decision.")
    for name in (
        "decision", "decision_owner", "owner_authority_reference", "source_reference", "scope", "justification"
    ):
        _require_text(getattr(case, name), name)


def _validate_result(case: OperationalResultCase) -> ContinuityAssessment | None:
    if not isinstance(case, OperationalResultCase):
        raise GapHandlingError("case deve ser OperationalResultCase.")
    _require_text(case.operation, "operation")
    _require_text(case.outcome, "outcome")
    statements = [case.operation, case.outcome]
    for name in ("evidence_references", "limitations", "blocked_scopes"):
        values = getattr(case, name)
        if not isinstance(values, tuple):
            raise GapHandlingError(f"{name} deve ser uma tupla explícita de textos.")
        for value in values:
            statements.append(_require_text(value, name))
    if any(_declares_forbidden_gate(statement) for statement in statements):
        raise GapHandlingError("result não pode declarar gate ANALYZE PASS ou CONVERGED.")
    if not isinstance(case.scope_requests, tuple):
        raise GapHandlingError("scope_requests deve ser uma tupla explícita de ScopeRequest.")
    if case.blocked_scopes:
        return avaliar_continuidade_localizada(case.blocked_scopes, case.scope_requests)
    if case.scope_requests:
        raise GapHandlingError("scope_requests exige blocked_scopes/affected_scopes explícitos.")
    return None


def _declares_forbidden_gate(statement: str) -> bool:
    for match in _INVALID_RESULT_CLAIMS.finditer(statement):
        line_start = statement.rfind("\n", 0, match.start()) + 1
        prefix = statement[line_start:match.start()].rstrip().casefold()
        if re.search(r"\b(?:não|nao)\s+(?:declara|afirma)\s*$", prefix):
            continue
        return True
    return False


def _require_text(value: object, name: str) -> str:
    if type(value) is not str or not value.strip() or "\x00" in value:
        raise GapHandlingError(f"{name} deve ser texto explícito, não vazio e sem NUL.")
    return value.strip()


def _explicit_bool(value: object, name: str) -> bool:
    if type(value) is not bool:
        raise GapHandlingError(f"{name} deve ser informado como booleano explícito.")
    return value
