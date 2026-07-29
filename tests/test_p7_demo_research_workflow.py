import csv
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from typer.testing import CliRunner

from osca.bootstrap.cli import app
from osca.demo_research import (
    DemoResearchReportFormat,
    DemoResearchRequest,
    run_demo_research_workflow,
)
from osca.local_data_import import (
    LocalOHLCVImportRequest,
    LocalOHLCVImportResult,
    LocalOHLCVTimeframe,
    import_local_ohlcv,
)

runner = CliRunner()


def test_demo_research_report_consumes_p6_payload_and_computes_metrics(tmp_path: Path) -> None:
    import_result = _import_sample_payload(tmp_path)
    report_path = tmp_path / "reports" / "aapl.md"

    report = run_demo_research_workflow(
        DemoResearchRequest(
            payload_path=import_result.payload_uri,
            output_path=str(report_path),
            symbol="AAPL",
            timeframe=LocalOHLCVTimeframe.ONE_DAY,
            report_format=DemoResearchReportFormat.MARKDOWN,
        )
    )

    assert report.metrics.bar_count == 5
    assert report.metrics.total_return == pytest.approx(0.10)
    assert report.metrics.mean_period_return > 0
    assert report.metrics.volatility > 0
    assert report.metrics.max_drawdown == pytest.approx(-0.0454545454)
    assert report.metrics.simple_moving_average_3 == pytest.approx(105.0)
    assert report.metrics.simple_moving_average_5 == pytest.approx(104.0)
    assert report.evidence_only is True
    assert report.not_financial_advice is True
    assert report.deferred_boundaries["recommendations_enabled"] is False
    assert report.output_uri == str(report_path)
    assert "OSCA Demo Research Report" in report_path.read_text(encoding="utf-8")


def test_demo_research_report_writes_json_static_file(tmp_path: Path) -> None:
    import_result = _import_sample_payload(tmp_path)
    report_path = tmp_path / "reports" / "aapl.json"

    report = run_demo_research_workflow(
        DemoResearchRequest(
            payload_path=import_result.payload_uri,
            output_path=str(report_path),
            symbol="AAPL",
            timeframe=LocalOHLCVTimeframe.ONE_DAY,
            report_format=DemoResearchReportFormat.JSON,
        )
    )

    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert payload["family"] == "osca.demo-research.report"
    assert payload["metrics"]["bar_count"] == report.metrics.bar_count
    assert payload["deferred_boundaries"]["llm_execution_enabled"] is False


def test_demo_research_rejects_payload_missing_required_columns(tmp_path: Path) -> None:
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
        run_demo_research_workflow(
            DemoResearchRequest(
                payload_path=str(payload),
                symbol="AAPL",
                timeframe=LocalOHLCVTimeframe.ONE_DAY,
            )
        )


def test_cli_demo_research_report_writes_static_file_and_reports_boundaries(tmp_path: Path) -> None:
    import_result = _import_sample_payload(tmp_path)
    report_path = tmp_path / "report.md"

    result = runner.invoke(
        app,
        [
            "demo-research-report",
            import_result.payload_uri,
            "AAPL",
            "1d",
            "--output-file",
            str(report_path),
            "--report-format",
            "markdown",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)

    assert payload["watchlist"] == [{"symbol": "AAPL", "timeframe": "1d"}]
    assert payload["metrics"]["bar_count"] == 5
    assert payload["evidence_only"] is True
    assert payload["not_financial_advice"] is True
    assert payload["deferred_boundaries"]["live_provider_calls_enabled"] is False
    assert report_path.is_file()


def _import_sample_payload(tmp_path: Path) -> LocalOHLCVImportResult:
    source = tmp_path / "aapl.csv"
    _write_csv(
        source,
        [
            ("2026-07-21T13:30:00Z", "100", "102", "99", "100", "1000"),
            ("2026-07-22T13:30:00Z", "100", "106", "99", "105", "1100"),
            ("2026-07-23T13:30:00Z", "105", "111", "104", "110", "1200"),
            ("2026-07-24T13:30:00Z", "110", "111", "104", "105", "1300"),
            ("2026-07-25T13:30:00Z", "105", "112", "104", "110", "1400"),
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


def _write_csv(source: Path, rows: list[tuple[str, str, str, str, str, str]]) -> None:
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp", "open", "high", "low", "close", "volume"])
        writer.writerows(rows)
