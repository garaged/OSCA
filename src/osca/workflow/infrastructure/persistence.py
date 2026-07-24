from __future__ import annotations

from datetime import datetime
from typing import Any, cast
from uuid import UUID

from sqlalchemy import DateTime, Integer, String, Text, and_, or_, select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from osca.catalog.api import metadata_digest
from osca.workflow.api import (
    DiagnosticRun,
    DiagnosticRunId,
    DiagnosticRunState,
    JobRun,
    JobState,
)


class WorkflowBase(DeclarativeBase):
    pass


class DiagnosticRunRow(WorkflowBase):
    __tablename__ = "workflow_diagnostic_runs"
    run_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    actor: Mapped[str] = mapped_column(String(200), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(200), nullable=False)
    state: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    lease_owner: Mapped[str | None] = mapped_column(String(200))
    lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    payload: Mapped[str] = mapped_column(Text, nullable=False)


class JobRunRow(WorkflowBase):
    __tablename__ = "workflow_job_runs"
    job_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    actor: Mapped[str] = mapped_column(String(200), nullable=False)
    kind: Mapped[str] = mapped_column(String(128), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(200), nullable=False)
    state: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    lease_owner: Mapped[str | None] = mapped_column(String(200))
    lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    payload: Mapped[str] = mapped_column(Text, nullable=False)


class SqliteDiagnosticRunRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, run: DiagnosticRun) -> None:
        self._session.add(self._row(self._seal(run)))
        self._session.flush()

    def get(self, run_id: DiagnosticRunId) -> DiagnosticRun | None:
        row = self._session.get(DiagnosticRunRow, str(run_id.value))
        return None if row is None else DiagnosticRun.model_validate_json(row.payload)

    def find_idempotent(self, actor: str, key: str) -> DiagnosticRun | None:
        row = self._session.scalar(
            select(DiagnosticRunRow).where(
                and_(DiagnosticRunRow.actor == actor, DiagnosticRunRow.idempotency_key == key)
            )
        )
        return None if row is None else DiagnosticRun.model_validate_json(row.payload)

    def list(self, states: tuple[DiagnosticRunState, ...], limit: int) -> tuple[DiagnosticRun, ...]:
        stmt = select(DiagnosticRunRow).order_by(DiagnosticRunRow.run_id).limit(limit)
        if states:
            stmt = stmt.where(DiagnosticRunRow.state.in_([state.value for state in states]))
        return tuple(
            DiagnosticRun.model_validate_json(row.payload) for row in self._session.scalars(stmt)
        )

    def replace(self, run: DiagnosticRun, expected_revision: int) -> bool:
        run = self._seal(run)
        result = cast(
            CursorResult[Any],
            self._session.execute(
                update(DiagnosticRunRow)
                .where(
                    and_(
                        DiagnosticRunRow.run_id == str(run.run_id.value),
                        DiagnosticRunRow.revision == expected_revision,
                    )
                )
                .values(
                    state=run.state.value,
                    revision=run.revision,
                    lease_owner=run.lease_owner,
                    lease_expires_at=run.lease_expires_at,
                    next_attempt_at=run.next_attempt_at,
                    payload=run.model_dump_json(),
                )
            ),
        )
        self._session.flush()
        return result.rowcount == 1

    def claim(self, owner: str, now: datetime, lease_until: datetime) -> DiagnosticRun | None:
        candidate = self._session.scalar(
            select(DiagnosticRunRow)
            .where(
                and_(
                    DiagnosticRunRow.state.in_([DiagnosticRunState.PENDING.value]),
                    or_(
                        DiagnosticRunRow.next_attempt_at.is_(None),
                        DiagnosticRunRow.next_attempt_at <= now,
                    ),
                )
            )
            .order_by(DiagnosticRunRow.run_id)
            .limit(1)
        )
        if candidate is None:
            return None
        run = DiagnosticRun.model_validate_json(candidate.payload)
        claimed = run.model_copy(
            update={
                "state": DiagnosticRunState.RUNNING,
                "revision": run.revision + 1,
                "attempt": run.attempt + 1,
                "lease_owner": owner,
                "lease_expires_at": lease_until,
                "updated_at": now,
            }
        )
        return claimed if self.replace(claimed, run.revision) else None

    @staticmethod
    def _row(run: DiagnosticRun) -> DiagnosticRunRow:
        return DiagnosticRunRow(
            run_id=str(run.run_id.value),
            actor=run.actor,
            idempotency_key=run.idempotency_key,
            state=run.state.value,
            revision=run.revision,
            lease_owner=run.lease_owner,
            lease_expires_at=run.lease_expires_at,
            next_attempt_at=run.next_attempt_at,
            payload=run.model_dump_json(),
        )

    @staticmethod
    def _seal(run: DiagnosticRun) -> DiagnosticRun:
        lineage = run.lineage or (run.run_id.value,)
        with_lineage = run.model_copy(update={"lineage": lineage})
        payload = with_lineage.model_dump(mode="json", exclude={"integrity_digest"})
        digest = metadata_digest(payload)
        return with_lineage.model_copy(update={"integrity_digest": digest})


class SqliteJobRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add_job(self, job: JobRun) -> None:
        self._session.add(
            JobRunRow(
                job_id=str(job.job_id),
                actor=job.actor,
                kind=job.kind,
                idempotency_key=job.idempotency_key,
                state=job.state.value,
                revision=job.revision,
                lease_owner=job.lease_owner,
                lease_expires_at=job.lease_expires_at,
                next_attempt_at=job.next_attempt_at,
                payload=job.model_dump_json(),
            )
        )
        self._session.flush()

    def get_job(self, job_id: UUID) -> JobRun | None:
        row = self._session.get(JobRunRow, str(job_id))
        return None if row is None else JobRun.model_validate_json(row.payload)

    def find_job_idempotent(self, actor: str, kind: str, key: str) -> JobRun | None:
        row = self._session.scalar(
            select(JobRunRow).where(
                and_(
                    JobRunRow.actor == actor,
                    JobRunRow.kind == kind,
                    JobRunRow.idempotency_key == key,
                )
            )
        )
        return None if row is None else JobRun.model_validate_json(row.payload)

    def replace_job(self, job: JobRun, expected_revision: int) -> bool:
        result = cast(
            CursorResult[Any],
            self._session.execute(
                update(JobRunRow)
                .where(
                    and_(
                        JobRunRow.job_id == str(job.job_id),
                        JobRunRow.revision == expected_revision,
                    )
                )
                .values(
                    state=job.state.value,
                    revision=job.revision,
                    lease_owner=job.lease_owner,
                    lease_expires_at=job.lease_expires_at,
                    next_attempt_at=job.next_attempt_at,
                    payload=job.model_dump_json(),
                )
            ),
        )
        self._session.flush()
        return result.rowcount == 1

    def claim_job(self, owner: str, now: datetime, lease_until: datetime) -> JobRun | None:
        row = self._session.scalar(
            select(JobRunRow)
            .where(
                and_(
                    JobRunRow.state == JobState.PENDING,
                    or_(JobRunRow.next_attempt_at.is_(None), JobRunRow.next_attempt_at <= now),
                )
            )
            .order_by(JobRunRow.job_id)
            .limit(1)
        )
        if row is None:
            return None
        job = JobRun.model_validate_json(row.payload)
        claimed = job.model_copy(
            update={
                "state": JobState.RUNNING,
                "revision": job.revision + 1,
                "attempt": job.attempt + 1,
                "lease_owner": owner,
                "lease_expires_at": lease_until,
                "updated_at": now,
            }
        )
        return claimed if self.replace_job(claimed, job.revision) else None
