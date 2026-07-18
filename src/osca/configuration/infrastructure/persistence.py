from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, Text, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from osca.configuration.api import ValidatedConfiguration


class ConfigurationBase(DeclarativeBase):
    pass


class ConfigurationSnapshotRow(ConfigurationBase):
    __tablename__ = "configuration_snapshots"

    revision_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    validated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    contract_version: Mapped[str] = mapped_column(String(16), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)


class SqliteConfigurationRepository:
    """Configuration-owned adapter; no other capability may query this table."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, configuration: ValidatedConfiguration) -> None:
        self._session.add(
            ConfigurationSnapshotRow(
                revision_id=str(configuration.revision_id),
                validated_at=configuration.validated_at,
                contract_version=configuration.contract_version,
                payload=configuration.model_dump_json(),
            )
        )
        self._session.flush()

    def get(self, revision_id: UUID) -> ValidatedConfiguration | None:
        statement = select(ConfigurationSnapshotRow).where(
            ConfigurationSnapshotRow.revision_id == str(revision_id)
        )
        row = self._session.scalar(statement)
        if row is None:
            return None
        return ValidatedConfiguration.model_validate_json(row.payload)

