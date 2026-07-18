from __future__ import annotations

from osca import __version__
from osca.configuration.api.contracts import RawConfiguration
from osca.configuration.application import validate_configuration
from osca.operations.api import ComponentReadiness, HealthState, ReadinessSnapshot
from osca.operations.application import build_readiness
from osca.shared_kernel.api import CorrelationId


def readiness_snapshot(raw: RawConfiguration | None = None) -> ReadinessSnapshot:
    """Compose the M1 readiness query through public capability contracts."""

    configuration = validate_configuration(raw or RawConfiguration())
    components = (
        ComponentReadiness(
            component="configuration",
            required=True,
            state=HealthState.HEALTHY,
            code="CONFIGURATION_VALID",
        ),
    )
    return build_readiness(
        configuration,
        components,
        product_version=__version__,
        correlation_id=CorrelationId.new(),
    )

