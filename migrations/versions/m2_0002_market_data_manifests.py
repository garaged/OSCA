"""Create Market Data-owned dataset manifests.

Revision ID: m2_0002
Revises: m2_0001
Create Date: 2026-07-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "m2_0002"
down_revision: str | None = "m2_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "market_data_dataset_manifests",
        sa.Column("manifest_id", sa.String(36), primary_key=True),
        sa.Column("dataset_id", sa.String(36), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("fingerprint", sa.String(71), nullable=False),
        sa.Column("state", sa.String(20), nullable=False),
        sa.Column("instrument_id", sa.String(36), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.UniqueConstraint("fingerprint", name="uq_market_data_fingerprint"),
    )
    op.create_index(
        "ix_market_data_manifests_dataset_id",
        "market_data_dataset_manifests",
        ["dataset_id"],
    )
    op.create_index(
        "ix_market_data_manifests_state",
        "market_data_dataset_manifests",
        ["state"],
    )
    op.create_index(
        "ix_market_data_manifests_instrument_id",
        "market_data_dataset_manifests",
        ["instrument_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_market_data_manifests_instrument_id",
        table_name="market_data_dataset_manifests",
    )
    op.drop_index(
        "ix_market_data_manifests_state",
        table_name="market_data_dataset_manifests",
    )
    op.drop_index(
        "ix_market_data_manifests_dataset_id",
        table_name="market_data_dataset_manifests",
    )
    op.drop_table("market_data_dataset_manifests")
