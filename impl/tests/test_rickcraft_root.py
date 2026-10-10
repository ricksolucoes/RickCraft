from __future__ import annotations

import contextlib
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


RUNTIME_DIRECTORY = Path(__file__).resolve().parents[1] / "src" / "RickCraft"
sys.path.insert(0, str(RUNTIME_DIRECTORY))

from rickcraft_root import (  # noqa: E402
    RickCraftRootError,
    main,
    validate_rickcraft_root,
)


class RickCraftRootTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.debug_root = Path(__file__).resolve().parents[1] / "src" / "RickCraft"

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory(
            dir=Path(__file__).resolve().parent
        )
        self.addCleanup(self.temporary_directory.cleanup)
        self.base = Path(self.temporary_directory.name)

    def assert_no_workspace_artifacts(self) -> None:
        self.assertFalse((self.base / ".workspace").exists())
        self.assertFalse((self.base / "RickCraft" / ".workspace").exists())

    def test_accepts_explicit_existing_compatible_debug_root(self) -> None:
        result = validate_rickcraft_root(str(self.debug_root))

        self.assertEqual(result, self.debug_root.resolve(strict=True))
        self.assertTrue(result.is_absolute())

    def test_rejects_absent_parameter_without_operational_writes(self) -> None:
        with self.assertRaisesRegex(RickCraftRootError, "informado explicitamente"):
            validate_rickcraft_root(None)

        self.assert_no_workspace_artifacts()

    def test_rejects_relative_path_without_operational_writes(self) -> None:
        with self.assertRaisesRegex(RickCraftRootError, "caminho absoluto"):
            validate_rickcraft_root(Path("impl/src/RickCraft"))

        self.assert_no_workspace_artifacts()

    def test_rejects_nonexistent_absolute_path_without_operational_writes(self) -> None:
        missing_root = self.base / "RickCraft"

        with self.assertRaisesRegex(RickCraftRootError, "não existe"):
            validate_rickcraft_root(missing_root)

        self.assert_no_workspace_artifacts()

    def test_rejects_file_instead_of_directory_without_operational_writes(self) -> None:
        file_root = self.base / "RickCraft"
        file_root.write_text("não é diretório", encoding="utf-8")

        with self.assertRaisesRegex(RickCraftRootError, "diretório"):
            validate_rickcraft_root(file_root)

        self.assert_no_workspace_artifacts()

    def test_rejects_existing_directory_with_incompatible_identity(self) -> None:
        incompatible_root = self.base / "OutroProduto"
        incompatible_root.mkdir()

        with self.assertRaisesRegex(RickCraftRootError, "raiz lógica RickCraft"):
            validate_rickcraft_root(incompatible_root)

        self.assert_no_workspace_artifacts()

    def test_normalizes_dot_segments_without_discovering_another_root(self) -> None:
        expected_root = self.base / "RickCraft"
        expected_root.mkdir()
        intermediate = self.base / "intermediario"
        intermediate.mkdir()
        supplied = intermediate / ".." / "RickCraft" / "."

        result = validate_rickcraft_root(supplied)

        self.assertEqual(result, expected_root.resolve(strict=True))
        self.assert_no_workspace_artifacts()

    def test_changing_current_directory_does_not_change_explicit_root(self) -> None:
        original_directory = Path.cwd()
        try:
            os.chdir(self.base)
            result = validate_rickcraft_root(self.debug_root)
        finally:
            os.chdir(original_directory)

        self.assertEqual(result, self.debug_root.resolve(strict=True))
        self.assert_no_workspace_artifacts()

    def test_changing_home_variables_does_not_change_explicit_root(self) -> None:
        alternate_home = str(self.base / "home-alternativo")
        with patch.dict(
            os.environ,
            {"HOME": alternate_home, "USERPROFILE": alternate_home},
        ):
            result = validate_rickcraft_root(self.debug_root)

        self.assertEqual(result, self.debug_root.resolve(strict=True))
        self.assert_no_workspace_artifacts()

    def test_cli_rejects_missing_rickcraft_root_parameter_in_portuguese(self) -> None:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as raised:
                main([])

        self.assertEqual(raised.exception.code, 2)
        self.assertIn("Parâmetro obrigatório ausente: --rickcraft-root", stderr.getvalue())
        self.assert_no_workspace_artifacts()


if __name__ == "__main__":
    unittest.main()
