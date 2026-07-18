from __future__ import annotations

import logging
from typing import Protocol

from osca.operations.api import AuditOutcome, AuditRecord
from osca.workflow.api import DiagnosticRun


class AuditSink(Protocol):
    def add(self, record: AuditRecord) -> None: ...


class WorkflowObserver:
    """Operations-facing safe telemetry seam; no input or secret-bearing values."""

    def __init__(
        self,
        logger: logging.Logger | None = None,
        audit: AuditSink | None = None,
    ) -> None:
        self._logger = logger or logging.getLogger("osca.workflow")
        self._audit = audit

    def record(self, action: str, run: DiagnosticRun, outcome: str = "succeeded") -> None:
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
