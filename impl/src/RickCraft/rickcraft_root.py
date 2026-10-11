"""Validação explícita da raiz canônica do RickCraft para o host local."""

from __future__ import annotations

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
    argumentos = list(sys.argv[1:] if argv is None else argv)

    if argumentos in (["--help"], ["-h"]):
        print(
            "Valida a raiz canônica explicitamente fornecida do RickCraft.\n\n"
            "Uso:\n"
            "  rickcraft_root.py --rickcraft-root <caminho>\n\n"
            "Opções:\n"
            "  --rickcraft-root <caminho>  Caminho absoluto da pasta canônica RickCraft.\n"
            "  -h, --help                  Exibe esta ajuda e encerra."
        )
        return 0

    if not argumentos:
        _erro_cli("Parâmetro obrigatório ausente: --rickcraft-root")

    if argumentos[0] != "--rickcraft-root":
        _erro_cli(f"Argumento não reconhecido: {argumentos[0]}")

    if len(argumentos) < 2 or argumentos[1].startswith("-"):
        _erro_cli("Valor obrigatório ausente para --rickcraft-root.")

    if len(argumentos) > 2:
        _erro_cli(f"Argumento não reconhecido: {argumentos[2]}")

    try:
        root = validate_rickcraft_root(argumentos[1])
    except RickCraftRootError as exc:
        _erro_cli(f"Falha ao validar RickCraftRoot: {exc}")

    print(f"RickCraftRoot validado: {root}")
    return 0


def _erro_cli(mensagem: str) -> None:
    """Encerra o binding com diagnóstico e uso integralmente em pt-BR."""
    sys.stderr.write(
        "Uso: rickcraft_root.py --rickcraft-root <caminho>\n"
        f"Erro: {mensagem}\n"
    )
    raise SystemExit(2)


if __name__ == "__main__":
    raise SystemExit(main())
