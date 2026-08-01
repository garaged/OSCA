from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from fastapi.testclient import TestClient

from osca.analyst_workspace.app import create_app
from osca.quantitative_analysis import (
    DatasetComparisonRequest,
    QuantitativeAnalysisRequest,
    analyze_dataset,
    compare_datasets,
)


def _payload(path: Path, closes: tuple[float, ...], *, shift_days: int = 0) -> Path:
    start = datetime(2026, 1, 1, tzinfo=UTC) + timedelta(days=shift_days)
    rows = []
    for index, close in enumerate(closes):
        rows.append(
            {
                "timestamp": start + timedelta(days=index),
                "open": close - 0.5,
                "high": close + 1.0,
                "low": close - 1.0,
                "close": close,
                "volume": 1_000.0 + index * 10.0,
            }
        )
    pq.write_table(pa.Table.from_pylist(rows), path)
    return path


def _request(path: Path, *, revision=None) -> QuantitativeAnalysisRequest:
    return QuantitativeAnalysisRequest(
        dataset_revision_id=revision or uuid4(),
        payload_path=path,
        symbol="TEST",
        timeframe="1d",
        periods_per_year=252,
        rsi_window=3,
        atr_window=3,
        bollinger_window=3,
        fast_window=2,
        slow_window=4,
        signal_window=2,
    )


def test_analysis_produces_point_in_time_series_and_summary(tmp_path: Path) -> None:
    path = _payload(tmp_path / "series.parquet", (100, 102, 101, 104, 108, 107, 110))
    result = analyze_dataset(_request(path))

    assert result.summary.observation_count == 7
    assert result.summary.return_count == 6
    assert result.summary.total_return == pytest.approx(0.10)
    assert result.points[0].simple_return is None
    assert result.points[1].simple_return == pytest.approx(0.02)
    assert result.points[2].cumulative_return == pytest.approx(0.01)
    assert result.points[0].rsi is None
    assert result.points[-1].atr is not None
    assert result.points[-1].bollinger_upper is not None
    assert result.points[-1].macd is not None
    assert result.points[-1].trend_regime in {"uptrend", "downtrend", "flat"}
    assert result.point_in_time_safe is True
    assert result.network_used is False
    assert result.recommendations_enabled is False
    assert result.real_capital_enabled is False
    assert result.input_digest != result.output_digest


def test_drawdown_and_descriptive_risk_are_explicit(tmp_path: Path) -> None:
    path = _payload(tmp_path / "risk.parquet", (100, 110, 99, 90, 95, 105))
    result = analyze_dataset(_request(path))

    assert result.summary.maximum_drawdown == pytest.approx(90 / 110 - 1)
    assert result.summary.maximum_drawdown_duration == 4
    assert result.summary.historical_var is not None
    assert result.summary.historical_cvar is not None
    assert any("descriptive empirical estimates" in item for item in result.assumptions)
    assert any("Small sample" in item for item in result.findings)


def test_comparison_aligns_exact_timestamps_without_fill(tmp_path: Path) -> None:
    primary_path = _payload(tmp_path / "primary.parquet", (100, 101, 103, 102, 106))
    benchmark_path = _payload(
        tmp_path / "benchmark.parquet",
        (200, 202, 204, 208, 210),
        shift_days=1,
    )
    comparison = compare_datasets(
        DatasetComparisonRequest(
            primary=_request(primary_path),
            benchmark=_request(benchmark_path),
            rolling_window=2,
        )
    )

    assert comparison.aligned_return_count == 3
    assert comparison.correlation is not None
    assert comparison.beta is not None
    assert comparison.points[0].rolling_correlation is None
    assert comparison.points[1].rolling_correlation is not None
    assert "exact shared timestamps" in comparison.assumptions[0]


def test_analysis_api_returns_governed_evidence(tmp_path: Path) -> None:
    revision = uuid4()
    path = _payload(tmp_path / "api.parquet", (100, 102, 104, 103, 107, 109))
    client = TestClient(create_app(storage_root=tmp_path))
    response = client.get(
        "/api/quantitative-analysis",
        params={
            "payload_path": str(path),
            "dataset_revision_id": str(revision),
            "symbol": "TEST",
            "timeframe": "1d",
            "rsi_window": 3,
            "atr_window": 3,
            "bollinger_window": 3,
            "fast_window": 2,
            "slow_window": 4,
            "signal_window": 2,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["dataset_revision_id"] == str(revision)
    assert body["summary"]["observation_count"] == 6
    assert body["network_used"] is False
    assert body["credentials_used"] is False
    assert body["broker_execution_enabled"] is False


def test_invalid_window_order_fails_closed(tmp_path: Path) -> None:
    path = _payload(tmp_path / "invalid.parquet", (100, 101, 102))
    with pytest.raises(ValueError, match="fast_window"):
        QuantitativeAnalysisRequest(
            dataset_revision_id=uuid4(),
            payload_path=path,
            symbol="TEST",
            timeframe="1d",
            fast_window=10,
            slow_window=5,
        )
