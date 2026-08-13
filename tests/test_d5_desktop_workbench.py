from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from osca.desktop_api.contracts import DesktopRequest, DesktopResponse
from osca.desktop_api.d5_service import D5DesktopApplicationService
from osca.operator_experience import load_operator_config


def _call(
    service: D5DesktopApplicationService,
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


def _profile_with_sample(
    tmp_path: Path,
) -> tuple[D5DesktopApplicationService, Path]:
    service = D5DesktopApplicationService(state_root=tmp_path / "state")
    profile_root = tmp_path / "profile"
    created = _call(service, "profile.create", {"profile_root": str(profile_root)})
    assert created.status == "ok"
    imported = _call(service, "sample.import", {"profile_root": str(profile_root)})
    assert imported.status == "ok"
    return service, profile_root


def test_workbench_series_resolves_governed_sample_without_client_path(
    tmp_path: Path,
) -> None:
    service, profile_root = _profile_with_sample(tmp_path)

    response = _call(
        service,
        "workbench.series.get",
        {
            "profile_root": str(profile_root),
            "asset_id": "equity:XNAS:AAPL",
            "timeframe": "1d",
            "max_rows": 5,
            "derived": [{"kind": "sma", "window": 3}],
        },
    )

    assert response.status == "ok"
    assert response.result is not None
    assert response.result["asset_id"] == "equity:XNAS:AAPL"
    assert response.result["dataset"]["symbol"] == "AAPL-SYNTHETIC"
    assert response.result["dataset"]["source_kind"] == "local-import"
    assert response.result["network_access_enabled"] is False
    assert response.result["real_capital_execution_enabled"] is False
    series = response.result["series"]
    assert "payload_path" not in series
    assert series["returned_row_count"] <= 5
    assert series["derived_evidence"][0]["series_id"] == "sma_3"
    assert series["derived_evidence"][0]["point_in_time_safe"] is True


def test_workbench_series_rejects_arbitrary_payload_path(tmp_path: Path) -> None:
    service, profile_root = _profile_with_sample(tmp_path)

    response = _call(
        service,
        "workbench.series.get",
        {
            "profile_root": str(profile_root),
            "asset_id": "equity:XNAS:AAPL",
            "timeframe": "1d",
            "payload_path": str(tmp_path / "attacker.parquet"),
        },
    )

    assert response.status == "error"
    assert response.error is not None
    assert response.error.code == "invalid_parameters"


def test_workbench_series_reports_missing_governed_data(tmp_path: Path) -> None:
    service = D5DesktopApplicationService(state_root=tmp_path / "state")
    profile_root = tmp_path / "profile"
    assert _call(
        service,
        "profile.create",
        {"profile_root": str(profile_root)},
    ).status == "ok"

    response = _call(
        service,
        "workbench.series.get",
        {
            "profile_root": str(profile_root),
            "asset_id": "crypto:KRAKEN:XBTUSD",
            "timeframe": "1d",
        },
    )

    assert response.status == "error"
    assert response.error is not None
    assert response.error.code == "workbench_data_unavailable"


def test_workbench_series_ignores_metadata_payload_outside_storage_root(
    tmp_path: Path,
) -> None:
    service, profile_root = _profile_with_sample(tmp_path)
    storage_root = Path(load_operator_config(profile_root).storage_root)
    metadata_path = storage_root / "osca-local-data.sqlite"
    outside = tmp_path / "outside.parquet"
    outside.write_bytes(b"not governed")
    with sqlite3.connect(metadata_path) as connection:
        connection.execute(
            "UPDATE local_ohlcv_imports SET payload_uri = ?",
            (str(outside),),
        )

    response = _call(
        service,
        "workbench.series.get",
        {
            "profile_root": str(profile_root),
            "asset_id": "equity:XNAS:AAPL",
            "timeframe": "1d",
        },
    )

    assert response.status == "error"
    assert response.error is not None
    assert response.error.code == "workbench_data_unavailable"
