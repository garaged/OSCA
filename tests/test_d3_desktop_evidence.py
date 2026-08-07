from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from osca.desktop_api.contracts import DesktopRequest, DesktopResponse
from osca.desktop_api.d3_evidence_service import D3EvidenceApplicationService
from osca.production_ingestion.contracts import ProductionIngestionRequest
from osca.security.infrastructure import InMemoryVault


def _call(
    service: D3EvidenceApplicationService,
    method: str,
    params: dict[str, Any],
) -> DesktopResponse:
    return service.handle(
        DesktopRequest(request_id=f"test-{method}", method=method, params=params)
    )


def _payload(_: ProductionIngestionRequest) -> bytes:
    return json.dumps(
        {
            "error": [],
            "result": {
                "XXBTZUSD": [
                    [1722384000, "66000", "67000", "65000", "66500", "66300", "10", 50],
                    [1722470400, "66500", "68000", "66000", "67500", "67100", "12", 55],
                    [1722556800, "67500", "68200", "67000", "67800", "67700", "4", 20],
                ],
                "last": 1722556800,
            },
        }
    ).encode()


def test_retained_acquisition_list_survives_service_restart(tmp_path: Path) -> None:
    profile = tmp_path / "profiles" / "retained"
    state = tmp_path / "state"
    first = D3EvidenceApplicationService(
        state_root=state,
        secret_vault=InMemoryVault(),
        acquisition_transport=_payload,
    )
    profile.parent.mkdir(parents=True)
    created = _call(first, "profile.create", {"profile_root": str(profile)})
    assert created.status == "ok", created.error
    acquired = _call(
        first,
        "acquisition.run",
        {
            "profile_root": str(profile),
            "provider_id": "kraken",
            "asset_class": "crypto",
            "symbol": "XBTUSD",
            "timeframe": "1d",
            "expected_pair_key": "XXBTZUSD",
            "network_access_enabled": True,
        },
    )
    assert acquired.status == "ok", acquired.error
    assert acquired.result is not None

    restarted = D3EvidenceApplicationService(
        state_root=state,
        secret_vault=InMemoryVault(),
        acquisition_transport=lambda _: (_ for _ in ()).throw(AssertionError("network used")),
    )
    listed = _call(
        restarted,
        "acquisition.list",
        {"profile_root": str(profile), "limit": 10},
    )

    assert listed.status == "ok", listed.error
    assert listed.result is not None
    assert listed.result["invalid_evidence_count"] == 0
    assert len(listed.result["acquisitions"]) == 1
    retained = listed.result["acquisitions"][0]
    assert retained["status"] == "succeeded"
    assert retained["dataset_revision_id"] == acquired.result["evidence"]["dataset_revision_id"]


def test_acquisition_list_rejects_arbitrary_or_invalid_scope(tmp_path: Path) -> None:
    service = D3EvidenceApplicationService(
        state_root=tmp_path / "state",
        secret_vault=InMemoryVault(),
    )

    relative = _call(
        service,
        "acquisition.list",
        {"profile_root": "relative-profile"},
    )
    invalid_limit = _call(
        service,
        "acquisition.list",
        {"profile_root": str(tmp_path / "missing"), "limit": 1000},
    )

    assert relative.status == "error"
    assert relative.error is not None
    assert relative.error.code == "invalid_parameters"
    assert invalid_limit.status == "error"
    assert invalid_limit.error is not None
    assert invalid_limit.error.code in {"profile_unavailable", "invalid_parameters"}
