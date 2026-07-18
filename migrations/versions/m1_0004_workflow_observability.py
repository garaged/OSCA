"""Create Operations-owned workflow event evidence.

Revision ID: m1_0004
Revises: m1_0003
Create Date: 2026-07-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "m1_0004"
down_revision: str | None = "m1_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "operations_workflow_events",
        sa.Column("event_id", sa.String(36), primary_key=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("correlation_id", sa.String(36), nullable=False),
        sa.Column("run_id", sa.String(36), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
    )
    op.create_index(
        "ix_operations_workflow_events_correlation_id",
        "operations_workflow_events",
        ["correlation_id"],
    )
    op.create_index(
        "ix_operations_workflow_events_run_id", "operations_workflow_events", ["run_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_operations_workflow_events_run_id", table_name="operations_workflow_events")
    op.drop_index(
        "ix_operations_workflow_events_correlation_id", table_name="operations_workflow_events"
    )
    op.drop_table("operations_workflow_events")
