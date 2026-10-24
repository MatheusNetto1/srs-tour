"""Confere se as migrations do Alembic têm uma única head.

Roda com `make back-migration-single-head`. Duas migrations criadas em paralelo
a partir da mesma revisão geram duas heads, e o `alembic upgrade head` falha
com um erro genérico. Este script acusa o problema antes, sem acessar o banco.

Deve rodar a partir de `backend/` (o `alembic.ini` é lido do diretório atual).
Usa apenas a biblioteca padrão e o Alembic.
"""

from alembic.config import Config
from alembic.script import ScriptDirectory


def main() -> int:
    heads = ScriptDirectory.from_config(Config("alembic.ini")).get_heads()

    if len(heads) <= 1:
        return 0

    print(f"Erro: há {len(heads)} heads de migrations; deveria haver uma só.")

    for head in sorted(heads):
        print(f"  - {head}")

    print(
        "Ajuste o `down_revision` da migration que você criou para apontar para "
        "a revision da outra head (e renumere o prefixo do arquivo se houver "
        "colisão). Confira com: make back-migration-heads"
    )

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
