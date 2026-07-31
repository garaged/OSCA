import logging
from typing import Any, cast

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from osca.operations.infrastructure.telemetry import Telemetry
from osca.shared_kernel.api import CorrelationId
from osca.workflow.api import DiagnosticInput, DiagnosticRun
from osca.workflow.infrastructure.observation import WorkflowObserver


class AuditCapture:
    def __init__(self) -> None:
        self.records: list[Any] = []

    def add(self, record: Any) -> None:
        self.records.append(record)


class EventCapture:
    def __init__(self) -> None:
        self.events: list[Any] = []

    def add(self, event: Any) -> None:
        self.events.append(event)


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
    assert getattr(records[-1], "correlation_id", None) == str(run.correlation_id.value)
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


def test_operation_emits_correlated_span_metric_and_job_event() -> None:
    span_exporter = InMemorySpanExporter()
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
    metric_reader = InMemoryMetricReader()
    meter_provider = MeterProvider(metric_readers=[metric_reader])
    telemetry = Telemetry(
        tracer=tracer_provider.get_tracer("test"),
        meter=meter_provider.get_meter("test"),
    )
    events = EventCapture()
    run = DiagnosticRun(
        actor="local-os-user",
        correlation_id=CorrelationId.new(),
        idempotency_key="key",
        input=DiagnosticInput(probe="storage"),
    )
    WorkflowObserver(
        logging.getLogger("test.workflow.telemetry"),
        events=events,
        telemetry=telemetry,
    ).record("submitted", run)

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    attributes = spans[0].attributes
    assert attributes is not None
    assert attributes["osca.correlation_id"] == str(run.correlation_id.value)
    metrics_data = metric_reader.get_metrics_data()
    assert metrics_data is not None
    assert metrics_data.resource_metrics
    assert events.events[0].correlation_id == run.correlation_id
    assert events.events[0].run_id == run.run_id.value
