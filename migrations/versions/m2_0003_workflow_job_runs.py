"""Create generic durable Workflow job runs.

Revision ID: m2_0003
Revises: m2_0002
Create Date: 2026-07-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "m2_0003"
down_revision: str | None = "m2_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "workflow_job_runs",
        sa.Column("job_id", sa.String(36), primary_key=True),
        sa.Column("actor", sa.String(200), nullable=False),
        sa.Column("kind", sa.String(128), nullable=False),
        sa.Column("idempotency_key", sa.String(200), nullable=False),
        sa.Column("state", sa.String(20), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("lease_owner", sa.String(200), nullable=True),
        sa.Column("lease_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.UniqueConstraint(
            "actor", "kind", "idempotency_key", name="uq_workflow_job_idempotency"
        ),
    )
    op.create_index("ix_workflow_job_runs_state", "workflow_job_runs", ["state"])


def downgrade() -> None:
    op.drop_index("ix_workflow_job_runs_state", table_name="workflow_job_runs")
    op.drop_table("workflow_job_runs")
