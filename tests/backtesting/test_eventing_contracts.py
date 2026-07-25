from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from osca.backtesting.api import OrderIntent, OrderIntentSide, OrderIntentType
from osca.backtesting.eventing import (
    F2EventType,
    F2SimulationEvent,
    FillModelMetadata,
    JournalLine,
    JournalLineSide,
    JournalTransaction,
    OrderLifecycleEvent,
    OrderLifecycleState,
    PortfolioProjection,
    RiskDecision,
    RiskDecisionAction,
    SimulatedFill,
    ValuationHolding,
    ValuationSnapshot,
)


def test_f2_event_requires_timezone_aware_effective_time() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        F2SimulationEvent(
            request_id=uuid4(),
            event_type=F2EventType.CLOCK,
            effective_at=datetime(2026, 1, 1),
            source_id="clock.daily",
        )


def test_order_lifecycle_event_preserves_order_intent_linkage() -> None:
    order = OrderIntent(
        decision_id=uuid4(),
        instrument_id=uuid4(),
        side=OrderIntentSide.BUY,
        order_type=OrderIntentType.MARKET,
        quantity=5,
    )

    event = OrderLifecycleEvent.from_order_intent(
        request_id=uuid4(),
        order_intent=order,
        state=OrderLifecycleState.CREATED,
        rationale="strategy emitted order intent",
        effective_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    assert event.order_intent_id == order.order_intent_id
    assert event.decision_id == order.decision_id


def test_simulated_fill_retains_model_and_market_metadata() -> None:
    fill = SimulatedFill(
        request_id=uuid4(),
        order_intent_id=uuid4(),
        market_observation_id=uuid4(),
        fill_model=FillModelMetadata(
            model_id="bar-close-v1",
            version="1.0.0",
            spread_bps=2,
            slippage_bps=5,
            latency_seconds=1,
            liquidity_limit_quantity=10,
        ),
        filled_quantity=8,
        fill_price=101.25,
        fee_amount=0.25,
        partial_fill=True,
    )

    assert fill.family == "osca.backtest.fill"
    assert fill.fill_model.model_id == "bar-close-v1"


def test_simulated_fill_rejects_liquidity_overfill() -> None:
    with pytest.raises(ValidationError, match="liquidity limit"):
        SimulatedFill(
            request_id=uuid4(),
            order_intent_id=uuid4(),
            market_observation_id=uuid4(),
            fill_model=FillModelMetadata(
                model_id="bar-close-v1",
                version="1.0.0",
                liquidity_limit_quantity=5,
            ),
            filled_quantity=6,
            fill_price=100,
        )


def test_journal_transaction_must_balance_by_currency() -> None:
    request_id = uuid4()
    source_event_id = uuid4()

    transaction = JournalTransaction(
        request_id=request_id,
        source_event_id=source_event_id,
        effective_at=datetime(2026, 1, 1, tzinfo=UTC),
        description="simulated fill cash settlement",
        lines=(
            JournalLine(
                account="positions",
                side=JournalLineSide.DEBIT,
                amount=100,
                currency="USD",
            ),
            JournalLine(
                account="cash",
                side=JournalLineSide.CREDIT,
                amount=100,
                currency="USD",
            ),
        ),
    )

    assert transaction.request_id == request_id

    with pytest.raises(ValidationError, match="balance by currency"):
        JournalTransaction(
            request_id=request_id,
            source_event_id=source_event_id,
            effective_at=datetime(2026, 1, 1, tzinfo=UTC),
            description="imbalanced settlement",
            lines=(
                JournalLine(
                    account="positions",
                    side=JournalLineSide.DEBIT,
                    amount=100,
                    currency="USD",
                ),
                JournalLine(
                    account="cash",
                    side=JournalLineSide.CREDIT,
                    amount=99,
                    currency="USD",
                ),
            ),
        )


def test_risk_decision_and_projection_contracts_are_rebuildable() -> None:
    risk = RiskDecision(
        request_id=uuid4(),
        order_intent_id=uuid4(),
        policy_id="account.max-position",
        policy_version="1.0.0",
        action=RiskDecisionAction.APPROVE,
        rationale="within configured exposure",
    )
    valuation = ValuationSnapshot(
        request_id=risk.request_id,
        effective_at=datetime(2026, 1, 1, tzinfo=UTC),
        valuation_version="base-v1",
        holdings=(
            ValuationHolding(
                instrument_id=uuid4(),
                quantity=2,
                price=50,
                price_currency="USD",
                price_source_id="dataset.bar.close",
            ),
        ),
    )
    projection = PortfolioProjection(
        request_id=risk.request_id,
        journal_transaction_ids=(uuid4(),),
        valuation_id=valuation.valuation_id,
    )

    assert projection.valuation_id == valuation.valuation_id
