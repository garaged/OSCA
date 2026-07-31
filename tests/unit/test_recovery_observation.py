import logging
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from osca.operations.infrastructure.telemetry import Telemetry
from osca.recovery.domain import RecoveryAction, RecoveryOperation, RecoveryState
from osca.recovery.infrastructure.observation import RecoveryTelemetryObserver
from osca.shared_kernel.api import CorrelationId


def test_recovery_observation_is_correlated_and_secret_free() -> None:
    spans = InMemorySpanExporter()
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(SimpleSpanProcessor(spans))
    metrics = InMemoryMetricReader()
    meter_provider = MeterProvider(metric_readers=[metrics])
    telemetry = Telemetry(
        tracer=tracer_provider.get_tracer("test"),
        meter=meter_provider.get_meter("test"),
    )
    records: list[logging.LogRecord] = []

    class Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record)

    logger = logging.getLogger("test.recovery")
    logger.setLevel(logging.INFO)
    logger.addHandler(Capture())
    operation = RecoveryOperation(
        correlation_id=CorrelationId.new(),
        actor="local-owner",
        action=RecoveryAction.EXECUTE,
        state=RecoveryState.SUCCEEDED,
        target="/path/that/must/not/be/observed/SECRET-CANARY",
    )
    RecoveryTelemetryObserver(logger, telemetry).record(operation)
    assert getattr(records[-1], "correlation_id", None) == str(operation.correlation_id.value)
    assert "SECRET-CANARY" not in records[-1].getMessage()
    attributes = spans.get_finished_spans()[0].attributes
    assert attributes is not None
    assert attributes["osca.recovery.operation_id"] == str(operation.operation_id)
    metrics_data = metrics.get_metrics_data()
    assert metrics_data is not None
    assert metrics_data.resource_metrics
