import csv
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from typer.testing import CliRunner

from osca.backtest_paper import (
    BacktestPaperReportFormat,
    BacktestPaperRequest,
    run_backtest_paper_happy_path,
)
from osca.bootstrap.cli import app
from osca.local_data_import import (
    LocalOHLCVImportRequest,
    LocalOHLCVImportResult,
    LocalOHLCVTimeframe,
    import_local_ohlcv,
)

runner = CliRunner()


def test_backtest_paper_happy_path_consumes_p6_payload_and_retains_evidence(
    tmp_path: Path,
) -> None:
    import_result = _import_sample_payload(tmp_path)
    output_path = tmp_path / "reports" / "p8.md"

    report = run_backtest_paper_happy_path(
        BacktestPaperRequest(
            payload_path=import_result.payload_uri,
            output_path=str(output_path),
            symbol="AAPL",
            timeframe=LocalOHLCVTimeframe.ONE_DAY,
            report_format=BacktestPaperReportFormat.MARKDOWN,
        )
    )

    assert report.backtest.bars_processed == 10
    assert report.backtest.signal_bar_count == 6
    assert report.backtest.trade_count == 2
    assert report.backtest.exposure_bar_count == 5
    assert report.backtest.final_equity == pytest.approx(10_666.6666666667)
    assert report.backtest.total_return == pytest.approx(0.0666666667)
    assert report.backtest.buy_and_hold_return == pytest.approx(0.16)
    assert report.paper_evaluation.broker_integration_enabled is False
    assert report.paper_evaluation.real_orders_enabled is False
    assert report.paper_evaluation.retained_evidence_uris == (str(output_path),)
    assert report.deferred_boundaries["autonomous_execution_enabled"] is False
    assert "OSCA Backtest-to-Paper Evidence Report" in output_path.read_text(encoding="utf-8")


def test_backtest_paper_happy_path_writes_json_report(tmp_path: Path) -> None:
    import_result = _import_sample_payload(tmp_path)
    output_path = tmp_path / "reports" / "p8.json"

    report = run_backtest_paper_happy_path(
        BacktestPaperRequest(
            payload_path=import_result.payload_uri,
            output_path=str(output_path),
            symbol="AAPL",
            timeframe=LocalOHLCVTimeframe.ONE_DAY,
            report_format=BacktestPaperReportFormat.JSON,
        )
    )
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert payload["family"] == "osca.backtest-paper.report"
    assert payload["backtest"]["trade_count"] == report.backtest.trade_count
    assert payload["paper_evaluation"]["broker_integration_enabled"] is False
    assert payload["paper_evaluation"]["retained_evidence_uris"] == [str(output_path)]


def test_backtest_paper_rejects_payload_missing_required_columns(tmp_path: Path) -> None:
    payload = tmp_path / "bad.parquet"
    table = pa.Table.from_pylist(
        [
            {
                "timestamp": "2026-07-24T13:30:00Z",
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.0,
            }
        ]
    )
    pq.write_table(table, payload)

    with pytest.raises(ValueError, match="missing required columns: volume"):
        run_backtest_paper_happy_path(
            BacktestPaperRequest(
                payload_path=str(payload),
                symbol="AAPL",
                timeframe=LocalOHLCVTimeframe.ONE_DAY,
            )
        )


def test_backtest_paper_rejects_too_few_bars_for_builtin_strategy(tmp_path: Path) -> None:
    import_result = _import_short_payload(tmp_path)

    with pytest.raises(ValueError, match="at least 5 bars"):
        run_backtest_paper_happy_path(
            BacktestPaperRequest(
                payload_path=import_result.payload_uri,
                symbol="AAPL",
                timeframe=LocalOHLCVTimeframe.ONE_DAY,
            )
        )


def test_backtest_paper_rejects_deferred_live_execution_flags(tmp_path: Path) -> None:
    import_result = _import_sample_payload(tmp_path)

    with pytest.raises(ValueError, match="Input should be False"):
        BacktestPaperRequest(
            payload_path=import_result.payload_uri,
            symbol="AAPL",
            timeframe=LocalOHLCVTimeframe.ONE_DAY,
            enable_real_orders=True,
        )


def test_cli_backtest_paper_writes_report_and_reports_boundaries(tmp_path: Path) -> None:
    import_result = _import_sample_payload(tmp_path)
    output_path = tmp_path / "p8.md"

    result = runner.invoke(
        app,
        [
            "backtest-paper-run",
            import_result.payload_uri,
            "AAPL",
            "1d",
            "--output-file",
            str(output_path),
            "--report-format",
            "markdown",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)

    assert payload["symbol"] == "AAPL"
    assert payload["backtest"]["bars_processed"] == 10
    assert payload["paper_evaluation"]["broker_integration_enabled"] is False
    assert payload["deferred_boundaries"]["real_capital_orders_enabled"] is False
    assert payload["evidence_only"] is True
    assert output_path.is_file()


def _import_sample_payload(tmp_path: Path) -> LocalOHLCVImportResult:
    source = tmp_path / "aapl.csv"
    _write_csv(
        source,
        [
            ("2026-07-20T13:30:00Z", "100", "101", "99", "100", "1000"),
            ("2026-07-21T13:30:00Z", "100", "102", "99", "102", "1000"),
            ("2026-07-22T13:30:00Z", "102", "105", "101", "104", "1000"),
            ("2026-07-23T13:30:00Z", "104", "107", "103", "106", "1000"),
            ("2026-07-24T13:30:00Z", "106", "110", "105", "108", "1000"),
            ("2026-07-25T13:30:00Z", "108", "111", "107", "110", "1000"),
            ("2026-07-26T13:30:00Z", "110", "113", "109", "112", "1000"),
            ("2026-07-27T13:30:00Z", "112", "115", "111", "114", "1000"),
            ("2026-07-28T13:30:00Z", "114", "116", "112", "112", "1000"),
            ("2026-07-29T13:30:00Z", "112", "117", "111", "116", "1000"),
        ],
    )
    return import_local_ohlcv(
        LocalOHLCVImportRequest(
            input_path=str(source),
            storage_root=str(tmp_path / "store"),
            symbol="AAPL",
            timeframe=LocalOHLCVTimeframe.ONE_DAY,
        )
    )


def _import_short_payload(tmp_path: Path) -> LocalOHLCVImportResult:
    source = tmp_path / "short.csv"
    _write_csv(
        source,
        [
            ("2026-07-24T13:30:00Z", "100", "101", "99", "100", "1000"),
            ("2026-07-25T13:30:00Z", "100", "101", "99", "100", "1000"),
            ("2026-07-26T13:30:00Z", "100", "101", "99", "100", "1000"),
        ],
    )
    return import_local_ohlcv(
        LocalOHLCVImportRequest(
            input_path=str(source),
            storage_root=str(tmp_path / "short-store"),
            symbol="AAPL",
            timeframe=LocalOHLCVTimeframe.ONE_DAY,
        )
    )


def _write_csv(source: Path, rows: list[tuple[str, str, str, str, str, str]]) -> None:
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp", "open", "high", "low", "close", "volume"])
        writer.writerows(rows)
