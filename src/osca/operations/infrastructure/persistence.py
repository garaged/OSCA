from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, Text, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from osca.operations.api import AuditRecord


class AuditBase(DeclarativeBase):
    pass


class AuditRecordRow(AuditBase):
    __tablename__ = "operations_audit_records"

    record_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(100), nullable=False)
    target_id: Mapped[str] = mapped_column(String(200), nullable=False)
    outcome: Mapped[str] = mapped_column(String(20), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)


class SqliteAuditRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, record: AuditRecord) -> None:
        self._session.add(
            AuditRecordRow(
                record_id=str(record.record_id),
                occurred_at=record.occurred_at,
                correlation_id=str(record.correlation_id.value),
                action=record.action,
                target_type=record.target_type,
                target_id=record.target_id,
                outcome=record.outcome.value,
                payload=record.model_dump_json(),
            )
        )
        self._session.flush()

    def get(self, record_id: UUID) -> AuditRecord | None:
        row = self._session.scalar(
            select(AuditRecordRow).where(AuditRecordRow.record_id == str(record_id))
        )
        return None if row is None else AuditRecord.model_validate_json(row.payload)

