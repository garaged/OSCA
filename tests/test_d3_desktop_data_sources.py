from __future__ import annotations

from pathlib import Path
from typing import Any

from osca.desktop_api.contracts import DesktopRequest, DesktopResponse
from osca.desktop_api.d3_service import D3DesktopApplicationService
from osca.security.api import SecretReference
from osca.security.infrastructure import InMemoryVault


def _request(
    service: D3DesktopApplicationService,
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


def test_provider_catalog_reflects_policy_and_preserves_free_paths(tmp_path: Path) -> None:
    service = D3DesktopApplicationService(
        state_root=tmp_path / "state",
        secret_vault=InMemoryVault(),
    )

    response = _request(service, "provider.catalog")

    assert response.status == "ok", response.error
    assert response.result is not None
    providers = {row["provider_id"]: row for row in response.result["providers"]}

    kraken = providers["kraken"]
    assert kraken["admission_status"] == "approved"
    assert kraken["credential_mode"] == "public-no-key"
    assert kraken["credential_state"] == "not_required"
    assert kraken["d3_acquisition_resources"] == ["spot_ohlc"]
    assert kraken["acquisition_available"] is True
    assert kraken["network_required"] is True
    assert kraken["internal_use_only"] is True
    assert kraken["redistribution_enabled"] is False

    twelve_data = providers["twelve_data"]
    assert twelve_data["admission_status"] == "needs_evidence"
    assert twelve_data["credential_state"] == "missing"
    assert twelve_data["acquisition_available"] is False
    assert twelve_data["promotion_automatic"] is False
    assert "credential.store" in twelve_data["available_actions"]
    assert "acquisition.submit" not in twelve_data["available_actions"]

    assert providers["fred"]["admission_status"] == "policy_blocked"
    assert response.result["provider_promotion_automatic"] is False
    assert response.result["network_access_enabled"] is False
    assert response.result["recommendations_enabled"] is False
    assert response.result["live_execution_enabled"] is False
    assert all(
        path["network_required"] is False
        and path["credential_required"] is False
        and path["available"] is True
        for path in response.result["offline_paths"]
    )


def test_credential_lifecycle_never_returns_secret_or_promotes_provider(
    tmp_path: Path,
) -> None:
    vault = InMemoryVault()
    service = D3DesktopApplicationService(
        state_root=tmp_path / "state",
        secret_vault=vault,
    )
    secret = "d3-disposable-super-secret"

    stored = _request(
        service,
        "credential.store",
        {"provider_id": "twelve_data", "secret_value": secret},
    )

    assert stored.status == "ok", stored.error
    assert stored.result is not None
    assert stored.result["operation"] == "stored"
    assert stored.result["state"] == "available"
    assert stored.result["reference"] == "vault://provider/twelve_data/api-key"
    assert stored.result["admission_status"] == "needs_evidence"
    assert stored.result["approved_resources"] == []
    assert stored.result["acquisition_available"] is False
    assert stored.result["provider_promotion_automatic"] is False
    assert stored.result["secret_value_returned"] is False
    assert secret not in stored.model_dump_json()
    assert (
        vault.resolve(SecretReference(namespace="provider", name="twelve_data/api-key"))
        == secret
    )

    catalog = _request(service, "provider.catalog")
    assert catalog.result is not None
    twelve_data = next(
        row for row in catalog.result["providers"] if row["provider_id"] == "twelve_data"
    )
    assert twelve_data["credential_state"] == "available"
    assert twelve_data["admission_status"] == "needs_evidence"
    assert twelve_data["acquisition_available"] is False
    assert secret not in catalog.model_dump_json()

    probed = _request(
        service,
        "credential.probe",
        {"provider_id": "twelve_data"},
    )
    assert probed.status == "ok"
    assert probed.result is not None
    assert probed.result["state"] == "available"
    assert secret not in probed.model_dump_json()

    deleted = _request(
        service,
        "credential.delete",
        {"provider_id": "twelve_data"},
    )
    assert deleted.status == "ok"
    assert deleted.result is not None
    assert deleted.result["deleted"] is True
    assert deleted.result["state"] == "missing"
    assert deleted.result["admission_status"] == "needs_evidence"
    assert secret not in deleted.model_dump_json()


def test_public_no_key_provider_rejects_credential_without_echoing_value(
    tmp_path: Path,
) -> None:
    secret = "must-not-echo"
    service = D3DesktopApplicationService(
        state_root=tmp_path / "state",
        secret_vault=InMemoryVault(),
    )

    response = _request(
        service,
        "credential.store",
        {"provider_id": "kraken", "secret_value": secret},
    )

    assert response.status == "error"
    assert response.error is not None
    assert response.error.code == "credential_not_required"
    assert secret not in response.model_dump_json()


def test_unknown_provider_and_empty_secret_fail_with_stable_safe_codes(tmp_path: Path) -> None:
    service = D3DesktopApplicationService(
        state_root=tmp_path / "state",
        secret_vault=InMemoryVault(),
    )

    unknown = _request(
        service,
        "credential.probe",
        {"provider_id": "unknown-provider"},
    )
    empty = _request(
        service,
        "credential.store",
        {"provider_id": "twelve_data", "secret_value": ""},
    )

    assert unknown.status == "error"
    assert unknown.error is not None
    assert unknown.error.code == "provider_not_found"
    assert empty.status == "error"
    assert empty.error is not None
    assert empty.error.code == "invalid_parameters"


class _UnavailableVault:
    def store(self, reference: SecretReference, value: str) -> None:
        raise OSError("backend detail must not escape")

    def resolve(self, reference: SecretReference) -> str | None:
        raise OSError("backend detail must not escape")

    def delete(self, reference: SecretReference) -> bool:
        raise OSError("backend detail must not escape")


def test_unavailable_vault_fails_closed_without_plaintext_fallback(tmp_path: Path) -> None:
    service = D3DesktopApplicationService(
        state_root=tmp_path / "state",
        secret_vault=_UnavailableVault(),
    )
    secret = "not-persisted-anywhere"

    catalog = _request(service, "provider.catalog")
    stored = _request(
        service,
        "credential.store",
        {"provider_id": "twelve_data", "secret_value": secret},
    )

    assert catalog.status == "ok"
    assert catalog.result is not None
    twelve_data = next(
        row for row in catalog.result["providers"] if row["provider_id"] == "twelve_data"
    )
    assert twelve_data["credential_state"] == "unavailable"
    assert stored.status == "error"
    assert stored.error is not None
    assert stored.error.code == "vault_unavailable"
    assert stored.error.retryable is True
    assert "backend detail" not in stored.model_dump_json()
    assert secret not in stored.model_dump_json()
    assert not tuple(tmp_path.rglob("*secret*"))
