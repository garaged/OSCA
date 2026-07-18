"""Create operations-owned audit storage.

Revision ID: m1_0002
Revises: m1_0001
Create Date: 2026-07-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "m1_0002"
down_revision: str | None = "m1_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "operations_audit_records",
        sa.Column("record_id", sa.String(length=36), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("correlation_id", sa.String(length=36), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("target_type", sa.String(length=100), nullable=False),
        sa.Column("target_id", sa.String(length=200), nullable=False),
        sa.Column("outcome", sa.String(length=20), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("record_id"),
    )
    op.create_index(
        "ix_operations_audit_records_action",
        "operations_audit_records",
        ["action"],
    )
    op.create_index(
        "ix_operations_audit_records_correlation_id",
        "operations_audit_records",
        ["correlation_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_operations_audit_records_correlation_id",
        table_name="operations_audit_records",
    )
    op.drop_index("ix_operations_audit_records_action", table_name="operations_audit_records")
    op.drop_table("operations_audit_records")
