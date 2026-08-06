"""D3 extension of the authoritative desktop application service."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from osca.desktop_api.data_sources import (
    DataSourceError,
    delete_provider_credential,
    parse_provider_id,
    probe_provider_credential,
    provider_catalog,
    store_provider_credential,
)
from osca.desktop_api.service import DesktopApplicationService, DesktopServiceError
from osca.security.application.ports import SecretVault
from osca.security.infrastructure import KeyringVault


class D3DesktopApplicationService(DesktopApplicationService):
    """Add D3 provider catalog and credential methods without widening Rust authority."""

    def __init__(
        self,
        *,
        storage_root: Path | None = None,
        state_root: Path | None = None,
        sample_path: Path | None = None,
        secret_vault: SecretVault | None = None,
    ) -> None:
        super().__init__(
            storage_root=storage_root,
            state_root=state_root,
            sample_path=sample_path,
        )
        self._secret_vault = secret_vault or KeyringVault()
        self._handlers.update(
            {
                "provider.catalog": self._provider_catalog,
                "credential.store": self._credential_store,
                "credential.probe": self._credential_probe,
                "credential.delete": self._credential_delete,
            }
        )

    def _provider_catalog(self, params: dict[str, Any]) -> dict[str, Any]:
        _require_no_params(params, "provider.catalog")
        return provider_catalog(self._secret_vault)

    def _credential_store(self, params: dict[str, Any]) -> dict[str, Any]:
        _require_allowed_keys(params, {"provider_id", "secret_value"}, "credential.store")
        value = params.get("secret_value")
        if not isinstance(value, str):
            raise DesktopServiceError(
                "invalid_parameters",
                "secret_value must be a string",
            )
        return _translate_data_source_error(
            lambda: store_provider_credential(
                self._secret_vault,
                parse_provider_id(params.get("provider_id")),
                value,
            )
        )

    def _credential_probe(self, params: dict[str, Any]) -> dict[str, Any]:
        _require_allowed_keys(params, {"provider_id"}, "credential.probe")
        return _translate_data_source_error(
            lambda: probe_provider_credential(
                self._secret_vault,
                parse_provider_id(params.get("provider_id")),
            )
        )

    def _credential_delete(self, params: dict[str, Any]) -> dict[str, Any]:
        _require_allowed_keys(params, {"provider_id"}, "credential.delete")
        return _translate_data_source_error(
            lambda: delete_provider_credential(
                self._secret_vault,
                parse_provider_id(params.get("provider_id")),
            )
        )


def _translate_data_source_error(
    operation: Callable[[], dict[str, Any]],
) -> dict[str, Any]:
    try:
        return operation()
    except DataSourceError as exc:
        raise DesktopServiceError(
            exc.code,
            str(exc),
            retryable=exc.retryable,
        ) from exc


def _require_no_params(params: dict[str, Any], method: str) -> None:
    if params:
        raise DesktopServiceError(
            "invalid_parameters",
            f"{method} does not accept parameters",
        )


def _require_allowed_keys(params: dict[str, Any], allowed: set[str], method: str) -> None:
    unexpected = sorted(set(params) - allowed)
    if unexpected:
        raise DesktopServiceError(
            "invalid_parameters",
            f"{method} received unsupported parameters: {', '.join(unexpected)}",
        )
