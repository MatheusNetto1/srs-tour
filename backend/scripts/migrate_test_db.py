import os
import subprocess
import sys

from app.core.config import settings


def main() -> None:
    test_database_url = settings.test_database_url

    if not test_database_url:
        raise SystemExit(
            "Erro: TEST_DATABASE_URL não está configurada. "
            "Defina-a em backend/.env (veja backend/.env.example)."
        )

    database_name = test_database_url.rsplit("/", maxsplit=1)[-1].split("?")[0]

    if not database_name.endswith("_test"):
        raise SystemExit(
            "Erro: TEST_DATABASE_URL deve apontar para um banco "
            f"terminado em '_test' (encontrado: '{database_name}')."
        )

    # O Alembic (alembic/env.py) migra o banco definido em DATABASE_URL.
    # Variáveis de ambiente têm precedência sobre o .env no pydantic-settings.
    env = {**os.environ, "DATABASE_URL": test_database_url}

    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        env=env,
        check=True,
    )


if __name__ == "__main__":
    main()
