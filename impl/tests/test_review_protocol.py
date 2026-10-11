from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path
import sys
import unittest

RUNTIME_DIRECTORY = Path(__file__).resolve().parents[1] / "src" / "RickCraft"
sys.path.insert(0, str(RUNTIME_DIRECTORY))

from review_protocol import (  # noqa: E402
    AuthorizationGrant,
    AuthorityContext,
    AuthorityReference,
    AuthorizedPrecedence,
    RequestedEffect,
    ReviewInputError,
    ReviewRequest,
    ReviewScope,
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


if __name__ == "__main__":
    unittest.main()
