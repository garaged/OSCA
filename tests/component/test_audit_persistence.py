from pathlib import Path

from osca.bootstrap.database import SessionProvider, create_sqlite_engine
from osca.operations.api import AuditOutcome, AuditRecord
from osca.operations.infrastructure import AuditBase, SqliteAuditRepository
from osca.shared_kernel.api import CorrelationId


def test_audit_record_round_trip_uses_separate_owned_table(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "osca.db")
    AuditBase.metadata.create_all(engine)
    sessions = SessionProvider(engine)
    record = AuditRecord(
        correlation_id=CorrelationId.new(),
        actor="local-owner",
        action="configuration.reject",
        target_type="configuration",
        target_id="candidate-local",
        outcome=AuditOutcome.REJECTED,
        code="CONFIG_UNSAFE_LOCAL_BIND",
        policy_version="1.0.0",
    )

    with sessions.transaction() as session:
        SqliteAuditRepository(session).add(record)
    with sessions.transaction() as session:
        restored = SqliteAuditRepository(session).get(record.record_id)

    assert restored == record
    assert "secret" not in record.model_dump_json().casefold()

