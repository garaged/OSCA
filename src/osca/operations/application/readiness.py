from __future__ import annotations

from osca.configuration.api import ValidatedConfiguration
from osca.operations.api import ComponentReadiness, HealthState, ReadinessSnapshot
from osca.shared_kernel.api import CorrelationId

_PRIORITY = {
    HealthState.HEALTHY: 0,
    HealthState.RECOVERING: 1,
    HealthState.DEGRADED: 2,
    HealthState.UNAVAILABLE: 3,
    HealthState.BLOCKED: 4,
}


def build_readiness(
    configuration: ValidatedConfiguration,
    components: tuple[ComponentReadiness, ...],
    *,
    product_version: str,
    correlation_id: CorrelationId,
) -> ReadinessSnapshot:
    required_states = [item.state for item in components if item.required]
    state = max(required_states, key=_PRIORITY.get, default=HealthState.HEALTHY)
    return ReadinessSnapshot(
        correlation_id=correlation_id,
        configuration_revision=configuration.revision_id,
        product_version=product_version,
        state=state,
        components=components,
    )

