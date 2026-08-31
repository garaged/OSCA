from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

import pytest

from osca.paper.forward_comparison import (
    ComparisonMetric,
    build_forward_backtest_comparison,
)

RUN_ID = UUID("81000000-0000-0000-0000-000000000001")
ASSUMPTION_ID = UUID("82000000-0000-0000-0000-000000000002")


def at(day: int) -> datetime:
    return datetime(2026, 8, day, 12, tzinfo=UTC)


def test_comparison_retains_artifact_windows_assumptions_and_decimal_deltas() -> None:
    result = build_forward_backtest_comparison(
        backtest_result_id=42,
        paper_run_id=RUN_ID,
        strategy_version_id=7,
        assumption_id=ASSUMPTION_ID,
        backtest_started_at=at(1),
        backtest_ended_at=at(10),
        forward_started_at=at(11),
        forward_ended_at=at(20),
        metrics=(
            ComparisonMetric(
                name="total_return",
                backtest_value=Decimal("0.075"),
                forward_value=Decimal("0.031"),
                unit="ratio",
                methodology="same strategy; distinct historical and forward windows",
            ),
            ComparisonMetric(
                name="max_drawdown",
                backtest_value=Decimal("-0.021"),
                forward_value=Decimal("-0.034"),
                unit="ratio",
                methodology="D8 equity projection drawdown over each retained window",
            ),
        ),
        methodology_differences=(
            "backtest uses historical event-driven simulation",
            "forward run consumes only bars available after confirmation",
            "forward execution uses the pinned D9 assumption revision",
        ),
        compared_at=at(21),
    )

    assert result.research_only is True
    assert result.backtest_result_id == 42
    assert result.paper_run_id == RUN_ID
    assert result.assumption_id == ASSUMPTION_ID
    assert result.metrics[0].delta == Decimal("-0.044")
    assert result.metrics[1].delta == Decimal("-0.013")
    assert result.backtest_ended_at < result.forward_started_at


def test_comparison_rejects_ambiguous_windows_or_missing_methodology() -> None:
    metric = ComparisonMetric(
        name="return",
        backtest_value=Decimal("0.01"),
        forward_value=Decimal("0.02"),
        unit="ratio",
        methodology="descriptive return comparison",
    )
    with pytest.raises(ValueError, match="backtest comparison window"):
        build_forward_backtest_comparison(
            backtest_result_id=1,
            paper_run_id=RUN_ID,
            strategy_version_id=1,
            assumption_id=ASSUMPTION_ID,
            backtest_started_at=at(10),
            backtest_ended_at=at(10),
            forward_started_at=at(11),
            forward_ended_at=at(12),
            metrics=(metric,),
            methodology_differences=("windows differ",),
            compared_at=at(13),
        )
    with pytest.raises(ValueError):
        build_forward_backtest_comparison(
            backtest_result_id=1,
            paper_run_id=RUN_ID,
            strategy_version_id=1,
            assumption_id=ASSUMPTION_ID,
            backtest_started_at=at(1),
            backtest_ended_at=at(10),
            forward_started_at=at(11),
            forward_ended_at=at(12),
            metrics=(metric,),
            methodology_differences=(),
            compared_at=at(13),
        )
