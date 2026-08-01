from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pyarrow as pa
import pyarrow.parquet as pq
from fastapi.testclient import TestClient

from osca.analyst_workspace.app import create_app


def _payload(path: Path, count: int = 12) -> Path:
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


def test_chart_page_is_offline_accessible_and_export_capable(tmp_path: Path) -> None:
    client = TestClient(create_app(storage_root=tmp_path))

    response = client.get("/charts")

    assert response.status_code == 200
    assert "Market Data Visualization" in response.text
    assert "Export SVG" in response.text
    assert "Export CSV" in response.text
    assert "Accessible visible-data table" in response.text
    assert "cdn" not in response.text.lower()


def test_chart_api_uses_u2_runtime_and_preserves_boundaries(tmp_path: Path) -> None:
    payload = _payload(tmp_path / "bars.parquet")
    revision = uuid4()
    client = TestClient(create_app(storage_root=tmp_path))

    response = client.get(
        "/api/chart-series",
        params=[
            ("payload_path", str(payload)),
            ("dataset_revision_id", str(revision)),
            ("symbol", "AAPL"),
            ("timeframe", "1d"),
            ("max_rows", "8"),
            ("derived", "sma:3"),
        ],
    )

    assert response.status_code == 200
    body = response.json()
    assert body["dataset_revision_id"] == str(revision)
    assert body["returned_row_count"] == 8
    assert body["downsampling_preserves_first_last"] is True
    assert body["network_used"] is False
    assert body["credentials_used"] is False
    assert body["recommendations_enabled"] is False
    assert body["broker_execution_enabled"] is False
    assert body["real_capital_enabled"] is False
    assert "sma_3" in body["rows"][-1]["derived"]


def test_chart_csv_export_contains_provenance_and_derived_values(tmp_path: Path) -> None:
    payload = _payload(tmp_path / "bars.parquet", count=5)
    revision = uuid4()
    client = TestClient(create_app(storage_root=tmp_path))

    response = client.get(
        "/api/chart-series.csv",
        params=[
            ("payload_path", str(payload)),
            ("dataset_revision_id", str(revision)),
            ("symbol", "AAPL"),
            ("timeframe", "1d"),
            ("derived", "simple_return"),
        ],
    )

    assert response.status_code == 200
    assert "dataset_revision_id,symbol,timeframe,timestamp" in response.text
    assert str(revision) in response.text
    assert "simple_return" in response.text


def test_chart_api_rejects_unknown_derived_series(tmp_path: Path) -> None:
    payload = _payload(tmp_path / "bars.parquet")
    client = TestClient(create_app(storage_root=tmp_path))

    response = client.get(
        "/api/chart-series",
        params={
            "payload_path": str(payload),
            "dataset_revision_id": str(uuid4()),
            "symbol": "AAPL",
            "timeframe": "1d",
            "derived": "future_magic",
        },
    )

    assert response.status_code == 400
    assert "unknown derived series" in response.json()["detail"]
