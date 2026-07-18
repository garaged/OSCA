"""Create Instrument-owned registry metadata.

Revision ID: m2_0001
Revises: m1_0006
Create Date: 2026-07-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "m2_0001"
down_revision: str | None = "m1_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "instrument_references",
        sa.Column("instrument_id", sa.String(36), primary_key=True),
        sa.Column("identity_key", sa.String(640), nullable=False, unique=True),
        sa.Column("payload", sa.Text(), nullable=False),
    )
    op.create_table(
        "instrument_provider_mappings",
        sa.Column("mapping_id", sa.String(36), primary_key=True),
        sa.Column("instrument_id", sa.String(36), nullable=False),
        sa.Column("provider_id", sa.String(128), nullable=False),
        sa.Column("provider_symbol", sa.String(128), nullable=False),
        sa.Column("scope", sa.String(128), nullable=False),
        sa.Column("venue_context", sa.String(128), nullable=False),
        sa.Column("valid_from", sa.String(10), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.UniqueConstraint(
            "provider_id", "provider_symbol", "scope", "venue_context", "valid_from"
        ),
    )
    op.create_index(
        "ix_instrument_provider_mappings_instrument_id",
        "instrument_provider_mappings",
        ["instrument_id"],
    )
    op.create_index(
        "ix_instrument_provider_mappings_provider_id",
        "instrument_provider_mappings",
        ["provider_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_instrument_provider_mappings_provider_id", table_name="instrument_provider_mappings"
    )
    op.drop_index(
        "ix_instrument_provider_mappings_instrument_id", table_name="instrument_provider_mappings"
    )
    op.drop_table("instrument_provider_mappings")
    op.drop_table("instrument_references")
