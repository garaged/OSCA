from ipaddress import IPv4Address, IPv6Address
from unittest import TestCase

from osca.configuration.api import (
    DeploymentMode,
    ListenerConfiguration,
    SecurityConfiguration,
)
from osca.configuration.api.contracts import RawConfiguration
from osca.configuration.application import ConfigurationRejected, validate_configuration


class ConfigurationValidationTests(TestCase):
    def test_default_local_profile_is_loopback_safe(self) -> None:
        validated = validate_configuration(RawConfiguration())
        self.assertTrue(validated.listener.host.is_loopback)
        self.assertEqual(validated.deployment_mode, DeploymentMode.LOCAL)

    def test_ipv6_loopback_is_allowed(self) -> None:
        raw = RawConfiguration(listener=ListenerConfiguration(host=IPv6Address("::1")))
        self.assertEqual(validate_configuration(raw).listener.host, IPv6Address("::1"))

    def test_non_loopback_local_binding_is_rejected(self) -> None:
        raw = RawConfiguration(listener=ListenerConfiguration(host=IPv4Address("0.0.0.0")))
        with self.assertRaises(ConfigurationRejected) as raised:
            validate_configuration(raw)
        self.assertEqual(raised.exception.errors[0].code, "CONFIG_UNSAFE_LOCAL_BIND")

    def test_personal_server_requires_complete_security_profile(self) -> None:
        raw = RawConfiguration(
            deployment_mode=DeploymentMode.PERSONAL_SERVER,
            listener=ListenerConfiguration(host=IPv4Address("192.0.2.10")),
        )
        with self.assertRaises(ConfigurationRejected) as raised:
            validate_configuration(raw)
        self.assertEqual(len(raised.exception.errors), 4)

    def test_complete_personal_server_profile_is_accepted(self) -> None:
        raw = RawConfiguration(
            deployment_mode=DeploymentMode.PERSONAL_SERVER,
            listener=ListenerConfiguration(host=IPv4Address("192.0.2.10")),
            security=SecurityConfiguration(
                tls_certificate_reference="vault://tls/cert",
                tls_private_key_reference="vault://tls/key",
                trust_store_reference="vault://tls/trust",
                session_provider="local-session-v1",
            ),
        )
        self.assertEqual(validate_configuration(raw).deployment_mode, DeploymentMode.PERSONAL_SERVER)

