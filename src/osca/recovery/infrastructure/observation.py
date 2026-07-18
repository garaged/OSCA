from __future__ import annotations

import logging

from osca import __version__
from osca.operations.infrastructure.telemetry import Telemetry, configure_telemetry
from osca.recovery.domain import RecoveryOperation


class RecoveryTelemetryObserver:
    """Safe correlated telemetry for recovery operations."""

    def __init__(
        self,
        logger: logging.Logger | None = None,
        telemetry: Telemetry | None = None,
    ) -> None:
        self._logger = logger or logging.getLogger("osca.recovery")
        self._telemetry = telemetry or configure_telemetry(service_version=__version__)
        self._operations = self._telemetry.meter.create_counter(
            "osca.recovery.operations",
            unit="{operation}",
            description="Recovery operations by action and outcome.",
        )

    def record(self, operation: RecoveryOperation) -> None:
        attributes = {
            "osca.recovery.action": operation.action.value,
            "osca.recovery.outcome": operation.state.value,
            "osca.recovery.operation_id": str(operation.operation_id),
            "osca.correlation_id": str(operation.correlation_id.value),
        }
        with self._telemetry.tracer.start_as_current_span(
            f"recovery.{operation.action.value}", attributes=attributes
        ):
            self._operations.add(1, attributes)
        self._logger.info(
            "recovery.%s",
            operation.action.value,
            extra={
                "action": operation.action.value,
                "outcome": operation.state.value,
                "operation_id": str(operation.operation_id),
                "correlation_id": str(operation.correlation_id.value),
                "code": operation.code,
            },
        )
