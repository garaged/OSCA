from __future__ import annotations

from pathlib import Path
from typing import Any

from osca.desktop_api.contracts import DesktopRequest, DesktopResponse
from osca.desktop_api.d3_service import D3DesktopApplicationService
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


def _create_profile(service: D3DesktopApplicationService, profile_root: Path) -> None:
    profile_root.parent.mkdir(parents=True, exist_ok=True)
    response = _request(
        service,
        "profile.create",
        {"profile_root": str(profile_root)},
    )
    assert response.status == "ok", response.error


def _write_valid_csv(path: Path) -> None:
    path.write_text(
        "timestamp,open,high,low,close,volume\n"
        "2026-01-01T00:00:00+00:00,100,105,99,103,1000\n"
        "2026-01-02T00:00:00+00:00,103,108,102,107,1200\n",
        encoding="utf-8",
    )


def test_local_csv_import_is_offline_governed_and_idempotent(tmp_path: Path) -> None:
    profile_root = tmp_path / "profiles" / "local-import"
    source = tmp_path / "evidence.csv"
    _write_valid_csv(source)
    service = D3DesktopApplicationService(
        state_root=tmp_path / "state",
        secret_vault=InMemoryVault(),
    )
    _create_profile(service, profile_root)
    params = {
        "profile_root": str(profile_root),
        "input_path": str(source),
        "symbol": "TEST-EQUITY",
        "timeframe": "1d",
        "source_uri": "local-file://d3-manual-evidence",
        "calendar_assumption": "weekday-session-fixture",
        "revision_salt": "d3-import-test-v1",
    }

    first = _request(service, "local.import", params)
    second = _request(service, "local.import", params)

    assert first.status == "ok", first.error
    assert second.status == "ok", second.error
    assert first.result is not None
    assert second.result is not None
    assert first.result["network_access_enabled"] is False
    assert first.result["credential_required"] is False
    assert first.result["provider_account_required"] is False
    imported = first.result["import"]
    assert imported["symbol"] == "TEST-EQUITY"
    assert imported["timeframe"] == "1d"
    assert imported["row_count"] == 2
    assert imported["network_access_enabled"] is False
    assert imported["calendar_assumption"] == "weekday-session-fixture"
    assert imported["dataset_revision_id"] == second.result["import"]["dataset_revision_id"]
    assert Path(imported["payload_uri"]).is_file()
    assert Path(imported["metadata_uri"]).is_file()


def test_local_import_trims_pasted_absolute_paths(tmp_path: Path) -> None:
    profile_root = tmp_path / "profiles" / "pasted-path"
    source = tmp_path / "evidence.csv"
    _write_valid_csv(source)
    service = D3DesktopApplicationService(
        state_root=tmp_path / "state",
        secret_vault=InMemoryVault(),
    )
    _create_profile(service, profile_root)

    response = _request(
        service,
        "local.import",
        {
            "profile_root": str(profile_root),
            "input_path": f"  {source}  ",
            "symbol": "TEST-EQUITY",
            "timeframe": "1d",
        },
    )

    assert response.status == "ok", response.error
    assert response.result is not None
    assert response.result["import"]["row_count"] == 2


def test_local_import_rejects_hidden_network_parameter(tmp_path: Path) -> None:
    profile_root = tmp_path / "profiles" / "network-rejected"
    source = tmp_path / "evidence.csv"
    _write_valid_csv(source)
    service = D3DesktopApplicationService(
        state_root=tmp_path / "state",
        secret_vault=InMemoryVault(),
    )
    _create_profile(service, profile_root)

    response = _request(
        service,
        "local.import",
        {
            "profile_root": str(profile_root),
            "input_path": str(source),
            "symbol": "TEST",
            "timeframe": "1d",
            "network_access_enabled": True,
        },
    )

    assert response.status == "error"
    assert response.error is not None
    assert response.error.code == "invalid_parameters"


def test_local_import_rejects_relative_or_missing_sources(tmp_path: Path) -> None:
    profile_root = tmp_path / "profiles" / "invalid-source"
    service = D3DesktopApplicationService(
        state_root=tmp_path / "state",
        secret_vault=InMemoryVault(),
    )
    _create_profile(service, profile_root)

    relative = _request(
        service,
        "local.import",
        {
            "profile_root": str(profile_root),
            "input_path": "relative.csv",
            "symbol": "TEST",
            "timeframe": "1d",
        },
    )
    missing = _request(
        service,
        "local.import",
        {
            "profile_root": str(profile_root),
            "input_path": str(tmp_path / "missing.csv"),
            "symbol": "TEST",
            "timeframe": "1d",
        },
    )

    assert relative.status == "error"
    assert relative.error is not None
    assert relative.error.code == "invalid_parameters"
    assert missing.status == "error"
    assert missing.error is not None
    assert missing.error.code == "local_import_source_missing"


def test_malformed_local_import_fails_without_dataset_success(tmp_path: Path) -> None:
    profile_root = tmp_path / "profiles" / "malformed"
    source = tmp_path / "malformed.csv"
    source.write_text("timestamp,open\nnot-a-time,broken\n", encoding="utf-8")
    service = D3DesktopApplicationService(
        state_root=tmp_path / "state",
        secret_vault=InMemoryVault(),
    )
    _create_profile(service, profile_root)

    response = _request(
        service,
        "local.import",
        {
            "profile_root": str(profile_root),
            "input_path": str(source),
            "symbol": "TEST",
            "timeframe": "1d",
        },
    )

    assert response.status == "error"
    assert response.error is not None
    assert response.error.code == "local_import_failed"
    assert response.result is None
