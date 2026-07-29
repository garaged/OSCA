from __future__ import annotations

from collections.abc import Mapping, Sequence
import json
import math
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from osca.demo_research.contracts import (
    DemoResearchMetricSummary,
    DemoResearchQualitySummary,
    DemoResearchReport,
    DemoResearchReportFormat,
    DemoResearchRequest,
    DemoWatchlistItem,
)
from osca.local_data_import import LocalOHLCVBar

_REQUIRED_COLUMNS = ("timestamp", "open", "high", "low", "close", "volume")


def run_demo_research_workflow(request: DemoResearchRequest) -> DemoResearchReport:
    payload_path = Path(request.payload_path)
    if not payload_path.is_file():
        raise FileNotFoundError(f"demo research payload file does not exist: {payload_path}")

    rows = _read_payload_rows(payload_path)
    bars = tuple(_bar_from_row(row, row_number=index) for index, row in enumerate(rows, start=1))
    if not bars:
        raise ValueError("demo research payload must contain at least one OHLCV row")

    metrics = _metric_summary(bars)
    quality_summary = DemoResearchQualitySummary(accepted_bar_count=len(bars))
    report = DemoResearchReport(
        request_id=request.request_id,
        project_name=request.project_name,
        watchlist=(DemoWatchlistItem(symbol=request.symbol, timeframe=request.timeframe),),
        metrics=metrics,
        quality_summary=quality_summary,
        observations=_observations(metrics),
        deferred_boundaries=_deferred_boundaries(),
    )

    if request.output_path is None:
        return report

    output_path = Path(request.output_path)
    report_with_output = report.model_copy(update={"output_uri": str(output_path)})
    _write_report(output_path, report_with_output, request.report_format)
    return report_with_output


def _read_payload_rows(payload_path: Path) -> tuple[Mapping[str, Any], ...]:
    table = pq.read_table(payload_path)
    _require_columns(table.column_names)
    raw_rows: Any = table.to_pylist()
    if not isinstance(raw_rows, list):
        raise ValueError("demo research payload did not produce row records")
    return tuple(_ensure_mapping(row) for row in raw_rows)


def _ensure_mapping(row: Any) -> Mapping[str, Any]:
    if not isinstance(row, dict):
        raise ValueError("demo research payload rows must be key-value records")
    return row


def _require_columns(columns: Sequence[str]) -> None:
    column_set = set(columns)
    missing = tuple(column for column in _REQUIRED_COLUMNS if column not in column_set)
    if missing:
        missing_list = ", ".join(missing)
        raise ValueError(f"demo research payload is missing required columns: {missing_list}")


def _bar_from_row(row: Mapping[str, Any], row_number: int) -> LocalOHLCVBar:
    try:
        return LocalOHLCVBar(
            timestamp=row["timestamp"],
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            volume=float(row["volume"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"invalid demo research row {row_number}: {exc}") from exc


def _metric_summary(bars: tuple[LocalOHLCVBar, ...]) -> DemoResearchMetricSummary:
    closes = tuple(bar.close for bar in bars)
    returns = _period_returns(closes)
    mean_return = sum(returns) / len(returns) if returns else 0.0
    volatility = _sample_standard_deviation(returns) if len(returns) > 1 else 0.0
    return DemoResearchMetricSummary(
        bar_count=len(bars),
        first_timestamp=bars[0].timestamp,
        last_timestamp=bars[-1].timestamp,
        first_close=closes[0],
        latest_close=closes[-1],
        total_return=(closes[-1] / closes[0]) - 1.0 if len(closes) > 1 else 0.0,
        mean_period_return=mean_return,
        volatility=volatility,
        max_drawdown=_max_drawdown(closes),
        simple_moving_average_3=_simple_moving_average(closes, window=3),
        simple_moving_average_5=_simple_moving_average(closes, window=5),
    )


def _period_returns(closes: tuple[float, ...]) -> tuple[float, ...]:
    return tuple((current / previous) - 1.0 for previous, current in zip(closes, closes[1:]))


def _sample_standard_deviation(values: tuple[float, ...]) -> float:
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    return math.sqrt(variance)


def _max_drawdown(closes: tuple[float, ...]) -> float:
    peak = closes[0]
    max_drawdown = 0.0
    for close in closes:
        peak = max(peak, close)
        drawdown = (close / peak) - 1.0
        max_drawdown = min(max_drawdown, drawdown)
    return max_drawdown


def _simple_moving_average(closes: tuple[float, ...], *, window: int) -> float | None:
    if len(closes) < window:
        return None
    return sum(closes[-window:]) / window


def _observations(metrics: DemoResearchMetricSummary) -> tuple[str, ...]:
    direction = "positive" if metrics.total_return >= 0 else "negative"
    return (
        f"{metrics.bar_count} accepted bars were analyzed from the supplied local dataset.",
        f"The observed total return over the payload window was {direction}.",
        "This report is evidence-only and does not contain recommendations or financial advice.",
    )


def _write_report(
    output_path: Path,
    report: DemoResearchReport,
    report_format: DemoResearchReportFormat,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if report_format is DemoResearchReportFormat.JSON:
        output_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
        return
    output_path.write_text(_render_markdown(report), encoding="utf-8")


def _render_markdown(report: DemoResearchReport) -> str:
    item = report.watchlist[0]
    metrics = report.metrics
    observations = "\n".join(f"- {observation}" for observation in report.observations)
    return f"""# OSCA Demo Research Report

## Scope

- Project: {report.project_name}
- Symbol: {item.symbol}
- Timeframe: {item.timeframe.value}
- Evidence only: {report.evidence_only}
- Not financial advice: {report.not_financial_advice}

## Metrics

| Metric | Value |
|---|---:|
| Bars | {metrics.bar_count} |
| First close | {metrics.first_close:.6f} |
| Latest close | {metrics.latest_close:.6f} |
| Total return | {metrics.total_return:.6f} |
| Mean period return | {metrics.mean_period_return:.6f} |
| Volatility | {metrics.volatility:.6f} |
| Max drawdown | {metrics.max_drawdown:.6f} |
| SMA 3 | {_format_optional_float(metrics.simple_moving_average_3)} |
| SMA 5 | {_format_optional_float(metrics.simple_moving_average_5)} |

## Observations

{observations}

## Deferred Boundaries

Live providers, credentials, runtime routing, production ingestion, ML, LLM, recommendations, scheduler execution, and real-capital orders remain disabled.
"""


def _format_optional_float(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.6f}"


def _deferred_boundaries() -> dict[str, bool]:
    return {
        "live_provider_calls_enabled": False,
        "credential_materialization_enabled": False,
        "runtime_provider_routing_enabled": False,
        "production_ingestion_enabled": False,
        "ml_execution_enabled": False,
        "llm_execution_enabled": False,
        "recommendations_enabled": False,
        "scheduler_execution_enabled": False,
        "real_capital_orders_enabled": False,
    }
