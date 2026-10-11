from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path
import sys
import unittest

RUNTIME_DIRECTORY = Path(__file__).resolve().parents[1] / "src" / "RickCraft"
sys.path.insert(0, str(RUNTIME_DIRECTORY))

from review_protocol import (  # noqa: E402
    AuthorizationGrant,
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


if __name__ == "__main__":
    unittest.main()
