from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from osca.shared_kernel.api import CorrelationId
from osca.workflow.api import (
    CancelDiagnosticRun,
    DiagnosticInput,
    DiagnosticRunError,
    DiagnosticRunState,
    SubmitDiagnosticRun,
)
from osca.workflow.application.handlers import IdempotencyConflict, WorkflowService
from osca.workflow.infrastructure import SqliteDiagnosticRunRepository, WorkflowBase
from osca.workflow.infrastructure.executor import EmbeddedExecutor


@pytest.fixture
def session() -> Session:
    engine = create_engine("sqlite://")
    WorkflowBase.metadata.create_all(engine)
    with Session(engine) as value, value.begin():
        yield value


def command(key: str = "key", probe: str = "storage") -> SubmitDiagnosticRun:
    return SubmitDiagnosticRun(
        actor="operator",
        correlation_id=CorrelationId.new(),
        idempotency_key=key,
        input=DiagnosticInput(probe=probe),
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
    first = EmbeddedExecutor(repository, owner="one", lease_seconds=5)
    second = EmbeddedExecutor(repository, owner="two", lease_seconds=5)
    claimed = first.claim(now)
    assert claimed is not None and claimed.run_id == run.run_id
    assert second.claim(now) is None
    heartbeaten = first.heartbeat(claimed, now + timedelta(seconds=1))
    assert heartbeaten.lease_expires_at == now + timedelta(seconds=6)
    assert (
        second.recover_expired(now + timedelta(seconds=7))[0].state
        == DiagnosticRunState.INTERRUPTED
    )


def test_checkpoint_resume_result_before_success_retry_and_cancellation(session: Session) -> None:
    repository = SqliteDiagnosticRunRepository(session)
    service = WorkflowService(repository)
    executor = EmbeddedExecutor(repository, owner="one")
    service.submit(command())
    claimed = executor.claim()
    assert claimed is not None
    completed = executor.execute(claimed)
    assert completed.state == DiagnosticRunState.SUCCEEDED
    assert completed.result is not None
    assert completed.checkpoint is not None and completed.checkpoint.phase == 3

    retry_run = service.submit(command("retry"))
    retry_claim = executor.claim()
    assert retry_claim is not None and retry_claim.run_id == retry_run.run_id
    retry = executor.fail(
        retry_claim, DiagnosticRunError(code="temporary", message="retry", retryable=True)
    )
    assert retry.state == DiagnosticRunState.PENDING and retry.next_attempt_at is not None

    pending = service.submit(command("cancel"))
    cancelled = service.cancel(
        CancelDiagnosticRun(
            actor="operator", correlation_id=CorrelationId.new(), run_id=pending.run_id
        )
    )
    assert cancelled.state == DiagnosticRunState.CANCELLED
