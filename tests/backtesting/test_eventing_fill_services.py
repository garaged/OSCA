from datetime import UTC, datetime
from uuid import uuid4

from osca.backtesting.api import OrderIntent, OrderIntentSide, OrderIntentType
from osca.backtesting.eventing import (
    FillModelMetadata,
    JournalLineSide,
    OrderLifecycleState,
    build_fill_journal_transaction,
    build_order_lifecycle_event,
    simulate_bar_fill,
    validate_journal_transaction,
)


def make_order(side: OrderIntentSide = OrderIntentSide.BUY) -> OrderIntent:
    return OrderIntent(
        decision_id=uuid4(),
        instrument_id=uuid4(),
        side=side,
        order_type=OrderIntentType.MARKET,
        quantity=10,
    )


def test_build_order_lifecycle_event_preserves_order_intent() -> None:
    request_id = uuid4()
    order = make_order()

    event = build_order_lifecycle_event(
        request_id=request_id,
        order_intent=order,
        state=OrderLifecycleState.ACCEPTED,
        rationale="accepted by deterministic F2 checks",
        effective_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    assert event.request_id == request_id
    assert event.order_intent_id == order.order_intent_id
    assert event.state is OrderLifecycleState.ACCEPTED


def test_simulate_bar_fill_applies_liquidity_limit_and_cost_model() -> None:
    order = make_order()
    fill = simulate_bar_fill(
        request_id=uuid4(),
        order_intent=order,
        market_observation_id=uuid4(),
        fill_model=FillModelMetadata(
            model_id="bar-close-v1",
            version="1.0.0",
            spread_bps=2,
            slippage_bps=3,
            liquidity_limit_quantity=4,
        ),
        observed_price=100,
        effective_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    assert fill.partial_fill is True
    assert fill.filled_quantity == 4
    assert fill.fill_price > 100
    assert fill.fee_amount > 0


def test_build_fill_journal_transaction_balances_buy_fill() -> None:
    request_id = uuid4()
    order = make_order(OrderIntentSide.BUY)
    fill = simulate_bar_fill(
        request_id=request_id,
        order_intent=order,
        market_observation_id=uuid4(),
        fill_model=FillModelMetadata(model_id="bar-close-v1", version="1.0.0"),
        observed_price=100,
        effective_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    transaction = build_fill_journal_transaction(
        request_id=request_id,
        order_intent=order,
        fill=fill,
    )

    assert validate_journal_transaction(transaction) == ()
    assert [line.side for line in transaction.lines] == [
        JournalLineSide.DEBIT,
        JournalLineSide.DEBIT,
        JournalLineSide.CREDIT,
    ]


def test_build_fill_journal_transaction_balances_sell_fill() -> None:
    request_id = uuid4()
    order = make_order(OrderIntentSide.SELL)
    fill = simulate_bar_fill(
        request_id=request_id,
        order_intent=order,
        market_observation_id=uuid4(),
        fill_model=FillModelMetadata(model_id="bar-close-v1", version="1.0.0"),
        observed_price=100,
        effective_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    transaction = build_fill_journal_transaction(
        request_id=request_id,
        order_intent=order,
        fill=fill,
    )

    assert validate_journal_transaction(transaction) == ()
    assert [line.side for line in transaction.lines] == [
        JournalLineSide.DEBIT,
        JournalLineSide.DEBIT,
        JournalLineSide.CREDIT,
    ]
