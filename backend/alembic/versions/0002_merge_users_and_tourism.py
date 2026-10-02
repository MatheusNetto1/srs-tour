"""merge users and tourism

Revision ID: 2a93c2fcb5ba
Revises: 0b9508ac7e3f, d889579567c9
Create Date: 2026-10-02 15:05:05.600646

"""

from collections.abc import Sequence

# Revision identifiers, used by Alembic.
revision: str = "2a93c2fcb5ba"
down_revision: str | Sequence[str] | None = ("0b9508ac7e3f", "d889579567c9")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply schema changes."""
    pass


def downgrade() -> None:
    """Revert schema changes."""
    pass
