"""Valida as ferramentas e versões mínimas do ambiente (`make check`).

Usa apenas a biblioteca padrão para rodar antes de `poetry install`.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

# nome, comando que imprime a versão, versão mínima (None = só precisa existir)
TOOLS: list[tuple[str, list[str], tuple[int, int] | None]] = [
    ("Python", [sys.executable, "--version"], (3, 12)),
    ("Poetry", ["poetry", "--version"], (2, 0)),
    ("Node", ["node", "--version"], (24, 0)),
    ("npm", ["npm", "--version"], None),
    ("Docker", ["docker", "--version"], None),
]


def read_version(command: list[str]) -> tuple[int, ...] | None:
    # which() resolve extensões do Windows (npm vira npm.cmd).
    executable = shutil.which(command[0])

    if executable is None:
        return None

    try:
        result = subprocess.run(
            [executable, *command[1:]],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    match = re.search(r"(\d+(?:\.\d+)+)", result.stdout + result.stderr)

    if not match:
        return None

    return tuple(int(part) for part in match.group(1).split("."))


def docker_ok(*args: str) -> bool:
    try:
        result = subprocess.run(
            ["docker", *args], capture_output=True, timeout=30, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return False

    return result.returncode == 0


def main() -> int:
    print("Verificando ferramentas...")
    failed = False

    for name, command, minimum in TOOLS:
        version = read_version(command)
        needed = f" (mínimo {minimum[0]}.{minimum[1]})" if minimum else ""

        if version is None:
            print(f"  [ERRO] {name}: não encontrado{needed}")
            failed = True
        elif minimum and version[:2] < minimum:
            found = ".".join(map(str, version))
            print(f"  [ERRO] {name} {found}: mínimo exigido {minimum[0]}.{minimum[1]}")
            failed = True
        else:
            print(f"  [ok]   {name} {'.'.join(map(str, version))}")

    if shutil.which("docker") and not docker_ok("compose", "version"):
        print("  [ERRO] Docker Compose (plugin 'docker compose') não encontrado")
        failed = True

    if not ENV_FILE.exists():
        print("  [aviso] backend/.env não existe: rode 'make env' (ou 'make setup')")

    if failed:
        print("\nAmbiente incompleto: corrija os itens [ERRO] acima.")
        return 1

    if not docker_ok("info"):
        print("  [aviso] o daemon do Docker não está rodando (necessário para make up)")

    print("\nAmbiente OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
