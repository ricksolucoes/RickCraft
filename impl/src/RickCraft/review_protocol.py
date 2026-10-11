"""Value objects imutáveis do protocolo de revisão técnica."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import Enum
import json
import math
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Mapping, Sequence

import analysis_lifecycle
import document_publisher
import document_recovery
import document_search
import gap_handling


class ReviewInputError(ValueError):
    """Pedido ou escopo estruturalmente inválido."""


class AuthorizationGrant(Enum):
    """Autorizações explícitas suportadas pelo protocolo."""

    REVIEW = "REVIEW"
    STRUCTURAL_CHANGE = "STRUCTURAL_CHANGE"
    FUNCTIONAL_CHANGE = "FUNCTIONAL_CHANGE"
    LOCAL_PERSISTENCE = "LOCAL_PERSISTENCE"


class RequestedEffect(Enum):
    """Efeitos solicitados; externalidade é reconhecida, mas não suportada."""

    LOCAL_PERSISTENCE = "LOCAL_PERSISTENCE"
    EXTERNALITY = "EXTERNALITY"


class EvidenceKind(Enum):
    """Classe declarada da evidência recebida pelo Core."""

    DIRECT_OBSERVATION = "DIRECT_OBSERVATION"
    PERSISTED_EVIDENCE = "PERSISTED_EVIDENCE"
    REPORTED = "REPORTED"
    INFERENCE = "INFERENCE"


class VerificationStatus(Enum):
    """Estado declarado de um claim, distinto da proveniência da evidência."""

    EXECUTED_OBSERVED = "EXECUTED_OBSERVED"
    HISTORICAL_IDENTIFIED = "HISTORICAL_IDENTIFIED"
    NOT_EXECUTED = "NOT_EXECUTED"
    UNAVAILABLE = "UNAVAILABLE"
    INCONCLUSIVE = "INCONCLUSIVE"


def _texto_obrigatorio(value: object, field: str) -> str:
    if type(value) is not str or not value.strip():
        raise ReviewInputError(f"{field} deve ser texto explícito não vazio.")
    return value


def _texto_opcional(value: object, field: str) -> str | None:
    if value is None:
        return None
    return _texto_obrigatorio(value, field)


def _sequencia(value: object, field: str) -> tuple[object, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ReviewInputError(f"{field} deve ser uma sequência explícita.")
    return tuple(value)


def _textos_unicos(value: object, field: str, *, ordenar: bool = False) -> tuple[str, ...]:
    items = tuple(_texto_obrigatorio(item, field) for item in _sequencia(value, field))
    if len(set(items)) != len(items):
        raise ReviewInputError(f"{field} não pode conter valores duplicados.")
    return tuple(sorted(items)) if ordenar else items


@dataclass(frozen=True)
class ReviewScope:
    """Escopo factual com dependências e artefatos declarados explicitamente."""

    scope_id: str
    description: str
    depends_on: tuple[str, ...]
    artifacts: tuple[str, ...]

    def __post_init__(self) -> None:
        _texto_obrigatorio(self.scope_id, "scope_id")
        _texto_obrigatorio(self.description, "description")
        dependencies = _textos_unicos(self.depends_on, "depends_on", ordenar=True)
        if self.scope_id in dependencies:
            raise ReviewInputError("depends_on não pode conter o próprio scope_id.")
        artifacts = _textos_unicos(self.artifacts, "artifacts", ordenar=True)
        object.__setattr__(self, "depends_on", dependencies)
        object.__setattr__(self, "artifacts", artifacts)


@dataclass(frozen=True)
class ReviewRequest:
    """Entrada validada da TASK-001; não executa os grants ou efeitos."""

    objective: str
    scopes: tuple[ReviewScope, ...]
    authorized_artifacts: tuple[str, ...]
    excluded_artifacts: tuple[str, ...]
    expected_outcome: str
    authorization_grants: tuple[AuthorizationGrant, ...]
    requested_effects: tuple[RequestedEffect, ...]
    language: str | None = None
    source_versions: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        _texto_obrigatorio(self.objective, "objective")
        _texto_obrigatorio(self.expected_outcome, "expected_outcome")
        if self.language is not None:
            _texto_obrigatorio(self.language, "language")

        scopes = _sequencia(self.scopes, "scopes")
        if not scopes:
            raise ReviewInputError("scopes deve conter ao menos um ReviewScope.")
        if any(not isinstance(scope, ReviewScope) for scope in scopes):
            raise ReviewInputError("scopes deve conter somente ReviewScope.")
        scope_ids = tuple(scope.scope_id for scope in scopes)
        if len(set(scope_ids)) != len(scope_ids):
            raise ReviewInputError("scopes não pode conter scope_id duplicado.")
        object.__setattr__(self, "scopes", scopes)

        authorized = _textos_unicos(
            self.authorized_artifacts, "authorized_artifacts", ordenar=True
        )
        excluded = _textos_unicos(
            self.excluded_artifacts, "excluded_artifacts", ordenar=True
        )
        if set(authorized).intersection(excluded):
            raise ReviewInputError(
                "Um artefato não pode estar autorizado e excluído simultaneamente."
            )
        object.__setattr__(self, "authorized_artifacts", authorized)
        object.__setattr__(self, "excluded_artifacts", excluded)

        grants = _sequencia(self.authorization_grants, "authorization_grants")
        if any(not isinstance(grant, AuthorizationGrant) for grant in grants):
            raise ReviewInputError(
                "authorization_grants deve conter somente AuthorizationGrant."
            )
        if len(set(grants)) != len(grants):
            raise ReviewInputError("authorization_grants não pode conter duplicatas.")
        if AuthorizationGrant.REVIEW not in grants:
            raise ReviewInputError("AuthorizationGrant.REVIEW é obrigatório.")
        if (
            AuthorizationGrant.FUNCTIONAL_CHANGE in grants
            and AuthorizationGrant.STRUCTURAL_CHANGE not in grants
        ):
            raise ReviewInputError(
                "FUNCTIONAL_CHANGE exige também STRUCTURAL_CHANGE e REVIEW."
            )
        object.__setattr__(self, "authorization_grants", grants)

        effects = _sequencia(self.requested_effects, "requested_effects")
        if any(not isinstance(effect, RequestedEffect) for effect in effects):
            raise ReviewInputError(
                "requested_effects deve conter somente RequestedEffect."
            )
        if len(set(effects)) != len(effects):
            raise ReviewInputError("requested_effects não pode conter duplicatas.")
        object.__setattr__(self, "requested_effects", effects)

        versions = _sequencia(self.source_versions, "source_versions")
        validated_versions: list[tuple[str, str]] = []
        for item in versions:
            pair = _sequencia(item, "source_versions entry")
            if len(pair) != 2:
                raise ReviewInputError(
                    "Cada source_versions entry deve conter artefato e versão."
                )
            artifact = _texto_obrigatorio(pair[0], "source_versions artifact")
            version = _texto_obrigatorio(pair[1], "source_versions version")
            validated_versions.append((artifact, version))
        if len({artifact for artifact, _ in validated_versions}) != len(validated_versions):
            raise ReviewInputError("source_versions não pode repetir artefatos.")
        object.__setattr__(self, "source_versions", tuple(sorted(validated_versions)))


@dataclass(frozen=True)
class AuthorityReference:
    """Referência fornecida pelo host para owner e competência declarados."""

    source_reference: str
    owner: str
    competence_reference: str
    scopes: tuple[str, ...]

    def __post_init__(self) -> None:
        _texto_obrigatorio(self.source_reference, "source_reference")
        _texto_obrigatorio(self.owner, "owner")
        _texto_obrigatorio(self.competence_reference, "competence_reference")
        scopes = _textos_unicos(self.scopes, "authority scopes", ordenar=True)
        if not scopes:
            raise ReviewInputError("AuthorityReference requer ao menos um escopo explícito.")
        object.__setattr__(self, "scopes", scopes)


@dataclass(frozen=True)
class AuthorizedPrecedence:
    """Relação dirigida: prevailing_source prevalece sobre subordinate_source."""

    prevailing_source: str
    subordinate_source: str
    scope: str
    authorizing_authority: str
    decision_reference: str

    def __post_init__(self) -> None:
        _texto_obrigatorio(self.prevailing_source, "prevailing_source")
        _texto_obrigatorio(self.subordinate_source, "subordinate_source")
        if self.prevailing_source == self.subordinate_source:
            raise ReviewInputError("Uma precedência exige duas fontes distintas.")
        _texto_obrigatorio(self.scope, "precedence scope")
        _texto_obrigatorio(self.authorizing_authority, "authorizing_authority")
        _texto_obrigatorio(self.decision_reference, "decision_reference")


@dataclass(frozen=True)
class AuthorityContext:
    """Autoridades e precedências explícitas fornecidas, sem descoberta externa."""

    authorities: tuple[AuthorityReference, ...] = ()
    precedences: tuple[AuthorizedPrecedence, ...] = ()

    def __post_init__(self) -> None:
        authorities = _sequencia(self.authorities, "authorities")
        if any(not isinstance(item, AuthorityReference) for item in authorities):
            raise ReviewInputError(
                "authorities deve conter somente AuthorityReference."
            )
        authority_ids = tuple(item.source_reference for item in authorities)
        if len(set(authority_ids)) != len(authority_ids):
            raise ReviewInputError("authorities não pode duplicar source_reference.")
        authority_index = {item.source_reference: item for item in authorities}

        precedences = _sequencia(self.precedences, "precedences")
        if any(not isinstance(item, AuthorizedPrecedence) for item in precedences):
            raise ReviewInputError(
                "precedences deve conter somente AuthorizedPrecedence."
            )
        seen_exact: set[AuthorizedPrecedence] = set()
        seen_pair_scope: dict[tuple[frozenset[str], str], AuthorizedPrecedence] = {}
        for relation in precedences:
            if relation in seen_exact:
                raise ReviewInputError("precedences não pode conter relação duplicada.")
            seen_exact.add(relation)

            authorizer = authority_index.get(relation.authorizing_authority)
            if authorizer is None:
                raise ReviewInputError(
                    "A autoridade autorizadora deve estar explicitamente no contexto."
                )
            if relation.scope not in authorizer.scopes:
                raise ReviewInputError(
                    "A autoridade autorizadora não declarou competência para o escopo."
                )

            pair_scope = (
                frozenset((relation.prevailing_source, relation.subordinate_source)),
                relation.scope,
            )
            previous = seen_pair_scope.get(pair_scope)
            if previous is not None:
                if (
                    previous.prevailing_source == relation.subordinate_source
                    and previous.subordinate_source == relation.prevailing_source
                ):
                    raise ReviewInputError(
                        "Precedências opostas para o mesmo par e escopo são contraditórias."
                    )
                raise ReviewInputError(
                    "Há mais de uma relação de precedência para o mesmo par e escopo."
                )
            seen_pair_scope[pair_scope] = relation

        object.__setattr__(self, "authorities", tuple(sorted(authorities, key=lambda item: item.source_reference)))
        object.__setattr__(self, "precedences", tuple(sorted(
            precedences,
            key=lambda item: (
                item.scope,
                item.prevailing_source,
                item.subordinate_source,
                item.authorizing_authority,
                item.decision_reference,
            ),
        )))

    def precedence_for(
        self, source_a: str, source_b: str, scope: str
    ) -> AuthorizedPrecedence | None:
        """Retorna somente a relação declarada para o par e escopo exatos."""
        _texto_obrigatorio(source_a, "source_a")
        _texto_obrigatorio(source_b, "source_b")
        _texto_obrigatorio(scope, "precedence scope")
        if source_a == source_b:
            return None
        for relation in self.precedences:
            if relation.scope != scope:
                continue
            if {relation.prevailing_source, relation.subordinate_source} == {
                source_a,
                source_b,
            }:
                return relation
        return None


@dataclass(frozen=True)
class EvidenceReference:
    """Referência explícita a evidência já fornecida; não acessa sua origem."""

    kind: EvidenceKind
    origin: str
    reference: str
    target: str
    version: str | None = None
    digest: str | None = None
    limitation: str | None = None
    verifiability: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.kind, EvidenceKind):
            raise ReviewInputError("kind deve ser um EvidenceKind explícito.")
        _texto_obrigatorio(self.origin, "origin")
        _texto_obrigatorio(self.reference, "reference")
        _texto_obrigatorio(self.target, "target")
        _texto_opcional(self.version, "version")
        _texto_opcional(self.digest, "digest")
        _texto_opcional(self.limitation, "limitation")
        _texto_opcional(self.verifiability, "verifiability")


@dataclass(frozen=True)
class VerificationClaim:
    """Claim tipado associado apenas às referências fornecidas pelo chamador."""

    assertion: str
    target: str
    status: VerificationStatus
    evidence: tuple[EvidenceReference, ...] = ()
    version: str | None = None

    def __post_init__(self) -> None:
        _texto_obrigatorio(self.assertion, "assertion")
        _texto_obrigatorio(self.target, "target")
        if not isinstance(self.status, VerificationStatus):
            raise ReviewInputError("status deve ser um VerificationStatus explícito.")
        _texto_opcional(self.version, "claim version")

        references = _sequencia(self.evidence, "evidence")
        if any(not isinstance(item, EvidenceReference) for item in references):
            raise ReviewInputError(
                "evidence deve conter somente EvidenceReference."
            )
        if len(set(references)) != len(references):
            raise ReviewInputError("evidence não pode conter referências duplicadas.")

        for reference in references:
            if reference.target != self.target:
                raise ReviewInputError(
                    "A evidência deve pertencer ao mesmo target do claim."
                )
            if (
                self.version is not None
                and reference.version is not None
                and reference.version != self.version
            ):
                raise ReviewInputError(
                    "A versão da evidência não corresponde à versão do claim."
                )

        if self.status is VerificationStatus.EXECUTED_OBSERVED:
            if not references:
                raise ReviewInputError(
                    "EXECUTED_OBSERVED requer evidência de observação direta."
                )
            if not any(
                item.kind is EvidenceKind.DIRECT_OBSERVATION
                for item in references
            ):
                raise ReviewInputError(
                    "EXECUTED_OBSERVED exige DIRECT_OBSERVATION; relato, inferência ou histórico não bastam."
                )
        elif self.status is VerificationStatus.HISTORICAL_IDENTIFIED:
            if not any(
                item.kind is EvidenceKind.PERSISTED_EVIDENCE
                for item in references
            ):
                raise ReviewInputError(
                    "HISTORICAL_IDENTIFIED requer referência PERSISTED_EVIDENCE compatível."
                )

        ordered = tuple(sorted(
            references,
            key=lambda item: (
                item.kind.value,
                item.origin,
                item.reference,
                item.target,
                item.version or "",
                item.digest or "",
                item.limitation or "",
                item.verifiability or "",
            ),
        ))
        object.__setattr__(self, "evidence", ordered)


class ChangeKind(Enum):
    """Tipo declarado de mudança recebida do host."""

    STRUCTURAL = "STRUCTURAL"
    FUNCTIONAL = "FUNCTIONAL"


class BehaviorIntent(Enum):
    """Comportamento que a proposta declara preservar ou alterar."""

    PRESERVE = "PRESERVE"
    CHANGE = "CHANGE"


class BehaviorAssessmentState(Enum):
    """Resultados limitados de avaliação de uma proposta declarada."""

    PRESERVATION_EVIDENCED = "PRESERVATION_EVIDENCED"
    PRESERVATION_ASSERTED = "PRESERVATION_ASSERTED"
    NOT_VERIFIED = "NOT_VERIFIED"
    FUNCTIONAL_CHANGE_AUTHORIZED = "FUNCTIONAL_CHANGE_AUTHORIZED"
    FUNCTIONAL_CHANGE_UNAUTHORIZED = "FUNCTIONAL_CHANGE_UNAUTHORIZED"


@dataclass(frozen=True)
class BehaviorComparison:
    """Identificação explícita de uma comparação observada base↔candidata."""

    target: str
    case: str
    base_version: str
    candidate_version: str
    comparison_reference: str
    claim: VerificationClaim

    def __post_init__(self) -> None:
        _texto_obrigatorio(self.target, "comparison target")
        _texto_obrigatorio(self.case, "comparison case")
        _texto_obrigatorio(self.base_version, "comparison base_version")
        _texto_obrigatorio(self.candidate_version, "comparison candidate_version")
        _texto_obrigatorio(self.comparison_reference, "comparison_reference")
        if not isinstance(self.claim, VerificationClaim):
            raise ReviewInputError("comparison claim deve ser VerificationClaim explícito.")
        if (
            self.claim.status is not VerificationStatus.EXECUTED_OBSERVED
            or self.claim.target != self.target
            or self.claim.assertion != self.case
        ):
            raise ReviewInputError(
                "A comparação requer claim EXECUTED_OBSERVED do mesmo target e caso."
            )
        if not any(
            evidence.kind is EvidenceKind.DIRECT_OBSERVATION
            and evidence.reference == self.comparison_reference
            and evidence.target == self.target
            and evidence.limitation is None
            and evidence.verifiability not in ("UNAVAILABLE", "UNVERIFIABLE")
            and evidence.version in (None, self.base_version, self.candidate_version)
            for evidence in self.claim.evidence
        ):
            raise ReviewInputError(
                "A comparação requer EvidenceReference direta e compatível com seu locator."
            )


@dataclass(frozen=True)
class ChangeProposal:
    """Envelope declarativo de mudança; não contém nem aplica patch."""

    kind: ChangeKind
    scope: str
    targets: tuple[str, ...]
    proposal_reference: str
    technical_reason: str
    behavior_intent: BehaviorIntent
    consequences: str
    base_versions: tuple[tuple[str, str], ...] = ()
    candidate_versions: tuple[tuple[str, str], ...] = ()
    behavior_contract: str | None = None
    verified_cases: tuple[str, ...] = ()
    claims: tuple[VerificationClaim, ...] = ()
    comparisons: tuple[BehaviorComparison, ...] = ()
    preservation_assertion: str | None = None
    finding: ReviewFinding | None = None
    objective_reference: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ChangeKind):
            raise ReviewInputError("kind deve ser ChangeKind explícito.")
        _texto_obrigatorio(self.scope, "proposal scope")
        targets = _textos_unicos(self.targets, "proposal targets", ordenar=True)
        if not targets:
            raise ReviewInputError("ChangeProposal requer ao menos um target explícito.")
        object.__setattr__(self, "targets", targets)
        _texto_obrigatorio(self.proposal_reference, "proposal_reference")
        _texto_obrigatorio(self.technical_reason, "technical_reason")
        _texto_obrigatorio(self.consequences, "consequences")
        if not isinstance(self.behavior_intent, BehaviorIntent):
            raise ReviewInputError("behavior_intent deve ser BehaviorIntent explícito.")
        if (self.kind is ChangeKind.STRUCTURAL) != (
            self.behavior_intent is BehaviorIntent.PRESERVE
        ):
            raise ReviewInputError(
                "Mudança STRUCTURAL exige intenção PRESERVE; FUNCTIONAL exige CHANGE."
            )
        object.__setattr__(
            self, "behavior_contract", _texto_opcional(self.behavior_contract, "behavior_contract")
        )
        object.__setattr__(
            self,
            "preservation_assertion",
            _texto_opcional(self.preservation_assertion, "preservation_assertion"),
        )
        cases = _textos_unicos(self.verified_cases, "verified_cases", ordenar=True)
        object.__setattr__(self, "verified_cases", cases)
        object.__setattr__(self, "base_versions", _proposal_versions(
            self.base_versions, targets, "base_versions"
        ))
        object.__setattr__(self, "candidate_versions", _proposal_versions(
            self.candidate_versions, targets, "candidate_versions"
        ))
        claims = _sequencia(self.claims, "proposal claims")
        if any(not isinstance(item, VerificationClaim) for item in claims):
            raise ReviewInputError("claims deve conter somente VerificationClaim.")
        if len(set(claims)) != len(claims):
            raise ReviewInputError("claims não pode conter duplicatas.")
        if any(claim.target not in targets for claim in claims):
            raise ReviewInputError("Cada claim deve apontar para um target da proposta.")
        object.__setattr__(self, "claims", tuple(sorted(claims, key=lambda item: (
            item.target, item.status.value, item.assertion, item.version or ""
        ))))
        comparisons = _sequencia(self.comparisons, "proposal comparisons")
        if any(not isinstance(item, BehaviorComparison) for item in comparisons):
            raise ReviewInputError("comparisons deve conter somente BehaviorComparison.")
        if len(set(comparisons)) != len(comparisons):
            raise ReviewInputError("comparisons não pode conter duplicatas.")
        if any(item.target not in targets for item in comparisons):
            raise ReviewInputError("Cada comparação deve apontar para target da proposta.")
        object.__setattr__(self, "comparisons", tuple(sorted(comparisons, key=lambda item: (
            item.target, item.case, item.base_version, item.candidate_version,
            item.comparison_reference,
        ))))
        if self.finding is not None and not isinstance(self.finding, ReviewFinding):
            raise ReviewInputError("finding deve ser ReviewFinding explícito.")
        object.__setattr__(
            self, "objective_reference", _texto_opcional(self.objective_reference, "objective_reference")
        )
        if (self.finding is None) == (self.objective_reference is None):
            raise ReviewInputError(
                "ChangeProposal deve referenciar exatamente um ReviewFinding ou objective do pedido."
            )


def _proposal_versions(
    value: object, targets: tuple[str, ...], field: str
) -> tuple[tuple[str, str], ...]:
    entries = _sequencia(value, field)
    versions: list[tuple[str, str]] = []
    for entry in entries:
        pair = _sequencia(entry, f"{field} entry")
        if len(pair) != 2:
            raise ReviewInputError(f"Cada {field} entry deve conter target e versão.")
        target = _texto_obrigatorio(pair[0], f"{field} target")
        version = _texto_obrigatorio(pair[1], f"{field} version")
        if target not in targets:
            raise ReviewInputError(f"{field} contém target fora da proposta.")
        versions.append((target, version))
    if len({target for target, _ in versions}) != len(versions):
        raise ReviewInputError(f"{field} não pode repetir targets.")
    return tuple(sorted(versions))


def _preservation_is_evidenced(proposal: ChangeProposal) -> bool:
    """Requires an observed claim for each declared case and target version."""
    if (
        proposal.kind is not ChangeKind.STRUCTURAL
        or proposal.behavior_contract is None
        or not proposal.verified_cases
        or set(dict(proposal.base_versions)) != set(proposal.targets)
        or set(dict(proposal.candidate_versions)) != set(proposal.targets)
    ):
        return False
    base_versions = dict(proposal.base_versions)
    candidate_versions = dict(proposal.candidate_versions)
    for target in proposal.targets:
        for case in proposal.verified_cases:
            independent_evidence_complete = True
            for version in (base_versions[target], candidate_versions[target]):
                matching = [
                    claim for claim in proposal.claims
                    if claim.assertion == case
                    and claim.target == target
                    and claim.version == version
                    and claim.status is VerificationStatus.EXECUTED_OBSERVED
                ]
                if not matching:
                    independent_evidence_complete = False
                    break
                if not any(
                    evidence.kind is EvidenceKind.DIRECT_OBSERVATION
                    and evidence.target == target
                    and evidence.version == version
                    and evidence.limitation is None
                    and evidence.verifiability not in ("UNAVAILABLE", "UNVERIFIABLE")
                    for claim in matching
                    for evidence in claim.evidence
                ):
                    independent_evidence_complete = False
                    break
            if independent_evidence_complete:
                continue
            comparison = next((
                item for item in proposal.comparisons
                if item.target == target
                and item.case == case
                and item.base_version == base_versions[target]
                and item.candidate_version == candidate_versions[target]
            ), None)
            if comparison is None:
                return False
    return True


@dataclass(frozen=True)
class BehaviorAssessment:
    """Assessment calculado a partir do pedido e da proposta imutáveis."""

    state: BehaviorAssessmentState
    proposal: ChangeProposal
    request: ReviewRequest

    def __post_init__(self) -> None:
        if not isinstance(self.state, BehaviorAssessmentState):
            raise ReviewInputError("state deve ser BehaviorAssessmentState explícito.")
        if not isinstance(self.proposal, ChangeProposal):
            raise ReviewInputError("proposal deve ser ChangeProposal explícita.")
        if not isinstance(self.request, ReviewRequest):
            raise ReviewInputError("request deve ser ReviewRequest explícito.")
        expected = _behavior_assessment_state(self.proposal, self.request)
        if self.state is not expected:
            raise ReviewInputError("BehaviorAssessment.state não corresponde às entradas explícitas.")


def _behavior_assessment_state(
    proposal: ChangeProposal, request: ReviewRequest
) -> BehaviorAssessmentState:
    grants = set(request.authorization_grants)
    if AuthorizationGrant.REVIEW not in grants:
        raise ReviewInputError("REVIEW é obrigatório para avaliar ChangeProposal.")
    scope_map = {item.scope_id: item for item in request.scopes}
    if proposal.scope not in scope_map:
        raise ReviewInputError("proposal scope deve existir explicitamente no ReviewRequest.")
    scope_artifacts = set(scope_map[proposal.scope].artifacts)
    for target in proposal.targets:
        if target in request.excluded_artifacts:
            raise ReviewInputError("Target excluído não pode ser avaliado na proposta.")
        if target not in request.authorized_artifacts or target not in scope_artifacts:
            raise ReviewInputError("Todos os targets devem estar explicitamente autorizados no escopo.")
    if proposal.finding is not None:
        if proposal.finding.scope != proposal.scope:
            raise ReviewInputError("ReviewFinding deve pertencer ao scope da proposta.")
        if not any(item.target in proposal.targets for item in proposal.finding.evidence):
            raise ReviewInputError("ReviewFinding deve referenciar ao menos um target da proposta.")
    elif proposal.objective_reference != request.objective:
        raise ReviewInputError("objective_reference deve corresponder ao objective do pedido.")

    if proposal.kind is ChangeKind.FUNCTIONAL:
        if AuthorizationGrant.STRUCTURAL_CHANGE in grants and AuthorizationGrant.FUNCTIONAL_CHANGE in grants:
            return BehaviorAssessmentState.FUNCTIONAL_CHANGE_AUTHORIZED
        return BehaviorAssessmentState.FUNCTIONAL_CHANGE_UNAUTHORIZED
    if AuthorizationGrant.STRUCTURAL_CHANGE not in grants:
        raise ReviewInputError("STRUCTURAL_CHANGE é obrigatório para proposta estrutural.")
    if _preservation_is_evidenced(proposal):
        return BehaviorAssessmentState.PRESERVATION_EVIDENCED
    if proposal.preservation_assertion is not None:
        return BehaviorAssessmentState.PRESERVATION_ASSERTED
    return BehaviorAssessmentState.NOT_VERIFIED


def assess_change_proposal(
    proposal: ChangeProposal, request: ReviewRequest
) -> BehaviorAssessment:
    """Avalia autorização/evidência declaradas sem editar ou examinar artefatos."""
    if not isinstance(proposal, ChangeProposal):
        raise ReviewInputError("proposal deve ser ChangeProposal explícita.")
    if not isinstance(request, ReviewRequest):
        raise ReviewInputError("request deve ser ReviewRequest explícito.")
    state = _behavior_assessment_state(proposal, request)
    return BehaviorAssessment(state=state, proposal=proposal, request=request)


class TechnicalDimension(Enum):
    """Dimensões que podem ser consideradas sem implicar avaliação."""

    PATTERNS = "PATTERNS"
    SOLID = "SOLID"
    INTERFACE_ARCHITECTURE = "INTERFACE_ARCHITECTURE"
    CLEAN_CODE = "CLEAN_CODE"
    DELPHI_OBJECT_PASCAL = "DELPHI_OBJECT_PASCAL"
    OBJECTIVE_NORMATIVE_RULES = "OBJECTIVE_NORMATIVE_RULES"
    QUALITY_AUDIT = "QUALITY_AUDIT"


class DimensionAssessmentState(Enum):
    """Estado explícito da consideração de uma dimensão em um escopo."""

    NOT_APPLICABLE = "NOT_APPLICABLE"
    NOT_ASSESSED_INSUFFICIENT_EVIDENCE = "NOT_ASSESSED_INSUFFICIENT_EVIDENCE"
    SPECIALIST_REQUIRED = "SPECIALIST_REQUIRED"
    SPECIALIST_ASSESSMENT_RECEIVED = "SPECIALIST_ASSESSMENT_RECEIVED"
    CORE_SCOPE_ASSESSMENT = "CORE_SCOPE_ASSESSMENT"


class AssessmentCharacter(Enum):
    """Caráter declarado pelo host para uma avaliação recebida."""

    CONSULTATIVE = "CONSULTATIVE"
    AUTHORITATIVE = "AUTHORITATIVE"


def _evidencias_unicas(value: object, field: str) -> tuple[EvidenceReference, ...]:
    items = _sequencia(value, field)
    if any(not isinstance(item, EvidenceReference) for item in items):
        raise ReviewInputError(f"{field} deve conter somente EvidenceReference.")
    if len(set(items)) != len(items):
        raise ReviewInputError(f"{field} não pode conter evidências duplicadas.")
    return tuple(sorted(items, key=lambda item: (
        item.kind.value,
        item.origin,
        item.reference,
        item.target,
        item.version or "",
        item.digest or "",
        item.limitation or "",
        item.verifiability or "",
    )))


@dataclass(frozen=True)
class SpecialistAssessment:
    """Avaliação recebida do host, sem descoberta ou chamada de especialista."""

    dimension: TechnicalDimension
    scope: str
    conclusion: str
    evidence: tuple[EvidenceReference, ...]
    character: AssessmentCharacter
    owner: str | None = None
    competence_reference: str | None = None
    authority_reference: AuthorityReference | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.dimension, TechnicalDimension):
            raise ReviewInputError("dimension deve ser TechnicalDimension explícita.")
        _texto_obrigatorio(self.scope, "specialist scope")
        _texto_obrigatorio(self.conclusion, "specialist conclusion")
        if not isinstance(self.character, AssessmentCharacter):
            raise ReviewInputError("character deve ser AssessmentCharacter explícito.")
        evidence = _evidencias_unicas(self.evidence, "specialist evidence")
        object.__setattr__(self, "evidence", evidence)
        owner = _texto_opcional(self.owner, "owner")
        competence = _texto_opcional(self.competence_reference, "competence_reference")
        if self.authority_reference is not None and not isinstance(
            self.authority_reference, AuthorityReference
        ):
            raise ReviewInputError("authority_reference deve ser AuthorityReference.")
        if self.character is AssessmentCharacter.AUTHORITATIVE:
            if owner is None:
                raise ReviewInputError("AUTHORITATIVE requer owner explícito.")
            if competence is None:
                raise ReviewInputError("AUTHORITATIVE requer competence_reference.")
            if self.authority_reference is None:
                raise ReviewInputError("AUTHORITATIVE requer AuthorityReference explícita.")
            authority = self.authority_reference
            if (
                authority.owner != owner
                or authority.competence_reference != competence
                or self.scope not in authority.scopes
            ):
                raise ReviewInputError(
                    "AuthorityReference deve corresponder ao owner, competência e escopo."
                )
            if not evidence:
                raise ReviewInputError("AUTHORITATIVE requer ao menos uma evidência explícita.")

    def validate_authority(self, context: AuthorityContext) -> None:
        """Confirma presença da referência no contexto fornecido explicitamente."""
        if not isinstance(context, AuthorityContext):
            raise ReviewInputError("context deve ser AuthorityContext explícito.")
        if self.character is not AssessmentCharacter.AUTHORITATIVE:
            return
        if self.authority_reference not in context.authorities:
            raise ReviewInputError(
                "AuthorityReference autoritativa deve estar presente no contexto explícito."
            )


@dataclass(frozen=True)
class DimensionAssessment:
    """Estado imutável de uma dimensão para um escopo declarado."""

    dimension: TechnicalDimension
    scope: str
    state: DimensionAssessmentState
    evidence: tuple[EvidenceReference, ...] = ()
    specialist_assessment: SpecialistAssessment | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.dimension, TechnicalDimension):
            raise ReviewInputError("dimension deve ser TechnicalDimension explícita.")
        _texto_obrigatorio(self.scope, "dimension scope")
        if not isinstance(self.state, DimensionAssessmentState):
            raise ReviewInputError("state deve ser DimensionAssessmentState explícito.")
        object.__setattr__(self, "evidence", _evidencias_unicas(self.evidence, "dimension evidence"))
        specialist = self.specialist_assessment
        if specialist is not None and not isinstance(specialist, SpecialistAssessment):
            raise ReviewInputError("specialist_assessment deve ser SpecialistAssessment.")
        if specialist is not None and (
            specialist.dimension is not self.dimension or specialist.scope != self.scope
        ):
            raise ReviewInputError("SpecialistAssessment deve corresponder à dimensão e ao escopo.")
        if self.state is DimensionAssessmentState.SPECIALIST_ASSESSMENT_RECEIVED and specialist is None:
            raise ReviewInputError(
                "SPECIALIST_ASSESSMENT_RECEIVED requer SpecialistAssessment correspondente."
            )
        if self.state is DimensionAssessmentState.NOT_APPLICABLE and specialist is not None:
            raise ReviewInputError("NOT_APPLICABLE não pode carregar SpecialistAssessment.")
        if self.state is DimensionAssessmentState.SPECIALIST_REQUIRED and (
            specialist is not None and specialist.character is AssessmentCharacter.AUTHORITATIVE
        ):
            raise ReviewInputError(
                "SPECIALIST_REQUIRED não pode carregar assessment autoritativa suficiente."
            )
        if self.state is DimensionAssessmentState.CORE_SCOPE_ASSESSMENT and (
            specialist is not None and specialist.character is AssessmentCharacter.AUTHORITATIVE
        ):
            raise ReviewInputError(
                "CORE_SCOPE_ASSESSMENT não pode atribuir competência especializada ao Core."
            )


class ConclusionState(Enum):
    """Estados de conclusão limitados às bases explicitamente fornecidas."""

    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"
    NO_FINDING_IN_SCOPE = "NO_FINDING_IN_SCOPE"


def _versoes_explicitas(value: object) -> tuple[tuple[str, str], ...]:
    entries = _sequencia(value, "versions")
    pairs: list[tuple[str, str]] = []
    for entry in entries:
        pair = _sequencia(entry, "versions entry")
        if len(pair) != 2:
            raise ReviewInputError("Cada versions entry deve conter alvo e versão.")
        pairs.append((
            _texto_obrigatorio(pair[0], "version target"),
            _texto_obrigatorio(pair[1], "version"),
        ))
    if len({target for target, _ in pairs}) != len(pairs):
        raise ReviewInputError("versions não pode repetir alvos.")
    return tuple(sorted(pairs))


@dataclass(frozen=True)
class ReviewFinding:
    """Achado rastreável com fato, regra, conclusão e impacto separados."""

    scope: str
    dimension: TechnicalDimension
    condition: str
    evidence: tuple[EvidenceReference, ...]
    normative_reference: str
    technical_conclusion: str
    impact: str
    recommendation: str | None = None
    specialist_assessment: SpecialistAssessment | None = None

    def __post_init__(self) -> None:
        _texto_obrigatorio(self.scope, "finding scope")
        if not isinstance(self.dimension, TechnicalDimension):
            raise ReviewInputError("dimension deve ser TechnicalDimension explícita.")
        _texto_obrigatorio(self.condition, "condition")
        object.__setattr__(self, "evidence", _evidencias_unicas(self.evidence, "finding evidence"))
        if not self.evidence:
            raise ReviewInputError("ReviewFinding requer ao menos uma EvidenceReference.")
        _texto_obrigatorio(self.normative_reference, "normative_reference")
        _texto_obrigatorio(self.technical_conclusion, "technical_conclusion")
        _texto_obrigatorio(self.impact, "impact")
        _texto_opcional(self.recommendation, "recommendation")
        specialist = self.specialist_assessment
        if specialist is not None:
            if not isinstance(specialist, SpecialistAssessment):
                raise ReviewInputError("specialist_assessment deve ser SpecialistAssessment.")
            if specialist.dimension is not self.dimension or specialist.scope != self.scope:
                raise ReviewInputError(
                    "SpecialistAssessment do finding deve corresponder à dimensão e ao escopo."
                )
            if specialist.conclusion != self.technical_conclusion:
                raise ReviewInputError(
                    "Com assessment especializado, technical_conclusion deve preservar a conclusão recebida."
                )

    @property
    def sort_key(self) -> tuple[str, int, str, str, str]:
        """Chave D-14; rank segue a ordem canônica declarada no enum."""
        rank = tuple(TechnicalDimension).index(self.dimension)
        return (
            self.scope,
            rank,
            self.normative_reference,
            self.condition.casefold(),
            self.condition,
        )


def sort_review_findings(findings: Sequence[ReviewFinding]) -> tuple[ReviewFinding, ...]:
    """Ordena findings de forma pura e determinística pela chave do PLAN."""
    items = _sequencia(findings, "findings")
    if any(not isinstance(item, ReviewFinding) for item in items):
        raise ReviewInputError("findings deve conter somente ReviewFinding.")
    return tuple(sorted(items, key=lambda item: item.sort_key))


@dataclass(frozen=True)
class ReviewConclusion:
    """Conclusão estruturalmente delimitada às bases efetivamente declaradas."""

    state: ConclusionState
    scopes: tuple[str, ...]
    artifacts: tuple[str, ...] = ()
    sources: tuple[str, ...] = ()
    versions: tuple[tuple[str, str], ...] = ()
    evidence: tuple[EvidenceReference, ...] = ()
    claims: tuple[VerificationClaim, ...] = ()
    limitation: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.state, ConclusionState):
            raise ReviewInputError("state deve ser ConclusionState explícito.")
        scopes = _textos_unicos(self.scopes, "conclusion scopes", ordenar=True)
        if not scopes:
            raise ReviewInputError("ReviewConclusion requer ao menos um scope explícito.")
        if "*" in scopes:
            raise ReviewInputError("conclusion scopes não aceita scope global '*'.")
        artifacts = _textos_unicos(self.artifacts, "artifacts", ordenar=True)
        sources = _textos_unicos(self.sources, "sources", ordenar=True)
        versions = _versoes_explicitas(self.versions)
        evidence = _evidencias_unicas(self.evidence, "conclusion evidence")
        claims = _sequencia(self.claims, "claims")
        if any(not isinstance(item, VerificationClaim) for item in claims):
            raise ReviewInputError("claims deve conter somente VerificationClaim.")
        if len(set(claims)) != len(claims):
            raise ReviewInputError("claims não pode conter duplicatas.")
        claims = tuple(sorted(claims, key=lambda item: (
            item.target,
            item.status.value,
            item.assertion,
            item.version or "",
        )))
        limitation = _texto_opcional(self.limitation, "limitation")
        bases = set(artifacts) | set(sources)
        if self.state is ConclusionState.BLOCKED:
            if not bases:
                raise ReviewInputError(
                    "BLOCKED requer artifact ou source explícitos além do scope."
                )
            if limitation is None:
                raise ReviewInputError("BLOCKED requer limitation explícita.")
        else:
            if not bases:
                raise ReviewInputError(
                    "Conclusão não bloqueada requer artifacts ou sources explícitos."
                )
            if self.state is ConclusionState.NO_FINDING_IN_SCOPE and not evidence:
                raise ReviewInputError(
                    "NO_FINDING_IN_SCOPE requer EvidenceReference do escopo examinado."
                )
            if not evidence and not claims:
                raise ReviewInputError(
                    "Conclusão não bloqueada requer evidence ou claims rastreáveis."
                )
        if self.state is ConclusionState.NO_FINDING_IN_SCOPE and not any(
            item.kind in (EvidenceKind.DIRECT_OBSERVATION, EvidenceKind.PERSISTED_EVIDENCE)
            for item in evidence
        ):
            raise ReviewInputError(
                "NO_FINDING_IN_SCOPE requer evidência observada ou persistida."
            )
        if bases and any(target not in bases for target, _ in versions):
            raise ReviewInputError("Version target está fora das bases declaradas.")
        version_map = dict(versions)
        for item in evidence:
            if bases and item.target not in bases:
                raise ReviewInputError("EvidenceReference target está fora das bases declaradas.")
            if item.target in version_map and item.version is not None and item.version != version_map[item.target]:
                raise ReviewInputError("EvidenceReference version contradiz a versão declarada.")
        for claim in claims:
            if bases and claim.target not in bases:
                raise ReviewInputError("VerificationClaim target está fora das bases declaradas.")
            if claim.target in version_map and claim.version is not None and claim.version != version_map[claim.target]:
                raise ReviewInputError("VerificationClaim version contradiz a versão declarada.")
        object.__setattr__(self, "scopes", scopes)
        object.__setattr__(self, "artifacts", artifacts)
        object.__setattr__(self, "sources", sources)
        object.__setattr__(self, "versions", versions)
        object.__setattr__(self, "evidence", evidence)
        object.__setattr__(self, "claims", claims)


def evaluate_source_conflict(
    source_a: gap_handling.SourceReference,
    source_b: gap_handling.SourceReference,
    *,
    scope: str,
    impact: str,
    resume_condition: str,
    materially_incompatible: bool,
    authority_context: AuthorityContext,
    required_authority: AuthorityReference | None = None,
) -> AuthorizedPrecedence | gap_handling.ConflictAssessment | None:
    """Uses explicit precedence first, then delegates conflict rules to SPEC1.

    ``required_authority`` must be supplied explicitly and belong to the given
    context. SPEC1 receives its explicit ``source_reference`` as the textual
    requirement; this preserves identity without inventing an owner.
    """
    _validate_gap_source(source_a, "source_a")
    _validate_gap_source(source_b, "source_b")
    _gap_text(scope, "scope")
    _gap_text(impact, "impact")
    _gap_text(resume_condition, "resume_condition")
    if type(materially_incompatible) is not bool:
        raise ReviewInputError("materially_incompatible deve ser booleano explícito.")
    if not isinstance(authority_context, AuthorityContext):
        raise ReviewInputError("authority_context deve ser AuthorityContext explícito.")
    required_authority_reference: str | None = None
    if required_authority is not None:
        if not isinstance(required_authority, AuthorityReference):
            raise ReviewInputError("required_authority deve ser AuthorityReference explícita.")
        if required_authority not in authority_context.authorities:
            raise ReviewInputError("required_authority deve pertencer ao AuthorityContext.")
        if scope not in required_authority.scopes:
            raise ReviewInputError("required_authority não declara competência para o scope.")
        _gap_text(required_authority.source_reference, "required_authority.source_reference")
        required_authority_reference = required_authority.source_reference

    if materially_incompatible:
        precedence = authority_context.precedence_for(
            source_a.reference, source_b.reference, scope
        )
        if precedence is not None:
            return precedence
    try:
        return gap_handling.avaliar_conflito_fontes(
            source_a,
            source_b,
            affected_scope=scope,
            impact=impact,
            resume_condition=resume_condition,
            materially_incompatible=materially_incompatible,
            required_authority=required_authority_reference,
        )
    except gap_handling.GapHandlingError as exc:
        raise ReviewInputError("Os dados explícitos do conflito são inválidos para SPEC1.") from exc


def _validate_gap_source(source: object, field: str) -> None:
    if not isinstance(source, gap_handling.SourceReference):
        raise ReviewInputError(f"{field} deve ser SourceReference explícita.")
    categories = {"normative", "workspace", "evidence", "operational"}
    if type(source.category) is not str or source.category not in categories:
        raise ReviewInputError(f"{field}.category deve ser categoria aceita por SPEC1.")
    _gap_text(source.reference, f"{field}.reference")
    _gap_text(source.statement, f"{field}.statement")
    if source.authority is not None:
        _gap_text(source.authority, f"{field}.authority")
    elif source.category == "normative":
        raise ReviewInputError(f"{field} requer authority explícita para fonte normativa.")


def _gap_text(value: object, field: str) -> str:
    text = _texto_obrigatorio(value, field)
    if "\x00" in text:
        raise ReviewInputError(f"{field} não pode conter NUL para o contrato SPEC1.")
    return text


def evaluate_scope_continuity(
    affected_scopes: Sequence[str],
    review_scopes: Sequence[ReviewScope],
    readiness_by_scope: Mapping[str, tuple[bool, bool, bool, bool, bool]],
) -> gap_handling.ContinuityAssessment:
    """Adapts ReviewScope facts to SPEC1; the evaluator owns all propagation."""
    affected = _textos_unicos(affected_scopes, "affected_scopes", ordenar=False)
    if not affected:
        raise ReviewInputError("affected_scopes requer ao menos um scope explícito.")
    scopes = _sequencia(review_scopes, "review_scopes")
    if not scopes:
        raise ReviewInputError("review_scopes requer ao menos um ReviewScope.")
    if any(not isinstance(item, ReviewScope) for item in scopes):
        raise ReviewInputError("review_scopes deve conter somente ReviewScope.")
    ids = tuple(item.scope_id for item in scopes)
    if len(set(ids)) != len(ids):
        raise ReviewInputError("review_scopes não pode repetir scope_id.")
    if not isinstance(readiness_by_scope, Mapping):
        raise ReviewInputError("readiness_by_scope deve ser mapeamento explícito por scope_id.")
    if set(readiness_by_scope) != set(ids):
        raise ReviewInputError("readiness_by_scope deve cobrir exatamente os ReviewScope informados.")
    requests: list[gap_handling.ScopeRequest] = []
    for scope in scopes:
        facts = readiness_by_scope[scope.scope_id]
        if not isinstance(facts, tuple) or len(facts) != 5:
            raise ReviewInputError(
                "Cada readiness entry deve ser tupla de cinco booleanos explícitos."
            )
        if any(type(value) is not bool for value in facts):
            raise ReviewInputError("Os cinco critérios de continuidade devem ser bool explícitos.")
        authorized, information, evidence, authority, conflict_free = facts
        requests.append(gap_handling.ScopeRequest(
            scope=scope.scope_id,
            depends_on=scope.depends_on,
            explicitly_authorized=authorized,
            information_sufficient=information,
            evidence_sufficient=evidence,
            authority_sufficient=authority,
            conflict_free=conflict_free,
        ))
    try:
        return gap_handling.avaliar_continuidade_localizada(affected, tuple(requests))
    except gap_handling.GapHandlingError as exc:
        raise ReviewInputError("Os dados explícitos de continuidade são inválidos para SPEC1.") from exc


class ResponseBlockKey(Enum):
    """Chaves semânticas fixas dos blocos de resposta."""

    CRITICAL_ANALYSIS = "CRITICAL_ANALYSIS"
    REFACTORING = "REFACTORING"
    ARCHITECTURAL_JUSTIFICATION = "ARCHITECTURAL_JUSTIFICATION"


_RESPONSE_BLOCK_ORDER = (
    ResponseBlockKey.CRITICAL_ANALYSIS,
    ResponseBlockKey.REFACTORING,
    ResponseBlockKey.ARCHITECTURAL_JUSTIFICATION,
)
_MARKDOWN_ESCAPABLE = frozenset("\\`*_{}[]()#+-=!|>~<")


def _texto_markdown_literal(value: str) -> str:
    """Escapa pontuação Markdown sem alterar o texto visível fornecido."""
    return "".join("\\" + character if character in _MARKDOWN_ESCAPABLE else character
                   for character in value)


@dataclass(frozen=True)
class ReviewResponseBlock:
    """Bloco semântico com título e corpo já localizados pelo host."""

    key: ResponseBlockKey
    title: str
    body: str

    def __post_init__(self) -> None:
        if not isinstance(self.key, ResponseBlockKey):
            raise ReviewInputError("ResponseBlock.key deve ser ResponseBlockKey explícito.")
        title = _texto_obrigatorio(self.title, "ResponseBlock.title")
        if "\n" in title or "\r" in title:
            raise ReviewInputError("ResponseBlock.title deve ocupar uma única linha.")
        _texto_obrigatorio(self.body, "ResponseBlock.body")


@dataclass(frozen=True)
class ReviewResponse:
    """Resposta única com os três blocos semânticos na ordem normativa."""

    language: str | None
    blocks: tuple[ReviewResponseBlock, ...]

    def __post_init__(self) -> None:
        if self.language is not None:
            _texto_obrigatorio(self.language, "ReviewResponse.language")
        blocks = _sequencia(self.blocks, "ReviewResponse.blocks")
        if len(blocks) != len(_RESPONSE_BLOCK_ORDER):
            raise ReviewInputError("ReviewResponse requer exatamente três blocos semânticos.")
        if any(not isinstance(block, ReviewResponseBlock) for block in blocks):
            raise ReviewInputError("ReviewResponse.blocks deve conter somente ReviewResponseBlock.")
        keys = tuple(block.key for block in blocks)
        if keys != _RESPONSE_BLOCK_ORDER:
            raise ReviewInputError(
                "ReviewResponse.blocks deve conter as três chaves únicas na ordem canônica."
            )
        object.__setattr__(self, "blocks", blocks)


def renderizar_resposta(response: ReviewResponse) -> str:
    """Renderiza uma única resposta Markdown, preservando texto e ordem semântica."""
    if not isinstance(response, ReviewResponse):
        raise ReviewInputError("renderizar_resposta requer ReviewResponse.")
    rendered_blocks = tuple(
        f"## {_texto_markdown_literal(block.title)}\n\n"
        f"{_texto_markdown_literal(block.body)}"
        for block in response.blocks
    )
    return "\n\n".join(rendered_blocks)


@dataclass(frozen=True)
class ReviewEvaluationResult:
    """Resultado integrado em memória; não representa aprovação universal nem persistência."""

    request: ReviewRequest
    dimension_assessments: tuple[DimensionAssessment, ...]
    conflict_results: tuple[AuthorizedPrecedence | gap_handling.ConflictAssessment | None, ...]
    findings: tuple[ReviewFinding, ...]
    claims: tuple[VerificationClaim, ...]
    behavior_assessments: tuple[BehaviorAssessment, ...]
    continuity: gap_handling.ContinuityAssessment | None
    conclusion: ReviewConclusion
    response: ReviewResponse
    rendered: str

    def __post_init__(self) -> None:
        if not isinstance(self.request, ReviewRequest):
            raise ReviewInputError("result.request deve ser ReviewRequest.")
        for field, expected in (
            ("dimension_assessments", DimensionAssessment),
            ("findings", ReviewFinding),
            ("claims", VerificationClaim),
            ("behavior_assessments", BehaviorAssessment),
        ):
            items = _sequencia(getattr(self, field), f"result.{field}")
            if any(not isinstance(item, expected) for item in items):
                raise ReviewInputError(f"result.{field} contém tipo incompatível.")
            object.__setattr__(self, field, tuple(items))
        conflicts = _sequencia(self.conflict_results, "result.conflict_results")
        if any(item is not None and not isinstance(
            item, (AuthorizedPrecedence, gap_handling.ConflictAssessment)
        ) for item in conflicts):
            raise ReviewInputError("result.conflict_results contém tipo incompatível.")
        object.__setattr__(self, "conflict_results", tuple(conflicts))
        if self.continuity is not None and not isinstance(
            self.continuity, gap_handling.ContinuityAssessment
        ):
            raise ReviewInputError("result.continuity deve ser ContinuityAssessment ou None.")
        if not isinstance(self.conclusion, ReviewConclusion):
            raise ReviewInputError("result.conclusion deve ser ReviewConclusion.")
        if not isinstance(self.response, ReviewResponse):
            raise ReviewInputError("result.response deve ser ReviewResponse.")
        if self.response.language != self.request.language:
            raise ReviewInputError("result.response deve preservar o idioma do request.")
        _texto_obrigatorio(self.rendered, "result.rendered")


def _evidence_sort_key(item: EvidenceReference) -> tuple[str, ...]:
    return (item.reference, item.target, item.version or "", item.kind.value,
            item.origin, item.digest or "", item.limitation or "", item.verifiability or "")


def _claim_sort_key(item: VerificationClaim) -> tuple[object, ...]:
    return (item.target, item.version or "", item.status.value, item.assertion,
            tuple(_evidence_sort_key(evidence) for evidence in item.evidence))


def _finding_sort_key(item: ReviewFinding) -> tuple[object, ...]:
    specialist = item.specialist_assessment
    authority = None if specialist is None else specialist.authority_reference
    specialist_key: tuple[str, ...] = () if specialist is None else (
        specialist.dimension.value, specialist.scope, specialist.character.value,
        specialist.owner or "", specialist.competence_reference or "",
        specialist.conclusion,
        "" if authority is None else repr((authority.source_reference, authority.owner,
                                            authority.competence_reference, authority.scopes)),
        repr(tuple(_evidence_sort_key(evidence) for evidence in specialist.evidence)),
    )
    return (item.sort_key, tuple(_evidence_sort_key(evidence) for evidence in item.evidence),
            item.technical_conclusion, item.impact, item.recommendation or "", specialist_key)


def _proposal_sort_key(item: ChangeProposal) -> tuple[object, ...]:
    finding_key = () if item.finding is None else _finding_sort_key(item.finding)
    comparisons = tuple(sorted((
        comparison.target, comparison.case, comparison.base_version,
        comparison.candidate_version, comparison.comparison_reference,
        _claim_sort_key(comparison.claim),
    ) for comparison in item.comparisons))
    return (
        item.scope, item.targets, item.proposal_reference, item.kind.value,
        item.technical_reason, item.behavior_intent.value, item.consequences,
        item.base_versions, item.candidate_versions, item.behavior_contract or "",
        item.verified_cases, tuple(_claim_sort_key(claim) for claim in item.claims),
        comparisons, item.preservation_assertion or "", finding_key,
        item.objective_reference or "",
    )


def _conflict_input_key(item: tuple[object, ...]) -> tuple[object, ...]:
    source_a, source_b, scope, impact, resume, incompatible, authority = item
    source_key = lambda source: (source.category, source.reference, source.statement, source.authority or "")
    pair = tuple(sorted((source_key(source_a), source_key(source_b))))
    authority_key = ("", "", "", ()) if authority is None else (
        authority.source_reference, authority.owner, authority.competence_reference, authority.scopes
    )
    return (scope, pair, impact, resume, incompatible, authority_key)


def evaluate_review(
    request: ReviewRequest,
    *,
    authority_context: AuthorityContext,
    continuity_readiness_by_scope: Mapping[str, tuple[bool, bool, bool, bool, bool]],
    conclusion: ReviewConclusion,
    response: ReviewResponse,
    dimension_assessments: Sequence[DimensionAssessment] = (),
    claims: Sequence[VerificationClaim] = (),
    findings: Sequence[ReviewFinding] = (),
    change_proposals: Sequence[ChangeProposal] = (),
    source_conflicts: Sequence[tuple[
        gap_handling.SourceReference, gap_handling.SourceReference, str, str, str,
        bool, AuthorityReference | None
    ]] = (),
) -> ReviewEvaluationResult:
    """Integra entradas explícitas em memória usando os avaliadores já existentes.

    Cada source_conflict é a tupla (source_a, source_b, scope, impact,
    resume_condition, materially_incompatible, required_authority). Nenhuma
    origem é observada e nenhuma ação de mudança ou persistência é executada.
    """
    if not isinstance(request, ReviewRequest):
        raise ReviewInputError("request deve ser ReviewRequest explícito.")
    if not isinstance(authority_context, AuthorityContext):
        raise ReviewInputError("authority_context deve ser AuthorityContext explícito.")
    if not isinstance(conclusion, ReviewConclusion):
        raise ReviewInputError("conclusion deve ser ReviewConclusion explícita.")
    if not isinstance(response, ReviewResponse):
        raise ReviewInputError("response deve ser ReviewResponse explícita.")
    if response.language != request.language:
        raise ReviewInputError("ReviewResponse.language deve corresponder ao ReviewRequest.language.")
    if RequestedEffect.EXTERNALITY in request.requested_effects:
        raise ReviewInputError("EXTERNALITY não é suportada pelo pipeline Core.")

    scopes = {scope.scope_id: scope for scope in request.scopes}
    scope_ids = set(scopes)
    artifacts = set(request.authorized_artifacts)
    if any(not set(scope.artifacts).issubset(artifacts) for scope in request.scopes):
        raise ReviewInputError("ReviewScope contém artefato fora da allowlist do request.")
    if any(target not in artifacts for target, _ in request.source_versions):
        raise ReviewInputError("source_versions contém artefato fora da allowlist do request.")
    request = replace(
        request,
        scopes=tuple(sorted(request.scopes, key=lambda item: item.scope_id)),
        authorization_grants=tuple(sorted(request.authorization_grants, key=lambda item: item.value)),
        requested_effects=tuple(sorted(request.requested_effects, key=lambda item: item.value)),
    )
    scopes = {scope.scope_id: scope for scope in request.scopes}

    dimensions_input = _sequencia(dimension_assessments, "dimension_assessments")
    if any(not isinstance(item, DimensionAssessment) for item in dimensions_input):
        raise ReviewInputError("dimension_assessments deve conter somente DimensionAssessment.")
    dimensions = tuple(dimensions_input)
    dimension_keys = tuple((item.dimension, item.scope) for item in dimensions)
    if len(set(dimension_keys)) != len(dimension_keys):
        raise ReviewInputError("dimension_assessments não pode duplicar dimensão e scope.")
    if any(item.scope not in scope_ids for item in dimensions):
        raise ReviewInputError("DimensionAssessment aponta para scope fora do request.")
    dimensions = tuple(sorted(dimensions, key=lambda item: (
        tuple(TechnicalDimension).index(item.dimension), item.scope
    )))

    claims_input = _sequencia(claims, "claims")
    if any(not isinstance(item, VerificationClaim) for item in claims_input):
        raise ReviewInputError("claims deve conter somente VerificationClaim.")
    claims_list = list(claims_input)
    explicit_claims = set(claims_input)
    proposal_versions: dict[str, set[str]] = {}
    for proposal in _sequencia(change_proposals, "change_proposals"):
        if not isinstance(proposal, ChangeProposal):
            raise ReviewInputError("change_proposals deve conter somente ChangeProposal.")
        claims_list.extend(proposal.claims)
        claims_list.extend(comparison.claim for comparison in proposal.comparisons)
        for target, version in proposal.base_versions + proposal.candidate_versions:
            proposal_versions.setdefault(target, set()).add(version)
    if len(set(claims_list)) != len(claims_list):
        raise ReviewInputError("claims integrados não podem conter duplicatas.")
    canonical_claims = tuple(sorted(claims_list, key=_claim_sort_key))
    version_map = dict(request.source_versions)
    for claim in canonical_claims:
        if claim.target not in artifacts:
            raise ReviewInputError("VerificationClaim target está fora da allowlist do request.")
        if (claim in explicit_claims and claim.version is not None and claim.target in version_map
                and claim.version != version_map[claim.target]):
            raise ReviewInputError("VerificationClaim version contradiz source_versions.")
        for evidence in claim.evidence:
            if evidence.target not in artifacts:
                raise ReviewInputError("EvidenceReference target está fora da allowlist do request.")
            if (claim in explicit_claims and evidence.version is not None and evidence.target in version_map
                    and evidence.version != version_map[evidence.target]):
                raise ReviewInputError("EvidenceReference version contradiz source_versions.")
            if (evidence.version is not None and evidence.target in version_map
                    and evidence.version != version_map[evidence.target]
                    and evidence.version not in proposal_versions.get(evidence.target, set())):
                raise ReviewInputError("EvidenceReference version não corresponde a versão fornecida.")

    findings_input = _sequencia(findings, "findings")
    if any(not isinstance(item, ReviewFinding) for item in findings_input):
        raise ReviewInputError("findings deve conter somente ReviewFinding.")
    if len(set(findings_input)) != len(findings_input):
        raise ReviewInputError("findings não pode conter duplicatas.")
    findings_by_key: dict[tuple[str, int, str, str, str], ReviewFinding] = {}
    for finding in findings_input:
        if finding.scope not in scope_ids:
            raise ReviewInputError("ReviewFinding aponta para scope fora do request.")
        scope_artifacts = set(scopes[finding.scope].artifacts)
        if any(item.target not in artifacts or item.target not in scope_artifacts
               for item in finding.evidence):
            raise ReviewInputError("EvidenceReference do finding excede o artefato autorizado no scope.")
        previous = findings_by_key.get(finding.sort_key)
        if previous is not None and previous != finding:
            raise ReviewInputError("findings possuem chave D-14 ambigua.")
        findings_by_key[finding.sort_key] = finding
    canonical_findings = sort_review_findings(findings_input)

    for assessment in dimensions:
        scope_artifacts = set(scopes[assessment.scope].artifacts)
        if any(item.target not in artifacts or item.target not in scope_artifacts
               for item in assessment.evidence):
            raise ReviewInputError("EvidenceReference da dimensão excede o artefato autorizado no scope.")
        specialist = assessment.specialist_assessment
        if specialist is not None:
            specialist.validate_authority(authority_context)
            if any(item.target not in artifacts or item.target not in scope_artifacts
                   for item in specialist.evidence):
                raise ReviewInputError("EvidenceReference especializada excede o artefato autorizado no scope.")
    for finding in canonical_findings:
        specialist = finding.specialist_assessment
        if specialist is not None:
            specialist.validate_authority(authority_context)
            scope_artifacts = set(scopes[finding.scope].artifacts)
            if any(item.target not in artifacts or item.target not in scope_artifacts
                   for item in specialist.evidence):
                raise ReviewInputError("EvidenceReference especializada excede o artefato autorizado no scope.")

    proposals_input = _sequencia(change_proposals, "change_proposals")
    if len(set(proposals_input)) != len(proposals_input):
        raise ReviewInputError("change_proposals não pode conter duplicatas.")
    for proposal in proposals_input:
        if proposal.scope not in scope_ids:
            raise ReviewInputError("ChangeProposal aponta para scope fora do request.")
    proposals = tuple(sorted(proposals_input, key=_proposal_sort_key))
    if any(proposal.finding is not None and proposal.finding not in canonical_findings
           for proposal in proposals):
        raise ReviewInputError("ChangeProposal.finding deve integrar findings fornecidos ao review.")
    behavior_assessments = tuple(
        assess_change_proposal(proposal, request) for proposal in proposals
    )
    for assessment in behavior_assessments:
        for specialist in (
            assessment.proposal.finding.specialist_assessment
            if assessment.proposal.finding is not None else None,
        ):
            if specialist is not None:
                specialist.validate_authority(authority_context)

    conflict_items: list[tuple[object, ...]] = []
    for raw in _sequencia(source_conflicts, "source_conflicts"):
        fields = _sequencia(raw, "source_conflicts entry")
        if len(fields) != 7:
            raise ReviewInputError("source_conflicts entry requer sete campos explícitos.")
        source_a, source_b, scope, impact, resume, incompatible, required = fields
        scope = _gap_text(scope, "conflict scope")
        if scope not in scope_ids:
            raise ReviewInputError("Source conflict aponta para scope fora do request.")
        _validate_gap_source(source_a, "source_a")
        _validate_gap_source(source_b, "source_b")
        if type(incompatible) is not bool:
            raise ReviewInputError("materially_incompatible deve ser booleano explícito.")
        if required is not None and not isinstance(required, AuthorityReference):
            raise ReviewInputError("required_authority deve ser AuthorityReference explícita.")
        conflict_items.append((source_a, source_b, scope,
                               _gap_text(impact, "conflict impact"),
                               _gap_text(resume, "conflict resume_condition"),
                               incompatible, required))
    conflict_keys = tuple(_conflict_input_key(item) for item in conflict_items)
    if len(set(conflict_keys)) != len(conflict_keys):
        raise ReviewInputError("source_conflicts não pode conter entradas duplicadas.")
    conflict_results_list: list[AuthorizedPrecedence | gap_handling.ConflictAssessment | None] = []
    for item in sorted(conflict_items, key=_conflict_input_key):
        source_a, source_b, scope, impact, resume, incompatible, required = item
        conflict_results_list.append(evaluate_source_conflict(
            source_a, source_b, scope=scope, impact=impact, resume_condition=resume,
            materially_incompatible=incompatible, authority_context=authority_context,
            required_authority=required,
        ))
    conflict_results = tuple(conflict_results_list)

    readiness = continuity_readiness_by_scope
    if not isinstance(readiness, Mapping) or set(readiness) != scope_ids:
        raise ReviewInputError("continuidade deve fornecer fatos explícitos para cada scope do request.")
    normalized_readiness: dict[str, tuple[bool, bool, bool, bool, bool]] = {}
    for scope_id in sorted(scope_ids):
        facts = readiness[scope_id]
        if not isinstance(facts, tuple) or len(facts) != 5 or any(type(flag) is not bool for flag in facts):
            raise ReviewInputError("Cada scope requer cinco booleanos explícitos de continuidade.")
        normalized_readiness[scope_id] = facts

    unresolved_scopes = {
        item.divergence.affected_scope for item in conflict_results
        if isinstance(item, gap_handling.ConflictAssessment) and item.blocker_required
    }
    for scope_id in unresolved_scopes:
        authorized, information, evidence, authority, _ = normalized_readiness[scope_id]
        normalized_readiness[scope_id] = (authorized, information, evidence, authority, False)
    for item in dimensions:
        authorized, information, evidence, authority, conflict_free = normalized_readiness[item.scope]
        if item.state is DimensionAssessmentState.NOT_ASSESSED_INSUFFICIENT_EVIDENCE:
            normalized_readiness[item.scope] = (authorized, information, False, authority, conflict_free)
        elif item.state is DimensionAssessmentState.SPECIALIST_REQUIRED:
            normalized_readiness[item.scope] = (authorized, information, evidence, False, conflict_free)
    for item in behavior_assessments:
        if item.state is BehaviorAssessmentState.FUNCTIONAL_CHANGE_UNAUTHORIZED:
            authorized, information, evidence, authority, conflict_free = normalized_readiness[item.proposal.scope]
            normalized_readiness[item.proposal.scope] = (
                False, information, evidence, authority, conflict_free
            )
        elif item.state in (
            BehaviorAssessmentState.NOT_VERIFIED,
            BehaviorAssessmentState.PRESERVATION_ASSERTED,
        ):
            authorized, information, _, authority, conflict_free = normalized_readiness[item.proposal.scope]
            normalized_readiness[item.proposal.scope] = (
                authorized, information, False, authority, conflict_free
            )
    affected_scopes = set(unresolved_scopes)
    affected_scopes.update(
        item.scope for item in dimensions
        if item.state in (DimensionAssessmentState.SPECIALIST_REQUIRED,
                          DimensionAssessmentState.NOT_ASSESSED_INSUFFICIENT_EVIDENCE)
    )
    affected_scopes.update(
        item.proposal.scope for item in behavior_assessments
        if item.state is BehaviorAssessmentState.FUNCTIONAL_CHANGE_UNAUTHORIZED
    )
    affected_scopes.update(
        scope_id for scope_id, facts in normalized_readiness.items() if not all(facts)
    )
    affected_scopes.update(
        scope.scope_id for scope in request.scopes
        if any(dependency not in scope_ids for dependency in scope.depends_on)
    )
    continuity = None
    if affected_scopes:
        continuity = evaluate_scope_continuity(
            tuple(sorted(affected_scopes)),
            tuple(sorted(request.scopes, key=lambda item: item.scope_id)),
            normalized_readiness,
        )

    if any(scope not in scope_ids for scope in conclusion.scopes):
        raise ReviewInputError("ReviewConclusion cita scope fora do request.")
    if (conclusion.state is not ConclusionState.BLOCKED and continuity is not None
            and any(scope not in continuity.continuable_scopes for scope in conclusion.scopes)):
        raise ReviewInputError("Conclusão não bloqueada excede escopo sem continuidade apta.")
    if any(artifact not in artifacts for artifact in conclusion.artifacts):
        raise ReviewInputError("ReviewConclusion cita artefato fora da allowlist.")
    known_evidence = set()
    for claim in canonical_claims:
        known_evidence.update(claim.evidence)
    for assessment in dimensions:
        known_evidence.update(assessment.evidence)
        if assessment.specialist_assessment is not None:
            known_evidence.update(assessment.specialist_assessment.evidence)
    for finding in canonical_findings:
        known_evidence.update(finding.evidence)
        if finding.specialist_assessment is not None:
            known_evidence.update(finding.specialist_assessment.evidence)
    known_sources = artifacts | {item.reference for item in known_evidence} | {
        item.origin for item in known_evidence
    }
    known_sources.update(finding.normative_reference for finding in canonical_findings)
    for item in conflict_items:
        known_sources.update((item[0].reference, item[1].reference))
    if any(source not in known_sources for source in conclusion.sources):
        raise ReviewInputError("ReviewConclusion cita fonte que não foi fornecida ao pipeline.")
    if any(evidence not in known_evidence for evidence in conclusion.evidence):
        raise ReviewInputError("ReviewConclusion inclui evidência não fornecida ao pipeline.")
    if any(claim not in set(canonical_claims) for claim in conclusion.claims):
        raise ReviewInputError("ReviewConclusion inclui claim não fornecido ao pipeline.")
    known_versions: dict[str, set[str]] = {}
    for target, version in request.source_versions:
        known_versions.setdefault(target, set()).add(version)
    for claim in canonical_claims:
        if claim.version is not None:
            known_versions.setdefault(claim.target, set()).add(claim.version)
        for evidence in claim.evidence:
            if evidence.version is not None:
                known_versions.setdefault(evidence.target, set()).add(evidence.version)
    for evidence in known_evidence:
        if evidence.version is not None:
            known_versions.setdefault(evidence.target, set()).add(evidence.version)
        if (evidence.version is not None and evidence.target in version_map
                and evidence.version != version_map[evidence.target]
                and evidence.version not in proposal_versions.get(evidence.target, set())):
            raise ReviewInputError("EvidenceReference version contradiz source_versions.")
    for proposal in proposals:
        for target, version in proposal.base_versions + proposal.candidate_versions:
            known_versions.setdefault(target, set()).add(version)
    if any(
        (target in version_map and version_map[target] != version)
        or version not in known_versions.get(target, set())
        for target, version in conclusion.versions
    ):
        raise ReviewInputError("ReviewConclusion cita versão não fornecida ao pipeline.")
    if (conclusion.state is ConclusionState.NO_FINDING_IN_SCOPE and canonical_findings):
        raise ReviewInputError("NO_FINDING_IN_SCOPE contradiz findings explícitos do pipeline.")
    if response.language != request.language:
        raise ReviewInputError("ReviewResponse.language deve corresponder ao ReviewRequest.language.")
    rendered = renderizar_resposta(response)
    return ReviewEvaluationResult(
        request=request,
        dimension_assessments=dimensions,
        conflict_results=conflict_results,
        findings=canonical_findings,
        claims=canonical_claims,
        behavior_assessments=behavior_assessments,
        continuity=continuity,
        conclusion=conclusion,
        response=response,
        rendered=rendered,
    )


def _freeze_json_value(value: object, name: str) -> object:
    if value is None or type(value) in {str, bool, int}:
        return value
    if type(value) is float:
        if math.isfinite(value):
            return value
        raise ReviewInputError(f"{name} nao aceita numero nao finito.")
    if isinstance(value, Mapping):
        frozen: dict[str, object] = {}
        for key, item in value.items():
            if type(key) is not str:
                raise ReviewInputError(f"{name} requer chaves textuais.")
            frozen[key] = _freeze_json_value(item, name)
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json_value(item, name) for item in value)
    raise ReviewInputError(f"{name} deve conter somente dados JSON explicitos.")


def _thaw_json_value(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: _thaw_json_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json_value(item) for item in value]
    return value


def _freeze_json_records(value: object, name: str) -> tuple[Mapping[str, object], ...]:
    entries = _sequencia(value, name)
    result: list[Mapping[str, object]] = []
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise ReviewInputError(f"Cada item de {name} deve ser um objeto explicitamente fornecido.")
        frozen = _freeze_json_value(entry, name)
        assert isinstance(frozen, Mapping)
        result.append(frozen)
    return tuple(result)


@dataclass(frozen=True)
class PersistenceIntent:
    """Intencao explicita e opt-in de continuidade documental local."""

    rickcraft_root: str | Path
    purpose: str
    resume_analysis_id: str | None = None
    provenance_inputs: tuple[Mapping[str, object], ...] = ()
    relations: tuple[Mapping[str, object], ...] = ()
    evidence_to_persist: tuple[EvidenceReference, ...] = ()
    search_query: document_search.SearchQuery | None = None
    title: str = "Revisao tecnica RickCraft"

    def __post_init__(self) -> None:
        if not isinstance(self.rickcraft_root, (str, Path)):
            raise ReviewInputError("rickcraft_root deve ser fornecido explicitamente.")
        if isinstance(self.rickcraft_root, str) and not self.rickcraft_root.strip():
            raise ReviewInputError("rickcraft_root nao pode ser vazio.")
        _texto_obrigatorio(self.purpose, "purpose")
        _texto_obrigatorio(self.title, "title")
        if self.resume_analysis_id is not None:
            _texto_obrigatorio(self.resume_analysis_id, "resume_analysis_id")

        object.__setattr__(self, "provenance_inputs",
                           _freeze_json_records(self.provenance_inputs, "provenance_inputs"))
        frozen_relations = _freeze_json_records(self.relations, "relations")
        object.__setattr__(self, "relations", frozen_relations)

        evidence = _sequencia(self.evidence_to_persist, "evidence_to_persist")
        if any(not isinstance(item, EvidenceReference) for item in evidence):
            raise ReviewInputError("evidence_to_persist deve conter EvidenceReference.")
        if len(set(evidence)) != len(evidence):
            raise ReviewInputError("evidence_to_persist nao pode conter duplicatas.")
        object.__setattr__(self, "evidence_to_persist",
                           tuple(sorted(evidence, key=_evidence_sort_key)))

        query = self.search_query
        if query is not None:
            if not isinstance(query, document_search.SearchQuery):
                raise ReviewInputError("search_query deve ser SearchQuery explicita.")
            frozen_mappings = {}
            for field_name in ("metadata_equals", "input_equals", "relation_equals"):
                mapping = getattr(query, field_name)
                if mapping is not None and not isinstance(mapping, Mapping):
                    raise ReviewInputError(f"search_query.{field_name} deve ser um Mapping.")
                frozen_mappings[field_name] = (
                    None if mapping is None else _freeze_json_value(mapping, field_name)
                )
            terms = query.text_terms
            if terms is not None:
                if not isinstance(terms, (tuple, list)) or not terms:
                    raise ReviewInputError("search_query.text_terms deve ser uma sequencia explicita nao vazia.")
                if any(type(term) is not str or not term.strip() for term in terms):
                    raise ReviewInputError("search_query.text_terms deve conter texto nao vazio.")
            object.__setattr__(self, "search_query", document_search.SearchQuery(
                analysis_id=query.analysis_id,
                document_type=query.document_type,
                document_id=query.document_id,
                metadata_equals=frozen_mappings["metadata_equals"],  # type: ignore[arg-type]
                input_equals=frozen_mappings["input_equals"],  # type: ignore[arg-type]
                relation_equals=frozen_mappings["relation_equals"],  # type: ignore[arg-type]
                text_terms=None if terms is None else tuple(terms),
            ))


@dataclass(frozen=True)
class PersistedReviewEvaluation:
    """Confirmacoes reais SPEC1 de uma revisao persistida."""

    analysis: analysis_lifecycle.AnalysisDirectory
    publication: document_publisher.PublicationResult
    evidence_publications: tuple[document_publisher.PublicationResult, ...]
    recovered_document: document_recovery.RecoveredDocument
    recovered_analysis: document_recovery.RecoveryResult
    search_result: document_search.SearchResult | None = None


def _persisted_evidence_body(
    evidence: EvidenceReference,
    claims: Sequence[VerificationClaim],
) -> str:
    records = []
    for claim in sorted(claims, key=_claim_sort_key):
        records.append({
            "assertion": claim.assertion,
            "target": claim.target,
            "version": claim.version,
            "status": claim.status.value,
        })
    record = {
        "kind": evidence.kind.value,
        "origin": evidence.origin,
        "reference": evidence.reference,
        "target": evidence.target,
        "version": evidence.version,
        "digest": evidence.digest,
        "limitation": evidence.limitation,
        "verifiability": evidence.verifiability,
        "claims": records,
    }
    return json.dumps(record, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2)


def persist_review_evaluation(
    result: ReviewEvaluationResult,
    intent: PersistenceIntent,
    *,
    clock: Callable[[], datetime] | None = None,
) -> PersistedReviewEvaluation:
    """Persiste, recupera e opcionalmente pesquisa apos autorizacao explicita."""
    if not isinstance(result, ReviewEvaluationResult):
        raise ReviewInputError("result deve ser ReviewEvaluationResult ja avaliado.")
    if not isinstance(intent, PersistenceIntent):
        raise ReviewInputError("PersistenceIntent valido e obrigatorio para persistir.")

    grants = result.request.authorization_grants
    effects = result.request.requested_effects
    has_grant = AuthorizationGrant.LOCAL_PERSISTENCE in grants
    has_effect = RequestedEffect.LOCAL_PERSISTENCE in effects
    if not has_grant:
        raise ReviewInputError("Persistencia requer grant LOCAL_PERSISTENCE explicito.")
    if not has_effect:
        raise ReviewInputError("Persistencia requer RequestedEffect.LOCAL_PERSISTENCE explicito.")

    selected_evidence = intent.evidence_to_persist
    evidence_claims: dict[EvidenceReference, tuple[VerificationClaim, ...]] = {}
    for evidence in selected_evidence:
        if evidence.kind is not EvidenceKind.DIRECT_OBSERVATION:
            raise ReviewInputError("Somente DIRECT_OBSERVATION pode ser persistida como evidence.")
        matching = tuple(
            claim for claim in result.claims
            if claim.status is VerificationStatus.EXECUTED_OBSERVED
            and evidence in claim.evidence
        )
        if not matching:
            raise ReviewInputError("Evidence selecionada deve pertencer a claim EXECUTED_OBSERVED do resultado.")
        evidence_claims[evidence] = matching

    query = intent.search_query
    if query is not None:
        query = document_search.SearchQuery(
            analysis_id=query.analysis_id,
            document_type=query.document_type,
            document_id=query.document_id,
            metadata_equals=None if query.metadata_equals is None else _thaw_json_value(query.metadata_equals),  # type: ignore[arg-type]
            input_equals=None if query.input_equals is None else _thaw_json_value(query.input_equals),  # type: ignore[arg-type]
            relation_equals=None if query.relation_equals is None else _thaw_json_value(query.relation_equals),  # type: ignore[arg-type]
            text_terms=query.text_terms,
        )

    instante = (clock or (lambda: datetime.now(timezone.utc)))()
    if not isinstance(instante, datetime) or instante.tzinfo is None:
        raise ReviewInputError("clock deve fornecer datetime com fuso horario.")
    created_at = instante.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")

    analysis = analysis_lifecycle.criar_ou_retomar_analise(
        intent.rickcraft_root, intent.resume_analysis_id
    )
    metadata = {
        "schema_version": 1,
        "type_catalog_version": 1,
        "created_at_utc": created_at,
        "purpose": intent.purpose,
        "origin": {"kind": "task_execution", "reference": "SPEC-0000000002 TASK-010"},
        "inputs": [_thaw_json_value(item) for item in intent.provenance_inputs],
        "relations": [_thaw_json_value(item) for item in intent.relations],
    }
    publication = document_publisher.publicar_documento(
        intent.rickcraft_root,
        analysis.analysis_id,
        "analysis",
        intent.title,
        result.rendered,
        metadata,
    )
    recovered_document = document_recovery.recuperar_documento(
        intent.rickcraft_root, publication.document_id
    )
    if recovered_document.parsed.corpo != result.rendered:
        raise RuntimeError("Documento recuperado nao preservou o render publicado.")
    recovered_analysis = document_recovery.recuperar_analise(
        intent.rickcraft_root, analysis.analysis_id
    )
    if not any(item.document_id == publication.document_id for item in recovered_analysis.documents):
        raise RuntimeError("Documento principal nao aparece na recuperacao da analysis_id.")

    evidence_publications: list[document_publisher.PublicationResult] = []
    for evidence in selected_evidence:
        evidence_metadata = {
            **metadata,
            "purpose": f"Evidencia observavel: {intent.purpose}",
            "relations": [{
                "relation_type": "supports",
                "document_id": publication.document_id,
                "analysis_id": analysis.analysis_id,
            }],
        }
        evidence_publications.append(document_publisher.publicar_documento(
            intent.rickcraft_root,
            analysis.analysis_id,
            "evidence",
            f"Evidencia observavel - {evidence.target}",
            _persisted_evidence_body(evidence, evidence_claims[evidence]),
            evidence_metadata,
        ))

    search_result = None
    if query is not None:
        search_result = document_search.pesquisar_documentos(intent.rickcraft_root, query)

    return PersistedReviewEvaluation(
        analysis=analysis,
        publication=publication,
        evidence_publications=tuple(evidence_publications),
        recovered_document=recovered_document,
        recovered_analysis=recovered_analysis,
        search_result=search_result,
    )
