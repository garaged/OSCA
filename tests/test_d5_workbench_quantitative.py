from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from osca.desktop_api.contracts import DesktopRequest, DesktopResponse
from osca.desktop_api.d5_service import D5DesktopApplicationService


def _call(
    service: D5DesktopApplicationService,
    method: str,
    params: dict[str, Any],
) -> DesktopResponse:
    return service.handle(
        DesktopRequest(
            request_id=f"test-{method}",
            method=method,
            params=params,
        )
    )


def _sample_service(tmp_path: Path) -> tuple[D5DesktopApplicationService, Path]:
    service = D5DesktopApplicationService(state_root=tmp_path / "state")
    profile_root = tmp_path / "profile"
    assert _call(
        service,
        "profile.create",
        {"profile_root": str(profile_root)},
    ).status == "ok"
    assert _call(
        service,
        "sample.import",
        {"profile_root": str(profile_root)},
    ).status == "ok"
    return service, profile_root


def _series_params(profile_root: Path) -> dict[str, Any]:
    return {
        "profile_root": str(profile_root),
        "asset_id": "equity:XNAS:AAPL",
        "timeframe": "1d",
    }


def test_workbench_range_is_applied_by_authoritative_series_service(tmp_path: Path) -> None:
    service, profile_root = _sample_service(tmp_path)
    full = _call(service, "workbench.series.get", _series_params(profile_root))
    assert full.status == "ok"
    assert full.result is not None
    rows = full.result["series"]["rows"]
    assert len(rows) >= 4

    start = rows[1]["timestamp"]
    end = rows[-2]["timestamp"]
    bounded = _call(
        service,
        "workbench.series.get",
        {
            **_series_params(profile_root),
            "start": start,
            "end": end,
        },
    )

    assert bounded.status == "ok"
    assert bounded.result is not None
    bounded_series = bounded.result["series"]
    assert bounded_series["first_timestamp"] == start
    assert bounded_series["last_timestamp"] == end
    assert bounded_series["filtered_row_count"] < full.result["series"]["filtered_row_count"]


def test_quantitative_analysis_is_python_authoritative_and_bounded(tmp_path: Path) -> None:
    service, profile_root = _sample_service(tmp_path)
    response = _call(
        service,
        "workbench.analysis.get",
        {
            **_series_params(profile_root),
            "max_rows": 5,
            "parameters": {
                "rsi_window": 3,
                "atr_window": 3,
                "bollinger_window": 3,
                "fast_window": 2,
                "slow_window": 4,
                "signal_window": 2,
            },
        },
    )

    assert response.status == "ok"
    assert response.result is not None
    result = response.result
    assert result["source_point_count"] > result["displayed_point_count"]
    assert result["displayed_point_count"] == 5
    assert result["display_method"] == "evenly_spaced"
    assert result["point_in_time_safe"] is True
    assert result["network_access_enabled"] is False
    assert result["recommendations_enabled"] is False
    assert result["broker_connections_enabled"] is False
    assert result["real_capital_execution_enabled"] is False
    assert result["summary"]["observation_count"] == result["source_point_count"]
    assert result["points"][-1]["trend_regime"] in {"uptrend", "downtrend", "flat", "warmup"}
    assert result["input_digest"]
    assert result["output_digest"]


def test_same_dataset_comparison_has_identity_statistics(tmp_path: Path) -> None:
    service, profile_root = _sample_service(tmp_path)
    response = _call(
        service,
        "workbench.comparison.get",
        {
            "profile_root": str(profile_root),
            "primary_asset_id": "equity:XNAS:AAPL",
            "comparison_asset_id": "equity:XNAS:AAPL",
            "timeframe": "1d",
            "rolling_window": 3,
            "max_rows": 5,
        },
    )

    assert response.status == "ok"
    assert response.result is not None
    result = response.result
    assert result["aligned_return_count"] > 0
    assert result["correlation"] == pytest.approx(1.0)
    assert result["beta"] == pytest.approx(1.0)
    assert result["normalization_basis"] == (
        "close-to-close simple returns aligned on exact shared timestamps"
    )
    assert result["point_in_time_safe"] is True
    assert result["network_access_enabled"] is False
    assert result["recommendations_enabled"] is False
    assert result["broker_connections_enabled"] is False
    assert result["real_capital_execution_enabled"] is False


def test_bundled_sample_pair_supports_compatible_comparison(tmp_path: Path) -> None:
    service, profile_root = _sample_service(tmp_path)
    response = _call(
        service,
        "workbench.comparison.get",
        {
            "profile_root": str(profile_root),
            "primary_asset_id": "equity:XNAS:AAPL",
            "comparison_asset_id": "equity:XNAS:MSFT",
            "timeframe": "1d",
            "rolling_window": 3,
            "max_rows": 5,
        },
    )

    assert response.status == "ok", response.error
    assert response.result is not None
    result = response.result
    assert result["primary"]["symbol"] == "AAPL-SYNTHETIC"
    assert result["comparison"]["symbol"] == "MSFT-SYNTHETIC"
    assert result["aligned_return_count"] > 0
    assert result["normalization_basis"] == (
        "close-to-close simple returns aligned on exact shared timestamps"
    )
    assert result["point_in_time_safe"] is True
    assert result["network_access_enabled"] is False
    assert result["recommendations_enabled"] is False
    assert result["broker_connections_enabled"] is False
    assert result["real_capital_execution_enabled"] is False


def test_comparison_rejects_incompatible_asset_semantics_before_dataset_join(
    tmp_path: Path,
) -> None:
    service, profile_root = _sample_service(tmp_path)
    response = _call(
        service,
        "workbench.comparison.get",
        {
            "profile_root": str(profile_root),
            "primary_asset_id": "equity:XNAS:AAPL",
            "comparison_asset_id": "crypto:KRAKEN:XBTUSD",
            "timeframe": "1d",
        },
    )

    assert response.status == "error"
    assert response.error is not None
    assert response.error.code == "workbench_comparison_incompatible"
    assert "matching asset-class and currency semantics" in response.error.message
