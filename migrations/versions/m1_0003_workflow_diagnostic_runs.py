"""Create Workflow run storage and Catalog-owned result metadata.

Revision ID: m1_0003
Revises: m1_0002
Create Date: 2026-07-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "m1_0003"
down_revision: str | None = "m1_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "workflow_diagnostic_runs",
        sa.Column("run_id", sa.String(36), primary_key=True),
        sa.Column("actor", sa.String(200), nullable=False),
        sa.Column("idempotency_key", sa.String(200), nullable=False),
        sa.Column("state", sa.String(20), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("lease_owner", sa.String(200)),
        sa.Column("lease_expires_at", sa.DateTime(timezone=True)),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True)),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.UniqueConstraint("actor", "idempotency_key", name="uq_workflow_actor_idempotency"),
    )
    op.create_index("ix_workflow_diagnostic_runs_state", "workflow_diagnostic_runs", ["state"])
    op.create_table(
        "catalog_result_metadata",
        sa.Column("result_id", sa.String(36), primary_key=True),
        sa.Column("producing_run_id", sa.String(36), nullable=False),
        sa.Column("correlation_id", sa.String(36), nullable=False),
        sa.Column("registered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("media_type", sa.String(100), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
    )
    op.create_index(
        "ix_catalog_result_metadata_producing_run_id",
        "catalog_result_metadata",
        ["producing_run_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_catalog_result_metadata_producing_run_id",
        table_name="catalog_result_metadata",
    )
    op.drop_table("catalog_result_metadata")
    op.drop_index("ix_workflow_diagnostic_runs_state", table_name="workflow_diagnostic_runs")
    op.drop_table("workflow_diagnostic_runs")
