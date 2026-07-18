from unittest import TestCase

from osca.bootstrap.runtime import readiness_snapshot
from osca.operations.api import HealthState


class BootstrapTests(TestCase):
    def test_default_snapshot_uses_public_contract(self) -> None:
        snapshot = readiness_snapshot()
        self.assertEqual(snapshot.contract_family, "osca.readiness.snapshot")
        self.assertEqual(snapshot.contract_version, "1.0.0")
        self.assertEqual(snapshot.state, HealthState.HEALTHY)
        self.assertEqual(snapshot.components[0].component, "configuration")

