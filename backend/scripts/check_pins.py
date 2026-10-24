"""Confere se as versões fixadas nos vários lugares do repositório coincidem.

Fonte única: `.python-version` e `.nvmrc` (raiz). Os Dockerfiles não leem esses
arquivos (o contexto de build do backend é `backend/`), então repetem a versão
em um `ARG`; este script acusa a divergência (`make check-pins`, rodado no CI).

Usa apenas a biblioteca padrão.
"""

import json
import re
import tomllib
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


def read(path: str) -> str:
    return (ROOT_DIR / path).read_text(encoding="utf-8")


def find(pattern: str, path: str) -> str | None:
    match = re.search(pattern, read(path), re.MULTILINE)

    return match.group(1) if match else None


def same_version(left: str, right: str) -> bool:
    """Compara só as partes que os dois informam (`3.12` bate com `3.12.10`)."""
    a, b = left.strip().lstrip("v").split("."), right.strip().lstrip("v").split(".")
    size = min(len(a), len(b))

    return a[:size] == b[:size]


def lower_bound(constraint: str) -> str | None:
    match = re.search(r">=\s*(\d+(?:\.\d+)*)", constraint)

    return match.group(1) if match else None


def main() -> int:
    python = read(".python-version").strip()
    node = read(".nvmrc").strip()
    pyproject = tomllib.loads(read("backend/pyproject.toml"))
    package = json.loads(read("frontend/package.json"))

    # descrição, valor encontrado (None = não achei), valor esperado, onde está
    checks = [
        (
            "backend/Dockerfile: ARG PYTHON_VERSION",
            find(r"^ARG PYTHON_VERSION=(\S+)", "backend/Dockerfile"),
            python,
            ".python-version",
        ),
        (
            "backend/pyproject.toml: requires-python",
            lower_bound(pyproject["project"]["requires-python"]),
            python,
            ".python-version",
        ),
        (
            "frontend/Dockerfile: ARG NODE_VERSION",
            find(r"^ARG NODE_VERSION=(\S+)", "frontend/Dockerfile"),
            node,
            ".nvmrc",
        ),
        (
            "frontend/package.json: engines.node",
            lower_bound(package.get("engines", {}).get("node", "")),
            node,
            ".nvmrc",
        ),
        (
            "backend/Dockerfile: ARG POETRY_VERSION",
            find(r"^ARG POETRY_VERSION=(\S+)", "backend/Dockerfile"),
            find(r'POETRY_VERSION:\s*"?([\d.]+)', ".github/workflows/backend-ci.yml"),
            ".github/workflows/backend-ci.yml",
        ),
    ]

    failed = False

    for label, found, expected, source in checks:
        if found is None or expected is None:
            print(f"  [ERRO] {label}: não encontrei a versão (esperada de {source})")
            failed = True
        elif not same_version(found, expected):
            print(f"  [ERRO] {label} = {found}, mas {source} = {expected}")
            failed = True
        else:
            print(f"  [ok]   {label} = {found}")

    if failed:
        print("\nVersões divergentes: alinhe os itens [ERRO] acima.")
        return 1

    print("\nVersões em sincronia.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
