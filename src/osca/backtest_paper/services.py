from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from itertools import pairwise
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from osca.backtest_paper.contracts import (
    BacktestPaperReport,
    BacktestPaperReportFormat,
    BacktestPaperRequest,
    BacktestSummary,
    BacktestTrade,
    PaperEvaluationRecord,
)
from osca.local_data_import import LocalOHLCVBar

_REQUIRED_COLUMNS = ("timestamp", "open", "high", "low", "close", "volume")


def run_backtest_paper_happy_path(request: BacktestPaperRequest) -> BacktestPaperReport:
    payload_path = Path(request.payload_path)
    if not payload_path.is_file():
        raise FileNotFoundError(f"backtest-to-paper payload file does not exist: {payload_path}")

    bars = _read_bars(payload_path)
    if len(bars) < request.strategy.long_window:
        raise ValueError(
            "backtest-to-paper payload must contain at least "
            f"{request.strategy.long_window} bars for the built-in strategy"
        )

    backtest = _run_long_only_sma_backtest(request, bars)
    paper_record = PaperEvaluationRecord(
        linked_request_id=request.request_id,
        comparison_summary=_comparison_summary(backtest),
    )
    report = BacktestPaperReport(
        request_id=request.request_id,
        project_name=request.project_name,
        symbol=request.symbol,
        timeframe=request.timeframe,
        strategy=request.strategy,
        backtest=backtest,
        paper_evaluation=paper_record,
        observations=_observations(backtest),
        deferred_boundaries=_deferred_boundaries(),
    )

    if request.output_path is None:
        return report

    output_path = Path(request.output_path)
    report_with_output = report.model_copy(
        update={
            "output_uri": str(output_path),
            "paper_evaluation": paper_record.model_copy(
                update={"retained_evidence_uris": (str(output_path),)}
            ),
        }
    )
    _write_report(output_path, report_with_output, request.report_format)
    return report_with_output


def _read_bars(payload_path: Path) -> tuple[LocalOHLCVBar, ...]:
    table = pq.read_table(payload_path)
    _require_columns(table.column_names)
    raw_rows: Any = table.to_pylist()
    if not isinstance(raw_rows, list):
        raise ValueError("backtest-to-paper payload did not produce row records")
    return tuple(_bar_from_row(_ensure_mapping(row), index) for index, row in enumerate(raw_rows, 1))


def _ensure_mapping(row: Any) -> Mapping[str, Any]:
    if not isinstance(row, dict):
        raise ValueError("backtest-to-paper payload rows must be key-value records")
    return row


def _require_columns(columns: Sequence[str]) -> None:
    column_set = set(columns)
    missing = tuple(column for column in _REQUIRED_COLUMNS if column not in column_set)
    if missing:
        missing_list = ", ".join(missing)
        raise ValueError(f"backtest-to-paper payload is missing required columns: {missing_list}")


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
        raise ValueError(f"invalid backtest-to-paper row {row_number}: {exc}") from exc


def _run_long_only_sma_backtest(
    request: BacktestPaperRequest,
    bars: tuple[LocalOHLCVBar, ...],
) -> BacktestSummary:
    cash = request.initial_cash
    units = 0.0
    trades: list[BacktestTrade] = []
    equity_curve: list[float] = []
    exposure_bar_count = 0
    signal_bar_count = 0
    closes: list[float] = []

    for bar in bars:
        closes.append(bar.close)
        signal = False
        if len(closes) >= request.strategy.long_window:
            signal_bar_count += 1
            short_sma = _simple_moving_average(tuple(closes), request.strategy.short_window)
            long_sma = _simple_moving_average(tuple(closes), request.strategy.long_window)
            signal = bar.close > short_sma > long_sma

        if signal and units == 0.0:
            units = cash / bar.close
            cash = 0.0
            trades.append(
                BacktestTrade(
                    timestamp=bar.timestamp,
                    action="buy",
                    price=bar.close,
                    units=units,
                    cash_after=cash,
                    position_units_after=units,
                    reason="close-above-sma-trend-signal",
                )
            )
        elif not signal and units > 0.0:
            cash = units * bar.close
            trades.append(
                BacktestTrade(
                    timestamp=bar.timestamp,
                    action="sell",
                    price=bar.close,
                    units=units,
                    cash_after=cash,
                    position_units_after=0.0,
                    reason="trend-signal-cleared",
                )
            )
            units = 0.0

        if units > 0.0:
            exposure_bar_count += 1
        equity_curve.append(cash + (units * bar.close))

    final_equity = equity_curve[-1]
    return BacktestSummary(
        strategy_id=request.strategy.strategy_id,
        bars_processed=len(bars),
        signal_bar_count=signal_bar_count,
        initial_cash=request.initial_cash,
        final_equity=final_equity,
        total_return=(final_equity / request.initial_cash) - 1.0,
        max_drawdown=_max_drawdown(tuple(equity_curve)),
        trade_count=len(trades),
        exposure_bar_count=exposure_bar_count,
        buy_and_hold_return=(bars[-1].close / bars[0].close) - 1.0,
        trades=tuple(trades),
    )


def _simple_moving_average(values: tuple[float, ...], window: int) -> float:
    return sum(values[-window:]) / window


def _max_drawdown(values: tuple[float, ...]) -> float:
    peak = values[0]
    max_drawdown = 0.0
    for value in values:
        peak = max(peak, value)
        if peak == 0.0:
            continue
        drawdown = (value / peak) - 1.0
        max_drawdown = min(max_drawdown, drawdown)
    return max_drawdown


def _comparison_summary(backtest: BacktestSummary) -> str:
    relative = backtest.total_return - backtest.buy_and_hold_return
    if math.isclose(relative, 0.0, abs_tol=1e-12):
        relation = "matched"
    elif relative > 0:
        relation = "outperformed"
    else:
        relation = "underperformed"
    return (
        f"The built-in strategy {relation} buy-and-hold by {relative:.6f} "
        "over the supplied local evidence window."
    )


def _observations(backtest: BacktestSummary) -> tuple[str, ...]:
    return (
        f"{backtest.bars_processed} local bars were evaluated by the built-in strategy.",
        f"{backtest.trade_count} simulated evidence trades were generated.",
        "The linked paper-evaluation record is local evidence only, not broker execution.",
        "This report is not financial advice and contains no recommendation to trade.",
    )


def _write_report(
    output_path: Path,
    report: BacktestPaperReport,
    report_format: BacktestPaperReportFormat,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if report_format is BacktestPaperReportFormat.JSON:
        output_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
        return
    output_path.write_text(_render_markdown(report), encoding="utf-8")


def _render_markdown(report: BacktestPaperReport) -> str:
    rows = [
        "# OSCA Backtest-to-Paper Evidence Report",
        "",
        "## Scope",
        "",
        f"- Project: {report.project_name}",
        f"- Symbol: {report.symbol}",
        f"- Timeframe: {report.timeframe.value}",
        f"- Strategy: {report.strategy.strategy_id.value}",
        f"- Evidence only: {report.evidence_only}",
        f"- Not financial advice: {report.not_financial_advice}",
        "",
        "## Backtest",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Bars processed | {report.backtest.bars_processed} |",
        f"| Signal bars | {report.backtest.signal_bar_count} |",
        f"| Initial cash | {report.backtest.initial_cash:.2f} |",
        f"| Final equity | {report.backtest.final_equity:.2f} |",
        f"| Strategy return | {report.backtest.total_return:.6f} |",
        f"| Buy-and-hold return | {report.backtest.buy_and_hold_return:.6f} |",
        f"| Max drawdown | {report.backtest.max_drawdown:.6f} |",
        f"| Evidence trades | {report.backtest.trade_count} |",
        "",
        "## Paper Evaluation",
        "",
        f"- Paper run: {report.paper_evaluation.paper_run_id}",
        f"- Mode: {report.paper_evaluation.paper_account_mode}",
        f"- Comparison: {report.paper_evaluation.comparison_summary}",
        "",
        "## Observations",
        "",
    ]
    rows.extend(f"- {observation}" for observation in report.observations)
    rows.extend(
        [
            "",
            "## Deferred Boundaries",
            "",
            "Live paper brokers, autonomous execution, live providers, production ingestion,",
            "recommendations, and real-capital orders remain disabled.",
            "",
        ]
    )
    return "\n".join(rows)


def _deferred_boundaries() -> dict[str, bool]:
    return {
        "live_provider_calls_enabled": False,
        "credential_materialization_enabled": False,
        "runtime_provider_routing_enabled": False,
        "production_ingestion_enabled": False,
        "live_paper_broker_enabled": False,
        "autonomous_execution_enabled": False,
        "recommendations_enabled": False,
        "real_capital_orders_enabled": False,
    }
