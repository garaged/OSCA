"""Authoritative application-service boundary used by desktop adapters."""

from collections.abc import Callable
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from osca.desktop_api.contracts import DesktopError, DesktopRequest, DesktopResponse

Handler = Callable[[dict[str, Any]], dict[str, Any]]


class DesktopApplicationService:
    """Dispatch a deliberately small allow-listed desktop command surface."""

    def __init__(self, *, storage_root: Path | None = None) -> None:
        self._storage_root = storage_root
        self._handlers: dict[str, Handler] = {
            "system.health": self._system_health,
            "profile.inspect": self._profile_inspect,
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
        except (OSError, ValueError) as exc:
            return DesktopResponse(
                request_id=request.request_id,
                status="error",
                error=DesktopError(code="application_error", message=str(exc)),
            )
        return DesktopResponse(request_id=request.request_id, status="ok", result=result)

    def _system_health(self, params: dict[str, Any]) -> dict[str, Any]:
        if params:
            raise ValueError("system.health does not accept parameters")
        try:
            package_version = version("osca")
        except PackageNotFoundError:
            package_version = "development"
        return {
            "service": "osca-desktop-api",
            "status": "ready",
            "protocol_version": "1.0",
            "package_version": package_version,
            "live_order_execution": False,
        }

    def _profile_inspect(self, params: dict[str, Any]) -> dict[str, Any]:
        if params:
            raise ValueError("profile.inspect does not accept parameters")
        root = self._storage_root
        return {
            "configured": root is not None,
            "storage_root": str(root) if root is not None else None,
            "exists": root.exists() if root is not None else False,
            "writable": root.is_dir() if root is not None and root.exists() else False,
        }
