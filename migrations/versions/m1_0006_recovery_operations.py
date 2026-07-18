"""Create Recovery-owned operation state.

Revision ID: m1_0006
Revises: m1_0005
Create Date: 2026-07-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "m1_0006"
down_revision: str | None = "m1_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "recovery_operations",
        sa.Column("operation_id", sa.String(36), primary_key=True),
        sa.Column("correlation_id", sa.String(36), nullable=False),
        sa.Column("action", sa.String(30), nullable=False),
        sa.Column("state", sa.String(20), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("payload", sa.Text(), nullable=False),
    )
    op.create_index(
        "ix_recovery_operations_correlation_id",
        "recovery_operations",
        ["correlation_id"],
    )
    op.create_index("ix_recovery_operations_action", "recovery_operations", ["action"])
    op.create_index("ix_recovery_operations_state", "recovery_operations", ["state"])


def downgrade() -> None:
    op.drop_index("ix_recovery_operations_state", table_name="recovery_operations")
    op.drop_index("ix_recovery_operations_action", table_name="recovery_operations")
    op.drop_index(
        "ix_recovery_operations_correlation_id", table_name="recovery_operations"
    )
    op.drop_table("recovery_operations")
