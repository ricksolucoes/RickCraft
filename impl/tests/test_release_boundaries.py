"""Verificações de fronteira Debug/Release em fixtures controladas."""

from __future__ import annotations

import ast
import hashlib
import os
from pathlib import Path, PureWindowsPath
import socket
import subprocess
import sys
import tempfile
import unittest
import uuid
from unittest.mock import patch
import urllib.request


RUNTIME_DIRECTORY = Path(__file__).resolve().parents[1] / "src" / "RickCraft"
sys.path.insert(0, str(RUNTIME_DIRECTORY))

import document_format  # noqa: E402
import document_publisher  # noqa: E402
from workspace_resolver import RaizWorkspaceSelecionada, TipoRaizWorkspace  # noqa: E402


ANALYSIS_ID = "ANL-aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
TIME_UTC = "2026-10-11T12:00:00Z"
_IMPORTS_EXTERNOS_PROIBIDOS = frozenset(
    {"subprocess", "socket", "urllib", "http", "ftplib", "requests", "httpx"}
)
_CHAMADAS_EXTERNAS_PROIBIDAS = frozenset(
    {
        "Popen",
        "run",
        "call",
        "check_call",
        "check_output",
        "system",
        "startfile",
        "create_connection",
        "urlopen",
        "connect",
        "upload",
        "push",
        "send",
    }
)


def _inventariar_fixture(
    raiz: Path,
    candidatos: tuple[Path, ...],
    allowlist: frozenset[str],
) -> tuple[str, ...]:
    """Inventaria somente arquivos permitidos e contidos na raiz de fixture."""
    raiz_fisica = raiz.resolve(strict=True)
    encontrados: set[str] = set()

    for candidato in candidatos:
        try:
            lexical = candidato if candidato.is_absolute() else raiz / candidato
            relativo_lexical = lexical.relative_to(raiz)
            partes_lexicais = relativo_lexical.parts
            if any(parte in {"", ".", ".."} for parte in partes_lexicais):
                continue
            if any(parte.casefold() == ".workspace" for parte in partes_lexicais):
                continue

            fisico = lexical.resolve(strict=True)
            relativo_fisico = fisico.relative_to(raiz_fisica)
            if any(parte.casefold() == ".workspace" for parte in relativo_fisico.parts):
                continue
            chave = relativo_fisico.as_posix()
            if chave not in allowlist or not fisico.is_file():
                continue
            encontrados.add(chave)
        except (OSError, RuntimeError, ValueError):
            continue

    return tuple(sorted(encontrados))


def _snapshot_arvore(raiz: Path) -> tuple[tuple[str, str], ...]:
    """Snapshot somente leitura que não segue links de diretório."""
    if not raiz.exists():
        return ()
    registros: list[tuple[str, str]] = []
    for diretorio, nomes, arquivos in os.walk(raiz, followlinks=False):
        base = Path(diretorio)
        nomes.sort()
        arquivos.sort()
        for nome in nomes:
            caminho = base / nome
            relativo = caminho.relative_to(raiz).as_posix()
            if caminho.is_symlink():
                registros.append((relativo, f"symlink:{os.readlink(caminho)}"))
            else:
                registros.append((relativo, "directory"))
        for nome in arquivos:
            caminho = base / nome
            relativo = caminho.relative_to(raiz).as_posix()
            if caminho.is_symlink():
                registros.append((relativo, f"symlink:{os.readlink(caminho)}"))
            else:
                registros.append((relativo, hashlib.sha256(caminho.read_bytes()).hexdigest()))
    return tuple(sorted(registros))


class ReleaseBoundariesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="rickcraft-release-boundary-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.rickcraft_root = self.base / "repo" / "impl" / "src" / "RickCraft"
        self.rickcraft_root.mkdir(parents=True)
        self.preferred = self.rickcraft_root.parent.parent / ".workspace"
        self.fallback = self.rickcraft_root / ".workspace"

    def test_inventario_positivo_exclui_workspaces_preferencial_e_fallback(self) -> None:
        arquivos_estaticos = {
            "engine.py": "# runtime estático\n",
            "meu.workspace.txt": "texto permitido\n",
            "tests/test_local.py": "# ferramenta de teste\n",
            "specs/spec.md": "# especificação\n",
            "policies/policy.md": "# política\n",
            "tools/debug.ps1": "# ferramenta Debug\n",
        }
        for relativo, conteudo in arquivos_estaticos.items():
            caminho = self.rickcraft_root / relativo
            caminho.parent.mkdir(parents=True, exist_ok=True)
            caminho.write_text(conteudo, encoding="utf-8")

        id_documento = "DOC-bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
        para_workspace = (
            (self.preferred / ANALYSIS_ID / "evidence" / f"{id_documento}.md"),
            (self.fallback / ANALYSIS_ID / "evidence" / f"{id_documento}.md"),
        )
        preferred_document, fallback_document = para_workspace
        for documento in para_workspace:
            documento.parent.mkdir(parents=True, exist_ok=True)
            documento.write_text("estado operacional\n", encoding="utf-8")

        fallback_relative = fallback_document.relative_to(self.rickcraft_root).as_posix()

        allowlist = frozenset(
            {
                "engine.py",
                "meu.workspace.txt",
                # Mesmo presente na allowlist, o estado operacional fica excluído.
                fallback_relative,
            }
        )
        candidatos = (
            self.rickcraft_root / "engine.py",
            self.rickcraft_root / "meu.workspace.txt",
            self.rickcraft_root / "tests/test_local.py",
            self.rickcraft_root / "specs/spec.md",
            self.rickcraft_root / "policies/policy.md",
            self.rickcraft_root / "tools/debug.ps1",
            *para_workspace,
        )

        with self.assertRaises(ValueError):
            preferred_document.resolve().relative_to(self.rickcraft_root.resolve())
        self.assertIn(preferred_document, candidatos)
        self.assertIn(".workspace", Path(fallback_relative).parts)
        self.assertIn(fallback_relative, allowlist)
        self.assertIn(fallback_document, candidatos)

        inventario = _inventariar_fixture(self.rickcraft_root, candidatos, allowlist)

        self.assertEqual(inventario, ("engine.py", "meu.workspace.txt"))
        self.assertNotIn("workspace", inventario)
        self.assertNotIn("tests/test_local.py", inventario)
        self.assertNotIn("specs/spec.md", inventario)
        self.assertNotIn("policies/policy.md", inventario)
        self.assertNotIn("tools/debug.ps1", inventario)
        self.assertFalse(any(".workspace" in item.split("/") for item in inventario))
        # O teste diferencia o componente exato de um nome que apenas o contém.
        self.assertIn("meu.workspace.txt", inventario)

    def test_inventario_rejeita_absoluto_traversal_e_candidato_externo(self) -> None:
        permitido = self.rickcraft_root / "engine.py"
        permitido.write_text("# estático\n", encoding="utf-8")
        externo = self.base / "fora.py"
        externo.write_text("# fora\n", encoding="utf-8")
        allowlist = frozenset({"engine.py", "../fora.py"})

        inventario = _inventariar_fixture(
            self.rickcraft_root,
            (Path("engine.py"), Path("../fora.py"), externo),
            allowlist,
        )

        self.assertEqual(inventario, ("engine.py",))
        self.assertTrue(PureWindowsPath(str(externo)).is_absolute())

    def test_inventario_e_deterministico_e_nao_emite_saidas_de_release(self) -> None:
        for relativo in ("z.py", "a.py"):
            (self.rickcraft_root / relativo).write_text(relativo, encoding="utf-8")
        permitidos = frozenset({"z.py", "a.py"})

        resultado = _inventariar_fixture(
            self.rickcraft_root,
            (self.rickcraft_root / "z.py", self.rickcraft_root / "a.py"),
            permitidos,
        )

        self.assertEqual(resultado, ("a.py", "z.py"))
        for saida in ("dist", "build", "package", "out", "release"):
            self.assertFalse((self.base / saida).exists(), saida)

    def test_publicacao_e_leitura_local_ptbr_sem_chamadas_externas(self) -> None:
        self.preferred.mkdir(parents=True)
        (self.preferred / ANALYSIS_ID).mkdir()
        self.fallback.mkdir(parents=True)
        antes_preferencial = _snapshot_arvore(self.preferred)
        antes_fallback = _snapshot_arvore(self.fallback)
        chamadas_avaliador: list[Path] = []
        chamadas_resolvedor: list[Path] = []

        def resolver(raiz: str | Path, _avaliador):
            self.assertEqual(Path(raiz), self.rickcraft_root)
            chamadas_resolvedor.append(Path(raiz))
            return RaizWorkspaceSelecionada(
                TipoRaizWorkspace.PREFERENCIAL, self.preferred
            )

        def avaliador_factory():
            def avaliar(candidata: Path):
                chamadas_avaliador.append(candidata)
                raise AssertionError("D-02 real não faz parte desta fixture.")

            return avaliar

        metadados = {
            "schema_version": 1,
            "type_catalog_version": 1,
            "analysis_id": ANALYSIS_ID,
            "document_type": "evidence",
            "document_id": "DOC-cccccccc-cccc-4ccc-8ccc-cccccccccccc",
            "workspace_root_kind": "preferred",
            "created_at_utc": TIME_UTC,
            "purpose": "Registrar evidência local de Release.",
            "origin": {"kind": "task_execution", "reference": "TASK-012"},
            "inputs": [],
            "relations": [],
        }

        with (
            patch.object(subprocess, "Popen", side_effect=AssertionError("subprocess proibido")),
            patch.object(subprocess, "run", side_effect=AssertionError("subprocess proibido")),
            patch.object(subprocess, "call", side_effect=AssertionError("subprocess proibido")),
            patch.object(subprocess, "check_call", side_effect=AssertionError("subprocess proibido")),
            patch.object(subprocess, "check_output", side_effect=AssertionError("subprocess proibido")),
            patch.object(os, "system", side_effect=AssertionError("shell proibido")),
            patch.object(socket, "create_connection", side_effect=AssertionError("rede proibida")),
            patch.object(socket.socket, "connect", side_effect=AssertionError("rede proibida")),
            patch.object(urllib.request, "urlopen", side_effect=AssertionError("rede proibida")),
        ):
            publicado = document_publisher.publicar_documento(
                self.rickcraft_root,
                ANALYSIS_ID,
                "evidence",
                "Evidência de análise",
                "A análise preserva evidência, decisão e conteúdo em pt-BR.",
                metadados,
                uuid_factory=lambda: uuid.UUID("dddddddd-dddd-4ddd-8ddd-dddddddddddd"),
                resolver=resolver,
                avaliador_factory=avaliador_factory,
            )
            documento = document_format.parsear_documento(
                publicado.destination.read_bytes()
            )

        depois_preferencial = _snapshot_arvore(self.preferred)
        depois_fallback = _snapshot_arvore(self.fallback)
        novos_preferencial = set(depois_preferencial) - set(antes_preferencial)

        self.assertEqual(chamadas_resolvedor, [self.rickcraft_root])
        self.assertEqual(chamadas_avaliador, [])
        self.assertEqual(publicado.workspace_root_kind, "preferred")
        self.assertEqual(publicado.destination.parent, self.preferred / ANALYSIS_ID / "evidence")
        self.assertEqual(documento.titulo, "Evidência de análise")
        self.assertEqual(
            documento.corpo,
            "A análise preserva evidência, decisão e conteúdo em pt-BR.",
        )
        self.assertEqual(documento.metadata["document_id"], publicado.document_id)
        self.assertEqual(len([p for p, _ in depois_preferencial if p.endswith(".md")]), 1)
        self.assertFalse(any("_en" in p or p.endswith("_en.md") for p, _ in depois_preferencial))
        self.assertEqual(
            novos_preferencial,
            {
                ("ANL-aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa/evidence", "directory"),
                (
                    f"{ANALYSIS_ID}/evidence/{publicado.document_id}.md",
                    hashlib.sha256(publicado.destination.read_bytes()).hexdigest(),
                ),
            },
        )
        self.assertEqual(depois_fallback, antes_fallback)
        self.assertNotEqual(self.preferred, Path(__file__).resolve().parents[1] / ".workspace")

    def test_runtime_nao_importa_ou_invoca_integracoes_externas(self) -> None:
        nomes_runtime = (
            "rickcraft_root.py",
            "workspace_resolver.py",
            "workspace_probe.py",
            "analysis_lifecycle.py",
            "document_catalog.py",
            "document_format.py",
            "provenance.py",
            "document_publisher.py",
            "document_recovery.py",
            "document_search.py",
            "gap_handling.py",
        )
        chamadas_proibidas: list[str] = []
        for nome in nomes_runtime:
            origem = RUNTIME_DIRECTORY / nome
            arvore = ast.parse(origem.read_text(encoding="utf-8"), filename=str(origem))
            for no in ast.walk(arvore):
                if isinstance(no, ast.Import):
                    for alias in no.names:
                        if alias.name.split(".")[0] in _IMPORTS_EXTERNOS_PROIBIDOS:
                            chamadas_proibidas.append(f"{nome}: import {alias.name}")
                elif isinstance(no, ast.ImportFrom):
                    modulo = (no.module or "").split(".")[0]
                    if modulo in _IMPORTS_EXTERNOS_PROIBIDOS:
                        chamadas_proibidas.append(f"{nome}: from {no.module}")
                elif isinstance(no, ast.Call):
                    funcao = no.func
                    nome_chamada = (
                        funcao.id
                        if isinstance(funcao, ast.Name)
                        else funcao.attr
                        if isinstance(funcao, ast.Attribute)
                        else ""
                    )
                    if nome_chamada in _CHAMADAS_EXTERNAS_PROIBIDAS:
                        chamadas_proibidas.append(f"{nome}: chamada {nome_chamada}")

        self.assertEqual(chamadas_proibidas, [])


if __name__ == "__main__":
    unittest.main()
