from __future__ import annotations

import ast
from contextlib import ExitStack
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import socket
import sys
import subprocess
import tempfile
import unittest
import urllib.request
from unittest.mock import patch

RUNTIME_DIRECTORY = Path(__file__).resolve().parents[1] / "src" / "RickCraft"
sys.path.insert(0, str(RUNTIME_DIRECTORY))

import gap_handling as gaps  # noqa: E402
import provenance as provenance_api  # noqa: E402
import document_format as document_format_api  # noqa: E402
import review_protocol as protocol  # noqa: E402
from review_protocol import (  # noqa: E402
    AuthorizationGrant,
    AssessmentCharacter,
    AuthorityContext,
    AuthorityReference,
    AuthorizedPrecedence,
    BehaviorComparison,
    BehaviorAssessment,
    BehaviorAssessmentState,
    BehaviorIntent,
    ChangeKind,
    ChangeProposal,
    ConclusionState,
    DimensionAssessment,
    DimensionAssessmentState,
    EvidenceKind,
    EvidenceReference,
    RequestedEffect,
    PersistenceIntent,
    PersistedReviewEvaluation,
    ReviewConclusion,
    ReviewFinding,
    ReviewEvaluationResult,
    ReviewInputError,
    ReviewRequest,
    ReviewResponse,
    ReviewResponseBlock,
    ReviewScope,
    ResponseBlockKey,
    SpecialistAssessment,
    TechnicalDimension,
    VerificationClaim,
    VerificationStatus,
    assess_change_proposal,
    evaluate_scope_continuity,
    evaluate_source_conflict,
    evaluate_review,
    persist_review_evaluation,
    renderizar_resposta,
    sort_review_findings,
)


class ReviewScopeTests(unittest.TestCase):
    def test_scope_valido_preserva_valores_e_canonicaliza_colecoes(self) -> None:
        scope = ReviewScope(
            "core", "Revisar o Core", ["tests", "runtime"], ["b.py", "a.py"]
        )
        self.assertEqual(scope.scope_id, "core")
        self.assertEqual(scope.description, "Revisar o Core")
        self.assertEqual(scope.depends_on, ("runtime", "tests"))
        self.assertEqual(scope.artifacts, ("a.py", "b.py"))

    def test_id_vazio_e_rejeitado(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "scope_id"):
            ReviewScope(" ", "descrição", (), ())

    def test_descricao_vazia_e_rejeitada(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "description"):
            ReviewScope("core", "  ", (), ())

    def test_dependencia_vazia_e_rejeitada(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "depends_on"):
            ReviewScope("core", "descrição", [" "], ())

    def test_dependencias_duplicadas_sao_rejeitadas(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "duplicados"):
            ReviewScope("core", "descrição", ["base", "base"], ())

    def test_artefatos_duplicados_sao_rejeitados(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "duplicados"):
            ReviewScope("core", "descrição", (), ["a.py", "a.py"])

    def test_dependencia_propria_e_rejeitada(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "próprio scope_id"):
            ReviewScope("core", "descrição", ["core"], ())


class ReviewRequestTests(unittest.TestCase):
    @staticmethod
    def request(**overrides: object) -> ReviewRequest:
        values: dict[str, object] = {
            "objective": "Revisão delimitada",
            "scopes": (ReviewScope("core", "Revisar Core", (), ("src.py",)),),
            "authorized_artifacts": ("src.py",),
            "excluded_artifacts": (),
            "expected_outcome": "Relatório de achados",
            "authorization_grants": (AuthorizationGrant.REVIEW,),
            "requested_effects": (),
        }
        values.update(overrides)
        return ReviewRequest(**values)  # type: ignore[arg-type]

    def test_request_valido_somente_review(self) -> None:
        request = self.request()
        self.assertEqual(request.authorization_grants, (AuthorizationGrant.REVIEW,))
        self.assertEqual(request.requested_effects, ())

    def test_objective_e_expected_outcome_sao_obrigatorios(self) -> None:
        for field in ("objective", "expected_outcome"):
            with self.subTest(field=field), self.assertRaises(ReviewInputError):
                self.request(**{field: " "})

    def test_scopes_vazio_e_rejeitado(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "ao menos um"):
            self.request(scopes=())

    def test_ids_de_scope_duplicados_no_request_sao_rejeitados(self) -> None:
        scope = ReviewScope("same", "escopo", (), ())
        with self.assertRaisesRegex(ReviewInputError, "scope_id duplicado"):
            self.request(scopes=[scope, scope])

    def test_artifacts_autorizado_e_excluido_simultaneamente_e_rejeitado(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "autorizado e excluído"):
            self.request(authorized_artifacts=["a.py"], excluded_artifacts=["a.py"])

    def test_review_ausente_e_rejeitado(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "REVIEW é obrigatório"):
            self.request(authorization_grants=())

    def test_ausencia_de_grants_de_mudanca_nao_autoriza_mudanca(self) -> None:
        request = self.request()
        self.assertNotIn(
            AuthorizationGrant.STRUCTURAL_CHANGE, request.authorization_grants
        )
        self.assertNotIn(
            AuthorizationGrant.FUNCTIONAL_CHANGE, request.authorization_grants
        )

    def test_functional_change_sem_structural_change_e_rejeitado(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "exige também STRUCTURAL_CHANGE"):
            self.request(
                authorization_grants=(
                    AuthorizationGrant.REVIEW,
                    AuthorizationGrant.FUNCTIONAL_CHANGE,
                )
            )

    def test_ausencia_de_local_persistence_nao_autoriza_persistencia(self) -> None:
        request = self.request(
            requested_effects=(RequestedEffect.LOCAL_PERSISTENCE,)
        )
        self.assertIn(RequestedEffect.LOCAL_PERSISTENCE, request.requested_effects)
        self.assertNotIn(
            AuthorizationGrant.LOCAL_PERSISTENCE, request.authorization_grants
        )

    def test_local_persistence_grant_sem_review_nao_e_suficiente(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "REVIEW é obrigatório"):
            self.request(
                authorization_grants=(AuthorizationGrant.LOCAL_PERSISTENCE,)
            )

    def test_externality_e_reconhecida_sem_criar_grant_externo(self) -> None:
        request = self.request(requested_effects=(RequestedEffect.EXTERNALITY,))
        self.assertEqual(request.requested_effects, (RequestedEffect.EXTERNALITY,))
        self.assertEqual(
            {grant.value for grant in AuthorizationGrant},
            {"REVIEW", "STRUCTURAL_CHANGE", "FUNCTIONAL_CHANGE", "LOCAL_PERSISTENCE"},
        )

    def test_tipos_incorretos_de_grant_e_effect_sao_rejeitados(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "somente AuthorizationGrant"):
            self.request(authorization_grants=("REVIEW",))
        with self.assertRaisesRegex(ReviewInputError, "somente RequestedEffect"):
            self.request(requested_effects=("EXTERNALITY",))

    def test_grants_e_effects_duplicados_sao_rejeitados(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "authorization_grants.*duplicatas"):
            self.request(
                authorization_grants=(AuthorizationGrant.REVIEW, AuthorizationGrant.REVIEW)
            )
        with self.assertRaisesRegex(ReviewInputError, "requested_effects.*duplicatas"):
            self.request(
                requested_effects=(RequestedEffect.LOCAL_PERSISTENCE,) * 2
            )

    def test_language_none_e_default_semantico_ptbr(self) -> None:
        self.assertIsNone(self.request(language=None).language)

    def test_idioma_explicito_e_preservado_sem_normalizacao(self) -> None:
        self.assertEqual(self.request(language="EN-us").language, "EN-us")

    def test_idioma_vazio_ou_branco_e_rejeitado(self) -> None:
        for language in ("", " \t"):
            with self.subTest(language=language), self.assertRaises(ReviewInputError):
                self.request(language=language)

    def test_source_versions_validam_duplicidade_e_estrutura(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "repetir artefatos"):
            self.request(source_versions=(("src.py", "v1"), ("src.py", "v2")))
        with self.assertRaisesRegex(ReviewInputError, "artefato e versão"):
            self.request(source_versions=(("src.py",),))
        with self.assertRaisesRegex(ReviewInputError, "source_versions version"):
            self.request(source_versions=(("src.py", " "),))

    def test_input_original_mutavel_nao_altera_estado_validado(self) -> None:
        dependencies = ["base"]
        artifacts = ["b.py", "a.py"]
        versions = [["src.py", "v1"]]
        grants = [AuthorizationGrant.REVIEW]
        effects = [RequestedEffect.LOCAL_PERSISTENCE]
        scopes = [ReviewScope("core", "Revisar Core", dependencies, artifacts)]
        request = self.request(
            scopes=scopes,
            authorization_grants=grants,
            requested_effects=effects,
            source_versions=versions,
        )
        dependencies.append("later")
        artifacts.clear()
        versions[0][1] = "v2"
        grants.clear()
        effects.clear()
        scopes.clear()
        self.assertEqual(request.scopes[0].depends_on, ("base",))
        self.assertEqual(request.scopes[0].artifacts, ("a.py", "b.py"))
        self.assertEqual(request.source_versions, (("src.py", "v1"),))
        self.assertEqual(request.authorization_grants, (AuthorizationGrant.REVIEW,))
        self.assertEqual(
            request.requested_effects, (RequestedEffect.LOCAL_PERSISTENCE,)
        )

    def test_modelos_sao_imutaveis(self) -> None:
        scope = ReviewScope("core", "Revisar Core", (), ())
        request = self.request(scopes=(scope,))
        with self.assertRaises(FrozenInstanceError):
            scope.scope_id = "other"  # type: ignore[misc]
        with self.assertRaises(FrozenInstanceError):
            request.objective = "outra intenção"  # type: ignore[misc]
        with self.assertRaises(AttributeError):
            request.scopes.append(scope)  # type: ignore[attr-defined]

    def test_strings_em_lugar_de_colecoes_sao_rejeitadas(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "scopes deve ser"):
            self.request(scopes="core")
        with self.assertRaisesRegex(ReviewInputError, "authorized_artifacts deve ser"):
            self.request(authorized_artifacts="src.py")


class AuthorityContextTests(unittest.TestCase):
    @staticmethod
    def authority(
        *, source: str = "owner-ref", owner: str = "Owner X", scopes: object = ("core",)
    ) -> AuthorityReference:
        return AuthorityReference(
            source_reference=source,
            owner=owner,
            competence_reference="competence-doc#core",
            scopes=scopes,  # type: ignore[arg-type]
        )

    @staticmethod
    def precedence(
        *, prevailing: str = "policy-a", subordinate: str = "policy-b", scope: str = "core",
        authority: str = "owner-ref", decision: str = "decision#42",
    ) -> AuthorizedPrecedence:
        return AuthorizedPrecedence(
            prevailing_source=prevailing,
            subordinate_source=subordinate,
            scope=scope,
            authorizing_authority=authority,
            decision_reference=decision,
        )

    def test_authority_reference_valida(self) -> None:
        authority = self.authority(scopes=["workspace", "core"])
        self.assertEqual(authority.owner, "Owner X")
        self.assertEqual(authority.scopes, ("core", "workspace"))

    def test_authority_reference_rejeita_fonte_owner_e_competencia_vazios(self) -> None:
        for field, value in (
            ("source_reference", " "),
            ("owner", ""),
            ("competence_reference", "\t"),
        ):
            with self.subTest(field=field), self.assertRaises(ReviewInputError):
                arguments: dict[str, object] = {
                    "source_reference": "source",
                    "owner": "Owner",
                    "competence_reference": "competence",
                    "scopes": ("core",),
                }
                arguments[field] = value
                AuthorityReference(**arguments)  # type: ignore[arg-type]

    def test_authority_scopes_vazios_duplicados_ou_invalidos_sao_rejeitados(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "ao menos um escopo"):
            self.authority(scopes=())
        with self.assertRaisesRegex(ReviewInputError, "duplicados"):
            self.authority(scopes=["core", "core"])
        with self.assertRaisesRegex(ReviewInputError, "authority scopes"):
            self.authority(scopes=[""])
        with self.assertRaisesRegex(ReviewInputError, "sequência explícita"):
            self.authority(scopes={"core"})

    def test_contexto_vazio_e_valido_sem_owner_inventado(self) -> None:
        context = AuthorityContext()
        self.assertEqual(context.authorities, ())
        self.assertEqual(context.precedences, ())
        self.assertIsNone(context.precedence_for("A", "B", "core"))

    def test_precedencia_direcionada_valida_entre_fontes_distintas(self) -> None:
        relation = self.precedence()
        context = AuthorityContext([self.authority()], [relation])
        self.assertIs(context.precedence_for("policy-a", "policy-b", "core"), relation)
        self.assertIs(context.precedence_for("policy-b", "policy-a", "core"), relation)
        self.assertEqual(relation.prevailing_source, "policy-a")
        self.assertEqual(relation.subordinate_source, "policy-b")

    def test_mesma_fonte_nos_dois_lados_e_rejeitada(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "duas fontes distintas"):
            self.precedence(prevailing="policy-a", subordinate="policy-a")

    def test_precedencia_rejeita_escopo_authoridade_e_decisao_vazios(self) -> None:
        for field, value in (
            ("scope", " "),
            ("authorizing_authority", ""),
            ("decision_reference", "\t"),
        ):
            with self.subTest(field=field), self.assertRaises(ReviewInputError):
                arguments: dict[str, object] = {
                    "prevailing_source": "A",
                    "subordinate_source": "B",
                    "scope": "core",
                    "authorizing_authority": "owner-ref",
                    "decision_reference": "decision",
                }
                arguments[field] = value
                AuthorizedPrecedence(**arguments)  # type: ignore[arg-type]

    def test_autoridade_autorizadora_ausente_no_contexto_rejeita_relacao(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "explicitamente no contexto"):
            AuthorityContext((), (self.precedence(),))

    def test_autoridade_presente_fora_do_escopo_rejeita_relacao(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "não declarou competência"):
            AuthorityContext(
                (self.authority(scopes=("other-scope",)),), (self.precedence(),)
            )

    def test_autoridade_competente_no_escopo_valida_relacao(self) -> None:
        context = AuthorityContext((self.authority(),), (self.precedence(),))
        self.assertEqual(len(context.precedences), 1)
        self.assertEqual(context.precedence_for("policy-a", "policy-b", "core").decision_reference,
                         "decision#42")  # type: ignore[union-attr]

    def test_relacao_exatamente_duplicada_e_rejeitada(self) -> None:
        relation = self.precedence()
        with self.assertRaisesRegex(ReviewInputError, "relação duplicada"):
            AuthorityContext((self.authority(),), (relation, relation))

    def test_precedencias_opostas_para_mesmo_par_e_escopo_sao_rejeitadas(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "contraditórias"):
            AuthorityContext(
                (self.authority(),),
                (
                    self.precedence(),
                    self.precedence(prevailing="policy-b", subordinate="policy-a"),
                ),
            )

    def test_sem_precedencia_nao_existe_fonte_vencedora(self) -> None:
        context = AuthorityContext((self.authority(),), ())
        self.assertIsNone(context.precedence_for("policy-a", "policy-b", "core"))
        self.assertIsNone(context.precedence_for("policy-a", "policy-b", "other"))

    def test_textos_de_nome_data_ou_especificidade_nao_criam_precedencia(self) -> None:
        authority = self.authority(
            source="executor-2026-10-11-most-specific", owner="Executor"
        )
        context = AuthorityContext((authority,), ())
        self.assertEqual(context.authorities[0].owner, "Executor")
        self.assertEqual(context.precedences, ())
        self.assertIsNone(context.precedence_for("newer-A", "specific-B", "core"))

    def test_executor_agent_ou_auditor_nao_e_promovido_a_owner(self) -> None:
        context = AuthorityContext()
        self.assertEqual(context.authorities, ())
        supplied = self.authority(owner="Executor")
        context_with_supplied = AuthorityContext((supplied,), ())
        self.assertEqual(context_with_supplied.authorities[0].owner, "Executor")
        self.assertNotEqual(context_with_supplied.authorities[0].owner, "Auditor")

    def test_modelos_de_autoridade_sao_imutaveis(self) -> None:
        authority = self.authority()
        relation = self.precedence()
        context = AuthorityContext((authority,), (relation,))
        with self.assertRaises(FrozenInstanceError):
            authority.owner = "Other"  # type: ignore[misc]
        with self.assertRaises(FrozenInstanceError):
            relation.scope = "other"  # type: ignore[misc]
        with self.assertRaises(FrozenInstanceError):
            context.authorities = ()  # type: ignore[misc]

    def test_mutacao_das_colecoes_originais_nao_altera_contexto(self) -> None:
        scopes = ["core"]
        authorities = [self.authority(scopes=scopes)]
        precedences = [self.precedence()]
        context = AuthorityContext(authorities, precedences)
        scopes.append("later")
        authorities.clear()
        precedences.clear()
        self.assertEqual(context.authorities[0].scopes, ("core",))
        self.assertEqual(len(context.authorities), 1)
        self.assertEqual(len(context.precedences), 1)
        self.assertEqual(
            context.precedence_for("policy-a", "policy-b", "core").prevailing_source,
            "policy-a",
        )  # type: ignore[union-attr]

    def test_mudanca_da_ordem_de_entrada_preserva_contexto_canonico(self) -> None:
        first = self.authority(source="owner-a", scopes=("z", "a"))
        second = self.authority(source="owner-b", owner="Owner Y", scopes=("b",))
        a = AuthorityContext([first, second], ())
        b = AuthorityContext([second, first], ())
        self.assertEqual(a, b)


class EvidenceAndClaimTests(unittest.TestCase):
    @staticmethod
    def evidence(
        kind: EvidenceKind = EvidenceKind.DIRECT_OBSERVATION,
        **overrides: object,
    ) -> EvidenceReference:
        values: dict[str, object] = {
            "kind": kind,
            "origin": "unittest",
            "reference": "test://case-1",
            "target": "module.py",
            "version": "revision-1",
            "digest": "SHA256:explicit-value",
        }
        values.update(overrides)
        return EvidenceReference(**values)  # type: ignore[arg-type]

    @staticmethod
    def claim(
        status: VerificationStatus = VerificationStatus.EXECUTED_OBSERVED,
        evidence: object = (),
        **overrides: object,
    ) -> VerificationClaim:
        values: dict[str, object] = {
            "assertion": "O teste foi executado com resultado observado.",
            "target": "module.py",
            "version": "revision-1",
            "status": status,
            "evidence": evidence,
        }
        values.update(overrides)
        return VerificationClaim(**values)  # type: ignore[arg-type]

    def test_quatro_evidence_kinds_sao_distintos(self) -> None:
        self.assertEqual(
            {kind.value for kind in EvidenceKind},
            {"DIRECT_OBSERVATION", "PERSISTED_EVIDENCE", "REPORTED", "INFERENCE"},
        )
        self.assertEqual(len(set(EvidenceKind)), 4)

    def test_evidence_reference_valida_preserva_campos_fornecidos(self) -> None:
        item = self.evidence(
            EvidenceKind.PERSISTED_EVIDENCE,
            verifiability="MATCHED",
            limitation="observação histórica",
        )
        self.assertEqual(item.digest, "SHA256:explicit-value")
        self.assertEqual(item.verifiability, "MATCHED")
        self.assertEqual(item.limitation, "observação histórica")
        self.assertEqual(item.version, "revision-1")

    def test_campos_obrigatorios_vazios_sao_rejeitados(self) -> None:
        for field in ("origin", "reference", "target"):
            with self.subTest(field=field), self.assertRaises(ReviewInputError):
                self.evidence(**{field: " \t"})

    def test_campos_opcionais_vazios_sao_rejeitados(self) -> None:
        for field in ("version", "digest", "limitation", "verifiability"):
            with self.subTest(field=field), self.assertRaises(ReviewInputError):
                self.evidence(**{field: " "})

    def test_evidence_kind_arbitrario_nao_e_coagido(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "EvidenceKind explícito"):
            self.evidence("DIRECT_OBSERVATION")  # type: ignore[arg-type]

    def test_evidence_reference_e_imutavel(self) -> None:
        item = self.evidence()
        with self.assertRaises(FrozenInstanceError):
            item.target = "other.py"  # type: ignore[misc]

    def test_executed_observed_requer_evidence_direta_alvo_versao_compativeis(self) -> None:
        item = self.evidence()
        claim = self.claim(evidence=[item])
        self.assertEqual(claim.status, VerificationStatus.EXECUTED_OBSERVED)
        self.assertEqual(claim.evidence, (item,))

    def test_executed_observed_sem_evidence_e_rejeitado(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "requer evidência"):
            self.claim(evidence=())

    def test_reported_sozinho_nao_sustenta_executed_observed(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "DIRECT_OBSERVATION"):
            self.claim(evidence=[self.evidence(EvidenceKind.REPORTED)])

    def test_inference_sozinha_nao_sustenta_executed_observed(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "DIRECT_OBSERVATION"):
            self.claim(evidence=[self.evidence(EvidenceKind.INFERENCE)])

    def test_historical_evidence_nao_sustenta_executed_observed(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "DIRECT_OBSERVATION"):
            self.claim(evidence=[self.evidence(EvidenceKind.PERSISTED_EVIDENCE)])

    def test_evidence_de_outro_target_e_rejeitada(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "mesmo target"):
            self.claim(evidence=[self.evidence(target="other.py")])

    def test_versoes_explicitamente_diferentes_sao_rejeitadas(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "não corresponde"):
            self.claim(evidence=[self.evidence(version="revision-2")])

    def test_versao_ausente_na_evidence_nao_e_inferida(self) -> None:
        item = self.evidence(version=None)
        claim = self.claim(evidence=[item])
        self.assertIsNone(claim.evidence[0].version)

    def test_historical_identified_permanece_distinto_de_executed_observed(self) -> None:
        item = self.evidence(EvidenceKind.PERSISTED_EVIDENCE)
        claim = self.claim(
            status=VerificationStatus.HISTORICAL_IDENTIFIED, evidence=[item]
        )
        self.assertIs(claim.status, VerificationStatus.HISTORICAL_IDENTIFIED)
        self.assertIsNot(claim.status, VerificationStatus.EXECUTED_OBSERVED)

    def test_historical_identified_sem_evidencia_historica_e_rejeitado(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "PERSISTED_EVIDENCE"):
            self.claim(
                status=VerificationStatus.HISTORICAL_IDENTIFIED,
                evidence=[self.evidence(EvidenceKind.DIRECT_OBSERVATION)],
            )

    def test_not_executed_pode_ser_registrado_sem_evidence_e_nao_e_positivo(self) -> None:
        claim = self.claim(status=VerificationStatus.NOT_EXECUTED)
        self.assertEqual(claim.evidence, ())
        self.assertIs(claim.status, VerificationStatus.NOT_EXECUTED)

    def test_unavailable_e_inconclusive_permanecem_distintos(self) -> None:
        unavailable = self.claim(status=VerificationStatus.UNAVAILABLE)
        inconclusive = self.claim(status=VerificationStatus.INCONCLUSIVE)
        self.assertIs(unavailable.status, VerificationStatus.UNAVAILABLE)
        self.assertIs(inconclusive.status, VerificationStatus.INCONCLUSIVE)
        self.assertNotEqual(unavailable.status, inconclusive.status)

    def test_unavailable_pode_preservar_limitacao_fornecida(self) -> None:
        item = self.evidence(
            EvidenceKind.REPORTED,
            limitation="ambiente indisponível",
            verifiability="UNAVAILABLE",
        )
        claim = self.claim(
            status=VerificationStatus.UNAVAILABLE,
            evidence=[item],
        )
        self.assertEqual(claim.evidence[0].limitation, "ambiente indisponível")
        self.assertEqual(claim.evidence[0].verifiability, "UNAVAILABLE")

    def test_estado_arbitrario_nao_e_coagido(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "VerificationStatus explícito"):
            self.claim(status="PASS")  # type: ignore[arg-type]

    def test_claim_nao_e_criado_positivamente_por_ausencia_de_erro(self) -> None:
        with self.assertRaises(ReviewInputError):
            self.claim(evidence=())

    def test_mutacao_da_lista_original_nao_altera_claim(self) -> None:
        first = self.evidence(reference="test://first")
        second = self.evidence(reference="test://second")
        references = [second, first]
        claim = self.claim(evidence=references)
        references.clear()
        self.assertEqual(len(claim.evidence), 2)
        self.assertEqual(
            tuple(item.reference for item in claim.evidence),
            ("test://first", "test://second"),
        )

    def test_claim_rejeita_tipo_de_evidence_incorreto(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "somente EvidenceReference"):
            self.claim(evidence=["test passou"])

    def test_referencia_de_evidence_duplicada_e_rejeitada(self) -> None:
        item = self.evidence()
        with self.assertRaisesRegex(ReviewInputError, "duplicadas"):
            self.claim(evidence=[item, item])

    def test_provenance_states_sao_preservados_sem_se_tornarem_claim_states(self) -> None:
        item = self.evidence(
            EvidenceKind.PERSISTED_EVIDENCE, verifiability="CHANGED_REASSESS"
        )
        claim = self.claim(
            status=VerificationStatus.HISTORICAL_IDENTIFIED, evidence=[item]
        )
        self.assertEqual(claim.evidence[0].verifiability, "CHANGED_REASSESS")
        self.assertIs(claim.status, VerificationStatus.HISTORICAL_IDENTIFIED)


class TechnicalDimensionTests(unittest.TestCase):
    @staticmethod
    def evidence(reference: str = "test://assessment") -> EvidenceReference:
        return EvidenceReference(
            EvidenceKind.DIRECT_OBSERVATION, "fixture", reference, "scope-a"
        )

    @classmethod
    def specialist(cls, **overrides: object) -> SpecialistAssessment:
        authority = AuthorityReference(
            "authority:owner-a", "owner-a", "competence:patterns", ("scope-a",)
        )
        values: dict[str, object] = {
            "dimension": TechnicalDimension.PATTERNS,
            "scope": "scope-a",
            "conclusion": "Avaliação recebida no escopo informado.",
            "evidence": (cls.evidence(),),
            "character": AssessmentCharacter.CONSULTATIVE,
            "owner": "owner-a",
            "competence_reference": "competence:patterns",
        }
        values.update(overrides)
        if values.get("character") is AssessmentCharacter.AUTHORITATIVE:
            values.setdefault("authority_reference", authority)
        return SpecialistAssessment(**values)  # type: ignore[arg-type]

    def test_conjunto_exato_e_ordem_canonica_das_dimensoes(self) -> None:
        self.assertEqual(
            tuple(item.name for item in TechnicalDimension),
            (
                "PATTERNS", "SOLID", "INTERFACE_ARCHITECTURE", "CLEAN_CODE",
                "DELPHI_OBJECT_PASCAL", "OBJECTIVE_NORMATIVE_RULES", "QUALITY_AUDIT",
            ),
        )

    def test_estados_de_dimensao_validos_sem_inferir_resultado(self) -> None:
        for state in (
            DimensionAssessmentState.NOT_APPLICABLE,
            DimensionAssessmentState.NOT_ASSESSED_INSUFFICIENT_EVIDENCE,
            DimensionAssessmentState.SPECIALIST_REQUIRED,
            DimensionAssessmentState.CORE_SCOPE_ASSESSMENT,
        ):
            with self.subTest(state=state):
                assessment = DimensionAssessment(TechnicalDimension.SOLID, "scope-a", state)
                self.assertIs(assessment.state, state)

    def test_specialist_assessment_received_exige_avaliacao_correspondente(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "requer SpecialistAssessment"):
            DimensionAssessment(
                TechnicalDimension.PATTERNS, "scope-a",
                DimensionAssessmentState.SPECIALIST_ASSESSMENT_RECEIVED,
            )
        specialist = self.specialist()
        result = DimensionAssessment(
            TechnicalDimension.PATTERNS, "scope-a",
            DimensionAssessmentState.SPECIALIST_ASSESSMENT_RECEIVED,
            specialist_assessment=specialist,
        )
        self.assertIs(result.specialist_assessment, specialist)

    def test_specialist_consultative_nao_e_promovida(self) -> None:
        assessment = self.specialist()
        self.assertIs(assessment.character, AssessmentCharacter.CONSULTATIVE)
        assessment.validate_authority(AuthorityContext())
        self.assertIs(assessment.character, AssessmentCharacter.CONSULTATIVE)

    def test_authoritative_requer_owner_competencia_authority_evidence(self) -> None:
        required = {
            "character": AssessmentCharacter.AUTHORITATIVE,
            "authority_reference": AuthorityReference(
                "authority:owner-a", "owner-a", "competence:patterns", ("scope-a",)
            ),
        }
        for field, value, expected in (
            ("owner", None, "owner explícito"),
            ("competence_reference", None, "competence_reference"),
            ("evidence", (), "evidência explícita"),
        ):
            args = dict(required)
            args[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ReviewInputError, expected):
                self.specialist(**args)

    def test_authoritative_corresponde_a_referencia_explicita_no_contexto(self) -> None:
        reference = AuthorityReference(
            "authority:owner-a", "owner-a", "competence:patterns", ("scope-a",)
        )
        assessment = self.specialist(
            character=AssessmentCharacter.AUTHORITATIVE,
            authority_reference=reference,
        )
        assessment.validate_authority(AuthorityContext(authorities=[reference]))
        with self.assertRaisesRegex(ReviewInputError, "contexto explícito"):
            assessment.validate_authority(AuthorityContext())

    def test_dimensao_nao_inventa_owner_e_scope_vazio_e_rejeitado(self) -> None:
        assessment = self.specialist(owner=None, competence_reference=None)
        self.assertIsNone(assessment.owner)
        with self.assertRaisesRegex(ReviewInputError, "scope"):
            self.specialist(scope=" ")
        with self.assertRaisesRegex(ReviewInputError, "conclusion"):
            self.specialist(conclusion=" ")

    def test_enums_arbitrarios_e_evidencia_de_tipo_incorreto_sao_rejeitados(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "TechnicalDimension explícita"):
            DimensionAssessment("PATTERNS", "scope-a", DimensionAssessmentState.NOT_APPLICABLE)  # type: ignore[arg-type]
        with self.assertRaisesRegex(ReviewInputError, "DimensionAssessmentState explícito"):
            DimensionAssessment(TechnicalDimension.PATTERNS, "scope-a", "NOT_APPLICABLE")  # type: ignore[arg-type]
        with self.assertRaisesRegex(ReviewInputError, "AssessmentCharacter explícito"):
            self.specialist(character="CONSULTATIVE")  # type: ignore[arg-type]
        with self.assertRaisesRegex(ReviewInputError, "somente EvidenceReference"):
            self.specialist(evidence=["report"])

    def test_evidencia_duplicada_e_assessment_incompativel_sao_rejeitados(self) -> None:
        item = self.evidence()
        with self.assertRaisesRegex(ReviewInputError, "duplicadas"):
            self.specialist(evidence=[item, item])
        with self.assertRaisesRegex(ReviewInputError, "dimensão e ao escopo"):
            DimensionAssessment(
                TechnicalDimension.SOLID, "scope-a",
                DimensionAssessmentState.SPECIALIST_ASSESSMENT_RECEIVED,
                specialist_assessment=self.specialist(),
            )

    def test_estados_nao_carregam_decisao_contraditoria(self) -> None:
        authoritative = self.specialist(character=AssessmentCharacter.AUTHORITATIVE)
        for state in (
            DimensionAssessmentState.NOT_APPLICABLE,
            DimensionAssessmentState.SPECIALIST_REQUIRED,
            DimensionAssessmentState.CORE_SCOPE_ASSESSMENT,
        ):
            with self.subTest(state=state), self.assertRaises(ReviewInputError):
                DimensionAssessment(
                    TechnicalDimension.PATTERNS, "scope-a", state,
                    specialist_assessment=authoritative,
                )

    def test_colecoes_sao_copiadas_ordenadas_e_objetos_sao_imutaveis(self) -> None:
        first = self.evidence("test://a")
        second = self.evidence("test://b")
        provided = [second, first]
        specialist = self.specialist(evidence=provided)
        provided.clear()
        self.assertEqual(tuple(item.reference for item in specialist.evidence),
                         ("test://a", "test://b"))
        values = [second, first]
        assessment = DimensionAssessment(
            TechnicalDimension.PATTERNS, "scope-a",
            DimensionAssessmentState.NOT_ASSESSED_INSUFFICIENT_EVIDENCE,
            evidence=values,
        )
        values.clear()
        self.assertEqual(len(assessment.evidence), 2)
        with self.assertRaises(FrozenInstanceError):
            assessment.scope = "other"  # type: ignore[misc]
        with self.assertRaises(FrozenInstanceError):
            specialist.conclusion = "alterada"  # type: ignore[misc]

    def test_multiplas_dimensoes_coexistem_sem_regra_substantiva(self) -> None:
        assessments = (
            DimensionAssessment(TechnicalDimension.PATTERNS, "scope-a", DimensionAssessmentState.NOT_APPLICABLE),
            DimensionAssessment(TechnicalDimension.SOLID, "scope-a", DimensionAssessmentState.SPECIALIST_REQUIRED),
        )
        self.assertEqual(tuple(item.dimension for item in assessments),
                         (TechnicalDimension.PATTERNS, TechnicalDimension.SOLID))


class ReviewFindingTests(unittest.TestCase):
    @staticmethod
    def evidence(target: str = "Cliente.pas", reference: str = "test://evidence") -> EvidenceReference:
        return EvidenceReference(EvidenceKind.DIRECT_OBSERVATION, "fixture", reference, target, "v1")

    @staticmethod
    def finding(**overrides: object) -> ReviewFinding:
        values: dict[str, object] = {
            "scope": "ClasseCliente",
            "dimension": TechnicalDimension.DELPHI_OBJECT_PASCAL,
            "condition": "A classe não possui teste de contrato",
            "evidence": (ReviewFindingTests.evidence(),),
            "normative_reference": "contract:cliente",
            "technical_conclusion": "A evidência indica lacuna no contrato informado.",
            "impact": "A regressão nesse comportamento pode passar despercebida.",
        }
        values.update(overrides)
        return ReviewFinding(**values)  # type: ignore[arg-type]

    def test_finding_e_recomendacao_opcional_preservam_rastreabilidade(self) -> None:
        finding = self.finding(recommendation=None)
        self.assertEqual(finding.scope, "ClasseCliente")
        self.assertEqual(finding.evidence[0].target, "Cliente.pas")
        self.assertEqual(finding.normative_reference, "contract:cliente")
        self.assertIn("lacuna", finding.technical_conclusion)
        self.assertIn("regressão", finding.impact)
        self.assertIsNone(finding.recommendation)
        recommended = self.finding(recommendation="Adicionar teste de contrato.")
        self.assertEqual(recommended.recommendation, "Adicionar teste de contrato.")

    def test_campos_obrigatorios_e_recomendacao_vazia_sao_rejeitados(self) -> None:
        for field in ("scope", "condition", "normative_reference", "technical_conclusion", "impact"):
            with self.subTest(field=field), self.assertRaises(ReviewInputError):
                self.finding(**{field: " "})
        with self.assertRaisesRegex(ReviewInputError, "recommendation"):
            self.finding(recommendation=" ")

    def test_tipo_e_dimension_especifica_sao_obrigatorios(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "TechnicalDimension explícita"):
            self.finding(dimension="DELPHI_OBJECT_PASCAL")
        with self.assertRaisesRegex(ReviewInputError, "ao menos uma EvidenceReference"):
            self.finding(evidence=())
        with self.assertRaisesRegex(ReviewInputError, "somente EvidenceReference"):
            self.finding(evidence=["teste observado"])
        item = self.evidence()
        with self.assertRaisesRegex(ReviewInputError, "duplicadas"):
            self.finding(evidence=[item, item])

    def test_specialist_assessment_preserva_carater_e_requer_correspondencia(self) -> None:
        authority = AuthorityReference("owner-ref", "owner informado", "competência", ("ClasseCliente",))
        specialist = SpecialistAssessment(
            TechnicalDimension.DELPHI_OBJECT_PASCAL,
            "ClasseCliente",
            "Avaliação consultiva recebida.",
            (self.evidence(reference="test://specialist"),),
            AssessmentCharacter.CONSULTATIVE,
            owner="owner informado",
            competence_reference="competência",
        )
        finding = self.finding(
            technical_conclusion=specialist.conclusion,
            specialist_assessment=specialist,
        )
        self.assertIs(finding.specialist_assessment.character, AssessmentCharacter.CONSULTATIVE)
        self.assertIsNot(finding.specialist_assessment.character, AssessmentCharacter.AUTHORITATIVE)
        self.assertEqual(finding.evidence[0].reference, "test://evidence")
        with self.assertRaisesRegex(ReviewInputError, "dimensão e ao escopo"):
            self.finding(specialist_assessment=SpecialistAssessment(
                TechnicalDimension.SOLID, "ClasseCliente", specialist.conclusion,
                (self.evidence(reference="test://other"),), AssessmentCharacter.CONSULTATIVE,
            ))
        with self.assertRaisesRegex(ReviewInputError, "technical_conclusion deve preservar"):
            self.finding(specialist_assessment=specialist)
        self.assertEqual(authority.scopes, ("ClasseCliente",))

    def test_scope_incompativel_no_specialist_assessment_e_rejeitado(self) -> None:
        finding_dimension = TechnicalDimension.DELPHI_OBJECT_PASCAL
        finding_scope = "ClasseCliente"
        specialist = SpecialistAssessment(
            dimension=TechnicalDimension.DELPHI_OBJECT_PASCAL,
            scope="OutroEscopo",
            conclusion="Conclusão recebida para outro escopo.",
            evidence=(self.evidence(reference="test://other-scope"),),
            character=AssessmentCharacter.CONSULTATIVE,
        )
        self.assertIs(specialist.dimension, finding_dimension)
        self.assertNotEqual(specialist.scope, finding_scope)
        with self.assertRaisesRegex(ReviewInputError, "dimensão e ao escopo"):
            self.finding(scope=finding_scope, dimension=finding_dimension,
                         specialist_assessment=specialist)

    def test_owner_nao_e_inferido_por_dimension(self) -> None:
        finding = self.finding()
        self.assertFalse(hasattr(finding, "owner"))
        self.assertIsNone(finding.specialist_assessment)

    def test_finding_e_imutavel_e_copia_evidence(self) -> None:
        item = self.evidence()
        entries = [item]
        finding = self.finding(evidence=entries)
        entries.clear()
        self.assertEqual(finding.evidence, (item,))
        with self.assertRaises(FrozenInstanceError):
            finding.scope = "projeto"  # type: ignore[misc]

    def test_sort_key_aplica_scope_rank_referencia_casefold_e_desempate(self) -> None:
        def item(scope: str, dimension: TechnicalDimension, normative: str, condition: str) -> ReviewFinding:
            return self.finding(scope=scope, dimension=dimension,
                                normative_reference=normative, condition=condition)
        findings = [
            item("b", TechnicalDimension.PATTERNS, "a", "z"),
            item("a", TechnicalDimension.SOLID, "a", "x"),
            item("a", TechnicalDimension.PATTERNS, "b", "x"),
            item("a", TechnicalDimension.PATTERNS, "a", "beta"),
            item("a", TechnicalDimension.PATTERNS, "a", "Alpha"),
            item("a", TechnicalDimension.PATTERNS, "a", "alpha"),
        ]
        ordered = sort_review_findings(findings)
        self.assertEqual(
            [(f.scope, f.dimension, f.normative_reference, f.condition) for f in ordered],
            [
                ("a", TechnicalDimension.PATTERNS, "a", "Alpha"),
                ("a", TechnicalDimension.PATTERNS, "a", "alpha"),
                ("a", TechnicalDimension.PATTERNS, "a", "beta"),
                ("a", TechnicalDimension.PATTERNS, "b", "x"),
                ("a", TechnicalDimension.SOLID, "a", "x"),
                ("b", TechnicalDimension.PATTERNS, "a", "z"),
            ],
        )
        self.assertEqual(sort_review_findings(findings), sort_review_findings(tuple(reversed(findings))))
        self.assertLess(
            item("a", TechnicalDimension.PATTERNS, "a", "x").sort_key[1],
            item("a", TechnicalDimension.SOLID, "a", "x").sort_key[1],
        )


class ChangeProposalTests(unittest.TestCase):
    @staticmethod
    def request(
        grants: tuple[AuthorizationGrant, ...] = (
            AuthorizationGrant.REVIEW,
            AuthorizationGrant.STRUCTURAL_CHANGE,
        ),
        *,
        targets: tuple[str, ...] = ("src/a.py",),
        authorized: tuple[str, ...] | None = None,
        excluded: tuple[str, ...] = (),
        objective: str = "Revisar o comportamento de A",
    ) -> ReviewRequest:
        scope = ReviewScope("scope-a", "Escopo A", (), targets)
        return ReviewRequest(
            objective=objective,
            scopes=(scope,),
            authorized_artifacts=targets if authorized is None else authorized,
            excluded_artifacts=excluded,
            expected_outcome="Avaliação limitada",
            authorization_grants=grants,
            requested_effects=(),
        )

    @staticmethod
    def proposal(**overrides: object) -> ChangeProposal:
        values: dict[str, object] = {
            "kind": ChangeKind.STRUCTURAL,
            "scope": "scope-a",
            "targets": ("src/a.py",),
            "proposal_reference": "diff-ref-1",
            "technical_reason": "Remover duplicação constatada",
            "behavior_intent": BehaviorIntent.PRESERVE,
            "consequences": "Reduz duplicação no escopo informado",
            "objective_reference": "Revisar o comportamento de A",
        }
        values.update(overrides)
        return ChangeProposal(**values)  # type: ignore[arg-type]

    @staticmethod
    def observed_claim(target: str, version: str, case: str) -> VerificationClaim:
        reference = EvidenceReference(
            EvidenceKind.DIRECT_OBSERVATION,
            "test-run",
            f"run:{version}:{case}",
            target,
            version=version,
        )
        return VerificationClaim(
            assertion=case,
            target=target,
            status=VerificationStatus.EXECUTED_OBSERVED,
            evidence=(reference,),
            version=version,
        )

    @staticmethod
    def comparison(
        target: str = "src/a.py",
        case: str = "case:public-api",
        base: str = "base-1",
        candidate: str = "candidate-1",
        *,
        status: VerificationStatus = VerificationStatus.EXECUTED_OBSERVED,
        kind: EvidenceKind = EvidenceKind.DIRECT_OBSERVATION,
        limitation: str | None = None,
        reference: str = "compare:run-1",
        claim_case: str | None = None,
    ) -> BehaviorComparison:
        evidence = EvidenceReference(
            kind, "comparison-run", reference, target, limitation=limitation
        )
        claim = VerificationClaim(
            assertion=case if claim_case is None else claim_case,
            target=target, status=status,
            evidence=(evidence,),
        )
        return BehaviorComparison(
            target, case, base, candidate, reference, claim
        )

    def compared_proposal(self, **overrides: object) -> ChangeProposal:
        values: dict[str, object] = {
            "base_versions": (("src/a.py", "base-1"),),
            "candidate_versions": (("src/a.py", "candidate-1"),),
            "behavior_contract": "API pública conserva o contrato declarado",
            "verified_cases": ("case:public-api",),
            "comparisons": (self.comparison(),),
        }
        values.update(overrides)
        return self.proposal(**values)

    def complete_proposal(self, **overrides: object) -> ChangeProposal:
        claims = tuple(
            self.observed_claim("src/a.py", version, "case:public-api")
            for version in ("base-1", "candidate-1")
        )
        values: dict[str, object] = {
            "base_versions": (("src/a.py", "base-1"),),
            "candidate_versions": (("src/a.py", "candidate-1"),),
            "behavior_contract": "API pública conserva o contrato declarado",
            "verified_cases": ("case:public-api",),
            "claims": claims,
        }
        values.update(overrides)
        return self.proposal(**values)

    def test_proposta_estrutural_valida_com_grants_suficientes(self) -> None:
        result = assess_change_proposal(
            self.proposal(), self.request()
        )
        self.assertIs(result.state, BehaviorAssessmentState.NOT_VERIFIED)
        self.assertEqual(result.proposal.targets, ("src/a.py",))

    def test_estados_de_behavior_assessment_sao_exatamente_os_cinco_previstos(self) -> None:
        self.assertEqual(
            {item.value for item in BehaviorAssessmentState},
            {"PRESERVATION_EVIDENCED", "PRESERVATION_ASSERTED", "NOT_VERIFIED",
             "FUNCTIONAL_CHANGE_AUTHORIZED", "FUNCTIONAL_CHANGE_UNAUTHORIZED"},
        )

    def test_enums_arbitrarios_nao_sao_coagidos(self) -> None:
        with self.assertRaises(ReviewInputError):
            self.proposal(kind="STRUCTURAL")
        with self.assertRaises(ReviewInputError):
            self.proposal(behavior_intent="PRESERVE")

    def test_mudanca_estrutural_sem_grant_e_rejeitada(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "STRUCTURAL_CHANGE"):
            assess_change_proposal(
                self.proposal(), self.request((AuthorizationGrant.REVIEW,))
            )

    def test_mudanca_funcional_com_grants_e_classificada_como_funcional(self) -> None:
        proposal = self.proposal(
            kind=ChangeKind.FUNCTIONAL,
            behavior_intent=BehaviorIntent.CHANGE,
        )
        request = self.request((
            AuthorizationGrant.REVIEW,
            AuthorizationGrant.STRUCTURAL_CHANGE,
            AuthorizationGrant.FUNCTIONAL_CHANGE,
        ))
        self.assertIs(
            assess_change_proposal(proposal, request).state,
            BehaviorAssessmentState.FUNCTIONAL_CHANGE_AUTHORIZED,
        )

    def test_mudanca_funcional_sem_grant_fica_explicitamente_nao_autorizada(self) -> None:
        proposal = self.proposal(
            kind=ChangeKind.FUNCTIONAL,
            behavior_intent=BehaviorIntent.CHANGE,
        )
        self.assertIs(
            assess_change_proposal(proposal, self.request()).state,
            BehaviorAssessmentState.FUNCTIONAL_CHANGE_UNAUTHORIZED,
        )

    def test_target_fora_da_allowlist_e_rejeitado(self) -> None:
        proposal = self.proposal(targets=("src/other.py",))
        with self.assertRaisesRegex(ReviewInputError, "autorizados"):
            assess_change_proposal(proposal, self.request())

    def test_target_excluido_e_rejeitado(self) -> None:
        proposal = self.proposal()
        request = self.request(authorized=(), excluded=("src/a.py",))
        with self.assertRaisesRegex(ReviewInputError, "excluído"):
            assess_change_proposal(proposal, request)

    def test_ausencia_de_versao_base_nao_prova_preservacao(self) -> None:
        proposal = self.complete_proposal(base_versions=())
        self.assertIs(assess_change_proposal(proposal, self.request()).state,
                      BehaviorAssessmentState.NOT_VERIFIED)

    def test_ausencia_de_versao_candidata_nao_prova_preservacao(self) -> None:
        proposal = self.complete_proposal(candidate_versions=())
        self.assertIs(assess_change_proposal(proposal, self.request()).state,
                      BehaviorAssessmentState.NOT_VERIFIED)

    def test_contrato_ausente_nao_prova_preservacao(self) -> None:
        proposal = self.complete_proposal(behavior_contract=None)
        self.assertIs(assess_change_proposal(proposal, self.request()).state,
                      BehaviorAssessmentState.NOT_VERIFIED)

    def test_claims_observados_nas_duas_versoes_sustentam_preservacao_limitada(self) -> None:
        result = assess_change_proposal(self.complete_proposal(), self.request())
        self.assertIs(result.state, BehaviorAssessmentState.PRESERVATION_EVIDENCED)

    def test_comparacao_explicitamente_identificada_sustenta_preservacao_limitada(self) -> None:
        proposal = self.compared_proposal()
        assessment = assess_change_proposal(proposal, self.request())
        self.assertIs(assessment.state, BehaviorAssessmentState.PRESERVATION_EVIDENCED)

    def test_referencia_textual_sem_objeto_comparacao_nao_evidencia_preservacao(self) -> None:
        proposal = self.proposal(
            proposal_reference="comparado e equivalente",
            preservation_assertion="A comparação foi concluída.",
        )
        self.assertIs(assess_change_proposal(proposal, self.request()).state,
                      BehaviorAssessmentState.PRESERVATION_ASSERTED)

    def test_comparacao_sem_versao_base_ou_candidata_nao_evidencia(self) -> None:
        for field in ("base_versions", "candidate_versions"):
            values: dict[str, object] = {field: ()}
            proposal = self.compared_proposal(**values)
            with self.subTest(field=field):
                self.assertIs(assess_change_proposal(proposal, self.request()).state,
                              BehaviorAssessmentState.NOT_VERIFIED)

    def test_comparacao_requer_claim_executed_observed(self) -> None:
        for status in (VerificationStatus.HISTORICAL_IDENTIFIED,
                       VerificationStatus.NOT_EXECUTED,
                       VerificationStatus.UNAVAILABLE,
                       VerificationStatus.INCONCLUSIVE):
            with self.subTest(status=status), self.assertRaises(ReviewInputError):
                self.comparison(status=status)

    def test_comparacao_requer_evidencia_direta_localizavel(self) -> None:
        for kind in (EvidenceKind.REPORTED, EvidenceKind.INFERENCE):
            with self.subTest(kind=kind), self.assertRaises(ReviewInputError):
                self.comparison(kind=kind)
        with self.assertRaisesRegex(ReviewInputError, "locator"):
            self.comparison(limitation="Comparação parcial")

    def test_comparacao_de_target_ou_caso_incompativel_nao_e_aceita(self) -> None:
        with self.assertRaises(ReviewInputError):
            self.compared_proposal(comparisons=(self.comparison(target="src/b.py"),))
        with self.assertRaises(ReviewInputError):
            self.comparison(claim_case="case:different")

    def test_comparacao_com_versoes_divergentes_nao_evidencia_preservacao(self) -> None:
        proposal = self.compared_proposal(
            comparisons=(self.comparison(base="other-base"),)
        )
        self.assertIs(assess_change_proposal(proposal, self.request()).state,
                      BehaviorAssessmentState.NOT_VERIFIED)

    def test_comparacao_de_caso_nao_declarado_nao_evidencia_preservacao(self) -> None:
        proposal = self.compared_proposal(
            comparisons=(self.comparison(case="case:other"),)
        )
        self.assertIs(assess_change_proposal(proposal, self.request()).state,
                      BehaviorAssessmentState.NOT_VERIFIED)

    def test_comparacao_limitada_nao_evidencia_preservacao(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "locator"):
            self.comparison(limitation="Não cobre o caso declarado")

    def test_multiplos_targets_e_casos_exigem_comparacao_para_cada_combinacao(self) -> None:
        targets = ("src/a.py", "src/b.py")
        cases = ("case:one", "case:two")
        request = self.request(targets=targets)
        comparisons = tuple(
            self.comparison(target, case)
            for target in targets for case in cases
        )
        kwargs = {
            "targets": targets,
            "base_versions": tuple((target, "base-1") for target in targets),
            "candidate_versions": tuple((target, "candidate-1") for target in targets),
            "verified_cases": cases,
            "comparisons": comparisons,
        }
        complete = self.compared_proposal(**kwargs)
        self.assertIs(assess_change_proposal(complete, request).state,
                      BehaviorAssessmentState.PRESERVATION_EVIDENCED)
        partial = self.compared_proposal(**{**kwargs, "comparisons": comparisons[:-1]})
        self.assertIs(assess_change_proposal(partial, request).state,
                      BehaviorAssessmentState.NOT_VERIFIED)

    def test_comparacao_e_proposta_sao_imutaveis_e_copiam_colecoes(self) -> None:
        comparisons = [self.comparison()]
        proposal = self.compared_proposal(comparisons=comparisons)
        comparisons.clear()
        self.assertEqual(len(proposal.comparisons), 1)
        with self.assertRaises(FrozenInstanceError):
            proposal.comparisons[0].case = "other"  # type: ignore[misc]

    def test_historico_identificado_nao_prova_preservacao_atual(self) -> None:
        historical = VerificationClaim(
            "case:public-api", "src/a.py", VerificationStatus.HISTORICAL_IDENTIFIED,
            (EvidenceReference(EvidenceKind.PERSISTED_EVIDENCE, "archive", "doc:1",
                               "src/a.py", version="base-1"),), version="base-1"
        )
        proposal = self.complete_proposal(claims=(historical,))
        self.assertIs(assess_change_proposal(proposal, self.request()).state,
                      BehaviorAssessmentState.NOT_VERIFIED)

    def test_not_executed_unavailable_e_inconclusive_nao_provam_preservacao(self) -> None:
        for status in (VerificationStatus.NOT_EXECUTED,
                       VerificationStatus.UNAVAILABLE,
                       VerificationStatus.INCONCLUSIVE):
            claim = VerificationClaim("case:public-api", "src/a.py", status,
                                      version="base-1")
            proposal = self.complete_proposal(claims=(claim,))
            with self.subTest(status=status):
                self.assertIs(assess_change_proposal(proposal, self.request()).state,
                              BehaviorAssessmentState.NOT_VERIFIED)

    def test_relato_textual_isolado_permanece_asserted(self) -> None:
        proposal = self.proposal(preservation_assertion="O host relata preservação.")
        self.assertIs(assess_change_proposal(proposal, self.request()).state,
                      BehaviorAssessmentState.PRESERVATION_ASSERTED)

    def test_boolean_behavior_preserved_nao_faz_parte_do_contrato(self) -> None:
        with self.assertRaises(TypeError):
            self.proposal(behavior_preserved=True)

    def test_ausencia_de_erro_nao_gera_preservacao(self) -> None:
        self.assertIs(assess_change_proposal(self.proposal(), self.request()).state,
                      BehaviorAssessmentState.NOT_VERIFIED)

    def test_todos_os_targets_devem_estar_explicitamente_allowlisted(self) -> None:
        request = self.request(targets=("src/a.py",))
        proposal = self.proposal(targets=("src/a.py", "src/b.py"))
        with self.assertRaises(ReviewInputError):
            assess_change_proposal(proposal, request)

    def test_target_explicitamente_excluido_bloqueia_multiplos_targets(self) -> None:
        request = self.request(targets=("src/a.py", "src/b.py"),
                               authorized=("src/a.py",), excluded=("src/b.py",))
        proposal = self.proposal(targets=("src/a.py", "src/b.py"))
        with self.assertRaisesRegex(ReviewInputError, "excluído"):
            assess_change_proposal(proposal, request)

    def test_proposta_e_assessment_sao_imutaveis(self) -> None:
        targets = ["src/a.py"]
        proposal = self.proposal(targets=targets)
        targets.append("src/b.py")
        result = assess_change_proposal(proposal, self.request())
        self.assertEqual(proposal.targets, ("src/a.py",))
        with self.assertRaises(FrozenInstanceError):
            result.state = BehaviorAssessmentState.NOT_VERIFIED  # type: ignore[misc]

    def test_mutacao_das_colecoes_originais_nao_altera_proposta_ou_assessment(self) -> None:
        targets = ["src/a.py"]
        cases = ["case:public-api"]
        proposal = self.complete_proposal(targets=targets, verified_cases=cases)
        assessment = assess_change_proposal(proposal, self.request())
        targets.append("src/b.py")
        cases.clear()
        self.assertEqual(proposal.targets, ("src/a.py",))
        self.assertEqual(proposal.verified_cases, ("case:public-api",))
        self.assertIs(assessment.state, BehaviorAssessmentState.PRESERVATION_EVIDENCED)

    def test_objetivo_da_proposta_deve_corresponder_ao_pedido(self) -> None:
        proposal = self.proposal(objective_reference="qualquer objetivo")
        with self.assertRaisesRegex(ReviewInputError, "objective do pedido"):
            assess_change_proposal(proposal, self.request())

    def test_objetivo_textual_nao_concede_grant_ausente(self) -> None:
        request = self.request((AuthorizationGrant.REVIEW,), objective="Refatorar e corrigir tudo")
        proposal = self.proposal(objective_reference=request.objective)
        with self.assertRaisesRegex(ReviewInputError, "STRUCTURAL_CHANGE"):
            assess_change_proposal(proposal, request)

    def test_finding_existente_e_reutilizado_sem_duplicacao(self) -> None:
        evidence = EvidenceReference(EvidenceKind.DIRECT_OBSERVATION, "test", "run:1",
                                     "src/a.py", version="base-1")
        finding = ReviewFinding(
            scope="scope-a", dimension=TechnicalDimension.SOLID,
            condition="Duplicação observada", evidence=(evidence,),
            normative_reference="rule:1", technical_conclusion="Refatorar",
            impact="Manutenção", recommendation="Revisar proposta",
        )
        proposal = self.proposal(finding=finding, objective_reference=None)
        assessment = assess_change_proposal(proposal, self.request())
        self.assertIs(assessment.proposal.finding, finding)

    def test_finding_de_outro_scope_ou_sem_target_e_rejeitado(self) -> None:
        evidence = EvidenceReference(EvidenceKind.DIRECT_OBSERVATION, "test", "run:1",
                                     "elsewhere.py")
        finding = ReviewFinding(
            scope="other", dimension=TechnicalDimension.SOLID, condition="Fato",
            evidence=(evidence,), normative_reference="rule:1",
            technical_conclusion="Conclusão", impact="Impacto",
        )
        proposal = self.proposal(finding=finding, objective_reference=None)
        with self.assertRaises(ReviewInputError):
            assess_change_proposal(proposal, self.request())

    def test_versao_generica_e_preservada_sem_resolucao_externa(self) -> None:
        proposal = self.complete_proposal(
            base_versions=(("src/a.py", "latest"),),
            candidate_versions=(("src/a.py", "current"),),
            claims=(self.observed_claim("src/a.py", "latest", "case:public-api"),
                    self.observed_claim("src/a.py", "current", "case:public-api")),
        )
        self.assertEqual(proposal.base_versions, (("src/a.py", "latest"),))
        self.assertIs(assess_change_proposal(proposal, self.request()).state,
                      BehaviorAssessmentState.PRESERVATION_EVIDENCED)

    def test_claim_somente_base_ou_somente_candidata_nao_prova_preservacao(self) -> None:
        for version in ("base-1", "candidate-1"):
            proposal = self.complete_proposal(
                claims=(self.observed_claim("src/a.py", version, "case:public-api"),)
            )
            with self.subTest(version=version):
                self.assertIs(assess_change_proposal(proposal, self.request()).state,
                              BehaviorAssessmentState.NOT_VERIFIED)

    def test_preservacao_exige_cobertura_de_cada_target_e_versao(self) -> None:
        targets = ("src/a.py", "src/b.py")
        request = self.request(targets=targets)
        claims = tuple(
            self.observed_claim(target, version, "case:public-api")
            for target in targets
            for version in ("base-1", "candidate-1")
        )
        proposal = self.complete_proposal(
            targets=targets,
            base_versions=tuple((target, "base-1") for target in targets),
            candidate_versions=tuple((target, "candidate-1") for target in targets),
            claims=claims,
        )
        self.assertIs(assess_change_proposal(proposal, request).state,
                      BehaviorAssessmentState.PRESERVATION_EVIDENCED)
        partial = self.complete_proposal(
            targets=targets,
            base_versions=tuple((target, "base-1") for target in targets),
            candidate_versions=tuple((target, "candidate-1") for target in targets),
            claims=claims[:-1],
        )
        self.assertIs(assess_change_proposal(partial, request).state,
                      BehaviorAssessmentState.NOT_VERIFIED)

    def test_versoes_sem_contrato_ou_casos_nao_provam_preservacao(self) -> None:
        proposal = self.complete_proposal(verified_cases=())
        self.assertIs(assess_change_proposal(proposal, self.request()).state,
                      BehaviorAssessmentState.NOT_VERIFIED)

    def test_claim_com_target_ou_versao_divergente_nao_sustenta_preservacao(self) -> None:
        wrong_target = self.observed_claim("src/a.py", "base-1", "case:public-api")
        wrong_version = self.observed_claim("src/a.py", "other-version", "case:public-api")
        proposal = self.complete_proposal(claims=(wrong_target, wrong_version))
        self.assertIs(assess_change_proposal(proposal, self.request()).state,
                      BehaviorAssessmentState.NOT_VERIFIED)

    def test_evidencia_com_limitacao_material_nao_sustenta_preservacao(self) -> None:
        limited = VerificationClaim(
            "case:public-api", "src/a.py", VerificationStatus.EXECUTED_OBSERVED,
            (EvidenceReference(EvidenceKind.DIRECT_OBSERVATION, "test", "run:base",
                               "src/a.py", version="base-1", limitation="Execução parcial"),),
            version="base-1",
        )
        proposal = self.complete_proposal(claims=(limited, self.observed_claim(
            "src/a.py", "candidate-1", "case:public-api")))
        self.assertIs(assess_change_proposal(proposal, self.request()).state,
                      BehaviorAssessmentState.NOT_VERIFIED)

    def test_evidencia_explicitamente_unavailable_nao_sustenta_preservacao(self) -> None:
        unavailable = VerificationClaim(
            "case:public-api", "src/a.py", VerificationStatus.EXECUTED_OBSERVED,
            (EvidenceReference(EvidenceKind.DIRECT_OBSERVATION, "test", "run:base",
                               "src/a.py", version="base-1", verifiability="UNAVAILABLE"),),
            version="base-1",
        )
        proposal = self.complete_proposal(claims=(unavailable, self.observed_claim(
            "src/a.py", "candidate-1", "case:public-api")))
        self.assertIs(assess_change_proposal(proposal, self.request()).state,
                      BehaviorAssessmentState.NOT_VERIFIED)

    def test_mudanca_funcional_autorizada_nao_e_rotulada_como_preservacao(self) -> None:
        proposal = self.complete_proposal(
            kind=ChangeKind.FUNCTIONAL,
            behavior_intent=BehaviorIntent.CHANGE,
        )
        request = self.request((AuthorizationGrant.REVIEW,
                                 AuthorizationGrant.STRUCTURAL_CHANGE,
                                 AuthorizationGrant.FUNCTIONAL_CHANGE))
        self.assertIs(assess_change_proposal(proposal, request).state,
                      BehaviorAssessmentState.FUNCTIONAL_CHANGE_AUTHORIZED)

    def test_structural_grant_nao_implica_functional_grant(self) -> None:
        proposal = self.proposal(kind=ChangeKind.FUNCTIONAL,
                                 behavior_intent=BehaviorIntent.CHANGE)
        self.assertIs(assess_change_proposal(proposal, self.request()).state,
                      BehaviorAssessmentState.FUNCTIONAL_CHANGE_UNAUTHORIZED)

    def test_recommendation_nao_concede_grant(self) -> None:
        evidence = EvidenceReference(EvidenceKind.DIRECT_OBSERVATION, "test", "run:1",
                                     "src/a.py")
        finding = ReviewFinding(
            scope="scope-a", dimension=TechnicalDimension.SOLID, condition="Fato",
            evidence=(evidence,), normative_reference="rule:1",
            technical_conclusion="Conclusão", impact="Impacto",
            recommendation="Executar a refatoração",
        )
        proposal = self.proposal(finding=finding, objective_reference=None)
        request = self.request((AuthorizationGrant.REVIEW,))
        with self.assertRaises(ReviewInputError):
            assess_change_proposal(proposal, request)

    def test_diretorio_pai_nao_autoriza_filho_e_wildcard_nao_tem_semantica(self) -> None:
        request = self.request(targets=("src/",))
        for target in ("src/a.py", "*"):
            proposal = self.proposal(targets=(target,))
            with self.subTest(target=target), self.assertRaises(ReviewInputError):
                assess_change_proposal(proposal, request)

    def test_mesmas_entradas_produzem_mesmo_assessment(self) -> None:
        proposal = self.complete_proposal()
        request = self.request()
        first = assess_change_proposal(proposal, request)
        second = assess_change_proposal(proposal, request)
        self.assertEqual(first, second)

    def test_api_de_avaliacao_e_pura_e_nao_chama_efeitos_externos(self) -> None:
        import builtins
        import socket
        import subprocess

        proposal = self.complete_proposal()
        request = self.request()
        with patch.object(builtins, "open", side_effect=AssertionError("I/O")) as opened, \
             patch.object(subprocess, "Popen", side_effect=AssertionError("processo")) as process, \
             patch.object(socket, "create_connection", side_effect=AssertionError("rede")) as network:
            result = assess_change_proposal(proposal, request)
            compared_result = assess_change_proposal(self.compared_proposal(), request)
        self.assertIs(result.state, BehaviorAssessmentState.PRESERVATION_EVIDENCED)
        self.assertIs(compared_result.state, BehaviorAssessmentState.PRESERVATION_EVIDENCED)
        opened.assert_not_called()
        process.assert_not_called()
        network.assert_not_called()

    def test_assessment_nao_pode_ser_forjado_com_estado_positivo(self) -> None:
        proposal = self.proposal()
        with self.assertRaises(ReviewInputError):
            BehaviorAssessment(BehaviorAssessmentState.PRESERVATION_EVIDENCED,
                              proposal, self.request())


class ReviewConclusionTests(unittest.TestCase):
    @staticmethod
    def evidence(target: str = "Cliente.pas", *, kind: EvidenceKind = EvidenceKind.DIRECT_OBSERVATION,
                 version: str | None = "v1", reference: str = "test://inspection") -> EvidenceReference:
        return EvidenceReference(kind, "fixture", reference, target, version)

    @classmethod
    def claim(cls, target: str = "Cliente.pas", *, status: VerificationStatus = VerificationStatus.EXECUTED_OBSERVED,
              version: str | None = "v1") -> VerificationClaim:
        evidence = cls.evidence(target, version=version)
        return VerificationClaim("inspeção executada", target, status, (evidence,), version)

    @classmethod
    def conclusion(cls, **overrides: object) -> ReviewConclusion:
        values: dict[str, object] = {
            "state": ConclusionState.LIMITED,
            "scopes": ("ClasseCliente",),
            "artifacts": ("Cliente.pas",),
            "sources": ("Cliente.pas",),
            "versions": (("Cliente.pas", "v1"),),
            "evidence": (cls.evidence(),),
            "claims": (cls.claim(),),
            "limitation": "Conclusão limitada à classe examinada.",
        }
        values.update(overrides)
        return ReviewConclusion(**values)  # type: ignore[arg-type]

    def test_enum_tem_exatamente_os_tres_estados_permitidos(self) -> None:
        self.assertEqual(tuple(item.name for item in ConclusionState),
                         ("LIMITED", "BLOCKED", "NO_FINDING_IN_SCOPE"))

    def test_limited_valida_com_bases_explicitas(self) -> None:
        result = self.conclusion()
        self.assertIs(result.state, ConclusionState.LIMITED)
        self.assertEqual(result.scopes, ("ClasseCliente",))
        self.assertEqual(result.artifacts, ("Cliente.pas",))
        self.assertEqual(result.sources, ("Cliente.pas",))

    def test_blocked_nao_exige_evidencia_ausente_mas_exige_limite_e_escopo(self) -> None:
        result = self.conclusion(
            state=ConclusionState.BLOCKED,
            artifacts=(), sources=("Cliente.pas",), versions=(), evidence=(), claims=(),
            limitation="A fonte necessária não estava disponível.",
        )
        self.assertEqual(result.evidence, ())
        self.assertEqual(result.limitation, "A fonte necessária não estava disponível.")
        with self.assertRaisesRegex(ReviewInputError, "limitation explícita"):
            self.conclusion(state=ConclusionState.BLOCKED, limitation=None)
        with self.assertRaisesRegex(ReviewInputError, "artifact ou source explícitos"):
            self.conclusion(state=ConclusionState.BLOCKED, artifacts=(), sources=(),
                            versions=(), evidence=(), claims=())

    def test_no_finding_requer_bases_e_evidencia_rastreavel(self) -> None:
        result = self.conclusion(
            state=ConclusionState.NO_FINDING_IN_SCOPE,
            claims=(),
        )
        self.assertIs(result.state, ConclusionState.NO_FINDING_IN_SCOPE)
        with self.assertRaisesRegex(ReviewInputError, "observada ou persistida"):
            self.conclusion(
                state=ConclusionState.NO_FINDING_IN_SCOPE,
                evidence=(self.evidence(kind=EvidenceKind.REPORTED),),
                claims=(),
            )
        with self.assertRaisesRegex(ReviewInputError, "EvidenceReference do escopo"):
            self.conclusion(state=ConclusionState.NO_FINDING_IN_SCOPE, evidence=(), claims=())

    def test_scope_ausente_vazio_ou_duplicado_e_rejeitado(self) -> None:
        for scopes in ((), (" ",), ("one", "one")):
            with self.subTest(scopes=scopes), self.assertRaises(ReviewInputError):
                self.conclusion(scopes=scopes)
        with self.assertRaisesRegex(ReviewInputError, "scope global"):
            self.conclusion(scopes=("*",))

    def test_artifacts_sources_e_versions_validam_duplicatas_e_forma(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "duplicados"):
            self.conclusion(artifacts=("Cliente.pas", "Cliente.pas"))
        with self.assertRaisesRegex(ReviewInputError, "duplicados"):
            self.conclusion(sources=("source", "source"))
        with self.assertRaisesRegex(ReviewInputError, "repetir alvos"):
            self.conclusion(versions=(("Cliente.pas", "v1"), ("Cliente.pas", "v2")))
        with self.assertRaisesRegex(ReviewInputError, "alvo e versão"):
            self.conclusion(versions=(("Cliente.pas",),))

    def test_evidence_e_claims_validam_tipos_duplicatas_e_targets(self) -> None:
        item = self.evidence()
        with self.assertRaisesRegex(ReviewInputError, "somente EvidenceReference"):
            self.conclusion(evidence=("texto",))
        with self.assertRaisesRegex(ReviewInputError, "duplicadas"):
            self.conclusion(evidence=(item, item))
        claim = self.claim()
        with self.assertRaisesRegex(ReviewInputError, "somente VerificationClaim"):
            self.conclusion(claims=("passou",))
        with self.assertRaisesRegex(ReviewInputError, "claims não pode conter duplicatas"):
            self.conclusion(claims=(claim, claim))
        with self.assertRaisesRegex(ReviewInputError, "EvidenceReference target está fora"):
            self.conclusion(artifacts=("Outro.pas",), sources=(), versions=(),
                            evidence=(item,), claims=())
        other_claim = self.claim("Outro.pas")
        with self.assertRaisesRegex(ReviewInputError, "VerificationClaim target está fora"):
            self.conclusion(claims=(other_claim,))

    def test_versoes_contraditorias_sao_rejeitadas_sem_resolver_versoes(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "version contradiz"):
            self.conclusion(versions=(("Cliente.pas", "v2"),))
        with self.assertRaisesRegex(ReviewInputError, "version contradiz"):
            self.conclusion(claims=(self.claim(version="v2"),))

    def test_conclusao_de_classe_permanece_limitada_a_classe(self) -> None:
        result = self.conclusion(
            state=ConclusionState.NO_FINDING_IN_SCOPE,
            scopes=("ClasseCliente",),
            artifacts=("Cliente.pas",),
            sources=("Cliente.pas",),
            evidence=(self.evidence(),), claims=(),
        )
        self.assertEqual(result.scopes, ("ClasseCliente",))
        self.assertEqual(result.artifacts, ("Cliente.pas",))
        self.assertFalse(any("projeto" in scope.casefold() for scope in result.scopes))
        self.assertFalse(hasattr(result, "project_approved"))

    def test_nao_existem_estados_universais_e_objeto_e_imutavel(self) -> None:
        self.assertEqual(set(ConclusionState.__members__),
                         {"LIMITED", "BLOCKED", "NO_FINDING_IN_SCOPE"})
        scopes = ["ClasseCliente"]
        artifacts = ["Cliente.pas"]
        evidence = [self.evidence()]
        claims = [self.claim()]
        result = self.conclusion(scopes=scopes, artifacts=artifacts,
                                 evidence=evidence, claims=claims)
        scopes.clear(); artifacts.clear(); evidence.clear(); claims.clear()
        self.assertEqual(result.scopes, ("ClasseCliente",))
        self.assertEqual(result.artifacts, ("Cliente.pas",))
        self.assertEqual(len(result.evidence), 1)
        self.assertEqual(len(result.claims), 1)
        with self.assertRaises(FrozenInstanceError):
            result.state = ConclusionState.BLOCKED  # type: ignore[misc]


class GapHandlingIntegrationTests(unittest.TestCase):
    @staticmethod
    def normative(reference: str, statement: str = "regra") -> gaps.SourceReference:
        return gaps.SourceReference("normative", reference, statement, "authority from host")

    @staticmethod
    def workspace(reference: str, statement: str = "registro operacional") -> gaps.SourceReference:
        return gaps.SourceReference("workspace", reference, statement)

    @staticmethod
    def scope(scope_id: str, dependencies: tuple[str, ...] = ()) -> ReviewScope:
        return ReviewScope(scope_id, f"Escopo {scope_id}", dependencies, (f"{scope_id}.py",))

    @staticmethod
    def ready(**overrides: tuple[bool, bool, bool, bool, bool]) -> dict[str, tuple[bool, bool, bool, bool, bool]]:
        facts = {"scope": (True, True, True, True, True)}
        facts.update(overrides)
        return facts

    def conflict(self, **overrides: object):
        values: dict[str, object] = {
            "source_a": self.normative("POL-A"),
            "source_b": self.normative("POL-B"),
            "scope": "scope",
            "impact": "impacto material",
            "resume_condition": "precedência formal explícita",
            "materially_incompatible": True,
            "authority_context": AuthorityContext(),
        }
        values.update(overrides)
        return evaluate_source_conflict(**values)  # type: ignore[arg-type]

    def test_duas_normativas_sem_precedencia_preservam_conflito_sem_vencedor(self) -> None:
        result = self.conflict()
        self.assertIsInstance(result, gaps.ConflictAssessment)
        self.assertTrue(result.blocker_required)
        self.assertIsNone(result.authoritative_reference)
        self.assertIsNone(result.required_authority)
        self.assertIsNone(result.divergence.required_authority)
        self.assertIn("identificar a autoridade competente", result.divergence.required_information)

    def test_autoridade_competente_explicita_fica_requisito_sem_resolver(self) -> None:
        authority = AuthorityReference("authority:ref-1", "Owner informado", "competência declarada", ("scope",))
        context = AuthorityContext(authorities=(authority,))
        result = self.conflict(authority_context=context, required_authority=authority)
        self.assertIsInstance(result, gaps.ConflictAssessment)
        self.assertEqual(result.required_authority, "authority:ref-1")
        self.assertEqual(result.divergence.required_authority, "authority:ref-1")
        self.assertTrue(result.blocker_required)
        self.assertIsNone(result.authoritative_reference)
        self.assertIn("nenhuma vencedora", result.divergence.unresolved_reason)

    def test_precedencia_valida_do_par_e_scope_exatos_e_reconhecida_primeiro(self) -> None:
        authority = AuthorityReference("authority:ref-1", "Owner", "competência", ("scope",))
        relation = AuthorizedPrecedence("POL-A", "POL-B", "scope", "authority:ref-1", "decision:7")
        context = AuthorityContext((authority,), (relation,))
        result = self.conflict(authority_context=context)
        self.assertIs(result, relation)

    def test_precedencia_de_outro_scope_nao_resolve_conflito(self) -> None:
        authority = AuthorityReference("authority:ref-1", "Owner", "competência", ("other",))
        relation = AuthorizedPrecedence("POL-A", "POL-B", "other", "authority:ref-1", "decision:7")
        result = self.conflict(authority_context=AuthorityContext((authority,), (relation,)))
        self.assertIsInstance(result, gaps.ConflictAssessment)
        self.assertTrue(result.blocker_required)
        self.assertIsNone(result.authoritative_reference)

    def test_normative_versus_workspace_preserva_resultado_spec1(self) -> None:
        result = self.conflict(source_a=self.workspace("DOC-workspace"),
                               source_b=self.normative("POL-A"))
        self.assertIsInstance(result, gaps.ConflictAssessment)
        self.assertEqual(result.authoritative_reference, "POL-A")
        self.assertFalse(result.blocker_required)
        self.assertIn("workspace é evidência operacional", result.divergence.unresolved_reason)

    def test_incompatibilidade_falsa_retorna_ausencia_de_conflito(self) -> None:
        self.assertIsNone(self.conflict(materially_incompatible=False))

    def test_nomes_datas_e_ordem_nao_criam_precedencia(self) -> None:
        one = self.conflict(source_a=self.normative("newest-2026", "mais nova"),
                            source_b=self.normative("specific-policy", "mais específica"))
        two = self.conflict(source_a=self.normative("specific-policy", "mais específica"),
                            source_b=self.normative("newest-2026", "mais nova"))
        for result in (one, two):
            self.assertIsInstance(result, gaps.ConflictAssessment)
            self.assertIsNone(result.authoritative_reference)
            self.assertTrue(result.blocker_required)

    def test_authority_required_deve_ser_referencia_competente_no_contexto(self) -> None:
        authority = AuthorityReference("authority:ref", "Owner", "competência", ("elsewhere",))
        context = AuthorityContext((authority,))
        with self.assertRaisesRegex(ReviewInputError, "não declara competência"):
            self.conflict(authority_context=context, required_authority=authority)
        with self.assertRaisesRegex(ReviewInputError, "deve pertencer"):
            self.conflict(required_authority=authority)

    def test_criterios_de_continuidade_sao_bools_explicitos(self) -> None:
        with self.assertRaisesRegex(ReviewInputError, "cinco booleanos"):
            evaluate_scope_continuity(("A",), (self.scope("B"),), {"B": (True, True)})  # type: ignore[dict-item]
        with self.assertRaisesRegex(ReviewInputError, "bool explícitos"):
            evaluate_scope_continuity(("A",), (self.scope("B"),),
                                      {"B": (1, True, True, True, True)})  # type: ignore[dict-item]

    def test_scope_affected_diretamente_nao_continua(self) -> None:
        assessment = evaluate_scope_continuity(
            ("A",), (self.scope("A"),), {"A": (True, True, True, True, True)}
        )
        item = assessment.scopes[0]
        self.assertFalse(item.continuable)
        self.assertIn("escopo diretamente afetado pela lacuna", item.reasons)

    def test_scope_independente_totalmente_apto_continua(self) -> None:
        result = evaluate_scope_continuity(
            ("A",), (self.scope("B"),), {"B": (True, True, True, True, True)}
        )
        self.assertEqual(result.continuable_scopes, ("B",))

    def test_falha_de_cada_criterio_preserva_razao_spec1(self) -> None:
        cases = (
            (0, "não há autorização explícita para este escopo"),
            (1, "informação necessária insuficiente"),
            (2, "evidência necessária insuficiente"),
            (3, "autoridade necessária insuficiente"),
            (4, "há conflito material não resolvido"),
        )
        for index, expected_reason in cases:
            facts = [True, True, True, True, True]
            facts[index] = False
            with self.subTest(index=index):
                result = evaluate_scope_continuity(
                    ("A",), (self.scope("B"),), {"B": tuple(facts)}  # type: ignore[dict-item]
                )
                item = result.scopes[0]
                self.assertFalse(item.continuable)
                self.assertEqual(item.reasons, (expected_reason,))

    def test_dependencia_desconhecida_permanece_nao_avaliada(self) -> None:
        result = evaluate_scope_continuity(
            ("A",), (self.scope("B", ("UNKNOWN",)),),
            {"B": (True, True, True, True, True)},
        )
        self.assertIn("depende de escopo não avaliado: UNKNOWN", result.scopes[0].reasons)

    def test_propagacao_transitiva_e_delegada_a_gap_handling(self) -> None:
        scopes = (self.scope("A"), self.scope("B", ("A",)), self.scope("C", ("B",)))
        result = evaluate_scope_continuity(
            ("A",), scopes,
            {key: (True, True, True, True, True) for key in ("A", "B", "C")},
        )
        self.assertEqual(result.continuable_scopes, ())
        for item in result.scopes:
            self.assertFalse(item.continuable)
        self.assertIn("depende de escopo bloqueado: A", result.scopes[1].reasons)
        self.assertIn("depende de escopo bloqueado: B", result.scopes[2].reasons)

    def test_scope_independente_continua_apesar_de_outro_ramo_bloqueado(self) -> None:
        scopes = (self.scope("A"), self.scope("B", ("A",)), self.scope("Independent"))
        result = evaluate_scope_continuity(
            ("A",), scopes,
            {key: (True, True, True, True, True) for key in ("A", "B", "Independent")},
        )
        self.assertEqual(result.continuable_scopes, ("Independent",))

    def test_autorizacao_ausente_bloqueia_scope_e_dependente_sem_bloquear_independente(self) -> None:
        scopes = (self.scope("B"), self.scope("C", ("B",)), self.scope("Independent"))
        result = evaluate_scope_continuity(
            ("Outside",), scopes,
            {
                "B": (False, True, True, True, True),
                "C": (True, True, True, True, True),
                "Independent": (True, True, True, True, True),
            },
        )
        self.assertEqual(result.continuable_scopes, ("Independent",))
        self.assertIn("não há autorização explícita para este escopo", result.scopes[0].reasons)
        self.assertTrue(any("depende de escopo bloqueado" in reason for reason in result.scopes[1].reasons))

    def test_ordem_e_razoes_do_evaluator_spec1_sao_preservadas(self) -> None:
        scopes = (self.scope("z"), self.scope("a"))
        result = evaluate_scope_continuity(
            ("affected",), scopes,
            {"z": (False, False, False, False, False), "a": (True, True, True, True, True)},
        )
        self.assertEqual(tuple(item.scope for item in result.scopes), ("z", "a"))
        self.assertEqual(result.scopes[0].reasons, (
            "não há autorização explícita para este escopo",
            "informação necessária insuficiente",
            "evidência necessária insuficiente",
            "autoridade necessária insuficiente",
            "há conflito material não resolvido",
        ))

    def test_adaptadores_nao_chamam_persistencia(self) -> None:
        with patch.object(gaps, "registrar_divergencia", side_effect=AssertionError) as divergence, \
             patch.object(gaps, "registrar_blocker", side_effect=AssertionError) as blocker, \
             patch.object(gaps, "registrar_decisao_existente", side_effect=AssertionError) as decision, \
             patch.object(gaps, "registrar_resultado", side_effect=AssertionError) as result, \
             patch.object(gaps, "publicar_documento", side_effect=AssertionError) as publish:
            self.conflict()
            evaluate_scope_continuity(
                ("A",), (self.scope("B"),), {"B": (True, True, True, True, True)}
            )
        for spy in (divergence, blocker, decision, result, publish):
            spy.assert_not_called()


class ReviewResponseTests(unittest.TestCase):
    @staticmethod
    def blocks(*, titles: tuple[str, str, str] | None = None,
               bodies: tuple[str, str, str] | None = None) -> tuple[ReviewResponseBlock, ...]:
        actual_titles = titles or (
            "Análise Crítica", "Refatoração", "Justificativa Arquitetural"
        )
        actual_bodies = bodies or (
            "A evidência confirma a condição observada.",
            "Não aplicável: nenhuma refatoração indicada.",
            "Não aplicável: sem impacto arquitetural material.",
        )
        return tuple(
            ReviewResponseBlock(key, title, body)
            for key, title, body in zip(
                (ResponseBlockKey.CRITICAL_ANALYSIS, ResponseBlockKey.REFACTORING,
                 ResponseBlockKey.ARCHITECTURAL_JUSTIFICATION),
                actual_titles, actual_bodies,
            )
        )

    @classmethod
    def response(cls, language: str | None = None, *,
                 blocks: tuple[ReviewResponseBlock, ...] | list[ReviewResponseBlock] | None = None
                 ) -> ReviewResponse:
        return ReviewResponse(language, cls.blocks() if blocks is None else blocks)  # type: ignore[arg-type]

    def test_response_possui_exatamente_tres_chaves_canonicas(self) -> None:
        response = self.response()
        self.assertEqual(tuple(block.key for block in response.blocks), (
            ResponseBlockKey.CRITICAL_ANALYSIS,
            ResponseBlockKey.REFACTORING,
            ResponseBlockKey.ARCHITECTURAL_JUSTIFICATION,
        ))
        self.assertEqual(len(response.blocks), 3)

    def test_blocos_sao_renderizados_na_ordem_semantica_fixa(self) -> None:
        rendered = renderizar_resposta(self.response())
        positions = tuple(rendered.index(title) for title in (
            "Análise Crítica", "Refatoração", "Justificativa Arquitetural"
        ))
        self.assertEqual(positions, tuple(sorted(positions)))

    def test_bloco_ausente_adicional_duplicado_ou_fora_de_ordem_e_rejeitado(self) -> None:
        blocks = self.blocks()
        for candidate in (blocks[:2], blocks + (blocks[0],),
                          (blocks[0], blocks[0], blocks[2]),
                          (blocks[1], blocks[0], blocks[2])):
            with self.subTest(candidate=candidate), self.assertRaises(ReviewInputError):
                self.response(blocks=candidate)

    def test_chave_desconhecida_nao_e_coagida_para_enum(self) -> None:
        with self.assertRaises(ReviewInputError):
            ReviewResponseBlock("CRITICAL_ANALYSIS", "Título", "Corpo")  # type: ignore[arg-type]

    def test_titulo_vazio_branco_ou_multilinha_e_rejeitado(self) -> None:
        for title in ("", "   ", "linha 1\nlinha 2"):
            with self.subTest(title=title), self.assertRaises(ReviewInputError):
                ReviewResponseBlock(ResponseBlockKey.CRITICAL_ANALYSIS, title, "Corpo")

    def test_corpo_vazio_ou_branco_e_rejeitado_sem_placeholder(self) -> None:
        for body in ("", " \t\n"):
            with self.subTest(body=body), self.assertRaises(ReviewInputError):
                ReviewResponseBlock(ResponseBlockKey.CRITICAL_ANALYSIS, "Título", body)

    def test_language_none_permanece_default_semantico_sem_reescrita(self) -> None:
        response = self.response(None)
        self.assertIsNone(response.language)
        rendered = renderizar_resposta(response)
        self.assertIn("Análise Crítica", rendered)
        self.assertIn("Não aplicável: nenhuma refatoração indicada.", rendered)

    def test_idioma_explicito_e_textos_localizados_sao_preservados_sem_traducao(self) -> None:
        blocks = self.blocks(
            titles=("Critical analysis", "Refactoring", "Architectural justification"),
            bodies=("Evidence supports the finding.", "Not applicable.", "No material impact."),
        )
        response = self.response("en", blocks=blocks)
        rendered = renderizar_resposta(response)
        self.assertEqual(response.language, "en")
        for value in ("Critical analysis", "Evidence supports the finding.", "Not applicable."):
            self.assertIn(value, rendered)
        self.assertNotIn("Análise Crítica", rendered)
        self.assertNotIsInstance(rendered, (tuple, list, dict))

    def test_language_vazio_ou_whitespace_e_rejeitado(self) -> None:
        for language in ("", "   "):
            with self.subTest(language=language), self.assertRaises(ReviewInputError):
                self.response(language)

    def test_uma_chamada_retorna_uma_unica_string_deterministica(self) -> None:
        response = self.response()
        first = renderizar_resposta(response)
        second = renderizar_resposta(response)
        equivalent = renderizar_resposta(self.response(blocks=self.blocks()))
        self.assertIsInstance(first, str)
        self.assertEqual(first, second)
        self.assertEqual(first, equivalent)

    def test_titulos_e_corpos_nao_criam_estrutura_markdown_adicional(self) -> None:
        blocks = self.blocks(
            titles=("# título", "**refatoração**", "[justificativa](x)"),
            bodies=("### heading\n---\n<h2>texto</h2>", "`código`", "*ênfase*"),
        )
        rendered = renderizar_resposta(self.response(blocks=blocks))
        self.assertEqual(rendered.count("## "), 3)
        self.assertIn(r"\# título", rendered)
        self.assertIn(r"\#\#\# heading", rendered)
        self.assertIn(r"\<h2\>texto\</h2\>", rendered)

    def test_corpo_nao_cria_heading_setext_com_sinais_de_igual(self) -> None:
        blocks = self.blocks(bodies=(
            "texto\n===", "Não aplicável.", "Não aplicável."
        ))
        response = self.response(blocks=blocks)
        rendered = renderizar_resposta(response)
        self.assertIn("texto", rendered)
        self.assertIn(r"\=\=\=", rendered)
        self.assertNotRegex(rendered, r"(?m)^={3,}\s*$")
        self.assertEqual(rendered.count("## "), 3)
        self.assertEqual(renderizar_resposta(response), rendered)
        self.assertEqual(rendered.encode("utf-8").decode("utf-8"), rendered)

    def test_escaping_e_unicode_sao_deterministicos_e_utf8_round_trip(self) -> None:
        response = self.response(blocks=self.blocks(
            titles=("Análise Crítica", "Refatoração", "Justificativa Arquitetural"),
            bodies=("ação, coração, ç, € e 🧭", "N/A — sem mudança.", "N/A — sem impacto."),
        ))
        rendered = renderizar_resposta(response)
        self.assertEqual(renderizar_resposta(response), rendered)
        self.assertEqual(rendered.encode("utf-8").decode("utf-8"), rendered)
        self.assertIn("ação, coração, ç, € e 🧭", rendered)

    def test_na_permanece_nos_tres_blocos_sem_codigo_ou_recomendacao_inventada(self) -> None:
        blocks = self.blocks(bodies=(
            "Inspeção concluída.",
            "Não aplicável: nenhuma refatoração é indicada.",
            "Não aplicável: não há impacto arquitetural material.",
        ))
        rendered = renderizar_resposta(self.response(blocks=blocks))
        self.assertEqual(rendered.count("## "), 3)
        self.assertIn("Não aplicável: nenhuma refatoração é indicada.", rendered)
        self.assertIn("Não aplicável: não há impacto arquitetural material.", rendered)
        self.assertNotIn("def ", rendered)

    def test_response_e_blocos_sao_frozen_e_copiam_colecao_de_entrada(self) -> None:
        blocks = list(self.blocks())
        response = self.response(blocks=blocks)
        blocks.clear()
        self.assertEqual(len(response.blocks), 3)
        with self.assertRaises(FrozenInstanceError):
            response.language = "en"  # type: ignore[misc]
        with self.assertRaises(FrozenInstanceError):
            response.blocks[0].title = "alterado"  # type: ignore[misc]

    def test_renderizador_rejeita_tipo_incorreto(self) -> None:
        with self.assertRaises(ReviewInputError):
            renderizar_resposta("texto")  # type: ignore[arg-type]

    def test_renderizador_nao_acessa_io_rede_processos_ou_persistencia(self) -> None:
        import builtins
        import socket
        import subprocess

        response = self.response()
        with patch.object(builtins, "open", side_effect=AssertionError("I/O")) as opened, \
             patch.object(socket, "create_connection", side_effect=AssertionError("rede")) as network, \
             patch.object(subprocess, "Popen", side_effect=AssertionError("processo")) as process:
            renderizar_resposta(response)
        opened.assert_not_called()
        network.assert_not_called()
        process.assert_not_called()

    def test_idioma_do_request_pode_ser_representado_sem_pipeline_automatico(self) -> None:
        request = ReviewRequest(
            objective="Revisar", scopes=(ReviewScope("s", "escopo", (), ("a.py",)),),
            authorized_artifacts=("a.py",), excluded_artifacts=(), expected_outcome="análise",
            authorization_grants=(AuthorizationGrant.REVIEW,), requested_effects=(),
            language="en", source_versions=(),
        )
        response = ReviewResponse(request.language, self.blocks())
        self.assertEqual(response.language, request.language)
        self.assertEqual(renderizar_resposta(response).count("## "), 3)


class IntegratedReviewTests(unittest.TestCase):
    @staticmethod
    def request(*, scopes: tuple[ReviewScope, ...] | None = None,
                grants: tuple[AuthorizationGrant, ...] = (AuthorizationGrant.REVIEW,),
                effects: tuple[RequestedEffect, ...] = (), language: str | None = None,
                versions: tuple[tuple[str, str], ...] = (("a.py", "v1"),)) -> ReviewRequest:
        actual_scopes = scopes or (ReviewScope("S", "Escopo S", (), ("a.py",)),)
        artifacts = tuple(sorted({artifact for item in actual_scopes for artifact in item.artifacts}))
        return ReviewRequest(
            objective="Revisar o comportamento declarado",
            scopes=actual_scopes,
            authorized_artifacts=artifacts,
            excluded_artifacts=(),
            expected_outcome="Conclusão limitada ao escopo fornecido",
            authorization_grants=grants,
            requested_effects=effects,
            language=language,
            source_versions=versions,
        )

    @staticmethod
    def evidence(target: str = "a.py", version: str | None = "v1",
                 reference: str = "run:1", kind: EvidenceKind = EvidenceKind.DIRECT_OBSERVATION
                 ) -> EvidenceReference:
        return EvidenceReference(kind, "host", reference, target, version=version)

    @classmethod
    def claim(cls, target: str = "a.py", version: str | None = "v1",
              status: VerificationStatus = VerificationStatus.EXECUTED_OBSERVED,
              reference: str = "run:1", assertion: str = "verificação executada") -> VerificationClaim:
        evidence = () if status is VerificationStatus.NOT_EXECUTED else (
            cls.evidence(target, version, reference),
        )
        return VerificationClaim(assertion, target, status, evidence, version)

    @staticmethod
    def response(language: str | None = None) -> ReviewResponse:
        return ReviewResponse(language, (
            ReviewResponseBlock(ResponseBlockKey.CRITICAL_ANALYSIS, "Análise Crítica", "Escopo examinado."),
            ReviewResponseBlock(ResponseBlockKey.REFACTORING, "Refatoração", "Não aplicável."),
            ReviewResponseBlock(ResponseBlockKey.ARCHITECTURAL_JUSTIFICATION,
                                "Justificativa Arquitetural", "Não aplicável."),
        ))

    @classmethod
    def conclusion(cls, *, request: ReviewRequest | None = None,
                   state: ConclusionState = ConclusionState.NO_FINDING_IN_SCOPE,
                   scopes: tuple[str, ...] = ("S",), artifacts: tuple[str, ...] = ("a.py",),
                   sources: tuple[str, ...] = ("run:1",), versions: tuple[tuple[str, str], ...] = (("a.py", "v1"),),
                   evidence: tuple[EvidenceReference, ...] | None = None,
                   claims: tuple[VerificationClaim, ...] | None = None) -> ReviewConclusion:
        actual_evidence = (cls.evidence(),) if evidence is None else evidence
        actual_claims = (cls.claim(),) if claims is None else claims
        limitation = "Escopo limitado ao material identificado." if state is ConclusionState.BLOCKED else None
        return ReviewConclusion(state, scopes, artifacts, sources, versions,
                                actual_evidence, actual_claims, limitation)

    @classmethod
    def evaluate(cls, *, request: ReviewRequest | None = None,
                 claims: tuple[VerificationClaim, ...] | list[VerificationClaim] | None = None,
                 findings: tuple[ReviewFinding, ...] | list[ReviewFinding] = (),
                 dimensions: tuple[DimensionAssessment, ...] | list[DimensionAssessment] = (),
                 proposals: tuple[ChangeProposal, ...] | list[ChangeProposal] = (),
                 conflicts: tuple[tuple[object, ...], ...] = (),
                 conclusion: ReviewConclusion | None = None,
                 response: ReviewResponse | None = None,
                 readiness: dict[str, tuple[bool, bool, bool, bool, bool]] | None = None
                 ) -> ReviewEvaluationResult:
        actual_request = request or cls.request()
        actual_claims = [cls.claim()] if claims is None else claims
        return evaluate_review(
            actual_request,
            authority_context=AuthorityContext(),
            continuity_readiness_by_scope=(readiness if readiness is not None else {
                item.scope_id: (True, True, True, True, True) for item in actual_request.scopes
            }),
            conclusion=conclusion or cls.conclusion(request=actual_request),
            response=response or cls.response(actual_request.language),
            dimension_assessments=dimensions,
            claims=actual_claims,
            findings=findings,
            change_proposals=proposals,
            source_conflicts=conflicts,  # type: ignore[arg-type]
        )

    def test_request_valido_produz_resultado_integrado_limitado_em_memoria(self) -> None:
        result = self.evaluate()
        self.assertEqual(result, self.evaluate())
        self.assertIsInstance(result, ReviewEvaluationResult)
        self.assertIs(result.conclusion.state, ConclusionState.NO_FINDING_IN_SCOPE)
        self.assertIsNone(result.continuity)
        self.assertEqual(result.rendered, renderizar_resposta(result.response))
        self.assertFalse(hasattr(result, "project_approved"))
        self.assertFalse(any(item.name in {"PASS", "SUCCESS", "APPROVED"}
                             for item in type(result.conclusion.state)))

    def test_response_language_divergente_e_none_default_sao_validados(self) -> None:
        with self.assertRaises(ReviewInputError):
            self.evaluate(response=self.response("en"))
        result = self.evaluate(response=self.response(None))
        self.assertIsNone(result.response.language)

    def test_effect_externality_e_rejeitado_sem_tentar_executar(self) -> None:
        request = self.request(effects=(RequestedEffect.EXTERNALITY,))
        with self.assertRaises(ReviewInputError):
            self.evaluate(request=request)

    def test_local_persistence_requested_remains_memory_only(self) -> None:
        request = self.request(effects=(RequestedEffect.LOCAL_PERSISTENCE,))
        result = self.evaluate(request=request)
        self.assertEqual(result.request.requested_effects, (RequestedEffect.LOCAL_PERSISTENCE,))
        self.assertFalse(hasattr(result, "receipt"))

    def test_finding_sem_escopo_do_request_e_rejeitado(self) -> None:
        finding = ReviewFinding("unknown", TechnicalDimension.SOLID, "condição",
                                (self.evidence(),), "regra", "conclusão", "impacto")
        with self.assertRaises(ReviewInputError):
            self.evaluate(findings=(finding,))

    def test_dimension_assessment_sem_escopo_do_request_e_rejeitado(self) -> None:
        dimension = DimensionAssessment(TechnicalDimension.SOLID, "unknown",
                                        DimensionAssessmentState.NOT_APPLICABLE)
        with self.assertRaises(ReviewInputError):
            self.evaluate(dimensions=(dimension,))

    def test_finding_e_dimension_nao_podem_ampliar_artifacts_do_scope(self) -> None:
        finding = ReviewFinding("S", TechnicalDimension.SOLID, "condição",
                                (self.evidence("outside.py"),), "regra", "conclusão", "impacto")
        dimension = DimensionAssessment(TechnicalDimension.SOLID, "S",
                                       DimensionAssessmentState.NOT_ASSESSED_INSUFFICIENT_EVIDENCE,
                                       (self.evidence("outside.py"),))
        with self.assertRaises(ReviewInputError):
            self.evaluate(findings=(finding,))
        with self.assertRaises(ReviewInputError):
            self.evaluate(dimensions=(dimension,))

    def test_claim_com_target_fora_da_allowlist_e_rejeitado(self) -> None:
        with self.assertRaises(ReviewInputError):
            self.evaluate(claims=(self.claim("outside.py"),))

    def test_proposta_fora_da_allowlist_e_rejeitada_pela_integracao(self) -> None:
        proposal = ChangeProposal(
            ChangeKind.FUNCTIONAL, "S", ("outside.py",), "proposal:outside", "motivo",
            BehaviorIntent.CHANGE, "consequência", objective_reference="Revisar o comportamento declarado",
        )
        with patch.object(protocol, "assess_change_proposal",
                           wraps=protocol.assess_change_proposal) as assessor:
            with self.assertRaises(ReviewInputError):
                self.evaluate(proposals=(proposal,))
        assessor.assert_called_once()

    def test_readiness_precisa_cobrir_cada_scope_com_cinco_bools(self) -> None:
        request = self.request()
        for readiness in ({}, {"S": (True, True)}, {"S": (True, True, True, True, 1)}):
            with self.subTest(readiness=readiness), self.assertRaises(ReviewInputError):
                self.evaluate(request=request, readiness=readiness)  # type: ignore[arg-type]

    def test_conclusao_com_scope_artifact_ou_versao_fora_do_request_e_rejeitada(self) -> None:
        cases = (
            self.conclusion(state=ConclusionState.BLOCKED, scopes=("unknown",),
                            evidence=(), claims=()),
            self.conclusion(state=ConclusionState.BLOCKED, artifacts=("outside.py",),
                            versions=(), evidence=(), claims=()),
            self.conclusion(state=ConclusionState.BLOCKED, versions=(("a.py", "other"),),
                            evidence=(), claims=()),
        )
        for conclusion in cases:
            with self.subTest(conclusion=conclusion), self.assertRaises(ReviewInputError):
                self.evaluate(conclusion=conclusion)

    def test_claim_historico_ou_nao_executado_nao_e_promovido(self) -> None:
        historical_evidence = EvidenceReference(EvidenceKind.PERSISTED_EVIDENCE, "archive",
                                                "history:1", "a.py", version="v1")
        historical = VerificationClaim("execução anterior", "a.py",
                                       VerificationStatus.HISTORICAL_IDENTIFIED,
                                       (historical_evidence,), "v1")
        conclusion = self.conclusion(state=ConclusionState.BLOCKED,
                                     sources=("history:1",), versions=(),
                                     evidence=(historical_evidence,), claims=(historical,))
        result = self.evaluate(claims=(historical,), conclusion=conclusion)
        self.assertIs(result.claims[0].status, VerificationStatus.HISTORICAL_IDENTIFIED)
        not_run = self.claim(status=VerificationStatus.NOT_EXECUTED)
        blocked = self.conclusion(state=ConclusionState.BLOCKED, sources=("a.py",),
                                  evidence=(), claims=())
        result = self.evaluate(claims=(not_run,), conclusion=blocked)
        self.assertIs(result.claims[0].status, VerificationStatus.NOT_EXECUTED)

    def test_findings_em_ordens_diferentes_tem_canonicalizacao_igual(self) -> None:
        first = ReviewFinding("S", TechnicalDimension.SOLID, "A condição",
                              (self.evidence(reference="evidence:a"),), "rule", "c1", "impact")
        second = ReviewFinding("S", TechnicalDimension.PATTERNS, "B condição",
                               (self.evidence(reference="evidence:b"),), "rule", "c2", "impact")
        blocked = self.conclusion(state=ConclusionState.BLOCKED,
                                  sources=("evidence:a", "evidence:b"), evidence=(), claims=())
        a = self.evaluate(findings=(first, second), conclusion=blocked)
        b = self.evaluate(findings=(second, first), conclusion=blocked)
        self.assertEqual(a.findings, b.findings)
        self.assertEqual(a, b)

    def test_findings_com_mesma_chave_d14_e_conteudo_distinto_sao_rejeitados(self) -> None:
        base = ReviewFinding("S", TechnicalDimension.SOLID, "Mesma condicao",
                             (self.evidence(reference="evidence:a"),), "rule",
                             "Conclusao", "Impacto", "Recomendacao")
        variants = (
            ReviewFinding("S", TechnicalDimension.SOLID, "Mesma condicao",
                          (self.evidence(reference="evidence:b"),), "rule",
                          "Conclusao", "Impacto", "Recomendacao"),
            ReviewFinding("S", TechnicalDimension.SOLID, "Mesma condicao",
                          base.evidence, "rule", "Outra conclusao", "Impacto", "Recomendacao"),
            ReviewFinding("S", TechnicalDimension.SOLID, "Mesma condicao",
                          base.evidence, "rule", "Conclusao", "Outro impacto", "Recomendacao"),
            ReviewFinding("S", TechnicalDimension.SOLID, "Mesma condicao",
                          base.evidence, "rule", "Conclusao", "Impacto", "Outra recomendacao"),
        )
        self.assertTrue(all(item.sort_key == base.sort_key for item in variants))
        for variant in variants:
            for findings in ((base, variant), (variant, base)):
                with self.subTest(variant=variant), self.assertRaisesRegex(
                        ReviewInputError, "chave D-14 ambigua"):
                    self.evaluate(findings=findings)

    def test_findings_com_chaves_d14_distintas_usam_sort_review_findings(self) -> None:
        first = ReviewFinding("S", TechnicalDimension.SOLID, "A condicao",
                              (self.evidence(reference="evidence:a"),), "rule", "c1", "impact")
        second = ReviewFinding("S", TechnicalDimension.PATTERNS, "B condicao",
                               (self.evidence(reference="evidence:b"),), "rule", "c2", "impact")
        blocked = self.conclusion(state=ConclusionState.BLOCKED,
                                  sources=("evidence:a", "evidence:b"), evidence=(), claims=())
        with patch.object(protocol, "sort_review_findings", wraps=sort_review_findings) as sorter:
            result = self.evaluate(findings=(first, second), conclusion=blocked)
        sorter.assert_called_once_with((first, second))
        self.assertEqual(result.findings, sort_review_findings((first, second)))

    def test_proposta_funcional_sem_grant_fica_nao_autorizada_e_bloqueia_scope(self) -> None:
        proposal = ChangeProposal(
            ChangeKind.FUNCTIONAL, "S", ("a.py",), "proposal:1", "motivo",
            BehaviorIntent.CHANGE, "consequência", objective_reference="Revisar o comportamento declarado",
        )
        blocked = self.conclusion(state=ConclusionState.BLOCKED, evidence=(), claims=())
        result = self.evaluate(proposals=(proposal,), conclusion=blocked)
        self.assertIs(result.behavior_assessments[0].state,
                      BehaviorAssessmentState.FUNCTIONAL_CHANGE_UNAUTHORIZED)
        self.assertIsNotNone(result.continuity)
        self.assertNotIn("S", result.continuity.continuable_scopes)

    def test_proposta_estrutural_com_preservacao_evidenciada_usa_avaliador_existente(self) -> None:
        request = self.request(grants=(AuthorizationGrant.REVIEW,
                                       AuthorizationGrant.STRUCTURAL_CHANGE))
        base = self.claim(version="v0", reference="run:base")
        candidate = self.claim(version="v1", reference="run:candidate")
        proposal = ChangeProposal(
            ChangeKind.STRUCTURAL, "S", ("a.py",), "proposal:structural", "motivo",
            BehaviorIntent.PRESERVE, "sem mudança funcional",
            base_versions=(("a.py", "v0"),), candidate_versions=(("a.py", "v1"),),
            behavior_contract="contrato explícito", verified_cases=("verificação executada",),
            claims=(base, candidate), objective_reference=request.objective,
        )
        result = self.evaluate(request=request, proposals=(proposal,))
        self.assertIs(result.behavior_assessments[0].state,
                      BehaviorAssessmentState.PRESERVATION_EVIDENCED)

    def test_scope_conflitual_bloqueia_sem_impedir_scope_independente(self) -> None:
        request = self.request(scopes=(
            ReviewScope("A", "Escopo A", (), ("a.py",)),
            ReviewScope("B", "Escopo independente", (), ("b.py",)),
        ), versions=(("a.py", "v1"), ("b.py", "v1")))
        source_a = gaps.SourceReference("normative", "POL-A", "regra A", "autoridade A")
        source_b = gaps.SourceReference("normative", "POL-B", "regra B", "autoridade B")
        conflict = (source_a, source_b, "A", "impacto", "precedência explícita", True, None)
        conclusion = self.conclusion(state=ConclusionState.BLOCKED, scopes=("A", "B"),
                                     sources=("POL-A", "POL-B"), artifacts=("a.py",),
                                     versions=(), evidence=(), claims=())
        result = self.evaluate(request=request, conflicts=(conflict,), conclusion=conclusion)
        self.assertIsInstance(result.conflict_results[0], gaps.ConflictAssessment)
        self.assertIsNone(result.conflict_results[0].authoritative_reference)
        self.assertTrue(result.conflict_results[0].blocker_required)
        self.assertEqual(result.continuity.continuable_scopes, ("B",))

    def test_conflicto_propaga_por_dependencia_transitiva_sem_bloquear_independente(self) -> None:
        request = self.request(scopes=(
            ReviewScope("A", "A", (), ("a.py",)),
            ReviewScope("B", "B depende de A", ("A",), ("b.py",)),
            ReviewScope("C", "C depende de B", ("B",), ("c.py",)),
            ReviewScope("D", "Independente", (), ("d.py",)),
        ), versions=())
        source_a = gaps.SourceReference("normative", "POL-A", "regra A", "authority A")
        source_b = gaps.SourceReference("normative", "POL-B", "regra B", "authority B")
        conflict = (source_a, source_b, "A", "impacto", "resolver", True, None)
        blocked = self.conclusion(state=ConclusionState.BLOCKED, scopes=("A", "B", "C"),
                                  artifacts=("a.py",), sources=("POL-A", "POL-B"),
                                  versions=(), evidence=(), claims=())
        readiness = {key: (True, True, True, True, True) for key in "ABCD"}
        result = self.evaluate(request=request, conflicts=(conflict,), conclusion=blocked,
                               readiness=readiness)
        self.assertEqual(result.continuity.continuable_scopes, ("D",))
        self.assertFalse(any(item.continuable for item in result.continuity.scopes
                             if item.scope in {"A", "B", "C"}))

    def test_precedencia_explicita_permanece_resultado_da_fronteira_existente(self) -> None:
        authority = AuthorityReference("authority:1", "Owner informado", "competência", ("S",))
        precedence = AuthorizedPrecedence("POL-A", "POL-B", "S", "authority:1", "decision:1")
        context = AuthorityContext((authority,), (precedence,))
        source_a = gaps.SourceReference("normative", "POL-A", "regra A", "autoridade A")
        source_b = gaps.SourceReference("normative", "POL-B", "regra B", "autoridade B")
        conflict = (source_a, source_b, "S", "impacto", "seguir decisão", True, None)
        with patch.object(protocol, "evaluate_source_conflict",
                           wraps=protocol.evaluate_source_conflict) as evaluator:
            result = evaluate_review(
                self.request(), authority_context=context,
                continuity_readiness_by_scope={"S": (True, True, True, True, True)},
                conclusion=self.conclusion(), response=self.response(), claims=(self.claim(),),
                source_conflicts=(conflict,),
            )
        evaluator.assert_called_once()
        self.assertEqual(result.conflict_results, (precedence,))

    def test_conflito_nao_material_e_representado_com_none(self) -> None:
        source_a = gaps.SourceReference("normative", "POL-A", "regra A", "autoridade A")
        source_b = gaps.SourceReference("workspace", "DOC-1", "registro")
        conflict = (source_a, source_b, "S", "impacto", "retomar", False, None)
        result = self.evaluate(conflicts=(conflict,))
        self.assertEqual(result.conflict_results, (None,))

    def test_dependencia_desconhecida_permanece_bloqueada(self) -> None:
        request = self.request(scopes=(ReviewScope("S", "Escopo", ("missing",), ("a.py",)),))
        conclusion = self.conclusion(state=ConclusionState.BLOCKED, sources=("run:1",),
                                     evidence=(), claims=())
        result = self.evaluate(request=request, conclusion=conclusion)
        self.assertIn("S", result.continuity.affected_scopes)
        self.assertTrue(any("não avaliado: missing" in reason
                            for item in result.continuity.scopes for reason in item.reasons))

    def test_bases_dos_avaliadores_existentes_sao_reutilizadas(self) -> None:
        with patch.object(protocol, "assess_change_proposal", wraps=protocol.assess_change_proposal) as change, \
             patch.object(protocol, "evaluate_source_conflict", wraps=protocol.evaluate_source_conflict) as conflict, \
             patch.object(protocol, "evaluate_scope_continuity", wraps=protocol.evaluate_scope_continuity) as continuity, \
             patch.object(protocol, "renderizar_resposta", wraps=protocol.renderizar_resposta) as renderer:
            proposal = ChangeProposal(
                ChangeKind.FUNCTIONAL, "S", ("a.py",), "proposal:2", "motivo",
                BehaviorIntent.CHANGE, "consequência", objective_reference="Revisar o comportamento declarado",
            )
            blocked = self.conclusion(state=ConclusionState.BLOCKED, evidence=(), claims=())
            result = self.evaluate(proposals=(proposal,), conclusion=blocked)
        change.assert_called_once()
        conflict.assert_not_called()
        continuity.assert_called_once()
        renderer.assert_called_once_with(result.response)

    def test_pipeline_nao_chama_io_rede_processos_ou_persistencia(self) -> None:
        import builtins
        import socket
        import subprocess

        with patch.object(builtins, "open", side_effect=AssertionError("I/O")) as opened, \
             patch.object(socket, "create_connection", side_effect=AssertionError("rede")) as network, \
             patch.object(subprocess, "Popen", side_effect=AssertionError("processo")) as process, \
             patch.object(gaps, "registrar_divergencia", side_effect=AssertionError("persistência")) as divergence, \
             patch.object(gaps, "registrar_blocker", side_effect=AssertionError("persistência")) as blocker, \
             patch.object(gaps, "registrar_resultado", side_effect=AssertionError("persistência")) as persisted, \
             patch.object(gaps, "registrar_decisao_existente", side_effect=AssertionError("persistência")) as decision, \
             patch.object(gaps, "publicar_documento", side_effect=AssertionError("persistência")) as publish:
            self.evaluate()
        for spy in (opened, network, process, divergence, blocker, persisted, decision, publish):
            spy.assert_not_called()

    def test_pipeline_copia_e_canonicaliza_colecoes_sem_mutar_entradas(self) -> None:
        findings = [
            ReviewFinding("S", TechnicalDimension.SOLID, "condição",
                          (self.evidence(reference="finding:1"),), "rule", "conclusão", "impacto")
        ]
        conclusion = self.conclusion(state=ConclusionState.BLOCKED,
                                     sources=("finding:1",), evidence=(), claims=())
        result = self.evaluate(findings=findings, conclusion=conclusion)
        findings.clear()
        self.assertEqual(len(result.findings), 1)
        self.assertIsInstance(result.findings, tuple)
        with self.assertRaises(FrozenInstanceError):
            result.rendered = "alterado"  # type: ignore[misc]

    def test_conclusao_bloqueada_permanece_fornecida_sem_estado_global(self) -> None:
        blocked = self.conclusion(state=ConclusionState.BLOCKED, evidence=(), claims=())
        result = self.evaluate(conclusion=blocked)
        self.assertIs(result.conclusion, blocked)
        self.assertIs(result.conclusion.state, ConclusionState.BLOCKED)
        with self.assertRaises(FrozenInstanceError):
            result.conclusion.state = ConclusionState.LIMITED  # type: ignore[misc]

    def test_conclusao_nao_pode_introduzir_claim_nao_fornecido(self) -> None:
        other = self.claim(reference="other:claim")
        conclusion = self.conclusion(claims=(other,))
        with self.assertRaises(ReviewInputError):
            self.evaluate(conclusion=conclusion)

    def test_dimension_especialista_e_authoritative_somente_com_contexto_fornecido(self) -> None:
        authority = AuthorityReference("authority:1", "Owner", "competência", ("S",))
        assessment = SpecialistAssessment(
            TechnicalDimension.SOLID, "S", "avaliação recebida", (self.evidence(),),
            AssessmentCharacter.AUTHORITATIVE, "Owner", "competência", authority,
        )
        dimension = DimensionAssessment(
            TechnicalDimension.SOLID, "S", DimensionAssessmentState.SPECIALIST_ASSESSMENT_RECEIVED,
            specialist_assessment=assessment,
        )
        with self.assertRaises(ReviewInputError):
            self.evaluate(dimensions=(dimension,))
        result = evaluate_review(
            self.request(), authority_context=AuthorityContext((authority,), ()),
            continuity_readiness_by_scope={"S": (True, True, True, True, True)},
            conclusion=self.conclusion(), response=self.response(), claims=(self.claim(),),
            dimension_assessments=(dimension,),
        )
        self.assertIs(result.dimension_assessments[0].specialist_assessment.character,
                      AssessmentCharacter.AUTHORITATIVE)


class PersistenceIntentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="rickcraft-review-persistence-")
        self.addCleanup(self.temporary.cleanup)
        base = Path(self.temporary.name)
        self.root = base / "impl" / "src" / "RickCraft"
        self.root.mkdir(parents=True)
        self.workspace = base / "impl" / ".workspace"
        self.workspace.mkdir(parents=True)

    @staticmethod
    def evaluated(*, grants=(AuthorizationGrant.REVIEW, AuthorizationGrant.LOCAL_PERSISTENCE),
                  effects=(RequestedEffect.LOCAL_PERSISTENCE,)) -> ReviewEvaluationResult:
        request = IntegratedReviewTests.request(grants=grants, effects=effects)
        return IntegratedReviewTests.evaluate(request=request)

    def intent(self, **kwargs: object) -> PersistenceIntent:
        return PersistenceIntent(self.root, "Continuidade e rastreabilidade da revisao", **kwargs)

    @staticmethod
    def fixed_clock() -> datetime:
        return datetime(2026, 10, 11, 12, 30, tzinfo=timezone.utc)

    def test_intent_e_imutavel_copia_proveniencia_aninhada(self) -> None:
        original = {"kind": "versioned_source", "locator": "source://a", "extra": {"tags": ["x"]}}
        intent = self.intent(provenance_inputs=[original])
        original["extra"]["tags"].append("mutado")
        self.assertEqual(intent.provenance_inputs[0]["extra"]["tags"], ("x",))
        with self.assertRaises(TypeError):
            intent.provenance_inputs[0]["kind"] = "changed"  # type: ignore[index]
        with self.assertRaises(FrozenInstanceError):
            intent.purpose = "alterado"  # type: ignore[misc]

    def test_ausencia_de_grant_rejeita_antes_de_qualquer_api_workspace(self) -> None:
        result = self.evaluated(grants=(AuthorizationGrant.REVIEW,))
        with patch.object(protocol.analysis_lifecycle, "criar_ou_retomar_analise") as lifecycle:
            with self.assertRaises(ReviewInputError):
                persist_review_evaluation(result, self.intent())
        lifecycle.assert_not_called()
        self.assertEqual(tuple(self.workspace.iterdir()), ())

    def test_effect_sem_grant_rejeita_antes_do_lifecycle(self) -> None:
        result = self.evaluated(grants=(AuthorizationGrant.REVIEW,),
                                effects=(RequestedEffect.LOCAL_PERSISTENCE,))
        with patch.object(protocol.analysis_lifecycle, "criar_ou_retomar_analise") as lifecycle:
            with self.assertRaises(ReviewInputError):
                persist_review_evaluation(result, self.intent())
        lifecycle.assert_not_called()

    def test_grant_sem_requested_effect_nao_persiste(self) -> None:
        result = self.evaluated(effects=())
        with patch.object(protocol.analysis_lifecycle, "criar_ou_retomar_analise") as lifecycle:
            with self.assertRaises(ReviewInputError):
                persist_review_evaluation(result, self.intent())
        lifecycle.assert_not_called()

    def test_evaluate_review_permanece_puro_sem_intent(self) -> None:
        with patch.object(protocol.analysis_lifecycle, "criar_ou_retomar_analise") as lifecycle, \
             patch.object(protocol.document_publisher, "publicar_documento") as publisher, \
             patch.object(protocol.document_recovery, "recuperar_documento") as recovery, \
             patch.object(protocol.document_search, "pesquisar_documentos") as search:
            result = IntegratedReviewTests.evaluate()
        self.assertIsInstance(result, ReviewEvaluationResult)
        lifecycle.assert_not_called()
        publisher.assert_not_called()
        recovery.assert_not_called()
        search.assert_not_called()
        self.assertEqual(tuple(self.workspace.iterdir()), ())

    def test_persistencia_real_reusa_lifecycle_publisher_recovery_e_schema_v1(self) -> None:
        result = self.evaluated()
        inputs = [{"kind": "versioned_source", "locator": "source://modulo",
                   "version_kind": "git_commit", "version": "abc123",
                   "sha256": "a" * 64, "verification": "MATCHED"}]
        intent = self.intent(provenance_inputs=inputs)
        with patch.object(protocol.document_search, "pesquisar_documentos",
                          wraps=protocol.document_search.pesquisar_documentos) as search:
            persisted = persist_review_evaluation(result, intent, clock=self.fixed_clock)
        self.assertIsInstance(persisted, PersistedReviewEvaluation)
        self.assertEqual(persisted.publication.document_type, "analysis")
        self.assertEqual(persisted.publication.analysis_id, persisted.analysis.analysis_id)
        self.assertEqual(persisted.recovered_document.parsed.corpo, result.rendered)
        self.assertEqual(persisted.recovered_document.parsed.metadata["schema_version"], 1)
        self.assertEqual(persisted.recovered_document.parsed.metadata["type_catalog_version"], 1)
        self.assertEqual(persisted.recovered_document.parsed.metadata["inputs"], inputs)
        self.assertIn(persisted.publication.document_id,
                      {item.document_id for item in persisted.recovered_analysis.documents})
        self.assertIsNone(persisted.search_result)
        search.assert_not_called()

    def test_nova_ocorrencia_e_append_only_e_resume_reusa_id_explicito(self) -> None:
        result = self.evaluated()
        first = persist_review_evaluation(result, self.intent(), clock=self.fixed_clock)
        old_bytes = first.publication.destination.read_bytes()
        old_digest = first.publication.sha256
        resumed_intent = self.intent(resume_analysis_id=first.analysis.analysis_id)
        with patch.object(protocol.analysis_lifecycle, "criar_ou_retomar_analise",
                          wraps=protocol.analysis_lifecycle.criar_ou_retomar_analise) as lifecycle:
            second = persist_review_evaluation(result, resumed_intent, clock=self.fixed_clock)
        lifecycle.assert_called_once_with(self.root, first.analysis.analysis_id)
        self.assertEqual(second.analysis.analysis_id, first.analysis.analysis_id)
        self.assertNotEqual(second.publication.document_id, first.publication.document_id)
        self.assertEqual(first.publication.destination.read_bytes(), old_bytes)
        self.assertEqual(first.publication.sha256, old_digest)
        self.assertEqual(second.recovered_document.parsed.corpo, result.rendered)

    def test_nova_analise_delega_geracao_de_identidade_ao_lifecycle(self) -> None:
        result = self.evaluated()
        with patch.object(protocol.analysis_lifecycle, "criar_ou_retomar_analise",
                          wraps=protocol.analysis_lifecycle.criar_ou_retomar_analise) as lifecycle:
            persisted = persist_review_evaluation(result, self.intent(), clock=self.fixed_clock)
        lifecycle.assert_called_once_with(self.root, None)
        self.assertTrue(persisted.analysis.analysis_id.startswith("ANL-"))

    def test_evidence_separada_exige_observacao_executada_e_relaciona_supports(self) -> None:
        result = self.evaluated()
        selected = result.claims[0].evidence[0]
        persisted = persist_review_evaluation(
            result, self.intent(evidence_to_persist=[selected]), clock=self.fixed_clock
        )
        self.assertEqual(len(persisted.evidence_publications), 1)
        evidence_doc = protocol.document_recovery.recuperar_documento(
            self.root, persisted.evidence_publications[0].document_id
        )
        self.assertEqual(evidence_doc.document_type, "evidence")
        self.assertEqual(evidence_doc.relations[0].relation_type, "supports")
        self.assertEqual(evidence_doc.relations[0].document_id, persisted.publication.document_id)

    def test_token_de_relacao_invalido_e_rejeitado_pelo_formato_spec1(self) -> None:
        result = self.evaluated()
        relation = {"relation_type": "invented", "document_id":
                    "DOC-12345678-1234-4234-8234-123456789abc"}
        with self.assertRaises(protocol.document_publisher.DocumentPublicationError) as caught:
            persist_review_evaluation(result, self.intent(relations=(relation,)),
                                      clock=self.fixed_clock)
        self.assertIsInstance(caught.exception.cause, document_format_api.DocumentFormatError)

    def test_provenance_nao_e_observada_automaticamente(self) -> None:
        result = self.evaluated()
        with patch.object(provenance_api, "observar_arquivo_local",
                          side_effect=AssertionError("observacao automatica")) as observe_file, \
             patch.object(provenance_api, "observar_documento_workspace",
                          side_effect=AssertionError("observacao automatica")) as observe_doc, \
             patch.object(provenance_api, "observar_fonte_versionada",
                          side_effect=AssertionError("observacao automatica")) as observe_version:
            persisted = persist_review_evaluation(result, self.intent(), clock=self.fixed_clock)
        self.assertEqual(persisted.recovered_document.parsed.metadata["inputs"], [])
        observe_file.assert_not_called()
        observe_doc.assert_not_called()
        observe_version.assert_not_called()

    def test_falha_de_recovery_propaga_excecao_real_sem_resultado(self) -> None:
        result = self.evaluated()
        failure = protocol.document_recovery.DocumentRecoveryError("falha de recovery")
        with patch.object(protocol.document_recovery, "recuperar_documento", side_effect=failure):
            with self.assertRaises(protocol.document_recovery.DocumentRecoveryError) as caught:
                persist_review_evaluation(result, self.intent(), clock=self.fixed_clock)
        self.assertIs(caught.exception, failure)

    def test_reported_inference_ou_evidence_nao_associada_nao_pode_ser_persistida(self) -> None:
        result = self.evaluated()
        reported = EvidenceReference(EvidenceKind.REPORTED, "host", "report:1", "a.py", "v1")
        for item in (reported, self.evidence_not_in_result()):
            with self.subTest(item=item), self.assertRaises(ReviewInputError):
                persist_review_evaluation(result, self.intent(evidence_to_persist=(item,)),
                                           clock=self.fixed_clock)

    @staticmethod
    def evidence_not_in_result() -> EvidenceReference:
        return EvidenceReference(EvidenceKind.INFERENCE, "host", "inference:1", "a.py", "v1")

    def test_search_somente_quando_query_explicita(self) -> None:
        result = self.evaluated()
        query = protocol.document_search.SearchQuery(document_type="analysis")
        with patch.object(protocol.document_search, "pesquisar_documentos",
                          wraps=protocol.document_search.pesquisar_documentos) as search:
            persisted = persist_review_evaluation(result, self.intent(search_query=query),
                                                  clock=self.fixed_clock)
        search.assert_called_once()
        self.assertIsNotNone(persisted.search_result)
        self.assertTrue(all(item.document_type == "analysis"
                            for item in persisted.search_result.matches))

    def test_intent_nao_pode_mutar_query_ou_provenance_original(self) -> None:
        nested = {"nested": [1, {"x": "y"}]}
        query_mapping = {"purpose": "Continuidade", "nested": ["original"]}
        query = protocol.document_search.SearchQuery(metadata_equals=query_mapping)
        intent = self.intent(provenance_inputs=[nested], search_query=query)
        nested["nested"].append(2)
        query_mapping["nested"].append("mutated")
        self.assertEqual(intent.provenance_inputs[0]["nested"][1]["x"], "y")
        self.assertEqual(intent.search_query.metadata_equals["nested"], ("original",))

    def test_search_terms_invalidos_nao_sao_coagidos_silenciosamente(self) -> None:
        with self.assertRaises(ReviewInputError):
            self.intent(search_query=protocol.document_search.SearchQuery(text_terms="abc"))  # type: ignore[arg-type]

    def test_falha_do_publisher_propaga_sem_receipt_ficticio(self) -> None:
        result = self.evaluated()
        failure = RuntimeError("falha de publicacao")
        with patch.object(protocol.document_publisher, "publicar_documento", side_effect=failure):
            with self.assertRaisesRegex(RuntimeError, "falha de publicacao"):
                persist_review_evaluation(result, self.intent(), clock=self.fixed_clock)


class NegativeBoundaryTests(unittest.TestCase):
    @staticmethod
    def _snapshot_tree(root: Path) -> tuple[tuple[str, str, str], ...] | None:
        """Inventaria uma árvore sem seguir links e sem modificá-la."""
        if not root.exists():
            return None
        entries: list[tuple[str, str, str]] = []
        for current, directories, files in os.walk(root, followlinks=False):
            current_path = Path(current)
            for name in tuple(directories):
                path = current_path / name
                relative = path.relative_to(root).as_posix()
                if path.is_symlink():
                    entries.append((relative, "symlink-dir", os.readlink(path)))
                    directories.remove(name)
                else:
                    entries.append((relative, "dir", ""))
            for name in files:
                path = current_path / name
                relative = path.relative_to(root).as_posix()
                if path.is_symlink():
                    entries.append((relative, "symlink-file", os.readlink(path)))
                else:
                    entries.append((relative, "file", hashlib.sha256(path.read_bytes()).hexdigest()))
        return tuple(sorted(entries))

    @staticmethod
    def _forbidden_boundary_patches():
        boundaries = (
            (protocol.analysis_lifecycle, "criar_ou_retomar_analise"),
            (protocol.document_publisher, "publicar_documento"),
            (protocol.document_recovery, "recuperar_documento"),
            (protocol.document_recovery, "recuperar_analise"),
            (protocol.document_search, "pesquisar_documentos"),
            (gaps, "registrar_divergencia"),
            (gaps, "registrar_blocker"),
            (gaps, "registrar_decisao_existente"),
            (gaps, "registrar_resultado"),
            (provenance_api, "observar_arquivo_local"),
            (provenance_api, "observar_documento_workspace"),
            (provenance_api, "observar_fonte_versionada"),
            (subprocess, "run"),
            (subprocess, "Popen"),
            (os, "system"),
            (socket, "create_connection"),
            (urllib.request, "urlopen"),
        )
        return tuple(
            patch.object(owner, name, side_effect=AssertionError(f"fronteira inesperada: {name}"))
            for owner, name in boundaries
        )

    def test_review_only_integrado_preserva_artifact_e_nao_chama_fronteiras_de_efeito(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rickcraft-review-only-") as temporary:
            fixture = Path(temporary)
            artifact = fixture / "a.py"
            original_bytes = "# artefato examinado\nvalor = 'preservar'\n".encode("utf-8")
            artifact.write_bytes(original_bytes)
            fixture_before = self._snapshot_tree(fixture)
            real_workspace = Path(__file__).resolve().parents[1] / ".workspace"
            workspace_before = self._snapshot_tree(real_workspace)

            request = replace(
                IntegratedReviewTests.request(
                    grants=(AuthorizationGrant.REVIEW,), effects=()
                ),
                objective=("Revisar somente; publicar, push, upload, sync e Release são texto, "
                           "não autorizações."),
            )
            evidence = IntegratedReviewTests.evidence(reference="run:review-only")
            finding = ReviewFinding(
                "S", TechnicalDimension.SOLID, "Condição observada", (evidence,),
                "regra fornecida", "Conclusão limitada", "Impacto localizado",
                recommendation="Considerar uma refatoração manual posterior.",
            )
            proposal = ChangeProposal(
                ChangeKind.FUNCTIONAL, "S", ("a.py",), "proposal:functional",
                "proposta avaliada", BehaviorIntent.CHANGE, "efeito funcional proposto",
                objective_reference=request.objective,
            )
            conclusion = IntegratedReviewTests.conclusion(
                request=request, state=ConclusionState.BLOCKED,
                artifacts=("a.py",), sources=(evidence.reference,),
                evidence=(evidence,), claims=(), versions=(),
            )
            response = ReviewResponse(None, (
                ReviewResponseBlock(ResponseBlockKey.CRITICAL_ANALYSIS,
                                    "Análise Crítica", "Achado limitado ao escopo S."),
                ReviewResponseBlock(ResponseBlockKey.REFACTORING,
                                    "Refatoração", finding.recommendation + " Não executada."),
                ReviewResponseBlock(ResponseBlockKey.ARCHITECTURAL_JUSTIFICATION,
                                    "Justificativa Arquitetural", "Sem impacto arquitetural material."),
            ))

            with ExitStack() as stack:
                spies = [stack.enter_context(item) for item in self._forbidden_boundary_patches()]
                result = IntegratedReviewTests.evaluate(
                    request=request, findings=(finding,), proposals=(proposal,),
                    conclusion=conclusion, response=response,
                )

            self.assertIsInstance(result, ReviewEvaluationResult)
            self.assertIs(result.conclusion.state, ConclusionState.BLOCKED)
            self.assertIn("Não executada", result.rendered)
            self.assertIs(result.behavior_assessments[0].state,
                          BehaviorAssessmentState.FUNCTIONAL_CHANGE_UNAUTHORIZED)
            self.assertEqual(artifact.read_bytes(), original_bytes)
            self.assertEqual(self._snapshot_tree(fixture), fixture_before)
            self.assertEqual(self._snapshot_tree(real_workspace), workspace_before)
            for spy in spies:
                spy.assert_not_called()

    def test_proposta_estrutural_sem_grant_e_rejeitada_sem_materializacao(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rickcraft-review-structural-denied-") as temporary:
            fixture = Path(temporary)
            artifact = fixture / "a.py"
            artifact.write_bytes(b"original\n")
            before = self._snapshot_tree(fixture)
            request = IntegratedReviewTests.request(grants=(AuthorizationGrant.REVIEW,))
            proposal = ChangeProposal(
                ChangeKind.STRUCTURAL, "S", ("a.py",), "proposal:structural",
                "recomendação estrutural", BehaviorIntent.PRESERVE, "contrato preservado",
                objective_reference=request.objective,
            )
            with ExitStack() as stack:
                spies = [stack.enter_context(item) for item in self._forbidden_boundary_patches()]
                with self.assertRaisesRegex(ReviewInputError, "STRUCTURAL_CHANGE"):
                    IntegratedReviewTests.evaluate(request=request, proposals=(proposal,))
            self.assertEqual(artifact.read_bytes(), b"original\n")
            self.assertEqual(self._snapshot_tree(fixture), before)
            for spy in spies:
                spy.assert_not_called()

    def test_externality_e_mencao_textual_nao_ativam_fronteiras_externas(self) -> None:
        with ExitStack() as stack:
            spies = [stack.enter_context(item) for item in self._forbidden_boundary_patches()]
            request = IntegratedReviewTests.request(effects=(RequestedEffect.EXTERNALITY,))
            with self.assertRaisesRegex(ReviewInputError, "EXTERNALITY"):
                IntegratedReviewTests.evaluate(request=request)

            textual_request = replace(
                IntegratedReviewTests.request(),
                objective="Revisar; fazer push, upload, sync ou Release é apenas texto.",
            )
            result = IntegratedReviewTests.evaluate(request=textual_request)
        self.assertIsInstance(result, ReviewEvaluationResult)
        for spy in spies:
            spy.assert_not_called()

    def test_runtime_nao_importa_capacidades_de_rede_processo_git_ou_release(self) -> None:
        source = (RUNTIME_DIRECTORY / "review_protocol.py").read_text(
            encoding="utf-8", errors="strict"
        )
        tree = ast.parse(source)
        imported = {
            alias.name.split(".", 1)[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported.update(
            node.module.split(".", 1)[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        )
        self.assertTrue(imported.isdisjoint({"subprocess", "socket", "urllib", "requests", "git"}))


if __name__ == "__main__":
    unittest.main()
