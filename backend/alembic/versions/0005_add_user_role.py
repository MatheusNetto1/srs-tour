"""add user role

Revision ID: f4b8a1d62c7e
Revises: a3f1c9d27b64
Create Date: 2026-10-26 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f4b8a1d62c7e"
down_revision: str | Sequence[str] | None = "a3f1c9d27b64"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(length=20),
            server_default="admin",
            nullable=False,
        ),
    )
    op.create_check_constraint(
        "ck_users_role",
        "users",
        "role IN ('admin')",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("ck_users_role", "users", type_="check")
    op.drop_column("users", "role")
