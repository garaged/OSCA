from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from osca.backtesting.api import (
    BacktestAssumptionSet,
    BacktestDataAvailability,
    BacktestExecutionMode,
    BacktestFidelityProfile,
    BacktestMetric,
    BacktestRequest,
    BacktestResult,
    BacktestStatus,
    BacktestWindow,
    OrderIntent,
    OrderIntentSide,
    OrderIntentType,
    StrategyDecision,
)


def test_backtest_request_preserves_point_in_time_inputs() -> None:
    request = BacktestRequest(
        project_id=uuid4(),
        strategy_id="strategy.mean-reversion",
        fidelity_profile=BacktestFidelityProfile.F2_EVENT_DRIVEN_BAR,
        execution_mode=BacktestExecutionMode.EVENT_DRIVEN,
        window=BacktestWindow(
            start_at=datetime(2026, 1, 1, tzinfo=UTC),
            end_at=datetime(2026, 2, 1, tzinfo=UTC),
        ),
        dataset_revision_ids=(uuid4(),),
        data_availability=BacktestDataAvailability.POINT_IN_TIME,
        assumptions=BacktestAssumptionSet(assumption_set_id="base"),
        random_seed=42,
    )

    assert request.family == "osca.backtest.request"
    assert request.fidelity_profile is BacktestFidelityProfile.F2_EVENT_DRIVEN_BAR
    assert request.dataset_revision_ids


def test_backtest_window_rejects_naive_or_reversed_time() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        BacktestWindow(
            start_at=datetime(2026, 1, 1),
            end_at=datetime(2026, 1, 2, tzinfo=UTC),
        )

    with pytest.raises(ValidationError, match="after start_at"):
        BacktestWindow(
            start_at=datetime(2026, 1, 2, tzinfo=UTC),
            end_at=datetime(2026, 1, 1, tzinfo=UTC),
        )


def test_order_intent_keeps_strategy_decision_linkage() -> None:
    decision = StrategyDecision(
        strategy_id="strategy.breakout",
        effective_at=datetime(2026, 1, 3, tzinfo=UTC),
        rationale="breakout confirmed by governed signal",
        confidence=0.72,
        evidence_ids=(uuid4(),),
    )

    order = OrderIntent(
        decision_id=decision.decision_id,
        instrument_id=uuid4(),
        side=OrderIntentSide.BUY,
        order_type=OrderIntentType.LIMIT,
        quantity=10,
        limit_price=125.5,
    )

    assert order.family == "osca.backtest.order-intent"
    assert order.decision_id == decision.decision_id


def test_market_order_intent_cannot_declare_limit_price() -> None:
    with pytest.raises(ValidationError, match="market order intents cannot declare"):
        OrderIntent(
            decision_id=uuid4(),
            instrument_id=uuid4(),
            side=OrderIntentSide.SELL,
            order_type=OrderIntentType.MARKET,
            quantity=1,
            limit_price=10,
        )


def test_completed_backtest_result_requires_metrics() -> None:
    with pytest.raises(ValidationError, match="completed backtest results require"):
        BacktestResult(request_id=uuid4(), status=BacktestStatus.COMPLETED)

    result = BacktestResult(
        request_id=uuid4(),
        status=BacktestStatus.COMPLETED,
        metrics=(BacktestMetric(name="total_return", value=0.12, unit="ratio", methodology="simple"),),
    )

    assert result.status is BacktestStatus.COMPLETED
