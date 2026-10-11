from __future__ import annotations

import errno
from pathlib import Path
import sys
import tempfile
import unittest
import uuid
from unittest.mock import patch


RUNTIME_DIRECTORY = Path(__file__).resolve().parents[1] / "src" / "RickCraft"
sys.path.insert(0, str(RUNTIME_DIRECTORY))

from analysis_lifecycle import (  # noqa: E402
    AnalysisCollisionLimitError,
    AnalysisIdInvalidError,
    AnalysisLifecycleError,
    AnalysisNotFoundError,
    criar_ou_retomar_analise,
    validar_analysis_id,
)
from workspace_resolver import (  # noqa: E402
    ResultadoCapacidade,
    ResultadoDesconhecidoError,
    TipoRaizWorkspace,
    resolver_workspace,
)


class CicloAnaliseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory(
            dir=Path(__file__).resolve().parent
        )
        self.addCleanup(self.temporary_directory.cleanup)
        self.base = Path(self.temporary_directory.name)
        self.rickcraft_root = self.base / "impl" / "src" / "RickCraft"
        self.rickcraft_root.mkdir(parents=True)
        self.preferencial = self.base / "impl" / ".workspace"
        self.fallback = self.rickcraft_root / ".workspace"
        self.preferencial.mkdir(parents=True)
        self.fallback.mkdir()

    @staticmethod
    def uuid4(valor: str) -> uuid.UUID:
        return uuid.UUID(valor)

    def avaliador_controlado(self, resultados, observados=None):
        fila = iter(resultados)

        def avaliar(caminho: Path):
            if observados is not None:
                observados.append(caminho)
            return next(fila)

        return avaliar

    def executar(
        self,
        *,
        resume_analysis_id: str | None = None,
        uuid_factory=lambda: uuid.UUID("12345678-1234-4234-8234-123456789abc"),
        resolver=None,
        resultados=(ResultadoCapacidade.UTILIZAVEL,),
        observados=None,
        avaliador_factory=None,
    ):
        return criar_ou_retomar_analise(
            self.rickcraft_root,
            resume_analysis_id,
            uuid_factory=uuid_factory,
            resolver=resolver or resolver_workspace,
            avaliador_factory=avaliador_factory
            or (lambda: self.avaliador_controlado(resultados, observados)),
        )

    def test_id_gerado_comeca_com_prefixo_anl(self) -> None:
        resultado = self.executar()
        self.assertTrue(resultado.analysis_id.startswith("ANL-"))

    def test_uuid_interno_gerado_e_sintaticamente_valido(self) -> None:
        resultado = self.executar()
        self.assertIsInstance(uuid.UUID(resultado.analysis_id.removeprefix("ANL-")), uuid.UUID)

    def test_uuid_interno_gerado_e_versao_quatro(self) -> None:
        resultado = self.executar()
        self.assertEqual(uuid.UUID(resultado.analysis_id[4:]).version, 4)

    def test_id_gerado_e_canonico_em_minusculas(self) -> None:
        resultado = self.executar()
        self.assertEqual(resultado.analysis_id, "ANL-12345678-1234-4234-8234-123456789abc")
        self.assertEqual(resultado.analysis_id[4:], resultado.analysis_id[4:].lower())

    def test_cria_um_diretorio_exclusivo_sem_pastas_de_tipo(self) -> None:
        resultado = self.executar()
        self.assertTrue(resultado.directory.is_dir())
        self.assertEqual(list(self.preferencial.iterdir()), [resultado.directory])
        self.assertEqual(list(resultado.directory.iterdir()), [])

    def test_primeira_colisao_gera_novo_candidato(self) -> None:
        primeiro = self.uuid4("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
        segundo = self.uuid4("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")
        (self.preferencial / f"ANL-{primeiro}").mkdir()
        candidatos = iter((primeiro, segundo))

        resultado = self.executar(uuid_factory=lambda: next(candidatos))

        self.assertEqual(resultado.analysis_id, f"ANL-{segundo}")
        self.assertTrue((self.preferencial / f"ANL-{primeiro}").is_dir())
        self.assertTrue(resultado.directory.is_dir())

    def test_varias_colisoes_prosseguem_dentro_do_limite(self) -> None:
        candidatos = [
            self.uuid4(f"{i:08x}-1234-4abc-8abc-{i:012x}") for i in range(1, 4)
        ]
        for candidato in candidatos[:2]:
            (self.preferencial / f"ANL-{candidato}").mkdir()
        sequencia = iter(candidatos)

        resultado = self.executar(uuid_factory=lambda: next(sequencia))

        self.assertEqual(resultado.analysis_id, f"ANL-{candidatos[2]}")

    def test_oito_colisoes_bloqueiam_sem_nona_tentativa(self) -> None:
        candidatos = [
            self.uuid4(f"{i:08x}-1234-4abc-8abc-{i:012x}") for i in range(1, 9)
        ]
        for candidato in candidatos:
            (self.preferencial / f"ANL-{candidato}").mkdir()
        chamadas: list[uuid.UUID] = []

        def gerar():
            indice = len(chamadas)
            chamadas.append(candidatos[indice] if indice < len(candidatos) else uuid.uuid4())
            return chamadas[-1]

        with self.assertRaises(AnalysisCollisionLimitError):
            self.executar(uuid_factory=gerar)

        self.assertEqual(len(chamadas), 8)
        self.assertEqual(len(list(self.preferencial.glob("ANL-*"))), 8)

    def test_falha_de_filesystem_nao_e_convertida_em_colisao(self) -> None:
        gerar = unittest.mock.Mock(return_value=self.uuid4("12345678-1234-4234-8234-123456789abc"))
        with patch.object(Path, "mkdir", side_effect=PermissionError(errno.EACCES, "acesso negado")):
            with self.assertRaises(PermissionError):
                self.executar(uuid_factory=gerar)
        self.assertEqual(gerar.call_count, 1)

    def test_file_exists_sem_codigo_e_propaga_como_erro_desconhecido(self) -> None:
        with patch.object(Path, "mkdir", side_effect=FileExistsError("falha sem código")):
            with self.assertRaises(FileExistsError):
                self.executar()

    def test_retoma_id_valido_existente_sem_alterar_identidade(self) -> None:
        analysis_id = "ANL-12345678-1234-4234-8234-123456789abc"
        directory = self.preferencial / analysis_id
        directory.mkdir(parents=True)

        resultado = self.executar(resume_analysis_id=analysis_id)

        self.assertEqual(resultado.analysis_id, analysis_id)
        self.assertEqual(resultado.directory, directory)

    def test_retomada_nao_gera_uuid_novo(self) -> None:
        analysis_id = "ANL-12345678-1234-4234-8234-123456789abc"
        (self.preferencial / analysis_id).mkdir(parents=True)
        gerador = unittest.mock.Mock(side_effect=AssertionError("UUID não deve ser gerado"))

        resultado = self.executar(resume_analysis_id=analysis_id, uuid_factory=gerador)

        self.assertEqual(resultado.analysis_id, analysis_id)
        gerador.assert_not_called()

    def test_id_malformado_bloqueia(self) -> None:
        with self.assertRaises(AnalysisIdInvalidError):
            validar_analysis_id("ANL-nao-e-uuid")

    def test_id_de_tipo_nao_textual_bloqueia(self) -> None:
        with self.assertRaises(AnalysisIdInvalidError):
            validar_analysis_id(42)

    def test_prefixo_diferente_de_anl_bloqueia(self) -> None:
        with self.assertRaises(AnalysisIdInvalidError):
            validar_analysis_id("DOC-12345678-1234-4234-8234-123456789abc")

    def test_uuid_que_nao_e_versao_quatro_bloqueia(self) -> None:
        with self.assertRaises(AnalysisIdInvalidError):
            validar_analysis_id("ANL-12345678-1234-1234-8234-123456789abc")

    def test_id_maiusculo_ou_nao_canonico_bloqueia(self) -> None:
        with self.assertRaises(AnalysisIdInvalidError):
            validar_analysis_id("ANL-12345678-1234-4234-8234-123456789ABC")

    def test_id_com_separador_ou_path_traversal_bloqueia(self) -> None:
        for value in (
            "ANL-../12345678-1234-4234-8234-123456789abc",
            "ANL-12345678-1234-4234-8234-123456789abc/../../outro",
            "ANL-12345678-1234-4234-8234-123456789abc\\..\\outro",
        ):
            with self.subTest(value=value), self.assertRaises(AnalysisIdInvalidError):
                validar_analysis_id(value)

    def test_id_valido_inexistente_bloqueia_sem_criar_analise(self) -> None:
        analysis_id = "ANL-12345678-1234-4234-8234-123456789abc"
        with self.assertRaises(AnalysisNotFoundError):
            self.executar(resume_analysis_id=analysis_id)
        self.assertFalse((self.preferencial / analysis_id).exists())

    def test_id_que_aponta_para_arquivo_bloqueia(self) -> None:
        analysis_id = "ANL-12345678-1234-4234-8234-123456789abc"
        (self.preferencial / analysis_id).write_text("arquivo", encoding="utf-8")

        with self.assertRaises(AnalysisNotFoundError):
            self.executar(resume_analysis_id=analysis_id)

    def test_identidade_nao_usa_contador_horario_ou_conversa(self) -> None:
        candidato = self.uuid4("87654321-4321-4321-8432-cba987654321")
        resultado = self.executar(uuid_factory=lambda: candidato)
        self.assertEqual(resultado.analysis_id, f"ANL-{candidato}")
        self.assertEqual(len(list(self.preferencial.iterdir())), 1)

    def test_raiz_preferencial_resolvida_recebe_diretorio(self) -> None:
        avaliadas: list[Path] = []
        resultado = self.executar(observados=avaliadas)
        self.assertEqual(resultado.workspace.tipo, TipoRaizWorkspace.PREFERENCIAL)
        self.assertTrue(resultado.directory.is_relative_to(self.preferencial))
        self.assertEqual(avaliadas, [self.preferencial])

    def test_raiz_fallback_controlada_recebe_diretorio(self) -> None:
        avaliadas: list[Path] = []
        resultado = self.executar(
            resultados=(ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA,
                        ResultadoCapacidade.UTILIZAVEL),
            observados=avaliadas,
        )
        self.assertEqual(resultado.workspace.tipo, TipoRaizWorkspace.FALLBACK)
        self.assertTrue(resultado.directory.is_relative_to(self.fallback))
        self.assertEqual(avaliadas, [self.preferencial, self.fallback])

    def test_erro_desconhecido_na_resolucao_nao_cria_diretorio_anl(self) -> None:
        with self.assertRaises(ResultadoDesconhecidoError):
            self.executar(resultados=(ResultadoCapacidade.ERRO_DESCONHECIDO,))
        self.assertEqual(list(self.preferencial.glob("ANL-*")), [])
        self.assertEqual(list(self.fallback.glob("ANL-*")), [])

    def test_raiz_e_resolvida_novamente_em_cada_operacao(self) -> None:
        filas = iter(
            (
                (ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA,
                 ResultadoCapacidade.UTILIZAVEL),
                (ResultadoCapacidade.UTILIZAVEL,),
            )
        )

        raiz_observada: list[Path] = []
        primeiro = criar_ou_retomar_analise(
            self.rickcraft_root,
            uuid_factory=lambda: self.uuid4("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
            resolver=resolver_workspace,
            avaliador_factory=lambda: self.avaliador_controlado(
                next(filas), raiz_observada
            ),
        )
        gerador = unittest.mock.Mock(side_effect=AssertionError("retomada não gera UUID"))
        with self.assertRaises(AnalysisNotFoundError):
            criar_ou_retomar_analise(
                self.rickcraft_root,
                primeiro.analysis_id,
                uuid_factory=gerador,
                resolver=resolver_workspace,
                avaliador_factory=lambda: self.avaliador_controlado(
                    next(filas), raiz_observada
                ),
            )
        self.assertEqual(primeiro.workspace.tipo, TipoRaizWorkspace.FALLBACK)
        self.assertEqual(
            raiz_observada,
            [self.preferencial, self.fallback, self.preferencial],
        )
        gerador.assert_not_called()


if __name__ == "__main__":
    unittest.main()
