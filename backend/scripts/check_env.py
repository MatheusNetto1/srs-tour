"""Valida as ferramentas e versões mínimas do ambiente (`make check`).

As versões mínimas não ficam aqui: vêm de `.python-version` e `.nvmrc` (raiz) e
de `requires-poetry` em `backend/pyproject.toml`.

Usa apenas a biblioteca padrão para rodar antes de `poetry install`.
"""

import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BACKEND_DIR.parent
ENV_FILE = BACKEND_DIR / ".env"


def parse_minimum(text: str, source: str) -> tuple[int, int]:
    match = re.search(r"(\d+)(?:\.(\d+))?", text)

    if not match:
        raise SystemExit(f"Não foi possível ler a versão mínima de {source}: {text!r}")

    return int(match.group(1)), int(match.group(2) or 0)


def read_pin(name: str) -> tuple[int, int]:
    return parse_minimum((ROOT_DIR / name).read_text(encoding="utf-8"), name)


def read_poetry_minimum() -> tuple[int, int]:
    pyproject = tomllib.loads((BACKEND_DIR / "pyproject.toml").read_text("utf-8"))
    constraint = pyproject["tool"]["poetry"]["requires-poetry"]

    return parse_minimum(constraint, "backend/pyproject.toml (requires-poetry)")


def build_tools() -> list[tuple[str, list[str], tuple[int, int] | None]]:
    # nome, comando que imprime a versão, versão mínima (None = só precisa existir)
    return [
        ("Python", [sys.executable, "--version"], read_pin(".python-version")),
        ("Poetry", ["poetry", "--version"], read_poetry_minimum()),
        ("Node", ["node", "--version"], read_pin(".nvmrc")),
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

    for name, command, minimum in build_tools():
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
