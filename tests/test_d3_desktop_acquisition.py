from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from osca.desktop_api.contracts import DesktopRequest, DesktopResponse
from osca.desktop_api.d3_acquisition_service import D3AcquisitionApplicationService
from osca.production_ingestion.contracts import ProductionIngestionRequest
from osca.security.infrastructure import InMemoryVault


def _payload(*, errors: list[str] | None = None) -> bytes:
    return json.dumps(
        {
            "error": errors or [],
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


def _request(
    service: D3AcquisitionApplicationService,
    method: str,
    params: dict[str, Any] | None = None,
) -> DesktopResponse:
    return service.handle(
        DesktopRequest(
            request_id=f"test-{method}",
            method=method,
            params=params or {},
        )
    )


def _create_profile(service: D3AcquisitionApplicationService, root: Path) -> None:
    root.parent.mkdir(parents=True, exist_ok=True)
    response = _request(service, "profile.create", {"profile_root": str(root)})
    assert response.status == "ok", response.error


def _params(root: Path, **updates: Any) -> dict[str, Any]:
    values: dict[str, Any] = {
        "profile_root": str(root),
        "provider_id": "kraken",
        "asset_class": "crypto",
        "symbol": "XBTUSD",
        "timeframe": "1d",
        "expected_pair_key": "XXBTZUSD",
        "network_access_enabled": True,
    }
    values.update(updates)
    return values


def test_kraken_acquisition_returns_retained_evidence_and_reuses_result(
    tmp_path: Path,
) -> None:
    calls = 0

    def transport(_: ProductionIngestionRequest) -> bytes:
        nonlocal calls
        calls += 1
        return _payload()

    profile = tmp_path / "profiles" / "kraken"
    service = D3AcquisitionApplicationService(
        state_root=tmp_path / "state",
        secret_vault=InMemoryVault(),
        acquisition_transport=transport,
    )
    _create_profile(service, profile)

    first = _request(service, "acquisition.run", _params(profile))
    second = _request(service, "acquisition.run", _params(profile))

    assert first.status == "ok", first.error
    assert second.status == "ok", second.error
    assert first.result is not None
    assert second.result is not None
    assert first.result["execution_model"] == "synchronous-sidecar-request"
    assert first.result["live_progress_available"] is False
    assert first.result["cancellation_mode"] == "pre-network-request-only"
    assert first.result["credential_required"] is False
    evidence = first.result["evidence"]
    assert evidence["status"] == "succeeded"
    assert evidence["job_status"] == "succeeded"
    assert evidence["provider_id"] == "kraken"
    assert evidence["provider_pair_key"] == "XXBTZUSD"
    assert evidence["canonical_row_count"] == 2
    assert evidence["dataset_revision_id"]
    assert evidence["raw_payload_uri"]
    assert evidence["job_evidence_uri"]
    assert evidence["redistribution_enabled"] is False
    assert evidence["recommendations_enabled"] is False
    assert evidence["broker_execution_enabled"] is False
    assert evidence["real_capital_execution_enabled"] is False
    assert second.result["evidence"]["reuse_state"] == "reused"
    assert second.result["evidence"]["dataset_revision_id"] == evidence["dataset_revision_id"]
    assert calls == 1


def test_network_consent_is_required_and_transport_is_not_called(tmp_path: Path) -> None:
    calls = 0

    def transport(_: ProductionIngestionRequest) -> bytes:
        nonlocal calls
        calls += 1
        return _payload()

    profile = tmp_path / "profiles" / "blocked"
    service = D3AcquisitionApplicationService(
        state_root=tmp_path / "state",
        secret_vault=InMemoryVault(),
        acquisition_transport=transport,
    )
    _create_profile(service, profile)

    response = _request(
        service,
        "acquisition.run",
        _params(profile, network_access_enabled=False),
    )

    assert response.status == "ok", response.error
    assert response.result is not None
    evidence = response.result["evidence"]
    assert evidence["status"] == "policy_blocked"
    assert "network-access-not-enabled" in evidence["findings"]
    assert evidence["dataset_revision_id"] is None
    assert calls == 0


def test_pre_network_cancellation_is_honest_and_offline(tmp_path: Path) -> None:
    profile = tmp_path / "profiles" / "cancelled"
    service = D3AcquisitionApplicationService(
        state_root=tmp_path / "state",
        secret_vault=InMemoryVault(),
        acquisition_transport=lambda _: (_ for _ in ()).throw(AssertionError("network used")),
    )
    _create_profile(service, profile)

    response = _request(
        service,
        "acquisition.run",
        _params(profile, network_access_enabled=False, cancel_requested=True),
    )

    assert response.status == "ok", response.error
    assert response.result is not None
    evidence = response.result["evidence"]
    assert evidence["status"] == "cancelled"
    assert evidence["job_status"] == "cancelled"
    assert "cancelled-before-network" in evidence["findings"]


def test_quota_and_corrupt_outcomes_remain_distinct(tmp_path: Path) -> None:
    quota_profile = tmp_path / "profiles" / "quota"
    quota = D3AcquisitionApplicationService(
        state_root=tmp_path / "quota-state",
        secret_vault=InMemoryVault(),
        acquisition_transport=lambda _: _payload(errors=["EAPI:Rate limit exceeded"]),
    )
    _create_profile(quota, quota_profile)
    quota_response = _request(quota, "acquisition.run", _params(quota_profile))

    corrupt_profile = tmp_path / "profiles" / "corrupt"
    corrupt = D3AcquisitionApplicationService(
        state_root=tmp_path / "corrupt-state",
        secret_vault=InMemoryVault(),
        acquisition_transport=lambda _: b"not-json",
    )
    _create_profile(corrupt, corrupt_profile)
    corrupt_response = _request(corrupt, "acquisition.run", _params(corrupt_profile))

    assert quota_response.result is not None
    assert quota_response.result["evidence"]["status"] == "quota_blocked"
    assert quota_response.result["evidence"]["retry_after_seconds"] == 60
    assert corrupt_response.result is not None
    assert corrupt_response.result["evidence"]["status"] == "corrupt"


def test_non_kraken_and_non_crypto_requests_fail_before_network(tmp_path: Path) -> None:
    profile = tmp_path / "profiles" / "unsupported"
    service = D3AcquisitionApplicationService(
        state_root=tmp_path / "state",
        secret_vault=InMemoryVault(),
        acquisition_transport=lambda _: (_ for _ in ()).throw(AssertionError("network used")),
    )
    _create_profile(service, profile)

    provider = _request(
        service,
        "acquisition.run",
        _params(profile, provider_id="twelve_data"),
    )
    asset = _request(
        service,
        "acquisition.run",
        _params(profile, asset_class="equity"),
    )

    assert provider.status == "error"
    assert provider.error is not None
    assert provider.error.code == "provider_not_supported"
    assert asset.status == "error"
    assert asset.error is not None
    assert asset.error.code == "provider_not_supported"
