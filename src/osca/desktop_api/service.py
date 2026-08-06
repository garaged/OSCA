"""Authoritative application-service boundary used by desktop adapters."""

from __future__ import annotations

import os
import shutil
from collections.abc import Callable
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, cast

from osca.desktop_api.contracts import DesktopError, DesktopRequest, DesktopResponse
from osca.desktop_api.profile_lock import (
    ProfileLockedError,
    ProfileMutationLock,
    profile_lock_status,
)
from osca.desktop_api.state import DesktopStateStore
from osca.local_data_import import (
    LocalOHLCVImportFormat,
    LocalOHLCVImportRequest,
    LocalOHLCVTimeframe,
    import_local_ohlcv,
)
from osca.operator_experience import doctor_profile, initialize_profile, load_operator_config
from osca.package_lifecycle import inspect_profile, version_report

Handler = Callable[[dict[str, Any]], dict[str, Any]]


class DesktopServiceError(ValueError):
    """A safe structured application error for the desktop protocol."""

    def __init__(self, code: str, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.retryable = retryable


class DesktopApplicationService:
    """Dispatch a deliberately small allow-listed desktop command surface."""

    def __init__(
        self,
        *,
        storage_root: Path | None = None,
        state_root: Path | None = None,
        sample_path: Path | None = None,
    ) -> None:
        self._storage_root = storage_root
        self._state_store = DesktopStateStore(state_root)
        self._sample_path = sample_path or (
            Path(__file__).parent / "sample_data" / "synthetic_aapl_daily.csv"
        )
        self._handlers: dict[str, Handler] = {
            "system.health": self._system_health,
            "desktop.bootstrap": self._desktop_bootstrap,
            "profile.list": self._profile_list,
            "profile.inspect": self._profile_inspect,
            "profile.create": self._profile_create,
            "profile.select": self._profile_select,
            "profile.open": self._profile_open,
            "system.diagnostics": self._system_diagnostics,
            "sample.import": self._sample_import,
        }

    def handle(self, request: DesktopRequest) -> DesktopResponse:
        handler = self._handlers.get(request.method)
        if handler is None:
            return DesktopResponse(
                request_id=request.request_id,
                status="error",
                error=DesktopError(
                    code="method_not_found",
                    message=f"Unsupported desktop method: {request.method}",
                ),
            )
        try:
            result = handler(request.params)
        except DesktopServiceError as exc:
            return DesktopResponse(
                request_id=request.request_id,
                status="error",
                error=DesktopError(
                    code=exc.code,
                    message=str(exc),
                    retryable=exc.retryable,
                ),
            )
        except ProfileLockedError as exc:
            return DesktopResponse(
                request_id=request.request_id,
                status="error",
                error=DesktopError(code="profile_locked", message=str(exc)),
            )
        except (OSError, ValueError) as exc:
            return DesktopResponse(
                request_id=request.request_id,
                status="error",
                error=DesktopError(code="application_error", message=str(exc)),
            )
        return DesktopResponse(request_id=request.request_id, status="ok", result=result)

    def _system_health(self, params: dict[str, Any]) -> dict[str, Any]:
        _require_no_params(params, "system.health")
        try:
            package_version = version("osca")
        except PackageNotFoundError:
            package_version = "development"
        return {
            "service": "osca-desktop-api",
            "status": "ready",
            "protocol_version": "1.0",
            "package_version": package_version,
            "network_access_enabled": False,
            "recommendations_enabled": False,
            "broker_connections_enabled": False,
            "autonomous_execution_enabled": False,
            "live_order_execution": False,
        }

    def _desktop_bootstrap(self, params: dict[str, Any]) -> dict[str, Any]:
        _require_no_params(params, "desktop.bootstrap")
        state = self._state_store.load()
        return {
            "family": "osca.desktop-bootstrap.result",
            "version": "1.0.0",
            "first_run_required": len(state.profiles) == 0,
            "selected_profile": state.selected_profile,
            "profiles": [profile.model_dump(mode="json") for profile in state.profiles],
            "navigation": [
                {"id": "home", "label": "Home", "available": True},
                {
                    "id": "research",
                    "label": "Research",
                    "available": False,
                    "reason": "Research workbench arrives in a later desktop milestone.",
                },
                {
                    "id": "evidence",
                    "label": "Evidence",
                    "available": False,
                    "reason": "Desktop evidence navigation arrives after the shell foundation.",
                },
                {"id": "system", "label": "System", "available": True},
            ],
            "disclosures": _disclosures(),
            "capabilities": _capabilities(),
        }

    def _profile_list(self, params: dict[str, Any]) -> dict[str, Any]:
        _require_no_params(params, "profile.list")
        state = self._state_store.load()
        return {
            "family": "osca.desktop-profile-list.result",
            "version": "1.0.0",
            "selected_profile": state.selected_profile,
            "profiles": [profile.model_dump(mode="json") for profile in state.profiles],
        }

    def _profile_inspect(self, params: dict[str, Any]) -> dict[str, Any]:
        if not params and self._storage_root is not None:
            return self._legacy_profile_inspect()
        _require_allowed_keys(params, {"profile_root"}, "profile.inspect")
        return self._inspect_profile(_required_path(params, "profile_root"))

    def _profile_create(self, params: dict[str, Any]) -> dict[str, Any]:
        _require_allowed_keys(
            params,
            {"profile_root", "storage_root", "workspace_port"},
            "profile.create",
        )
        profile_root = _required_path(params, "profile_root")
        storage_root = _optional_path(params, "storage_root")
        workspace_port = _optional_port(params)
        _require_safe_profile_root(profile_root)
        _require_safe_new_profile_target(profile_root)

        profile_existed = profile_root.exists()
        try:
            with ProfileMutationLock(profile_root):
                initialized = initialize_profile(
                    profile_root,
                    storage_root=storage_root,
                    workspace_port=workspace_port,
                )
        except Exception:
            _restore_pre_creation_target(profile_root, existed=profile_existed)
            raise

        profile = self._inspect_profile(profile_root)
        if not profile["can_open"]:
            raise DesktopServiceError(
                "profile_unavailable",
                "profile was initialized but failed final compatibility or storage validation",
            )
        state = self._state_store.remember(profile_root, opened=True)
        return {
            "family": "osca.desktop-profile-create.result",
            "version": "1.0.0",
            "status": "created",
            "profile": profile,
            "initialization": initialized,
            "selected_profile": state.selected_profile,
        }

    def _profile_select(self, params: dict[str, Any]) -> dict[str, Any]:
        _require_allowed_keys(params, {"profile_root"}, "profile.select")
        profile_root = _required_path(params, "profile_root")
        if not profile_root.is_dir():
            raise DesktopServiceError(
                "profile_not_found",
                f"profile directory does not exist: {profile_root}",
            )
        profile = self._inspect_profile(profile_root)
        state = self._state_store.remember(profile_root, opened=False)
        return {
            "family": "osca.desktop-profile-select.result",
            "version": "1.0.0",
            "status": "selected",
            "selected_profile": state.selected_profile,
            "profile": profile,
        }

    def _profile_open(self, params: dict[str, Any]) -> dict[str, Any]:
        _require_allowed_keys(params, {"profile_root"}, "profile.open")
        profile_root = _required_path(params, "profile_root")
        profile = self._inspect_profile(profile_root)
        if profile["lock_state"] == "locked":
            raise DesktopServiceError(
                "profile_locked",
                "profile is currently in use by another OSCA process",
            )
        if not profile["can_open"]:
            raise DesktopServiceError(
                "profile_unavailable",
                "profile failed compatibility, storage, or mutation-safety checks",
            )

        diagnostics = doctor_profile(profile_root)
        if diagnostics["status"] == "failed":
            raise DesktopServiceError(
                "profile_unavailable",
                "profile diagnostics failed; inspect the returned System guidance",
            )
        state = self._state_store.remember(profile_root, opened=True)
        return {
            "family": "osca.desktop-profile-open.result",
            "version": "1.0.0",
            "status": "opened",
            "selected_profile": state.selected_profile,
            "profile": profile,
            "diagnostics": diagnostics,
        }

    def _system_diagnostics(self, params: dict[str, Any]) -> dict[str, Any]:
        _require_allowed_keys(params, {"profile_root"}, "system.diagnostics")
        profile_root = _optional_path(params, "profile_root")
        payload: dict[str, Any] = {
            "family": "osca.desktop-diagnostics.result",
            "version": "1.0.0",
            "package": version_report(),
            "protocol_version": "1.0",
            "sidecar_status": "ready",
            "network_policy": "disabled-unless-explicitly-enabled-by-a-later-capability",
            "provider_status": "credential-free bundled sample available; setup deferred to D3",
            "recommendations_enabled": False,
            "live_execution_enabled": False,
        }
        if profile_root is None:
            payload["profile"] = None
            payload["profile_diagnostics"] = None
            return payload

        payload["profile"] = self._inspect_profile(profile_root)
        payload["profile_diagnostics"] = (
            doctor_profile(profile_root) if (profile_root / "config.json").is_file() else None
        )
        return payload

    def _sample_import(self, params: dict[str, Any]) -> dict[str, Any]:
        _require_allowed_keys(params, {"profile_root"}, "sample.import")
        profile_root = _required_path(params, "profile_root")
        profile = self._inspect_profile(profile_root)
        if not profile["can_open"]:
            raise DesktopServiceError(
                "profile_unavailable",
                "a compatible writable profile is required before importing sample data",
            )
        if not self._sample_path.is_file():
            raise DesktopServiceError(
                "sample_unavailable",
                "the bundled synthetic sample is unavailable in this installation",
            )

        config = load_operator_config(profile_root)
        request = LocalOHLCVImportRequest(
            input_path=str(self._sample_path),
            storage_root=config.storage_root,
            symbol="AAPL-SYNTHETIC",
            timeframe=LocalOHLCVTimeframe.ONE_DAY,
            input_format=LocalOHLCVImportFormat.CSV,
            source_uri="bundled-synthetic://osca/d2/aapl-daily-v1",
            revision_salt="d2-bundled-synthetic-aapl-daily-v1",
            calendar_assumption="synthetic-daily-sequence",
        )
        with ProfileMutationLock(profile_root):
            result = import_local_ohlcv(request)
        return {
            "family": "osca.desktop-sample-import.result",
            "version": "1.0.0",
            "status": "available",
            "sample_id": "d2-synthetic-aapl-daily-v1",
            "sample_label": "Synthetic AAPL-labelled daily research sample",
            "synthetic": True,
            "network_access_enabled": False,
            "provider_account_required": False,
            "credential_required": False,
            "import": result.model_dump(mode="json"),
        }

    def _legacy_profile_inspect(self) -> dict[str, Any]:
        root = self._storage_root
        return {
            "configured": root is not None,
            "storage_root": str(root) if root is not None else None,
            "exists": root.exists() if root is not None else False,
            "writable": root.is_dir() if root is not None and root.exists() else False,
        }

    def _inspect_profile(self, profile_root: Path) -> dict[str, Any]:
        lifecycle = inspect_profile(profile_root)
        raw_checks = lifecycle.get("checks", [])
        checks = cast(list[dict[str, Any]], raw_checks)
        lock_state = profile_lock_status(profile_root)
        findings = [
            {
                "check_id": str(check.get("check_id", "unknown")),
                "status": str(check.get("status", "fail")),
                "message": str(check.get("message", "Profile check failed.")),
                "remediation": check.get("remediation"),
            }
            for check in checks
            if check.get("status") != "pass"
        ]
        if lock_state != "available":
            findings.append(
                {
                    "check_id": "profile-mutation-lock",
                    "status": "fail" if lock_state == "locked" else "warning",
                    "message": (
                        "Profile is currently locked."
                        if lock_state == "locked"
                        else "Profile lock availability could not be verified."
                    ),
                    "remediation": "Close other OSCA processes and retry.",
                }
            )
        exists = profile_root.is_dir()
        writable = exists and os.access(profile_root, os.W_OK)
        lifecycle_status = str(lifecycle.get("status", "incompatible"))
        return {
            "family": "osca.desktop-profile-inspection.result",
            "version": "1.0.0",
            "profile_root": str(profile_root),
            "exists": exists,
            "configured": (profile_root / "config.json").is_file(),
            "writable": writable,
            "lock_state": lock_state,
            "compatibility_status": lifecycle_status,
            "storage_root": lifecycle.get("storage_root"),
            "can_open": (
                exists
                and writable
                and lock_state == "available"
                and lifecycle_status in {"compatible", "warning"}
            ),
            "findings": findings,
            "lifecycle": lifecycle,
        }


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


def _required_path(params: dict[str, Any], name: str) -> Path:
    value = params.get(name)
    if not isinstance(value, str) or not value.strip():
        raise DesktopServiceError("invalid_parameters", f"{name} must be a non-empty path")
    if len(value) > 4096:
        raise DesktopServiceError("invalid_parameters", f"{name} exceeds 4096 characters")
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise DesktopServiceError("invalid_parameters", f"{name} must be an absolute path")
    return path.resolve()


def _optional_path(params: dict[str, Any], name: str) -> Path | None:
    if name not in params or params[name] is None:
        return None
    return _required_path(params, name)


def _optional_port(params: dict[str, Any]) -> int:
    value = params.get("workspace_port", 8765)
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 65535:
        raise DesktopServiceError(
            "invalid_parameters",
            "workspace_port must be an integer between 1 and 65535",
        )
    return int(value)


def _require_safe_profile_root(profile_root: Path) -> None:
    if profile_root == Path(profile_root.anchor):
        raise DesktopServiceError(
            "unsafe_profile_path",
            "the filesystem root cannot be used as an OSCA profile",
        )
    if not profile_root.parent.is_dir():
        raise DesktopServiceError(
            "unsafe_profile_path",
            f"profile parent directory does not exist: {profile_root.parent}",
        )
    if not os.access(profile_root.parent, os.W_OK):
        raise DesktopServiceError(
            "unsafe_profile_path",
            f"profile parent directory is not writable: {profile_root.parent}",
        )


def _require_safe_new_profile_target(profile_root: Path) -> None:
    if profile_root.exists() and not profile_root.is_dir():
        raise DesktopServiceError(
            "unsafe_profile_target",
            f"profile target is not a directory: {profile_root}",
        )
    if profile_root.exists() and any(profile_root.iterdir()):
        raise DesktopServiceError(
            "unsafe_profile_target",
            "profile target must be new or empty; existing content was left unchanged",
        )


def _restore_pre_creation_target(profile_root: Path, *, existed: bool) -> None:
    if not profile_root.exists():
        return
    if not existed:
        shutil.rmtree(profile_root, ignore_errors=True)
        return
    for child in tuple(profile_root.iterdir()):
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child, ignore_errors=True)
        else:
            child.unlink(missing_ok=True)


def _disclosures() -> dict[str, str]:
    return {
        "research_only": "OSCA is research and simulation software, not financial advice.",
        "local_storage": "Profiles and imported data are stored locally on this machine.",
        "optional_network": "Network access is optional and must be enabled explicitly.",
        "providers": "No provider account is required for the bundled synthetic sample.",
        "credentials": "D2 does not request, store, or materialize provider credentials.",
        "recommendations": "Recommendation generation is unavailable in D2.",
        "live_execution": "Broker, exchange, autonomous, and real-capital execution are disabled.",
    }


def _capabilities() -> dict[str, bool]:
    return {
        "profile_management": True,
        "bundled_sample_import": True,
        "system_diagnostics": True,
        "provider_setup": False,
        "provider_acquisition": False,
        "credential_management": False,
        "recommendations": False,
        "broker_connectivity": False,
        "exchange_connectivity": False,
        "autonomous_execution": False,
        "live_order_execution": False,
    }
