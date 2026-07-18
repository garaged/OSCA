from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from osca.recovery.domain import RecoveryAction, RecoveryState
from osca.recovery.infrastructure import RecoveryBase, SqliteRecoveryOperationRepository
from osca.shared_kernel.api import CorrelationId


def test_recovery_operation_is_persisted_before_completion() -> None:
    engine = create_engine("sqlite://")
    RecoveryBase.metadata.create_all(engine)
    with Session(engine) as session, session.begin():
        repository = SqliteRecoveryOperationRepository(session)
        running = repository.start(
            correlation_id=CorrelationId.new(),
            actor="local-owner",
            action=RecoveryAction.CREATE,
            target="backup.age",
        )
        assert running.state == RecoveryState.RUNNING
        completed = repository.complete(
            running, succeeded=True, code="recovery.backup.created"
        )
        assert completed.state == RecoveryState.SUCCEEDED
        assert completed.revision == 2
