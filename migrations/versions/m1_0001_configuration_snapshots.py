"""Create configuration-owned snapshot storage.

Revision ID: m1_0001
Revises: None
Create Date: 2026-07-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "m1_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "configuration_snapshots",
        sa.Column("revision_id", sa.String(length=36), nullable=False),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("contract_version", sa.String(length=16), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("revision_id"),
    )


def downgrade() -> None:
    op.drop_table("configuration_snapshots")

