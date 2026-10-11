"""Value objects imutáveis do protocolo de revisão técnica."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

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
