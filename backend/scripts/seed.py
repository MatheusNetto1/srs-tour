"""Popula o banco de desenvolvimento com dados iniciais (`make seed`).

Hoje o seed está vazio de propósito: os dados serão definidos junto com a
integração front-back.

Como adicionar dados:

1. Crie uma função `seed_<recurso>(session: Session) -> None` neste arquivo.
2. Deixe-a idempotente: busque o registro por uma chave natural (e-mail, nome
   etc.) e só crie se não existir, para que `make seed` possa rodar várias
   vezes sem duplicar nem falhar. Nunca reative registro inativo
   implicitamente.
3. Reaproveite o repository/service do domínio. Senhas só via
   `app.core.security`.
4. Registre a função em `SEEDERS`.

O script usa `DATABASE_URL`, nunca `TEST_DATABASE_URL`.
"""

from collections.abc import Callable

from sqlalchemy.orm import Session

from app.core.database import SessionLocal

Seeder = Callable[[Session], None]

SEEDERS: list[Seeder] = []


def main() -> None:
    if not SEEDERS:
        print("Nenhum seed definido; nada foi inserido.")
        return

    with SessionLocal() as session:
        for seeder in SEEDERS:
            seeder(session)
            print(f"Seed aplicado: {seeder.__name__}")


if __name__ == "__main__":
    main()
