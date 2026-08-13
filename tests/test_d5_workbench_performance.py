from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from time import perf_counter
from uuid import uuid4

import pyarrow as pa
import pyarrow.parquet as pq

from osca.analytical_data import (
    ChartSeriesRequest,
    DerivedSeriesKind,
    DerivedSeriesRequest,
    DownsamplingMethod,
    build_chart_series,
)


def test_large_cached_series_is_bounded_within_d5_responsiveness_budget(
    tmp_path: Path,
) -> None:
    count = 25_000
    start = datetime(2020, 1, 1, tzinfo=UTC)
    rows = []
    for index in range(count):
        close = 100.0 + index * 0.01
        rows.append(
            {
                "timestamp": start + timedelta(minutes=index),
                "open": close - 0.05,
                "high": close + 0.10,
                "low": close - 0.10,
                "close": close,
                "volume": 1_000.0 + index % 500,
            }
        )
    payload = tmp_path / "large-bars.parquet"
    pq.write_table(pa.Table.from_pylist(rows), payload)

    request = ChartSeriesRequest(
        dataset_revision_id=uuid4(),
        payload_path=payload,
        symbol="PERF",
        timeframe="1m",
        max_rows=240,
        derived=(
            DerivedSeriesRequest(kind=DerivedSeriesKind.SMA, window=20),
            DerivedSeriesRequest(kind=DerivedSeriesKind.EMA, window=20),
        ),
    )

    started = perf_counter()
    result = build_chart_series(request)
    elapsed = perf_counter() - started

    assert elapsed < 3.0
    assert result.filtered_row_count == count
    assert result.returned_row_count == 240
    assert result.downsampling_method is DownsamplingMethod.EVENLY_SPACED
    assert result.rows[0].timestamp == start
    assert result.rows[-1].timestamp == start + timedelta(minutes=count - 1)
    assert all(item.point_in_time_safe for item in result.derived_evidence)
