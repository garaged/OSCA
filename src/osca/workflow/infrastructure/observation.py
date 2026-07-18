from __future__ import annotations

import logging
from typing import Protocol

from osca import __version__
from osca.operations.api import AuditOutcome, AuditRecord, WorkflowJobEvent
from osca.operations.infrastructure.telemetry import Telemetry, configure_telemetry
from osca.workflow.api import DiagnosticRun


class AuditSink(Protocol):
    def add(self, record: AuditRecord) -> None: ...


class EventSink(Protocol):
    def add(self, event: WorkflowJobEvent) -> None: ...


class WorkflowObserver:
    """Operations-facing safe telemetry seam; no input or secret-bearing values."""

    def __init__(
        self,
        logger: logging.Logger | None = None,
        audit: AuditSink | None = None,
        events: EventSink | None = None,
        telemetry: Telemetry | None = None,
    ) -> None:
        self._logger = logger or logging.getLogger("osca.workflow")
        self._audit = audit
        self._events = events
        self._telemetry = telemetry or configure_telemetry(service_version=__version__)
        self._operations = self._telemetry.meter.create_counter(
            "osca.workflow.operations",
            unit="{operation}",
            description="Durable workflow operations by action, outcome, and state.",
        )

    def record(self, action: str, run: DiagnosticRun, outcome: str = "succeeded") -> None:
        attributes = {
            "osca.workflow.action": action,
            "osca.workflow.outcome": outcome,
            "osca.workflow.run_id": str(run.run_id.value),
            "osca.correlation_id": str(run.correlation_id.value),
            "osca.workflow.state": run.state.value,
            "osca.workflow.attempt": run.attempt,
        }
        with self._telemetry.tracer.start_as_current_span(
            f"workflow.{action}", attributes=attributes
        ):
            self._operations.add(1, attributes)
        self._logger.info(
            "workflow.%s",
            action,
            extra={
                "action": action,
                "outcome": outcome,
                "run_id": str(run.run_id.value),
                "correlation_id": str(run.correlation_id.value),
                "state": run.state.value,
                "attempt": run.attempt,
            },
        )
        if self._events is not None:
            self._events.add(
                WorkflowJobEvent(
                    correlation_id=run.correlation_id,
                    run_id=run.run_id.value,
                    action=action,
                    state=run.state.value,
                    attempt=run.attempt,
                    outcome=outcome,
                )
            )
        if self._audit is not None and action == "cancellation_requested":
            self._audit.add(
                AuditRecord(
                    correlation_id=run.correlation_id,
                    actor=run.actor,
                    action="workflow.diagnostic.cancel",
                    target_type="diagnostic_run",
                    target_id=str(run.run_id.value),
                    outcome=AuditOutcome.SUCCEEDED,
                    code="workflow.cancellation_requested",
                    policy_version="1.0.0",
                )
            )
        if run.state.value in {"failed", "blocked"}:
            self._logger.warning(
                "workflow.health_finding",
                extra={
                    "code": run.error.code if run.error else "workflow.blocked",
                    "run_id": str(run.run_id.value),
                    "correlation_id": str(run.correlation_id.value),
                },
            )
