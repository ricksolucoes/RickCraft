"""Validação explícita da raiz canônica do RickCraft para o host local."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence


class RickCraftRootError(ValueError):
    """Indica que RickCraftRoot está ausente ou não atende ao contrato."""


def validate_rickcraft_root(value: str | Path | None) -> Path:
    """Valida e normaliza o caminho explícito de RickCraftRoot.

    A função não consulta CWD, diretórios de usuário ou a localização deste
    módulo, e não cria arquivos ou diretórios.
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        raise RickCraftRootError("RickCraftRoot deve ser informado explicitamente.")

    try:
        candidate = Path(value)
    except (TypeError, ValueError) as exc:
        raise RickCraftRootError("RickCraftRoot deve ser um caminho válido.") from exc

    if not candidate.is_absolute():
        raise RickCraftRootError("RickCraftRoot deve ser um caminho absoluto.")

    try:
        normalized = candidate.resolve(strict=True)
    except (OSError, RuntimeError, ValueError) as exc:
        raise RickCraftRootError(
            "RickCraftRoot não existe ou não pode ser resolvido."
        ) from exc

    if not normalized.is_dir():
        raise RickCraftRootError("RickCraftRoot deve apontar para um diretório.")

    if normalized.name.casefold() != "rickcraft":
        raise RickCraftRootError(
            "RickCraftRoot deve corresponder à raiz lógica RickCraft."
        )

    return normalized


def main(argv: Sequence[str] | None = None) -> int:
    """Binding CLI mínimo: recebe --rickcraft-root sem descoberta implícita."""
    parser = argparse.ArgumentParser(
        description="Valida a raiz canônica explicitamente fornecida do RickCraft."
    )
    parser.add_argument(
        "--rickcraft-root",
        dest="rickcraft_root",
        help="caminho absoluto da pasta canônica RickCraft",
    )
    args = parser.parse_args(argv)

    if args.rickcraft_root is None:
        parser.error("Parâmetro obrigatório ausente: --rickcraft-root")

    try:
        root = validate_rickcraft_root(args.rickcraft_root)
    except RickCraftRootError as exc:
        parser.exit(2, f"Erro ao validar RickCraftRoot: {exc}\n")

    print(f"RickCraftRoot validado: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
