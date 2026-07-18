import logging
from typing import Any

from osca.shared_kernel.api import CorrelationId
from osca.workflow.api import DiagnosticInput, DiagnosticRun
from osca.workflow.infrastructure.observation import WorkflowObserver


class AuditCapture:
    def __init__(self) -> None:
        self.records: list[Any] = []

    def add(self, record: Any) -> None:
        self.records.append(record)


def test_observation_contains_correlation_but_not_input() -> None:
    run = DiagnosticRun(
        actor="operator",
        correlation_id=CorrelationId.new(),
        idempotency_key="secret-key",
        input=DiagnosticInput(probe="storage", parameters={"token": "protected"}),
    )
    records: list[logging.LogRecord] = []

    class Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record)

    logger = logging.getLogger("test.workflow.observation")
    logger.setLevel(logging.INFO)
    logger.addHandler(Capture())
    WorkflowObserver(logger).record("submitted", run)
    record = records[-1]
    assert record.correlation_id == str(run.correlation_id.value)
    assert "protected" not in record.getMessage()
    assert "secret-key" not in record.getMessage()


def test_cancellation_emits_distinct_safe_audit_record() -> None:
    run = DiagnosticRun(
        actor="operator",
        correlation_id=CorrelationId.new(),
        idempotency_key="key",
        input=DiagnosticInput(probe="storage"),
    )
    audit = AuditCapture()
    WorkflowObserver(logging.getLogger("test.workflow.audit"), audit).record(
        "cancellation_requested", run
    )
    assert len(audit.records) == 1
    assert audit.records[0].action == "workflow.diagnostic.cancel"
    assert audit.records[0].target_id == str(run.run_id.value)
