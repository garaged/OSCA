from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from osca.recovery.domain import RecoveryAction, RecoveryOperation, RecoveryState
from osca.shared_kernel.api import CorrelationId


class RecoveryBase(DeclarativeBase):
    pass


class RecoveryOperationRow(RecoveryBase):
    __tablename__ = "recovery_operations"
    operation_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    correlation_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    payload: Mapped[str] = mapped_column(Text, nullable=False)


class SqliteRecoveryOperationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def start(
        self,
        *,
        correlation_id: CorrelationId,
        actor: str,
        action: RecoveryAction,
        target: str,
    ) -> RecoveryOperation:
        operation = RecoveryOperation(
            correlation_id=correlation_id,
            actor=actor,
            action=action,
            target=target,
        )
        self._session.add(self._row(operation))
        self._session.commit()
        return operation

    def complete(
        self, operation: RecoveryOperation, *, succeeded: bool, code: str
    ) -> RecoveryOperation:
        changed = operation.model_copy(
            update={
                "state": RecoveryState.SUCCEEDED if succeeded else RecoveryState.FAILED,
                "code": code,
                "revision": operation.revision + 1,
                "completed_at": datetime.now(UTC),
            }
        )
        row = self._session.get(RecoveryOperationRow, str(operation.operation_id))
        if row is None or row.revision != operation.revision:
            raise RuntimeError("recovery.operation.concurrent_update")
        row.state = changed.state
        row.revision = changed.revision
        row.completed_at = changed.completed_at
        row.payload = changed.model_dump_json()
        self._session.commit()
        return changed

    @staticmethod
    def _row(operation: RecoveryOperation) -> RecoveryOperationRow:
        return RecoveryOperationRow(
            operation_id=str(operation.operation_id),
            correlation_id=str(operation.correlation_id.value),
            action=operation.action,
            state=operation.state,
            revision=operation.revision,
            started_at=operation.started_at,
            completed_at=operation.completed_at,
            payload=operation.model_dump_json(),
        )
