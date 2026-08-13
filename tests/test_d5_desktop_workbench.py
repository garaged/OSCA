from __future__ import annotations

import json
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


def test_workbench_export_is_full_resolution_when_display_is_downsampled(
    tmp_path: Path,
) -> None:
    service, profile_root = _profile_with_sample(tmp_path)
    response = _call(
        service,
        "workbench.export.prepare",
        {
            "profile_root": str(profile_root),
            "asset_id": "equity:XNAS:AAPL",
            "timeframe": "1d",
            "max_rows": 2,
            "derived": [{"kind": "sma", "window": 3}],
        },
    )

    assert response.status == "ok"
    assert response.result is not None
    assert response.result["full_resolution"] is True
    assert response.result["display_downsampling_was_active"] is True
    assert response.result["row_count"] > 2
    csv_path = Path(response.result["csv_path"])
    metadata_path = Path(response.result["metadata_path"])
    assert profile_root in csv_path.parents
    assert csv_path.is_file()
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["full_resolution_row_count"] == response.result["row_count"]
    assert metadata["display_rows_exported"] is False
    assert metadata["requested_series"] == [{"kind": "sma", "window": 3}]


def test_saved_workbench_view_lifecycle_survives_service_restart(tmp_path: Path) -> None:
    service, profile_root = _profile_with_sample(tmp_path)
    config = {
        "primary_asset_id": "equity:XNAS:AAPL",
        "timeframe": "1d",
        "max_rows": 500,
        "derived": [{"kind": "sma", "window": 20}],
        "layout": {"volume_visible": True},
    }
    created = _call(
        service,
        "workbench.view.create",
        {
            "profile_root": str(profile_root),
            "name": "Daily research",
            "description": "Local daily workbench",
            "config": config,
        },
    )
    assert created.status == "ok"
    assert created.result is not None
    view_id = created.result["view"]["view_id"]

    restarted = D5DesktopApplicationService(state_root=tmp_path / "state-restarted")
    listed = _call(restarted, "workbench.view.list", {"profile_root": str(profile_root)})
    assert listed.status == "ok"
    assert listed.result is not None
    assert [view["name"] for view in listed.result["views"]] == ["Daily research"]

    renamed = _call(
        restarted,
        "workbench.view.rename",
        {
            "profile_root": str(profile_root),
            "view_id": view_id,
            "name": "Daily chart",
        },
    )
    assert renamed.status == "ok"
    updated = _call(
        restarted,
        "workbench.view.update",
        {
            "profile_root": str(profile_root),
            "view_id": view_id,
            "description": None,
            "config": {**config, "max_rows": 250},
        },
    )
    assert updated.status == "ok"
    assert updated.result is not None
    assert updated.result["view"]["config"]["max_rows"] == 250

    deleted = _call(
        restarted,
        "workbench.view.delete",
        {"profile_root": str(profile_root), "view_id": view_id},
    )
    assert deleted.status == "ok"
    empty = _call(restarted, "workbench.view.list", {"profile_root": str(profile_root)})
    assert empty.result is not None
    assert empty.result["views"] == []


def test_saved_workbench_views_are_profile_scoped_and_reject_secret_fields(
    tmp_path: Path,
) -> None:
    service, first = _profile_with_sample(tmp_path / "first")
    second = tmp_path / "second" / "profile"
    assert _call(service, "profile.create", {"profile_root": str(second)}).status == "ok"

    rejected = _call(
        service,
        "workbench.view.create",
        {
            "profile_root": str(first),
            "name": "Unsafe",
            "description": None,
            "config": {"primary_asset_id": "equity:XNAS:AAPL", "api_key": "nope"},
        },
    )
    assert rejected.status == "error"
    assert rejected.error is not None
    assert rejected.error.code == "invalid_parameters"

    created = _call(
        service,
        "workbench.view.create",
        {
            "profile_root": str(first),
            "name": "Safe",
            "description": None,
            "config": {"primary_asset_id": "equity:XNAS:AAPL", "timeframe": "1d"},
        },
    )
    assert created.status == "ok"
    other = _call(service, "workbench.view.list", {"profile_root": str(second)})
    assert other.result is not None
    assert other.result["views"] == []


def test_saved_workbench_view_rejects_newer_schema(tmp_path: Path) -> None:
    service, profile_root = _profile_with_sample(tmp_path)
    assert _call(service, "workbench.view.list", {"profile_root": str(profile_root)}).status == "ok"
    database = profile_root / ".osca" / "desktop" / "d5-workbench.sqlite3"
    with sqlite3.connect(database) as connection:
        connection.execute("PRAGMA user_version=99")

    response = _call(service, "workbench.view.list", {"profile_root": str(profile_root)})
    assert response.status == "error"
    assert response.error is not None
    assert response.error.code == "workbench_schema_newer"
