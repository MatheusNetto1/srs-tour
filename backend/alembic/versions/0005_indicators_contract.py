"""indicators contract

Revision ID: 35348943973c
Revises: a3f1c9d27b64
Create Date: 2026-10-29 18:43:11.360090

"""

import re
import unicodedata
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# Revision identifiers, used by Alembic.
revision: str = "35348943973c"
down_revision: str | Sequence[str] | None = "a3f1c9d27b64"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# Cópia de app/indicators/slug.py: migrations não importam `app`.
_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def _slugify(name: str) -> str:
    ascii_only = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()

    return _NON_ALNUM.sub("-", ascii_only.lower()).strip("-")


def upgrade() -> None:
    """Apply schema changes."""
    conn = op.get_bind()

    non_numeric = conn.execute(
        sa.text("SELECT id, period FROM indicators WHERE period !~ '^[0-9]+$'")
    ).all()

    if non_numeric:
        values = ", ".join(f"id={row.id} period={row.period!r}" for row in non_numeric)
        raise RuntimeError(
            "Não é possível converter `period` para inteiro: valores não "
            f"numéricos encontrados ({values}). Corrija-os antes de migrar."
        )

    op.drop_constraint("ck_indicators_status", "indicators", type_="check")
    conn.execute(sa.text("UPDATE indicators SET status = lower(status)"))
    op.alter_column(
        "indicators",
        "period",
        existing_type=sa.VARCHAR(length=50),
        type_=sa.Integer(),
        postgresql_using="period::integer",
        existing_nullable=False,
    )
    op.create_check_constraint(
        "ck_indicators_status",
        "indicators",
        "status IN ('draft', 'published')",
    )

    op.add_column("indicators", sa.Column("slug", sa.String(length=100), nullable=True))

    rows = conn.execute(
        sa.text("SELECT id, name, period FROM indicators ORDER BY id")
    ).all()
    seen: set[tuple[str, int]] = set()

    for row in rows:
        slug = _slugify(row.name)
        key = (slug, row.period)

        # Duplicata de (slug, period) já convertida: a linha mais nova (id
        # maior, pois a busca é ordenada por id) recebe o sufixo.
        if key in seen:
            slug = f"{slug}-{row.id}"
        else:
            seen.add(key)

        conn.execute(
            sa.text("UPDATE indicators SET slug = :slug WHERE id = :id"),
            {"slug": slug, "id": row.id},
        )

    op.alter_column("indicators", "slug", nullable=False)
    op.create_index(op.f("ix_indicators_slug"), "indicators", ["slug"], unique=False)
    op.create_unique_constraint(
        "uq_indicators_slug_period", "indicators", ["slug", "period"]
    )


def downgrade() -> None:
    """Revert schema changes."""
    conn = op.get_bind()

    op.drop_constraint("uq_indicators_slug_period", "indicators", type_="unique")
    op.drop_index(op.f("ix_indicators_slug"), table_name="indicators")
    op.drop_column("indicators", "slug")

    op.drop_constraint("ck_indicators_status", "indicators", type_="check")
    # A nova constraint (maiúsculo) só é criada depois de converter os dados,
    # senão as linhas já gravadas em minúsculo violam o CHECK na criação.
    conn.execute(sa.text("UPDATE indicators SET status = upper(status)"))
    op.alter_column(
        "indicators",
        "period",
        existing_type=sa.Integer(),
        type_=sa.VARCHAR(length=50),
        postgresql_using="period::varchar",
        existing_nullable=False,
    )
    op.create_check_constraint(
        "ck_indicators_status",
        "indicators",
        "status IN ('DRAFT', 'PUBLISHED')",
    )
