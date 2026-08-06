"""D3 Kraken acquisition extension for the desktop application service."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from osca.desktop_api.d3_service import D3DesktopApplicationService
from osca.desktop_api.profile_lock import ProfileMutationLock
from osca.desktop_api.service import DesktopServiceError
from osca.historical_acquisition import (
    HistoricalAcquisitionRequest,
    HistoricalAssetClass,
    run_historical_acquisition,
)
from osca.operator_experience import load_operator_config
from osca.production_ingestion.contracts import ProductionProvider
from osca.production_ingestion.services import Transport
from osca.security.application.ports import SecretVault


class D3AcquisitionApplicationService(D3DesktopApplicationService):
    """Expose canonical synchronous Kraken acquisition without fake background state."""

    def __init__(
        self,
        *,
        storage_root: Path | None = None,
        state_root: Path | None = None,
        sample_path: Path | None = None,
        secret_vault: SecretVault | None = None,
        acquisition_transport: Transport | None = None,
    ) -> None:
        super().__init__(
            storage_root=storage_root,
            state_root=state_root,
            sample_path=sample_path,
            secret_vault=secret_vault,
        )
        self._acquisition_transport = acquisition_transport
        self._handlers["acquisition.run"] = self._acquisition_run

    def _acquisition_run(self, params: dict[str, Any]) -> dict[str, Any]:
        _require_allowed_keys(
            params,
            {
                "profile_root",
                "provider_id",
                "asset_class",
                "symbol",
                "timeframe",
                "venue_context",
                "expected_pair_key",
                "start_at",
                "end_at",
                "freshness_max_age_seconds",
                "minimum_rows",
                "require_complete_range",
                "network_access_enabled",
                "cancel_requested",
                "since",
            },
        )
        profile_root = _absolute_path(params, "profile_root")
        profile = self._inspect_profile(profile_root)
        if not profile["can_open"]:
            raise DesktopServiceError(
                "profile_unavailable",
                "a compatible writable profile is required before provider acquisition",
            )
        provider = _required_string(params, "provider_id", 64)
        if provider != ProductionProvider.KRAKEN.value:
            raise DesktopServiceError(
                "provider_not_supported",
                "D3 acquisition supports Kraken public spot OHLC only.",
            )
        asset_class = _optional_string(params, "asset_class", "crypto", 16)
        if asset_class != HistoricalAssetClass.CRYPTO.value:
            raise DesktopServiceError(
                "provider_not_supported",
                "Kraken D3 acquisition supports crypto assets only.",
            )
        config = load_operator_config(profile_root)
        values: dict[str, Any] = {
            "provider_id": ProductionProvider.KRAKEN,
            "asset_class": HistoricalAssetClass.CRYPTO,
            "symbol": _required_string(params, "symbol", 80),
            "timeframe": _required_string(params, "timeframe", 8),
            "storage_root": config.storage_root,
            "venue_context": _optional_string(params, "venue_context", "kraken-spot", 160),
            "expected_pair_key": _optional_text(params, "expected_pair_key", 160),
            "start_at": _optional_datetime(params, "start_at"),
            "end_at": _optional_datetime(params, "end_at"),
            "freshness_max_age_seconds": _optional_int(
                params, "freshness_max_age_seconds", None, 0
            ),
            "minimum_rows": _optional_int(params, "minimum_rows", 1, 1),
            "require_complete_range": _optional_bool(
                params, "require_complete_range", False
            ),
            "network_access_enabled": _optional_bool(
                params, "network_access_enabled", False
            ),
            "cancel_requested": _optional_bool(params, "cancel_requested", False),
            "since": _optional_int(params, "since", None, 0),
        }
        try:
            request = HistoricalAcquisitionRequest.model_validate(values)
        except ValidationError as exc:
            first = exc.errors(include_url=False)[0]
            location = ".".join(str(part) for part in first.get("loc", ())) or "request"
            raise DesktopServiceError(
                "invalid_parameters",
                f"Invalid acquisition {location}: {first.get('msg', 'validation failed')}",
            ) from exc
        try:
            with ProfileMutationLock(profile_root):
                evidence = run_historical_acquisition(
                    request,
                    transport=self._acquisition_transport,
                )
        except (OSError, ValueError) as exc:
            raise DesktopServiceError(
                "acquisition_failed",
                f"Historical acquisition could not retain safe evidence: {exc}",
                retryable=True,
            ) from exc
        return {
            "family": "osca.desktop-acquisition.result",
            "version": "1.0.0",
            "execution_model": "synchronous-sidecar-request",
            "live_progress_available": False,
            "cancellation_mode": "pre-network-request-only",
            "credential_required": False,
            "provider_account_required": False,
            "evidence": evidence.model_dump(mode="json"),
        }


def _require_allowed_keys(params: dict[str, Any], allowed: set[str]) -> None:
    unexpected = sorted(set(params) - allowed)
    if unexpected:
        raise DesktopServiceError(
            "invalid_parameters",
            f"acquisition.run received unsupported parameters: {', '.join(unexpected)}",
        )


def _absolute_path(params: dict[str, Any], name: str) -> Path:
    value = params.get(name)
    if not isinstance(value, str) or not value.strip() or len(value) > 4096:
        raise DesktopServiceError("invalid_parameters", f"{name} must be a valid path")
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise DesktopServiceError("invalid_parameters", f"{name} must be an absolute path")
    return path.resolve()


def _required_string(params: dict[str, Any], name: str, limit: int) -> str:
    value = params.get(name)
    if not isinstance(value, str) or not value.strip():
        raise DesktopServiceError("invalid_parameters", f"{name} must be a non-empty string")
    value = value.strip()
    if len(value) > limit:
        raise DesktopServiceError("invalid_parameters", f"{name} exceeds {limit} characters")
    return value


def _optional_string(
    params: dict[str, Any], name: str, default: str, limit: int
) -> str:
    if name not in params or params[name] is None:
        return default
    return _required_string(params, name, limit)


def _optional_text(params: dict[str, Any], name: str, limit: int) -> str | None:
    if name not in params or params[name] is None:
        return None
    return _required_string(params, name, limit)


def _optional_bool(params: dict[str, Any], name: str, default: bool) -> bool:
    if name not in params or params[name] is None:
        return default
    value = params[name]
    if not isinstance(value, bool):
        raise DesktopServiceError("invalid_parameters", f"{name} must be a boolean")
    return value


def _optional_int(
    params: dict[str, Any], name: str, default: int | None, minimum: int
) -> int | None:
    if name not in params or params[name] is None:
        return default
    value = params[name]
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise DesktopServiceError(
            "invalid_parameters",
            f"{name} must be an integer greater than or equal to {minimum}",
        )
    return value


def _optional_datetime(params: dict[str, Any], name: str) -> str | datetime | None:
    if name not in params or params[name] is None:
        return None
    value = params[name]
    if not isinstance(value, (str, datetime)):
        raise DesktopServiceError(
            "invalid_parameters", f"{name} must be an ISO-8601 timestamp"
        )
    return value
