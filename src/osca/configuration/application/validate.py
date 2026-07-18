from __future__ import annotations

from collections.abc import Iterable

from osca.configuration.api import ConfigurationError, DeploymentMode, ValidatedConfiguration
from osca.configuration.api.contracts import RawConfiguration


class ConfigurationRejected(ValueError):
    def __init__(self, errors: Iterable[ConfigurationError]) -> None:
        self.errors = tuple(errors)
        super().__init__("configuration rejected")


def validate_configuration(raw: RawConfiguration) -> ValidatedConfiguration:
    errors: list[ConfigurationError] = []
    is_loopback = raw.listener.host.is_loopback

    if raw.deployment_mode is DeploymentMode.LOCAL and not is_loopback:
        errors.append(
            ConfigurationError(
                code="CONFIG_UNSAFE_LOCAL_BIND",
                field="listener.host",
                message="Local mode accepts loopback listeners only.",
                remediation="Use 127.0.0.1 or ::1, or explicitly configure personal_server mode.",
            )
        )

    if raw.deployment_mode is DeploymentMode.PERSONAL_SERVER:
        required = {
            "security.tls_certificate_reference": raw.security.tls_certificate_reference,
            "security.tls_private_key_reference": raw.security.tls_private_key_reference,
            "security.trust_store_reference": raw.security.trust_store_reference,
            "security.session_provider": raw.security.session_provider,
        }
        for field, value in required.items():
            if not value:
                errors.append(
                    ConfigurationError(
                        code="CONFIG_REMOTE_SECURITY_REQUIRED",
                        field=field,
                        message="Personal-server mode requires protected remote operation.",
                        remediation=f"Configure {field} with a named reference.",
                    )
                )

    if errors:
        raise ConfigurationRejected(errors)

    return ValidatedConfiguration(
        profile=raw.profile,
        deployment_mode=raw.deployment_mode,
        listener=raw.listener,
        security=raw.security,
    )

