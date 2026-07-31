from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from osca.bootstrap.authorization import local_authorization_context
from osca.catalog.infrastructure import CatalogBase, SqliteResultCatalog
from osca.shared_kernel.api import CorrelationId
from osca.workflow.api import (
    CancelDiagnosticRun,
    DiagnosticCheckpoint,
    DiagnosticInput,
    DiagnosticRunError,
    DiagnosticRunState,
    SubmitDiagnosticRun,
)
from osca.workflow.application.handlers import IdempotencyConflict, MissingResult, WorkflowService
from osca.workflow.infrastructure import SqliteDiagnosticRunRepository, WorkflowBase
from osca.workflow.infrastructure.executor import EmbeddedExecutor


@pytest.fixture
def session() -> Generator[Session, None, None]:
    engine = create_engine("sqlite://")
    WorkflowBase.metadata.create_all(engine)
    CatalogBase.metadata.create_all(engine)
    with Session(engine) as value, value.begin():
        yield value


def command(key: str = "key", probe: str = "storage") -> SubmitDiagnosticRun:
    return SubmitDiagnosticRun(
        authorization=local_authorization_context(),
        correlation_id=CorrelationId.new(),
        idempotency_key=key,
        input=DiagnosticInput(probe=probe),
    )


def executor(
    repository: SqliteDiagnosticRunRepository,
    session: Session,
    owner: str,
    **options: Any,
) -> EmbeddedExecutor:
    return EmbeddedExecutor(
        repository,
        owner=owner,
        result_catalog=SqliteResultCatalog(session),
        **options,
    )


def test_submission_is_idempotent_and_conflicts_are_rejected(session: Session) -> None:
    service = WorkflowService(SqliteDiagnosticRunRepository(session))
    first = service.submit(command())
    assert service.submit(command()).run_id == first.run_id
    with pytest.raises(IdempotencyConflict):
        service.submit(command(probe="network"))


def test_atomic_claim_lease_heartbeat_and_expiry_recovery(session: Session) -> None:
    repository = SqliteDiagnosticRunRepository(session)
    run = WorkflowService(repository).submit(command())
    now = datetime.now(UTC)
    first = executor(repository, session, "one", lease_seconds=5)
    second = executor(repository, session, "two", lease_seconds=5)
    claimed = first.claim(now)
    assert claimed is not None and claimed.run_id == run.run_id
    assert second.claim(now) is None
    heartbeaten = first.heartbeat(claimed, now + timedelta(seconds=1))
    assert heartbeaten.lease_expires_at == now + timedelta(seconds=6)
    interrupted = second.recover_expired(now + timedelta(seconds=7))[0]
    assert interrupted.state == DiagnosticRunState.INTERRUPTED
    second.resume(interrupted)
    reclaimed = second.claim(now + timedelta(seconds=7))
    assert reclaimed is not None and reclaimed.lease_owner == "two"


def test_checkpoint_resume_result_before_success_retry_and_cancellation(session: Session) -> None:
    repository = SqliteDiagnosticRunRepository(session)
    service = WorkflowService(repository)
    worker = executor(repository, session, "one")
    service.submit(command())
    claimed = worker.claim()
    assert claimed is not None
    completed = worker.execute(claimed)
    assert completed.state == DiagnosticRunState.SUCCEEDED
    assert completed.result is not None
    assert completed.result.verify_integrity()
    assert completed.result.producer_build == completed.producer_build
    assert completed.result.lineage == (completed.run_id.value,)
    assert session.scalar(text("SELECT COUNT(*) FROM catalog_result_metadata")) == 1
    retained = repository.get(completed.run_id)
    assert retained is not None and retained.verify_integrity()
    assert retained.lineage == (retained.run_id.value,)
    assert completed.checkpoint is not None and completed.checkpoint.phase == 3

    retry_run = service.submit(command("retry"))
    retry_claim = worker.claim()
    assert retry_claim is not None and retry_claim.run_id == retry_run.run_id
    retry = worker.fail(
        retry_claim, DiagnosticRunError(code="temporary", message="retry", retryable=True)
    )
    assert retry.state == DiagnosticRunState.PENDING and retry.next_attempt_at is not None

    pending = service.submit(command("cancel"))
    cancelled = service.cancel(
        CancelDiagnosticRun(
            authorization=local_authorization_context(),
            correlation_id=CorrelationId.new(),
            run_id=pending.run_id,
        )
    )
    assert cancelled.state == DiagnosticRunState.CANCELLED


def test_safe_shutdown_checkpoint_compatibility_and_result_invariant(session: Session) -> None:
    repository = SqliteDiagnosticRunRepository(session)
    service = WorkflowService(repository)
    worker = executor(repository, session, "one")
    service.submit(command("shutdown"))
    claimed = worker.claim()
    assert claimed is not None
    worker.stop()
    assert worker.execute(claimed).state == DiagnosticRunState.INTERRUPTED

    service.submit(command("checkpoint"))
    incompatible_worker = executor(repository, session, "one")
    incompatible = incompatible_worker.claim()
    assert incompatible is not None
    invalid = DiagnosticCheckpoint(
        family="osca.workflow.diagnostic-checkpoint",
        version="2.0.0",
        phase=1,
        completed_phases=("validate",),
    )
    incompatible = incompatible.model_copy(update={"checkpoint": invalid})
    assert repository.replace(incompatible, incompatible.revision)
    blocked = incompatible_worker.execute(incompatible)
    assert blocked.state == DiagnosticRunState.BLOCKED
    assert blocked.error is not None and blocked.error.code == "checkpoint.incompatible"

    service.submit(command("result"))
    without_result = executor(repository, session, "one").claim()
    assert without_result is not None
    with pytest.raises(MissingResult):
        service.transition(without_result, DiagnosticRunState.SUCCEEDED)


def test_retry_exhaustion_and_compare_and_transition_guard(session: Session) -> None:
    repository = SqliteDiagnosticRunRepository(session)
    service = WorkflowService(repository)
    service.submit(command("exhaust"))
    worker = executor(repository, session, "one", max_attempts=1)
    claimed = worker.claim()
    assert claimed is not None
    failed = worker.fail(
        claimed,
        DiagnosticRunError(code="temporary", message="retry exhausted", retryable=True),
    )
    assert failed.state == DiagnosticRunState.FAILED
    assert not repository.replace(failed.model_copy(update={"revision": 99}), claimed.revision)
