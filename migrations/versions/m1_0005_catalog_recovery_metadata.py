"""Create Catalog-owned recovery metadata.

Revision ID: m1_0005
Revises: m1_0004
Create Date: 2026-07-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "m1_0005"
down_revision: str | None = "m1_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "catalog_recovery_metadata",
        sa.Column("record_id", sa.String(36), primary_key=True),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("subject_id", sa.String(36), nullable=False),
        sa.Column("correlation_id", sa.String(36), nullable=False),
        sa.Column("registered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
    )
    op.create_index(
        "ix_catalog_recovery_metadata_kind", "catalog_recovery_metadata", ["kind"]
    )
    op.create_index(
        "ix_catalog_recovery_metadata_subject_id",
        "catalog_recovery_metadata",
        ["subject_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_catalog_recovery_metadata_subject_id",
        table_name="catalog_recovery_metadata",
    )
    op.drop_index(
        "ix_catalog_recovery_metadata_kind",
        table_name="catalog_recovery_metadata",
    )
    op.drop_table("catalog_recovery_metadata")
