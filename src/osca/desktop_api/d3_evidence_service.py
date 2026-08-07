"""D3 retained acquisition inspection service."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from osca.desktop_api.acquisition_evidence import list_retained_acquisitions
from osca.desktop_api.d3_acquisition_service import D3AcquisitionApplicationService
from osca.desktop_api.service import DesktopServiceError
from osca.operator_experience import load_operator_config
from osca.production_ingestion.services import Transport
from osca.security.application.ports import SecretVault


class D3EvidenceApplicationService(D3AcquisitionApplicationService):
    """Add bounded profile-derived retained evidence inspection."""

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
            acquisition_transport=acquisition_transport,
        )
        self._handlers["acquisition.list"] = self._acquisition_list

    def _acquisition_list(self, params: dict[str, Any]) -> dict[str, Any]:
        unexpected = sorted(set(params) - {"profile_root", "limit"})
        if unexpected:
            raise DesktopServiceError(
                "invalid_parameters",
                "acquisition.list received unsupported parameters: "
                + ", ".join(unexpected),
            )
        value = params.get("profile_root")
        if not isinstance(value, str) or not value.strip() or len(value) > 4096:
            raise DesktopServiceError(
                "invalid_parameters", "profile_root must be a valid path"
            )
        profile_root = Path(value).expanduser()
        if not profile_root.is_absolute():
            raise DesktopServiceError(
                "invalid_parameters", "profile_root must be an absolute path"
            )
        profile_root = profile_root.resolve()
        if not self._inspect_profile(profile_root)["can_open"]:
            raise DesktopServiceError(
                "profile_unavailable",
                "a compatible writable profile is required before inspecting acquisitions",
            )
        limit_value = params.get("limit", 50)
        if (
            isinstance(limit_value, bool)
            or not isinstance(limit_value, int)
            or not 1 <= limit_value <= 100
        ):
            raise DesktopServiceError(
                "invalid_parameters", "limit must be an integer from 1 through 100"
            )
        config = load_operator_config(profile_root)
        return list_retained_acquisitions(Path(config.storage_root), limit=limit_value)
