"""Value objects imutáveis do protocolo de revisão técnica."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence


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


def _texto_obrigatorio(value: object, field: str) -> str:
    if type(value) is not str or not value.strip():
        raise ReviewInputError(f"{field} deve ser texto explícito não vazio.")
    return value


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
