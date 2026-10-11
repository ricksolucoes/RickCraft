from __future__ import annotations

import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


RUNTIME_DIRECTORY = Path(__file__).resolve().parents[1] / "src" / "RickCraft"
sys.path.insert(0, str(RUNTIME_DIRECTORY))

from workspace_resolver import (  # noqa: E402
    ResultadoCapacidade,
    ResultadoDesconhecidoError,
    TipoRaizWorkspace,
    WorkspaceIndisponivelError,
    derivar_caminhos_workspace,
    resolver_workspace,
)


class ResolvedorWorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rickcraft_root = (
            Path(__file__).resolve().parents[1] / "src" / "RickCraft"
        ).resolve(strict=True)
        cls.caminhos = derivar_caminhos_workspace(cls.rickcraft_root)

    def resolver_sem_mutacoes(
        self,
        resultados: list[ResultadoCapacidade],
        avaliados: list[Path],
    ):
        fila = iter(resultados)

        def avaliar(candidata: Path) -> ResultadoCapacidade:
            avaliados.append(candidata)
            return next(fila)

        with (
            patch.object(Path, "mkdir") as mkdir,
            patch.object(Path, "open") as abrir,
            patch("os.link") as criar_link,
            patch("os.fsync") as fsync,
        ):
            try:
                return resolver_workspace(self.rickcraft_root, avaliar)
            finally:
                mkdir.assert_not_called()
                abrir.assert_not_called()
                criar_link.assert_not_called()
                fsync.assert_not_called()

    def test_deriva_local_definido_usuario(self) -> None:
        self.assertEqual(
            self.caminhos.local_definido_usuario,
            self.rickcraft_root.parent,
        )

    def test_deriva_workspace_preferencial(self) -> None:
        self.assertEqual(
            self.caminhos.preferencial,
            self.rickcraft_root.parent.parent / ".workspace",
        )

    def test_deriva_workspace_fallback(self) -> None:
        self.assertEqual(
            self.caminhos.fallback,
            self.rickcraft_root / ".workspace",
        )

    def test_caminhos_debug_correspondem_as_formulas_aprovadas(self) -> None:
        raiz_repositorio = Path(__file__).resolve().parents[2]
        self.assertEqual(
            self.caminhos.local_definido_usuario,
            raiz_repositorio / "impl" / "src",
        )
        self.assertEqual(
            self.caminhos.preferencial,
            raiz_repositorio / "impl" / ".workspace",
        )
        self.assertEqual(
            self.caminhos.fallback,
            self.rickcraft_root / ".workspace",
        )

    def test_preferencial_e_avaliado_primeiro(self) -> None:
        avaliados: list[Path] = []

        def avaliar(candidata: Path) -> ResultadoCapacidade:
            avaliados.append(candidata)
            return ResultadoCapacidade.UTILIZAVEL

        selecionada = resolver_workspace(self.rickcraft_root, avaliar)

        self.assertEqual(avaliados, [self.caminhos.preferencial])
        self.assertEqual(selecionada.caminho, self.caminhos.preferencial)
        self.assertEqual(selecionada.tipo, TipoRaizWorkspace.PREFERENCIAL)

    def test_preferencial_utilizavel_nao_avalia_fallback(self) -> None:
        avaliados: list[Path] = []

        def avaliar(candidata: Path) -> ResultadoCapacidade:
            avaliados.append(candidata)
            return ResultadoCapacidade.UTILIZAVEL

        resolver_workspace(self.rickcraft_root, avaliar)

        self.assertNotIn(self.caminhos.fallback, avaliados)
        self.assertEqual(len(avaliados), 1)

    def test_impossibilidade_concreta_no_preferencial_avalia_fallback(self) -> None:
        avaliados: list[Path] = []
        resultados = iter(
            [
                ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA,
                ResultadoCapacidade.UTILIZAVEL,
            ]
        )

        def avaliar(candidata: Path) -> ResultadoCapacidade:
            avaliados.append(candidata)
            return next(resultados)

        selecionada = resolver_workspace(self.rickcraft_root, avaliar)

        self.assertEqual(
            avaliados,
            [self.caminhos.preferencial, self.caminhos.fallback],
        )
        self.assertEqual(selecionada.caminho, self.caminhos.fallback)
        self.assertEqual(selecionada.tipo, TipoRaizWorkspace.FALLBACK)

    def test_erro_desconhecido_no_preferencial_bloqueia_sem_fallback(self) -> None:
        avaliados: list[Path] = []

        def avaliar(candidata: Path) -> ResultadoCapacidade:
            avaliados.append(candidata)
            return ResultadoCapacidade.ERRO_DESCONHECIDO

        with self.assertRaises(ResultadoDesconhecidoError):
            resolver_workspace(self.rickcraft_root, avaliar)

        self.assertEqual(avaliados, [self.caminhos.preferencial])

    def test_erro_desconhecido_no_fallback_bloqueia(self) -> None:
        avaliados: list[Path] = []
        resultados = iter(
            [
                ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA,
                ResultadoCapacidade.ERRO_DESCONHECIDO,
            ]
        )

        def avaliar(candidata: Path) -> ResultadoCapacidade:
            avaliados.append(candidata)
            return next(resultados)

        with self.assertRaises(ResultadoDesconhecidoError):
            resolver_workspace(self.rickcraft_root, avaliar)

        self.assertEqual(
            avaliados,
            [self.caminhos.preferencial, self.caminhos.fallback],
        )

    def test_duas_impossibilidades_concretas_nao_selecionam_raiz(self) -> None:
        avaliados: list[Path] = []

        def avaliar(candidata: Path) -> ResultadoCapacidade:
            avaliados.append(candidata)
            return ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA

        with self.assertRaises(WorkspaceIndisponivelError):
            resolver_workspace(self.rickcraft_root, avaliar)

        self.assertEqual(
            avaliados,
            [self.caminhos.preferencial, self.caminhos.fallback],
        )

    def test_consulta_somente_as_duas_localizacoes_autorizadas(self) -> None:
        avaliados: list[Path] = []

        def avaliar(candidata: Path) -> ResultadoCapacidade:
            avaliados.append(candidata)
            return ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA

        with self.assertRaises(WorkspaceIndisponivelError):
            resolver_workspace(self.rickcraft_root, avaliar)

        self.assertEqual(set(avaliados), {self.caminhos.preferencial, self.caminhos.fallback})
        self.assertEqual(len(avaliados), 2)

    def test_fallback_anterior_nao_fica_em_cache_e_preferencial_retorna(self) -> None:
        sequencias = iter(
            [
                [
                    ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA,
                    ResultadoCapacidade.UTILIZAVEL,
                ],
                [ResultadoCapacidade.UTILIZAVEL],
            ]
        )

        def resolver_com_proxima_sequencia() -> object:
            resultados = iter(next(sequencias))
            return resolver_workspace(self.rickcraft_root, lambda _: next(resultados))

        primeira = resolver_com_proxima_sequencia()
        segunda = resolver_com_proxima_sequencia()

        self.assertEqual(primeira.tipo, TipoRaizWorkspace.FALLBACK)
        self.assertEqual(segunda.tipo, TipoRaizWorkspace.PREFERENCIAL)

    def test_preferencial_pode_deixar_de_ser_utilizavel_na_resolucao_seguinte(self) -> None:
        resultados = iter(
            [
                [ResultadoCapacidade.UTILIZAVEL],
                [
                    ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA,
                    ResultadoCapacidade.UTILIZAVEL,
                ],
            ]
        )

        def resolver_com_proxima_sequencia() -> object:
            atual = iter(next(resultados))
            return resolver_workspace(self.rickcraft_root, lambda _: next(atual))

        primeira = resolver_com_proxima_sequencia()
        segunda = resolver_com_proxima_sequencia()

        self.assertEqual(primeira.tipo, TipoRaizWorkspace.PREFERENCIAL)
        self.assertEqual(segunda.tipo, TipoRaizWorkspace.FALLBACK)

    def test_erro_posterior_nao_reutiliza_fallback_anterior(self) -> None:
        sequencias = iter(
            [
                [
                    ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA,
                    ResultadoCapacidade.UTILIZAVEL,
                ],
                [ResultadoCapacidade.ERRO_DESCONHECIDO],
            ]
        )
        primeira_resposta = iter(next(sequencias))
        primeira = resolver_workspace(
            self.rickcraft_root,
            lambda _: next(primeira_resposta),
        )
        segunda_resposta = iter(next(sequencias))

        with self.assertRaises(ResultadoDesconhecidoError):
            resolver_workspace(
                self.rickcraft_root,
                lambda _: next(segunda_resposta),
            )

        self.assertEqual(primeira.tipo, TipoRaizWorkspace.FALLBACK)

    def test_alteracao_de_cwd_nao_muda_caminhos_derivados(self) -> None:
        cwd_original = Path.cwd()
        try:
            os.chdir(Path(__file__).resolve().parents[1])
            resolvidos = derivar_caminhos_workspace(self.rickcraft_root)
        finally:
            os.chdir(cwd_original)

        self.assertEqual(resolvidos, self.caminhos)

    def test_alteracao_de_home_nao_muda_caminhos_derivados(self) -> None:
        with patch.dict(
            os.environ,
            {"HOME": "Z:\\home-alternativo", "USERPROFILE": "Z:\\perfil-alternativo"},
        ):
            resolvidos = derivar_caminhos_workspace(self.rickcraft_root)

        self.assertEqual(resolvidos, self.caminhos)

    def test_preferencial_utilizavel_nao_executa_mutacoes_de_filesystem(self) -> None:
        avaliados: list[Path] = []

        selecionada = self.resolver_sem_mutacoes(
            [ResultadoCapacidade.UTILIZAVEL],
            avaliados,
        )

        self.assertEqual(selecionada.caminho, self.caminhos.preferencial)
        self.assertEqual(avaliados, [self.caminhos.preferencial])

    def test_fallback_controlado_nao_executa_mutacoes_de_filesystem(self) -> None:
        avaliados: list[Path] = []

        selecionada = self.resolver_sem_mutacoes(
            [
                ResultadoCapacidade.IMPOSSIBILIDADE_CONCRETA,
                ResultadoCapacidade.UTILIZAVEL,
            ],
            avaliados,
        )

        self.assertEqual(selecionada.caminho, self.caminhos.fallback)
        self.assertEqual(
            avaliados,
            [self.caminhos.preferencial, self.caminhos.fallback],
        )

    def test_erro_desconhecido_bloqueia_sem_mutacoes_ou_fallback(self) -> None:
        avaliados: list[Path] = []

        with self.assertRaises(ResultadoDesconhecidoError):
            self.resolver_sem_mutacoes(
                [ResultadoCapacidade.ERRO_DESCONHECIDO],
                avaliados,
            )

        self.assertEqual(avaliados, [self.caminhos.preferencial])

    def test_resultado_semantico_invalido_bloqueia_sem_tentar_fallback(self) -> None:
        avaliados: list[Path] = []

        def avaliar(candidata: Path) -> object:
            avaliados.append(candidata)
            return "resultado não reconhecido"

        with self.assertRaises(ResultadoDesconhecidoError):
            resolver_workspace(self.rickcraft_root, avaliar)  # type: ignore[arg-type]

        self.assertEqual(avaliados, [self.caminhos.preferencial])

if __name__ == "__main__":
    unittest.main()
