from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from pydantic import ValidationError

from osca.analytical_data import (
    ChartSeriesRequest,
    DerivedSeriesKind,
    DerivedSeriesRequest,
    DownsamplingMethod,
    build_chart_series,
)


def _payload(path: Path, count: int = 10) -> Path:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    rows = []
    for index in range(count):
        close = 100.0 + index
        rows.append(
            {
                "timestamp": start + timedelta(days=index),
                "open": close - 0.5,
                "high": close + 1.0,
                "low": close - 1.0,
                "close": close,
                "volume": 1_000.0 + index * 10,
            }
        )
    pq.write_table(pa.Table.from_pylist(rows), path)
    return path


def test_chart_query_returns_provenance_and_point_in_time_series(tmp_path: Path) -> None:
    payload = _payload(tmp_path / "bars.parquet")
    result = build_chart_series(
        ChartSeriesRequest(
            dataset_revision_id=uuid4(),
            payload_path=payload,
            symbol="AAPL",
            timeframe="1d",
            derived=(
                DerivedSeriesRequest(kind=DerivedSeriesKind.SIMPLE_RETURN),
                DerivedSeriesRequest(kind=DerivedSeriesKind.SMA, window=3),
                DerivedSeriesRequest(kind=DerivedSeriesKind.EMA, window=3),
            ),
        )
    )

    assert result.returned_row_count == 10
    assert result.downsampling_method is DownsamplingMethod.NONE
    assert result.rows[0].derived["simple_return"] is None
    assert result.rows[2].derived["sma_3"] == pytest.approx(101.0)
    assert result.rows[0].derived["ema_3"] == pytest.approx(100.0)
    assert all(item.point_in_time_safe for item in result.derived_evidence)
    assert result.payload_sha256
    assert result.network_used is False
    assert result.real_capital_enabled is False


def test_chart_query_filters_and_downsamples_deterministically(tmp_path: Path) -> None:
    payload = _payload(tmp_path / "bars.parquet", count=20)
    start = datetime(2026, 1, 5, tzinfo=UTC)
    end = datetime(2026, 1, 15, tzinfo=UTC)
    request = ChartSeriesRequest(
        dataset_revision_id=uuid4(),
        payload_path=payload,
        symbol="AAPL",
        timeframe="1d",
        start=start,
        end=end,
        max_rows=5,
    )

    first = build_chart_series(request)
    second = build_chart_series(request)

    assert first.filtered_row_count == 11
    assert first.returned_row_count == 5
    assert first.downsampling_method is DownsamplingMethod.EVENLY_SPACED
    assert first.rows == second.rows
    assert first.rows[0].timestamp == start
    assert first.rows[-1].timestamp == end


def test_chart_query_fails_closed_for_missing_payload(tmp_path: Path) -> None:
    request = ChartSeriesRequest(
        dataset_revision_id=uuid4(),
        payload_path=tmp_path / "missing.parquet",
        symbol="AAPL",
        timeframe="1d",
    )
    with pytest.raises(FileNotFoundError):
        build_chart_series(request)


def test_derived_windows_are_explicit() -> None:
    with pytest.raises(ValidationError):
        DerivedSeriesRequest(kind=DerivedSeriesKind.SMA)
    with pytest.raises(ValidationError):
        DerivedSeriesRequest(kind=DerivedSeriesKind.SIMPLE_RETURN, window=3)
