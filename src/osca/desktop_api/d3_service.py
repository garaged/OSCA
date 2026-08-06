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
from osca.desktop_api.profile_lock import ProfileMutationLock
from osca.desktop_api.service import DesktopApplicationService, DesktopServiceError
from osca.local_data_import import (
    LocalOHLCVImportFormat,
    LocalOHLCVImportRequest,
    LocalOHLCVTimeframe,
    import_local_ohlcv,
)
from osca.operator_experience import load_operator_config
from osca.security.application.ports import SecretVault
from osca.security.infrastructure import KeyringVault


class D3DesktopApplicationService(DesktopApplicationService):
    """Add D3 data-source methods without widening Rust or frontend authority."""

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
                "local.import": self._local_import,
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

    def _local_import(self, params: dict[str, Any]) -> dict[str, Any]:
        _require_allowed_keys(
            params,
            {
                "profile_root",
                "input_path",
                "symbol",
                "timeframe",
                "source_uri",
                "calendar_assumption",
                "revision_salt",
            },
            "local.import",
        )
        profile_root = _required_absolute_path(params, "profile_root")
        input_path = _required_absolute_path(params, "input_path")
        profile = self._inspect_profile(profile_root)
        if not profile["can_open"]:
            raise DesktopServiceError(
                "profile_unavailable",
                "a compatible writable profile is required before importing local data",
            )
        if not input_path.is_file():
            raise DesktopServiceError(
                "local_import_source_missing",
                "the selected local import source is not an available file",
            )
        symbol = _required_string(params, "symbol", max_length=128)
        timeframe_value = _required_string(params, "timeframe", max_length=8)
        try:
            timeframe = LocalOHLCVTimeframe(timeframe_value)
        except ValueError as exc:
            raise DesktopServiceError(
                "invalid_parameters",
                "timeframe must be one of 1m, 5m, 15m, 30m, 1h, 4h, or 1d",
            ) from exc
        source_uri = _optional_string(
            params,
            "source_uri",
            default="local-file://user-supplied",
            max_length=128,
        )
        calendar_assumption = _optional_string(
            params,
            "calendar_assumption",
            default="source-provided",
            max_length=128,
        )
        revision_salt = _optional_nullable_string(
            params,
            "revision_salt",
            max_length=128,
        )
        config = load_operator_config(profile_root)
        request = LocalOHLCVImportRequest(
            input_path=str(input_path),
            storage_root=config.storage_root,
            symbol=symbol,
            timeframe=timeframe,
            input_format=LocalOHLCVImportFormat.CSV,
            source_uri=source_uri,
            revision_salt=revision_salt,
            calendar_assumption=calendar_assumption,
        )
        try:
            with ProfileMutationLock(profile_root):
                result = import_local_ohlcv(request)
        except (OSError, ValueError) as exc:
            raise DesktopServiceError(
                "local_import_failed",
                f"Local OHLCV import failed: {exc}",
            ) from exc
        return {
            "family": "osca.desktop-local-import.result",
            "version": "1.0.0",
            "status": "imported",
            "network_access_enabled": False,
            "credential_required": False,
            "provider_account_required": False,
            "import": result.model_dump(mode="json"),
        }


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


def _required_absolute_path(params: dict[str, Any], name: str) -> Path:
    value = params.get(name)
    if not isinstance(value, str) or not value.strip():
        raise DesktopServiceError("invalid_parameters", f"{name} must be a non-empty path")
    if len(value) > 4096:
        raise DesktopServiceError("invalid_parameters", f"{name} exceeds 4096 characters")
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise DesktopServiceError("invalid_parameters", f"{name} must be an absolute path")
    return path.resolve()


def _required_string(params: dict[str, Any], name: str, *, max_length: int) -> str:
    value = params.get(name)
    if not isinstance(value, str) or not value.strip():
        raise DesktopServiceError(
            "invalid_parameters",
            f"{name} must be a non-empty string",
        )
    normalized = value.strip()
    if len(normalized) > max_length:
        raise DesktopServiceError(
            "invalid_parameters",
            f"{name} exceeds {max_length} characters",
        )
    return normalized


def _optional_string(
    params: dict[str, Any],
    name: str,
    *,
    default: str,
    max_length: int,
) -> str:
    if name not in params or params[name] is None:
        return default
    return _required_string(params, name, max_length=max_length)


def _optional_nullable_string(
    params: dict[str, Any],
    name: str,
    *,
    max_length: int,
) -> str | None:
    if name not in params or params[name] is None:
        return None
    return _required_string(params, name, max_length=max_length)
