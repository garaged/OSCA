import csv
import json
import sqlite3
from pathlib import Path

import pyarrow.parquet as pq
import pytest
from typer.testing import CliRunner

from osca.bootstrap.cli import app
from osca.local_data_import import (
    LocalOHLCVImportFormat,
    LocalOHLCVImportRequest,
    LocalOHLCVTimeframe,
    import_local_ohlcv,
)

runner = CliRunner()


def test_import_local_csv_writes_metadata_and_payload(tmp_path: Path) -> None:
    source = tmp_path / "aapl.csv"
    _write_csv(
        source,
        [
            ("2026-07-24T13:30:00Z", "100", "105", "99", "104", "1000"),
            ("2026-07-25T13:30:00Z", "104", "106", "103", "105", "1200"),
        ],
    )

    result = import_local_ohlcv(
        LocalOHLCVImportRequest(
            input_path=str(source),
            storage_root=str(tmp_path / "store"),
            symbol="AAPL",
            timeframe=LocalOHLCVTimeframe.ONE_DAY,
            calendar_assumption="user-supplied-daily-bars",
        )
    )

    assert result.row_count == 2
    assert result.input_format is LocalOHLCVImportFormat.CSV
    assert result.network_access_enabled is False
    assert result.deferred_boundaries["live_provider_calls_enabled"] is False
    assert Path(result.payload_uri).is_file()
    assert Path(result.metadata_uri).is_file()

    table = pq.read_table(result.payload_uri)
    assert table.num_rows == 2

    with sqlite3.connect(result.metadata_uri) as connection:
        row = connection.execute(
            "SELECT symbol, timeframe, row_count, source_sha256, network_access_enabled "
            "FROM local_ohlcv_imports WHERE dataset_revision_id = ?",
            (str(result.dataset_revision_id),),
        ).fetchone()

    assert row == ("AAPL", "1d", 2, result.source_sha256, 0)


def test_import_rejects_missing_required_column(tmp_path: Path) -> None:
    source = tmp_path / "bad.csv"
    source.write_text("timestamp,open,high,low,close\n2026-07-24T13:30:00Z,1,2,1,2\n")

    with pytest.raises(ValueError, match="missing required columns: volume"):
        import_local_ohlcv(
            LocalOHLCVImportRequest(
                input_path=str(source),
                storage_root=str(tmp_path / "store"),
                symbol="AAPL",
                timeframe=LocalOHLCVTimeframe.ONE_DAY,
            )
        )


def test_import_rejects_non_monotonic_timestamps(tmp_path: Path) -> None:
    source = tmp_path / "bad-order.csv"
    _write_csv(
        source,
        [
            ("2026-07-25T13:30:00Z", "100", "105", "99", "104", "1000"),
            ("2026-07-24T13:30:00Z", "104", "106", "103", "105", "1200"),
        ],
    )

    with pytest.raises(ValueError, match="non-monotonic-timestamp"):
        import_local_ohlcv(
            LocalOHLCVImportRequest(
                input_path=str(source),
                storage_root=str(tmp_path / "store"),
                symbol="AAPL",
                timeframe=LocalOHLCVTimeframe.ONE_DAY,
            )
        )


def test_cli_imports_local_ohlcv_and_reports_boundaries(tmp_path: Path) -> None:
    source = tmp_path / "aapl.csv"
    _write_csv(
        source,
        [
            ("2026-07-24T13:30:00Z", "100", "105", "99", "104", "1000"),
        ],
    )

    result = runner.invoke(
        app,
        [
            "local-ohlcv-import",
            str(source),
            "AAPL",
            "1d",
            "--storage-root",
            str(tmp_path / "store"),
            "--calendar-assumption",
            "user-supplied-daily-bars",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)

    assert payload["symbol"] == "AAPL"
    assert payload["row_count"] == 1
    assert payload["input_format"] == "csv"
    assert payload["network_access_enabled"] is False
    assert payload["deferred_boundaries"]["production_ingestion_enabled"] is False


def _write_csv(source: Path, rows: list[tuple[str, str, str, str, str, str]]) -> None:
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp", "open", "high", "low", "close", "volume"])
        writer.writerows(rows)
