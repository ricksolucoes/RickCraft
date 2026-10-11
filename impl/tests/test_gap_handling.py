from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import inspect
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


RUNTIME_DIRECTORY = Path(__file__).resolve().parents[1] / "src" / "RickCraft"
sys.path.insert(0, str(RUNTIME_DIRECTORY))

import document_publisher
import gap_handling as gaps
from document_catalog import DOCUMENT_TYPES
from document_format import TOKENS_RELACAO, parsear_documento
from document_publisher import DocumentPublicationError
from document_recovery import recuperar_documento
from workspace_resolver import RaizWorkspaceSelecionada, TipoRaizWorkspace


ANALYSIS_ID = "ANL-aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
TIME = datetime(2026, 10, 11, 15, 30, tzinfo=timezone.utc)


def _workspace_snapshot(root: Path) -> tuple[tuple[str, str, str], ...]:
    if not root.exists():
        return ()
    items = []
    for path in sorted(root.rglob("*")):
        relative = str(path.relative_to(root))
        if path.is_symlink():
            items.append((relative, "symlink", str(path.readlink())))
        elif path.is_file():
            items.append((relative, "file", hashlib.sha256(path.read_bytes()).hexdigest()))
        elif path.is_dir():
            items.append((relative, "directory", ""))
    return tuple(items)


def normative(reference: str, statement: str) -> gaps.SourceReference:
    return gaps.SourceReference("normative", reference, statement, "Project Decision Owner")


def workspace(reference: str, statement: str) -> gaps.SourceReference:
    return gaps.SourceReference("workspace", reference, statement)


class GapHandlingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="rickcraft-gap-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.rickcraft_root = self.base / "repo" / "impl" / "src" / "RickCraft"
        self.rickcraft_root.mkdir(parents=True)
        self.workspace_root = self.rickcraft_root.parent.parent / ".workspace"
        self.workspace_root.mkdir()
        (self.workspace_root / ANALYSIS_ID).mkdir()
        self.resolutions: list[tuple[Path, Path]] = []

        def resolver(root, evaluator):
            self.resolutions.append((Path(root), self.workspace_root))
            return RaizWorkspaceSelecionada(
                TipoRaizWorkspace.PREFERENCIAL, self.workspace_root
            )

        self.resolver = resolver

        def evaluator_factory():
            def evaluator(_path):
                raise AssertionError("D-02 não deve ser chamado pelo resolver controlado")
            return evaluator

        self.evaluator_factory = evaluator_factory

    def publish_kwargs(self):
        return {
            "clock": lambda: TIME,
            "resolver": self.resolver,
            "avaliador_factory": self.evaluator_factory,
        }

    def divergence_case(self) -> gaps.DivergenceCase:
        return gaps.DivergenceCase(
            occurrence="Duas observações têm valores incompatíveis.",
            references=(normative("SPEC §x", "regra X"), workspace("DOC-1", "regra Y")),
            affected_scope="publicação do tipo X",
            impact="o resultado pode alterar o comportamento",
            unresolved_reason="não cabe ao executor substituir a fonte aplicável",
            resume_condition="obter decisão da autoridade competente",
            required_authority="Decision Owner competente",
            required_evidence="referência verificável da decisão",
        )

    def blocker_case(self, **changes) -> gaps.BlockerCase:
        fields = {
            "affected_scope": "operação A",
            "cause": "a entrada obrigatória não foi fornecida",
            "dependency": "campo de configuração X",
            "resume_condition": "receber e validar o valor X",
            "required_information": "valor X fornecido pelo responsável",
        }
        fields.update(changes)
        return gaps.BlockerCase(**fields)

    def decision_case(self, **changes) -> gaps.ExistingDecisionCase:
        fields = {
            "decision": "manter a regra formalizada em D-01",
            "decision_owner": "Responsável pelo projeto",
            "owner_authority_reference": "POL-0000000001 §4",
            "source_reference": "status.md, decisão de 2026-10-10",
            "scope": "SPEC-0000000001",
            "justification": "decisão já aprovada e registrada",
            "explicitly_existing": True,
        }
        fields.update(changes)
        return gaps.ExistingDecisionCase(**fields)

    def result_case(self, **changes) -> gaps.OperationalResultCase:
        fields = {
            "operation": "consulta fixture",
            "outcome": "documentos processados com evidências registradas",
            "evidence_references": ("fixture/result-1",),
            "limitations": ("nenhum acesso externo realizado",),
            "blocked_scopes": ("operação A",),
            "scope_requests": (gaps.ScopeRequest("operação B", (), True, True, True, True, True),),
        }
        fields.update(changes)
        return gaps.OperationalResultCase(**fields)

    def read_published(self, receipt):
        data = receipt.publication.destination.read_bytes()
        parsed = parsear_documento(data)
        self.assertEqual(parsed.metadata["document_type"], receipt.document_type)
        self.assertEqual(parsed.metadata["analysis_id"], ANALYSIS_ID)
        self.assertEqual(parsed.metadata["document_id"], receipt.persisted_document_id)
        recovered = recuperar_documento(
            self.rickcraft_root,
            receipt.persisted_document_id,
            resolver=self.resolver,
            avaliador_factory=self.evaluator_factory,
        )
        self.assertEqual(recovered.document_id, receipt.persisted_document_id)
        return parsed

    # Divergence, blocker e registros mínimos
    def test_01_conflito_de_observacoes_classifica_divergencia(self):
        assessment = gaps.avaliar_conflito_fontes(
            normative("SPEC §1", "X"), workspace("DOC-A", "Y"),
            affected_scope="parte A", impact="impacto material",
            resume_condition="decisão explícita", materially_incompatible=True,
        )
        self.assertIsNotNone(assessment)
        self.assertEqual(assessment.divergence.affected_scope, "parte A")

    def test_02_divergencia_registra_ocorrencia(self):
        self.assertEqual(self.divergence_case().occurrence, "Duas observações têm valores incompatíveis.")

    def test_03_divergencia_registra_referencias(self):
        self.assertEqual(len(self.divergence_case().references), 2)

    def test_04_divergencia_registra_impacto(self):
        self.assertTrue(self.divergence_case().impact)

    def test_05_divergencia_registra_razao_para_nao_decidir(self):
        self.assertTrue(self.divergence_case().unresolved_reason)

    def test_06_divergencia_normativa_nao_escolhe_vencedor_sem_precedencia(self):
        result = gaps.avaliar_conflito_fontes(
            normative("POL-A", "X"), normative("POL-B", "Y"),
            affected_scope="parte A", impact="regras incompatíveis",
            resume_condition="autoridade formalizar precedência", materially_incompatible=True,
        )
        self.assertIsNone(result.authoritative_reference)
        self.assertTrue(result.blocker_required)

    def test_07_divergencia_workspace_preserva_referencia_normativa(self):
        result = gaps.avaliar_conflito_fontes(
            workspace("DOC-A", "Y"), normative("POL-A", "X"),
            affected_scope="parte A", impact="texto incompatível",
            resume_condition="revisar registro", materially_incompatible=True,
        )
        self.assertEqual(result.authoritative_reference, "POL-A")
        self.assertFalse(result.blocker_required)

    def test_08_sem_incompatibilidade_nao_cria_divergencia(self):
        result = gaps.avaliar_conflito_fontes(
            normative("POL-A", "X"), workspace("DOC-A", "X"),
            affected_scope="parte A", impact="sem impacto", resume_condition="nenhuma",
            materially_incompatible=False,
        )
        self.assertIsNone(result)

    def test_09_divergencia_publica_tipo_correto_e_parseia(self):
        receipt = gaps.registrar_divergencia(
            self.rickcraft_root, ANALYSIS_ID, self.divergence_case(),
            purpose="Registrar conflito observado", **self.publish_kwargs(),
        )
        parsed = self.read_published(receipt)
        self.assertEqual(receipt.document_type, "divergence")
        self.assertIn("Razão para não resolver silenciosamente", parsed.corpo)

    def test_10_divergencia_rejeita_uma_referencia(self):
        with self.assertRaises(gaps.GapHandlingError):
            gaps.registrar_divergencia(
                self.rickcraft_root, ANALYSIS_ID,
                gaps.DivergenceCase("evento", (normative("SPEC", "X"),), "A", "impacto", "razão", "retomar"),
                purpose="Divergência inválida", **self.publish_kwargs(),
            )

    def test_11_blocker_registra_escopo_e_condicao_de_retomada(self):
        case = self.blocker_case()
        self.assertEqual(case.affected_scope, "operação A")
        self.assertEqual(case.resume_condition, "receber e validar o valor X")

    def test_12_blocker_requer_causa_verificavel(self):
        with self.assertRaises(gaps.GapHandlingError):
            gaps.registrar_blocker(
                self.rickcraft_root, ANALYSIS_ID, self.blocker_case(cause=" "),
                purpose="Blocker inválido", **self.publish_kwargs(),
            )

    def test_13_blocker_requer_dependencia(self):
        with self.assertRaises(gaps.GapHandlingError):
            gaps.registrar_blocker(
                self.rickcraft_root, ANALYSIS_ID, self.blocker_case(dependency=""),
                purpose="Blocker inválido", **self.publish_kwargs(),
            )

    def test_14_blocker_requer_condicao_de_retomada(self):
        with self.assertRaises(gaps.GapHandlingError):
            gaps.registrar_blocker(
                self.rickcraft_root, ANALYSIS_ID, self.blocker_case(resume_condition=""),
                purpose="Blocker inválido", **self.publish_kwargs(),
            )

    def test_15_blocker_requer_informacao_autoridade_ou_evidencia(self):
        with self.assertRaises(gaps.GapHandlingError):
            gaps.registrar_blocker(
                self.rickcraft_root, ANALYSIS_ID,
                self.blocker_case(required_information=None),
                purpose="Blocker incompleto", **self.publish_kwargs(),
            )

    def test_16_blocker_de_evidencia_insuficiente_registra_evidencia_faltante(self):
        receipt = gaps.registrar_blocker(
            self.rickcraft_root, ANALYSIS_ID,
            self.blocker_case(
                cause="evidência atual não permite comparação",
                required_information=None,
                required_evidence="obter referência verificável da versão atual",
            ),
            purpose="Registrar evidência insuficiente", **self.publish_kwargs(),
        )
        self.assertIn("obter referência verificável", self.read_published(receipt).corpo)

    def test_17_ambiguidade_material_produz_blocker(self):
        receipt = gaps.registrar_blocker(
            self.rickcraft_root, ANALYSIS_ID,
            self.blocker_case(
                cause="duas interpretações alteram o comportamento",
                dependency="esclarecimento do requisito",
                required_information="definição inequívoca do requisito",
            ),
            purpose="Registrar ambiguidade material", **self.publish_kwargs(),
        )
        self.assertEqual(receipt.document_type, "blocker")

    def test_18_owner_indisponivel_bloqueia_sem_promover_executor(self):
        receipt = gaps.registrar_blocker(
            self.rickcraft_root, ANALYSIS_ID,
            self.blocker_case(
                cause="Decision Owner não está disponível",
                dependency="decisão reservada à autoridade competente",
                required_information=None,
                required_authority="Decision Owner indicado na fonte vigente",
            ),
            purpose="Registrar autoridade indisponível", **self.publish_kwargs(),
        )
        body = self.read_published(receipt).corpo
        self.assertIn("Decision Owner indicado", body)
        self.assertNotIn("Executor promovido", body)

    def test_19_blocker_publica_tipo_correto_e_parseia(self):
        receipt = gaps.registrar_blocker(
            self.rickcraft_root, ANALYSIS_ID, self.blocker_case(),
            purpose="Registrar informação ausente", **self.publish_kwargs(),
        )
        parsed = self.read_published(receipt)
        self.assertEqual(receipt.document_type, "blocker")
        self.assertIn("Condição objetiva de retomada", parsed.corpo)

    def test_20_falhas_de_lacuna_nao_criam_diretorio_antes_da_validacao(self):
        before = tuple(self.workspace_root.rglob("*"))
        with self.assertRaises(gaps.GapHandlingError):
            gaps.registrar_blocker(
                self.rickcraft_root, ANALYSIS_ID,
                self.blocker_case(required_evidence="", required_information=None),
                purpose="inválido", **self.publish_kwargs(),
            )
        self.assertEqual(tuple(self.workspace_root.rglob("*")), before)

    # Decision: somente decisão existente, owner e fonte explícitos
    def test_19_decisao_existente_owner_fonte_escopo_sao_registrados(self):
        receipt = gaps.registrar_decisao_existente(
            self.rickcraft_root, ANALYSIS_ID, self.decision_case(),
            purpose="Registrar decisão aprovada", **self.publish_kwargs(),
        )
        parsed = self.read_published(receipt)
        for phrase in ("Responsável pelo projeto", "POL-0000000001 §4", "status.md", "SPEC-0000000001"):
            self.assertIn(phrase, parsed.corpo)
        self.assertEqual(receipt.document_type, "decision")

    def test_20_owner_ausente_rejeita_decision(self):
        with self.assertRaises(gaps.GapHandlingError):
            gaps.registrar_decisao_existente(
                self.rickcraft_root, ANALYSIS_ID, self.decision_case(decision_owner=""),
                purpose="Decisão inválida", **self.publish_kwargs(),
            )

    def test_21_fonte_ausente_rejeita_decision(self):
        with self.assertRaises(gaps.GapHandlingError):
            gaps.registrar_decisao_existente(
                self.rickcraft_root, ANALYSIS_ID, self.decision_case(source_reference=""),
                purpose="Decisão inválida", **self.publish_kwargs(),
            )

    def test_22_referencia_de_competencia_do_owner_e_obrigatoria(self):
        with self.assertRaises(gaps.GapHandlingError):
            gaps.registrar_decisao_existente(
                self.rickcraft_root, ANALYSIS_ID,
                self.decision_case(owner_authority_reference=""),
                purpose="Decisão sem autoridade demonstrada", **self.publish_kwargs(),
            )

    def test_23_proposta_nao_e_decisao_existente(self):
        with self.assertRaises(gaps.GapHandlingError):
            gaps.registrar_decisao_existente(
                self.rickcraft_root, ANALYSIS_ID,
                self.decision_case(explicitly_existing=False),
                purpose="Proposta", **self.publish_kwargs(),
            )

    def test_24_hipotese_nao_e_decisao_existente(self):
        with self.assertRaises(gaps.GapHandlingError):
            gaps.registrar_decisao_existente(
                self.rickcraft_root, ANALYSIS_ID,
                self.decision_case(explicitly_existing=False, decision="hipótese: escolher X"),
                purpose="Hipótese", **self.publish_kwargs(),
            )

    def test_25_decisao_existente_deve_ser_assertion_booleano(self):
        with self.assertRaises(gaps.GapHandlingError):
            gaps.registrar_decisao_existente(
                self.rickcraft_root, ANALYSIS_ID,
                self.decision_case(explicitly_existing="yes"),
                purpose="Hipótese", **self.publish_kwargs(),
            )

    def test_26_decision_nao_transfere_authority(self):
        receipt = gaps.registrar_decisao_existente(
            self.rickcraft_root, ANALYSIS_ID, self.decision_case(),
            purpose="Registro sem transferência", **self.publish_kwargs(),
        )
        parsed = self.read_published(receipt)
        self.assertIn("não transfere autoridade", parsed.corpo)

    # Result: observação operacional, sem estado SDD
    def test_25_resultado_operacional_registra_limitacoes(self):
        receipt = gaps.registrar_resultado(
            self.rickcraft_root, ANALYSIS_ID, self.result_case(),
            purpose="Registrar resultado de operação", **self.publish_kwargs(),
        )
        parsed = self.read_published(receipt)
        self.assertEqual(receipt.document_type, "result")
        self.assertIn("nenhum acesso externo realizado", parsed.corpo)

    def test_26_resultado_registra_operacao_independente_continuavel(self):
        receipt = gaps.registrar_resultado(
            self.rickcraft_root, ANALYSIS_ID, self.result_case(),
            purpose="Resultado localizado", **self.publish_kwargs(),
        )
        parsed = self.read_published(receipt)
        self.assertIn("operação B", parsed.corpo)
        self.assertIn("operação A", parsed.corpo)

    def test_resultado_nao_aceita_lista_manual_de_continuaveis(self):
        with self.assertRaises(TypeError):
            gaps.OperationalResultCase(
                operation="consulta", outcome="feito", continuable_scopes=("B",)
            )

    def test_27_resultado_nao_pode_declarar_analyze_pass(self):
        with self.assertRaises(gaps.GapHandlingError):
            gaps.registrar_resultado(
                self.rickcraft_root, ANALYSIS_ID,
                self.result_case(outcome="ANALYZE PASS"),
                purpose="Gate inválido", **self.publish_kwargs(),
            )

    def test_28_resultado_nao_pode_declarar_converged(self):
        with self.assertRaises(gaps.GapHandlingError):
            gaps.registrar_resultado(
                self.rickcraft_root, ANALYSIS_ID,
                self.result_case(outcome="CONVERGED"),
                purpose="Gate inválido", **self.publish_kwargs(),
            )

    def test_29_resultado_nao_modifica_status_sdd(self):
        status = Path(__file__).resolve().parents[2] / "specs" / "SPEC-0000000001-workspace-operacional-rastreavel" / "status.md"
        before = hashlib.sha256(status.read_bytes()).digest()
        gaps.registrar_resultado(
            self.rickcraft_root, ANALYSIS_ID, self.result_case(),
            purpose="Resultado não altera status", **self.publish_kwargs(),
        )
        self.assertEqual(hashlib.sha256(status.read_bytes()).digest(), before)

    def test_30_resultado_nao_cria_campos_de_gate(self):
        receipt = gaps.registrar_resultado(
            self.rickcraft_root, ANALYSIS_ID, self.result_case(),
            purpose="Resultado operacional", **self.publish_kwargs(),
        )
        metadata = self.read_published(receipt).metadata
        self.assertNotIn("analyze", metadata)
        self.assertNotIn("converge", metadata)

    # Authority boundaries and conflict classification
    def test_31_policy_fixture_prevalece_sobre_workspace(self):
        self.assertEqual(self._normative_wins("POL-0000000001 §4").authoritative_reference, "POL-0000000001 §4")

    def test_32_registry_fixture_prevalece_sobre_workspace(self):
        self.assertEqual(self._normative_wins("registries/policies.md").authoritative_reference, "registries/policies.md")

    def test_33_spec_fixture_prevalece_sobre_workspace(self):
        self.assertEqual(self._normative_wins("spec.md#RF-011").authoritative_reference, "spec.md#RF-011")

    def test_34_plan_fixture_prevalece_sobre_workspace(self):
        self.assertEqual(self._normative_wins("plan.md#D-08").authoritative_reference, "plan.md#D-08")

    def test_35_tasks_fixture_prevalece_sobre_workspace(self):
        self.assertEqual(self._normative_wins("tasks.md#TASK-011").authoritative_reference, "tasks.md#TASK-011")

    def test_36_status_fixture_prevalece_sobre_workspace(self):
        self.assertEqual(self._normative_wins("status.md#gate").authoritative_reference, "status.md#gate")

    def test_37_gate_fixture_prevalece_sobre_workspace(self):
        self.assertEqual(self._normative_wins("ANALYZE-03").authoritative_reference, "ANALYZE-03")

    def _normative_wins(self, reference: str) -> gaps.ConflictAssessment:
        assessment = gaps.avaliar_conflito_fontes(
            normative(reference, "X vigente"), workspace("DOC-workspace", "Y incompatível"),
            affected_scope="operação dependente", impact="mudaria a regra aplicável",
            resume_condition="registrar a divergência", materially_incompatible=True,
        )
        self.assertIn("não a substitui", assessment.divergence.unresolved_reason)
        return assessment

    def test_38_workspace_nao_cria_autorizacao_de_continuidade(self):
        result = gaps.avaliar_continuidade_localizada(
            ("A",), (gaps.ScopeRequest("B", explicitly_authorized=False,
                information_sufficient=True, evidence_sufficient=True,
                authority_sufficient=True, conflict_free=True),),
        )
        self.assertNotIn("B", result.continuable_scopes)

    def test_39_workspace_nao_cria_analyze_pass_ou_converged(self):
        ref = workspace("DOC-A", "ANALYZE PASS and CONVERGED")
        assessment = gaps.avaliar_conflito_fontes(
            normative("status.md", "ANALYZE INVALIDATED"), ref,
            affected_scope="IMPLEMENT", impact="status incompatível",
            resume_condition="verificar gate real", materially_incompatible=True,
        )
        self.assertEqual(assessment.authoritative_reference, "status.md")

    def test_40_conflito_normativo_sem_precedencia_bloqueia_sem_vencedor(self):
        result = gaps.avaliar_conflito_fontes(
            normative("POL-A", "X"), normative("POL-B", "Y"),
            affected_scope="operação X", impact="regras incompatíveis",
            resume_condition="autoridade resolver", materially_incompatible=True,
        )
        self.assertTrue(result.blocker_required)
        self.assertIsNone(result.authoritative_reference)
        self.assertTrue(result.required_authority)

    def test_41_conflito_normativo_pode_gerar_divergence_e_blocker(self):
        conflict = gaps.avaliar_conflito_fontes(
            normative("POL-A", "X"), normative("POL-B", "Y"),
            affected_scope="parte dependente", impact="conflito normativo",
            resume_condition="decisão formal registrada", materially_incompatible=True,
        )
        divergence = gaps.registrar_divergencia(
            self.rickcraft_root, ANALYSIS_ID, conflict.divergence,
            purpose="Registrar conflito normativo", **self.publish_kwargs(),
        )
        blocker = gaps.registrar_blocker(
            self.rickcraft_root, ANALYSIS_ID,
            self.blocker_case(
                affected_scope="parte dependente", cause="duas fontes normativas incompatíveis",
                dependency="precedência formal", required_authority=conflict.required_authority,
                required_information=None,
            ),
            purpose="Bloquear somente a operação dependente", **self.publish_kwargs(),
        )
        self.assertEqual(divergence.document_type, "divergence")
        self.assertEqual(blocker.document_type, "blocker")

    def test_42_invalid_source_category_rejected(self):
        with self.assertRaises(gaps.GapHandlingError):
            gaps.avaliar_conflito_fontes(
                gaps.SourceReference("latest_wins", "X", "statement"), workspace("D", "Y"),
                affected_scope="A", impact="I", resume_condition="R", materially_incompatible=True,
            )

    def test_43_source_reference_cannot_be_empty(self):
        with self.assertRaises(gaps.GapHandlingError):
            gaps.avaliar_conflito_fontes(
                normative(" ", "X"), workspace("D", "Y"),
                affected_scope="A", impact="I", resume_condition="R", materially_incompatible=True,
            )

    # Interrupção localizada: somente escopo dependente/unqualified é bloqueado
    def test_44_escopo_afetado_fica_nao_continuavel(self):
        result = gaps.avaliar_continuidade_localizada(
            ("A",), (gaps.ScopeRequest("A", explicitly_authorized=True,
                information_sufficient=True, evidence_sufficient=True,
                authority_sufficient=True, conflict_free=True),),
        )
        self.assertNotIn("A", result.continuable_scopes)

    def test_45_escopo_independente_autorizado_e_apto_pode_continuar(self):
        result = gaps.avaliar_continuidade_localizada(
            ("A",), (gaps.ScopeRequest("B", (), True, True, True, True, True),),
        )
        self.assertEqual(result.continuable_scopes, ("B",))

    def test_46_escopo_dependente_de_A_nao_continua(self):
        result = gaps.avaliar_continuidade_localizada(
            ("A",), (gaps.ScopeRequest("B", ("A",), True, True, True, True, True),),
        )
        self.assertNotIn("B", result.continuable_scopes)

    def test_47_escopo_independente_sem_autorizacao_nao_continua(self):
        result = gaps.avaliar_continuidade_localizada(
            ("A",), (gaps.ScopeRequest("B", (), False, True, True, True, True),),
        )
        self.assertNotIn("B", result.continuable_scopes)

    def test_48_blocker_local_nao_bloqueia_parte_independente_autorizada(self):
        result = gaps.avaliar_continuidade_localizada(
            ("A",), (
                gaps.ScopeRequest("A", (), False, False, False, False, False),
                gaps.ScopeRequest("B", (), True, True, True, True, True),
            ),
        )
        self.assertEqual(result.continuable_scopes, ("B",))

    def test_49_evidencia_independente_de_B_pode_ser_suficiente(self):
        result = gaps.avaliar_continuidade_localizada(
            ("A",), (gaps.ScopeRequest("B", (), True, True, True, True, True),),
        )
        self.assertTrue(next(item for item in result.scopes if item.scope == "B").continuable)

    def test_50_insuficiencia_de_informacao_impede_continuidade(self):
        result = gaps.avaliar_continuidade_localizada(
            ("A",), (gaps.ScopeRequest("B", (), True, False, True, True, True),),
        )
        self.assertNotIn("B", result.continuable_scopes)

    def test_51_insuficiencia_de_evidencia_impede_continuidade(self):
        result = gaps.avaliar_continuidade_localizada(
            ("A",), (gaps.ScopeRequest("B", (), True, True, False, True, True),),
        )
        self.assertNotIn("B", result.continuable_scopes)

    def test_52_insuficiencia_de_autoridade_impede_continuidade(self):
        result = gaps.avaliar_continuidade_localizada(
            ("A",), (gaps.ScopeRequest("B", (), True, True, True, False, True),),
        )
        self.assertNotIn("B", result.continuable_scopes)

    def test_53_conflito_nao_resolvido_impede_continuidade(self):
        result = gaps.avaliar_continuidade_localizada(
            ("A",), (gaps.ScopeRequest("B", (), True, True, True, True, False),),
        )
        self.assertNotIn("B", result.continuable_scopes)

    def test_54_booleanos_de_continuidade_nao_coagem_string(self):
        with self.assertRaises(gaps.GapHandlingError):
            gaps.avaliar_continuidade_localizada(
                ("A",), (gaps.ScopeRequest("B", (), "yes", True, True, True, True),),
            )

    def test_55_assessment_nao_executa_escopo_continuavel(self):
        result = gaps.avaliar_continuidade_localizada(
            ("A",), (gaps.ScopeRequest("B", (), True, True, True, True, True),),
        )
        self.assertEqual(result.continuable_scopes, ("B",))
        self.assertFalse(hasattr(result, "execution_result"))

    # Persistência TASK-008, append-only e falhas
    def test_56_publicacao_chama_api_aprovada_task008(self):
        with patch.object(gaps, "publicar_documento", wraps=document_publisher.publicar_documento) as publish:
            receipt = gaps.registrar_divergencia(
                self.rickcraft_root, ANALYSIS_ID, self.divergence_case(),
                purpose="Teste de fronteira", **self.publish_kwargs(),
            )
        publish.assert_called_once()
        self.assertTrue(receipt.publication.destination.is_file())

    def test_57_nova_ocorrencia_publica_novo_document_id(self):
        one = gaps.registrar_divergencia(
            self.rickcraft_root, ANALYSIS_ID, self.divergence_case(),
            purpose="Ocorrência inicial", **self.publish_kwargs(),
        )
        two = gaps.registrar_divergencia(
            self.rickcraft_root, ANALYSIS_ID, self.divergence_case(),
            purpose="Nova avaliação", **self.publish_kwargs(),
        )
        self.assertNotEqual(one.persisted_document_id, two.persisted_document_id)

    def test_58_documento_anterior_e_hash_permanecem_inalterados(self):
        first = gaps.registrar_blocker(
            self.rickcraft_root, ANALYSIS_ID, self.blocker_case(),
            purpose="Primeiro blocker", **self.publish_kwargs(),
        )
        before = hashlib.sha256(first.publication.destination.read_bytes()).hexdigest()
        gaps.registrar_blocker(
            self.rickcraft_root, ANALYSIS_ID, self.blocker_case(),
            purpose="Nova avaliação do blocker", **self.publish_kwargs(),
        )
        self.assertEqual(hashlib.sha256(first.publication.destination.read_bytes()).hexdigest(), before)

    def test_59_relation_aponta_para_documento_anterior(self):
        first = gaps.registrar_divergencia(
            self.rickcraft_root, ANALYSIS_ID, self.divergence_case(),
            purpose="Documento anterior", **self.publish_kwargs(),
        )
        second = gaps.registrar_divergencia(
            self.rickcraft_root, ANALYSIS_ID, self.divergence_case(),
            purpose="Complemento da divergência",
            relations=({"relation_type": "complements", "document_id": first.persisted_document_id},),
            **self.publish_kwargs(),
        )
        self.assertEqual(self.read_published(second).metadata["relations"][0]["document_id"], first.persisted_document_id)

    def test_60_falha_de_publicacao_propaga_sem_receipt(self):
        failure = DocumentPublicationError("falha fixture")
        with patch.object(gaps, "publicar_documento", side_effect=failure):
            with self.assertRaises(DocumentPublicationError) as raised:
                gaps.registrar_resultado(
                    self.rickcraft_root, ANALYSIS_ID, self.result_case(),
                    purpose="Publicação falha", **self.publish_kwargs(),
                )
        self.assertIs(raised.exception, failure)

    def test_61_id_nao_e_reportado_se_publicador_nao_confirma(self):
        with patch.object(gaps, "publicar_documento", return_value=None):
            with self.assertRaises(gaps.GapHandlingError):
                gaps.registrar_resultado(
                    self.rickcraft_root, ANALYSIS_ID, self.result_case(),
                    purpose="Sem confirmação", **self.publish_kwargs(),
                )

    def test_62_resultado_in_memory_nao_e_rotulado_como_persistido(self):
        with patch.object(gaps, "publicar_documento", side_effect=DocumentPublicationError("sem persistência")):
            with self.assertRaises(DocumentPublicationError):
                gaps.registrar_resultado(
                    self.rickcraft_root, ANALYSIS_ID, self.result_case(),
                    purpose="Falha", **self.publish_kwargs(),
                )

    def test_63_workspace_root_kind_e_controlado_pelo_publicador(self):
        receipt = gaps.registrar_resultado(
            self.rickcraft_root, ANALYSIS_ID, self.result_case(),
            purpose="Raiz controlada", **self.publish_kwargs(),
        )
        self.assertEqual(receipt.publication.workspace_root_kind, "preferred")
        self.assertEqual(self.read_published(receipt).metadata["workspace_root_kind"], "preferred")

    def test_64_relacao_cross_analysis_requer_analysis_id(self):
        with self.assertRaises(DocumentPublicationError):
            gaps.registrar_resultado(
                self.rickcraft_root, ANALYSIS_ID, self.result_case(),
                purpose="Relação inválida",
                relations=({"relation_type": "supports", "document_id": "DOC-11111111-1111-4111-8111-111111111111", "analysis_id": "invalid"},),
                **self.publish_kwargs(),
            )

    # Limites: catálogo, tokens, rede, Git, agents, caches e SDD
    def test_65_tipos_documentais_sao_apenas_os_quatro_autorizados(self):
        used = {"divergence", "blocker", "decision", "result"}
        self.assertTrue(used.issubset(DOCUMENT_TYPES))
        self.assertEqual(set(DOCUMENT_TYPES), {
            "context", "analysis", "evidence", "decision", "divergence",
            "blocker", "result", "handoff",
        })
        self.assertEqual(set(TOKENS_RELACAO), {
            "corrects", "complements", "supersedes", "invalidates", "supports", "related_to"
        })

    def test_66_token_documental_novo_rejeitado_pelo_catalogo(self):
        with self.assertRaises(gaps.GapHandlingError):
            gaps._title_for("new_type")

    def test_67_nenhum_relation_type_novo_e_declarado(self):
        source = inspect.getsource(gaps)
        for token in ("corrects", "complements", "supersedes", "invalidates", "supports", "related_to"):
            self.assertNotIn(f'"{token}"', source)

    def test_68_owner_nao_e_inferido_sem_referencia(self):
        with self.assertRaises(gaps.GapHandlingError):
            gaps.registrar_decisao_existente(
                self.rickcraft_root, ANALYSIS_ID,
                self.decision_case(owner_authority_reference=""),
                purpose="Owner não demonstrado", **self.publish_kwargs(),
            )

    def test_69_nao_ha_ranking_por_data_ou_especificidade(self):
        source = inspect.getsource(gaps).casefold()
        self.assertNotIn("mais recente vence", source)
        self.assertNotIn("mais específico vence", source)

    def test_70_nao_cria_indice_cache_ou_banco_persistente(self):
        source = inspect.getsource(gaps).casefold()
        for forbidden in ("sqlite", "shelve", "cachetools", "index.json", "database"):
            self.assertNotIn(forbidden, source)

    def test_71_sem_rede_git_ou_agent_externo(self):
        with patch.object(socket, "create_connection", side_effect=AssertionError("rede")) as network, \
             patch.object(subprocess, "run", side_effect=AssertionError("processo/git")) as process:
            receipt = gaps.registrar_resultado(
                self.rickcraft_root, ANALYSIS_ID, self.result_case(),
                purpose="Operação local", **self.publish_kwargs(),
            )
        network.assert_not_called()
        process.assert_not_called()
        self.assertTrue(receipt.publication.destination.is_file())

    def test_72_nao_cria_sinteticos_no_workspace_debug_real(self):
        real_workspace = Path(__file__).resolve().parents[1] / ".workspace"
        before = _workspace_snapshot(real_workspace)
        gaps.registrar_resultado(
            self.rickcraft_root, ANALYSIS_ID, self.result_case(),
            purpose="Teste mantém publicação sob fixture", **self.publish_kwargs(),
        )
        self.assertEqual(_workspace_snapshot(real_workspace), before)
        self.assertTrue(self.workspace_root.is_relative_to(self.base))

    def test_73_sem_status_gate_release_ou_task12_automaticos(self):
        source = inspect.getsource(gaps).casefold()
        self.assertNotIn("status.write", source)
        self.assertNotIn("release", source)
        self.assertNotIn("task-012", source)

    def test_74_rejeita_materialmente_incompativel_nao_booleano(self):
        with self.assertRaises(gaps.GapHandlingError):
            gaps.avaliar_conflito_fontes(
                normative("A", "X"), normative("B", "Y"),
                affected_scope="A", impact="I", resume_condition="R", materially_incompatible="yes",
            )

    def test_75_analysis_id_precisa_ser_fornecido(self):
        with self.assertRaises(Exception):
            gaps.registrar_resultado(
                self.rickcraft_root, "", self.result_case(),
                purpose="Sem análise", **self.publish_kwargs(),
            )


if __name__ == "__main__":
    unittest.main()
