"""Cria o backend/.env a partir do .env.example, sem sobrescrever.

Usa apenas a biblioteca padrão para poder rodar antes de `poetry install`.
"""

import re
import secrets
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BACKEND_DIR / ".env"
EXAMPLE_FILE = BACKEND_DIR / ".env.example"
SECRET_KEY_PATTERN = re.compile(r"^SECRET_KEY=[^\r\n]*", re.MULTILINE)


def main() -> None:
    if ENV_FILE.exists():
        print("backend/.env já existe; nada a fazer (não foi sobrescrito).")
        return

    if not EXAMPLE_FILE.exists():
        raise SystemExit("Erro: backend/.env.example não encontrado.")

    with EXAMPLE_FILE.open(encoding="utf-8", newline="") as file:
        content = file.read()

    secret_key = f"SECRET_KEY={secrets.token_urlsafe(48)}"
    content, replaced = SECRET_KEY_PATTERN.subn(lambda _: secret_key, content)

    if not replaced:
        raise SystemExit("Erro: SECRET_KEY não encontrada em backend/.env.example.")

    # "x" falha se o arquivo surgir entre a checagem e a escrita.
    with ENV_FILE.open("x", encoding="utf-8", newline="") as file:
        file.write(content)

    print("backend/.env criado com uma SECRET_KEY aleatória.")


if __name__ == "__main__":
    main()
