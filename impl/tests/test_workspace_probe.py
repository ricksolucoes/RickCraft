from __future__ import annotations

import errno
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


RUNTIME_DIRECTORY = Path(__file__).resolve().parents[1] / "src" / "RickCraft"
sys.path.insert(0, str(RUNTIME_DIRECTORY))

from workspace_probe import (  # noqa: E402
    AvaliadorWorkspace,
    classificar_falha,
)
from workspace_resolver import (  # noqa: E402
    ResultadoCapacidade,
    ResultadoDesconhecidoError,
    TipoRaizWorkspace,
    WorkspaceIndisponivelError,
    derivar_caminhos_workspace,
    resolver_workspace,
)


class ClassificacaoFalhaTests(unittest.TestCase):
    def test_familias_concretas_d03(self) -> None:
        casos = (
            (PermissionError(errno.EACCES, "negado"), "criar raiz candidata"),
            (OSError(errno.EROFS, "somente leitura"), "escrever"),
            (NotADirectoryError(errno.ENOTDIR, "componente arquivo"), "criar raiz candidata"),
            (OSError(getattr(errno, "ENOTSUP", errno.EINVAL), "não suportado"), "os.link"),
            (OSError(errno.ENOSPC, "sem espaço"), "escrever"),
        )
        for erro, operacao in casos:
            with self.subTest(erro=erro.errno):
                self.assertIs(
                    classificar_falha(erro, operacao),
                    ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA,
                )

    def test_eexist_nao_classifica_raiz_indisponivel(self) -> None:
        erro = FileExistsError(errno.EEXIST, "colisão de nome aleatório")
        self.assertIs(
            classificar_falha(erro, "criar, escrever e sincronizar arquivo exclusivo"),
            ResultadoCapacidade.ERRO_DESCONHECIDO,
        )

    def test_erro_nao_reconhecido_preserva_resultado_desconhecido(self) -> None:
        erro = OSError(errno.EIO, "erro de entrada/saída")
        self.assertIs(
            classificar_falha(erro, "reler arquivo de sonda"),
            ResultadoCapacidade.ERRO_DESCONHECIDO,
        )


    def test_oserror_sem_errno_e_erro_desconhecido(self) -> None:
        erro = OSError("falha sem código")
        self.assertIsNone(erro.errno)
        self.assertIs(
            classificar_falha(erro, "sondar raiz"),
            ResultadoCapacidade.ERRO_DESCONHECIDO,
        )

    def test_errno_e_winerror_ausentes_nunca_sao_causa_concreta(self) -> None:
        erro = OSError("falha sem código")
        erro.winerror = None
        self.assertIsNone(erro.errno)
        self.assertIsNone(erro.winerror)
        self.assertIs(
            classificar_falha(erro, "sondar raiz"),
            ResultadoCapacidade.ERRO_DESCONHECIDO,
        )

    def test_simbolo_errno_opcional_ausente_nao_corresponde_a_none(self) -> None:
        errno_sem_simbolos_opcionais = SimpleNamespace(
            EACCES=errno.EACCES,
            EPERM=errno.EPERM,
            EEXIST=errno.EEXIST,
        )
        with patch("workspace_probe.errno", errno_sem_simbolos_opcionais):
            resultado = classificar_falha(OSError("sem código"), "sondar raiz")

        self.assertFalse(hasattr(errno_sem_simbolos_opcionais, "EROFS"))
        self.assertIs(resultado, ResultadoCapacidade.ERRO_DESCONHECIDO)


class SondaWorkspaceTests(unittest.TestCase):
    def test_raiz_ausente_e_capacidades_reais_em_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temporario:
            raiz = Path(temporario) / "workspace" / "nova"
            avaliador = AvaliadorWorkspace()

            resultado = avaliador(raiz)

            self.assertIs(resultado, ResultadoCapacidade.UTILIZAVEL)
            self.assertTrue(raiz.is_dir())
            evidencia = avaliador.evidencias[-1]
            self.assertEqual(evidencia.raiz, raiz)
            self.assertIsNone(evidencia.operacao_falha)
            self.assertIn("open xb exclusivo", evidencia.capacidades)
            self.assertIn("escrita", evidencia.capacidades)
            self.assertIn("flush", evidencia.capacidades)
            self.assertIn("fsync executado", evidencia.capacidades)
            self.assertIn("releitura da origem conferida byte a byte", evidencia.capacidades)
            self.assertIn("os.link para destino ausente", evidencia.capacidades)
            self.assertIn("releitura do destino publicada conferida", evidencia.capacidades)
            self.assertIn(
                "destino existente rejeitado sem substituir bytes sentinela",
                evidencia.capacidades,
            )
            self.assertEqual(list(raiz.iterdir()), [])

    def test_componente_da_raiz_que_e_arquivo_e_impossibilidade_concreta(self) -> None:
        with tempfile.TemporaryDirectory() as temporario:
            raiz = Path(temporario) / "arquivo"
            raiz.write_text("não é diretório", encoding="utf-8")
            avaliador = AvaliadorWorkspace()

            resultado = avaliador(raiz)

            self.assertIs(resultado, ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA)
            self.assertEqual(avaliador.evidencias[-1].operacao_falha, "criar raiz candidata")
            self.assertEqual(avaliador.evidencias[-1].errno, errno.ENOTDIR)

    def test_acesso_negado_e_classificado_com_diagnostico(self) -> None:
        with tempfile.TemporaryDirectory() as temporario:
            raiz = Path(temporario) / "workspace"
            avaliador = AvaliadorWorkspace()
            with patch.object(Path, "mkdir", side_effect=PermissionError(errno.EACCES, "negado")):
                resultado = avaliador(raiz)

            self.assertIs(resultado, ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA)
            self.assertEqual(avaliador.evidencias[-1].errno, errno.EACCES)
            self.assertIn("PermissionError", avaliador.evidencias[-1].causa or "")

    def test_erro_desconhecido_fica_registrado_sem_promover_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temporario:
            raiz = Path(temporario) / "workspace"
            avaliador = AvaliadorWorkspace()
            with patch.object(Path, "mkdir", side_effect=OSError(errno.EIO, "falha inesperada")):
                resultado = avaliador(raiz)

            self.assertIs(resultado, ResultadoCapacidade.ERRO_DESCONHECIDO)
            evidencia = avaliador.evidencias[-1]
            self.assertEqual(evidencia.errno, errno.EIO)
            self.assertEqual(evidencia.operacao_falha, "criar raiz candidata")

    def test_falha_de_limpeza_nao_altera_utilizavel_e_reporta_residuo(self) -> None:
        with tempfile.TemporaryDirectory() as temporario:
            raiz = Path(temporario) / "workspace"
            avaliador = AvaliadorWorkspace()
            unlink_original = Path.unlink
            origem_residual: list[Path] = []

            def falhar_somente_origem(path: Path, *args, **kwargs):
                if path.name.startswith("origem-"):
                    origem_residual.append(path)
                    raise PermissionError(errno.EACCES, "limpeza negada", str(path))
                return unlink_original(path, *args, **kwargs)

            with patch.object(Path, "unlink", new=falhar_somente_origem):
                resultado = avaliador(raiz)

            evidencia = avaliador.evidencias[-1]
            self.assertIs(resultado, ResultadoCapacidade.UTILIZAVEL)
            self.assertIn("PROBE_CLEANUP_PENDING", evidencia.avisos)
            self.assertIn(origem_residual[0], evidencia.residuos)
            self.assertIn(origem_residual[0].parent, evidencia.residuos)
            self.assertTrue(all(path.suffix == ".tmp" and path.exists() for path in evidencia.residuos))

    def test_artefatos_temporarios_nao_sao_documentos_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temporario:
            raiz = Path(temporario) / "workspace"
            nomes_observados: list[Path] = []
            abrir_original = Path.open

            def observar_abertura(path: Path, mode="r", *args, **kwargs):
                nomes_observados.append(path)
                return abrir_original(path, mode, *args, **kwargs)

            avaliador = AvaliadorWorkspace()
            with patch.object(Path, "open", new=observar_abertura):
                resultado = avaliador(raiz)

            self.assertIs(resultado, ResultadoCapacidade.UTILIZAVEL)
            self.assertTrue(nomes_observados)
            self.assertTrue(all(path.suffix == ".tmp" for path in nomes_observados))
            self.assertFalse(any(path.suffix == ".md" for path in raiz.rglob("*")))
            self.assertFalse(any(path.name.startswith(("ANL-", "DOC-")) for path in raiz.rglob("*")))


class IntegracaoResolvedorTests(unittest.TestCase):
    def criar_raiz_rickcraft(self, base: Path) -> Path:
        raiz = base / "impl" / "src" / "RickCraft"
        raiz.mkdir(parents=True)
        return raiz

    def test_preferencial_utilizavel_nao_sonda_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temporario:
            raiz = self.criar_raiz_rickcraft(Path(temporario))
            avaliador = AvaliadorWorkspace()

            selecionada = resolver_workspace(raiz, avaliador)

            caminhos = derivar_caminhos_workspace(raiz)
            self.assertIs(selecionada.tipo, TipoRaizWorkspace.PREFERENCIAL)
            self.assertEqual(selecionada.caminho, caminhos.preferencial)
            self.assertEqual([e.raiz for e in avaliador.evidencias], [caminhos.preferencial])

    def test_impossibilidade_concreta_preferencial_permite_sonda_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temporario:
            raiz = self.criar_raiz_rickcraft(Path(temporario))
            caminhos = derivar_caminhos_workspace(raiz)
            caminhos.preferencial.parent.mkdir(parents=True, exist_ok=True)
            caminhos.preferencial.write_text("arquivo no lugar da raiz", encoding="utf-8")
            avaliador = AvaliadorWorkspace()

            selecionada = resolver_workspace(raiz, avaliador)

            self.assertIs(selecionada.tipo, TipoRaizWorkspace.FALLBACK)
            self.assertEqual(selecionada.caminho, caminhos.fallback)
            self.assertEqual(
                [e.raiz for e in avaliador.evidencias],
                [caminhos.preferencial, caminhos.fallback],
            )
            self.assertIs(
                avaliador.evidencias[0].resultado,
                ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA,
            )

    def test_erro_desconhecido_preferencial_nao_sonda_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temporario:
            raiz = self.criar_raiz_rickcraft(Path(temporario))
            caminhos = derivar_caminhos_workspace(raiz)
            avaliador = AvaliadorWorkspace()
            link_original = os.link

            def erro_apenas_no_preferencial(origem, destino, *args, **kwargs):
                if Path(origem).is_relative_to(caminhos.preferencial):
                    raise OSError(errno.EIO, "falha não classificada")
                return link_original(origem, destino, *args, **kwargs)

            with patch("workspace_probe.os.link", new=erro_apenas_no_preferencial):
                with self.assertRaises(ResultadoDesconhecidoError):
                    resolver_workspace(raiz, avaliador)

            self.assertEqual([e.raiz for e in avaliador.evidencias], [caminhos.preferencial])
            self.assertIs(
                avaliador.evidencias[0].resultado,
                ResultadoCapacidade.ERRO_DESCONHECIDO,
            )

    def test_errno_ausente_no_preferencial_bloqueia_sem_sondar_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temporario:
            raiz = self.criar_raiz_rickcraft(Path(temporario))
            caminhos = derivar_caminhos_workspace(raiz)
            avaliadas: list[Path] = []

            def avaliar(candidata: Path) -> ResultadoCapacidade:
                avaliadas.append(candidata)
                if candidata == caminhos.preferencial:
                    return classificar_falha(
                        OSError("falha sem código"), "criar raiz candidata"
                    )
                return ResultadoCapacidade.UTILIZAVEL

            with self.assertRaises(ResultadoDesconhecidoError):
                resolver_workspace(raiz, avaliar)

            self.assertEqual(avaliadas, [caminhos.preferencial])

    def test_duas_raizes_concretamente_indisponiveis_nao_selecionam(self) -> None:
        with tempfile.TemporaryDirectory() as temporario:
            raiz = self.criar_raiz_rickcraft(Path(temporario))
            caminhos = derivar_caminhos_workspace(raiz)
            caminhos.preferencial.parent.mkdir(parents=True, exist_ok=True)
            caminhos.preferencial.write_text("arquivo preferencial", encoding="utf-8")
            caminhos.fallback.write_text("arquivo fallback", encoding="utf-8")
            avaliador = AvaliadorWorkspace()

            with self.assertRaises(WorkspaceIndisponivelError):
                resolver_workspace(raiz, avaliador)

            self.assertEqual(
                [e.raiz for e in avaliador.evidencias],
                [caminhos.preferencial, caminhos.fallback],
            )
            self.assertTrue(
                all(e.resultado is ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA
                    for e in avaliador.evidencias)
            )


if __name__ == "__main__":
    unittest.main()
