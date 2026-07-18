from unittest import TestCase

from osca import __version__
from osca.configuration.api.contracts import RawConfiguration
from osca.configuration.application import validate_configuration
from osca.operations.api import ComponentReadiness, HealthState
from osca.operations.application import build_readiness
from osca.shared_kernel.api import CorrelationId


class ReadinessTests(TestCase):
    def setUp(self) -> None:
        self.configuration = validate_configuration(RawConfiguration())

    def test_empty_required_component_set_is_healthy(self) -> None:
        snapshot = build_readiness(
            self.configuration,
            (),
            product_version=__version__,
            correlation_id=CorrelationId.new(),
        )
        self.assertEqual(snapshot.state, HealthState.HEALTHY)

    def test_required_blocker_prevents_healthy_status(self) -> None:
        components = (
            ComponentReadiness(
                component="configuration",
                required=True,
                state=HealthState.HEALTHY,
                code="CONFIGURATION_VALID",
            ),
            ComponentReadiness(
                component="vault",
                required=True,
                state=HealthState.BLOCKED,
                code="VAULT_UNAVAILABLE",
                impact="Secret-dependent work cannot start.",
                remediation="Configure an available credential-store adapter.",
            ),
        )
        snapshot = build_readiness(
            self.configuration,
            components,
            product_version=__version__,
            correlation_id=CorrelationId.new(),
        )
        self.assertEqual(snapshot.state, HealthState.BLOCKED)

    def test_optional_failure_does_not_override_required_health(self) -> None:
        components = (
            ComponentReadiness(
                component="telemetry-export",
                required=False,
                state=HealthState.UNAVAILABLE,
                code="EXPORTER_UNAVAILABLE",
            ),
        )
        snapshot = build_readiness(
            self.configuration,
            components,
            product_version=__version__,
            correlation_id=CorrelationId.new(),
        )
        self.assertEqual(snapshot.state, HealthState.HEALTHY)

