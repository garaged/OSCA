from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from osca.backtesting.api import OrderIntent, OrderIntentSide, OrderIntentType
from osca.backtesting.eventing import (
    OrderLifecycleState,
    FillModelMetadata,
    PortfolioProjection,
    SQLiteF2ValidationStore,
    ValuationSnapshot,
    build_fill_journal_transaction,
    build_order_lifecycle_event,
    evaluate_promotion_gate,
    simulate_bar_fill,
)


def make_order() -> OrderIntent:
    return OrderIntent(
        decision_id=uuid4(),
        instrument_id=uuid4(),
        side=OrderIntentSide.BUY,
        order_type=OrderIntentType.MARKET,
        quantity=3,
    )


def test_f2_validation_store_round_trips_validation_records(tmp_path: Path) -> None:
    request_id = uuid4()
    order = make_order()
    lifecycle = build_order_lifecycle_event(
        request_id=request_id,
        order_intent=order,
        state=OrderLifecycleState.CREATED,
        rationale="created from M6 order intent",
        effective_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    fill = simulate_bar_fill(
        request_id=request_id,
        order_intent=order,
        market_observation_id=uuid4(),
        fill_model=FillModelMetadata(model_id="bar-close-v1", version="1.0.0"),
        observed_price=25,
        effective_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    transaction = build_fill_journal_transaction(
        request_id=request_id,
        order_intent=order,
        fill=fill,
    )
    valuation = ValuationSnapshot(
        request_id=request_id,
        effective_at=datetime(2026, 1, 1, tzinfo=UTC),
        valuation_version="base-v1",
    )
    projection = PortfolioProjection(
        request_id=request_id,
        journal_transaction_ids=(transaction.transaction_id,),
        valuation_id=valuation.valuation_id,
    )
    gate = evaluate_promotion_gate(
        request_id=request_id,
        candidate_id="candidate.mean-reversion",
        findings=(),
    )

    store = SQLiteF2ValidationStore(tmp_path / "f2.sqlite")
    store.initialize()
    store.save_order_lifecycle_event(lifecycle)
    store.save_fill(fill)
    store.save_journal_transaction(transaction)
    store.save_valuation_snapshot(valuation)
    store.save_projection(projection)
    store.save_promotion_gate(gate)

    assert store.list_order_lifecycle_events(request_id) == (lifecycle,)
    assert store.list_fills(request_id) == (fill,)
    assert store.list_journal_transactions(request_id) == (transaction,)
    assert store.list_valuation_snapshots(request_id) == (valuation,)
    assert store.list_projections(request_id) == (projection,)
    assert store.list_promotion_gates(request_id) == (gate,)


def test_f2_validation_store_filters_by_request(tmp_path: Path) -> None:
    selected_request_id = uuid4()
    other_request_id = uuid4()
    selected_order = make_order()
    other_order = make_order()
    selected_lifecycle = build_order_lifecycle_event(
        request_id=selected_request_id,
        order_intent=selected_order,
        state=OrderLifecycleState.CREATED,
        rationale="selected",
        effective_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    other_lifecycle = build_order_lifecycle_event(
        request_id=other_request_id,
        order_intent=other_order,
        state=OrderLifecycleState.CREATED,
        rationale="other",
        effective_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    store = SQLiteF2ValidationStore(tmp_path / "f2.sqlite")
    store.initialize()
    store.save_order_lifecycle_event(selected_lifecycle)
    store.save_order_lifecycle_event(other_lifecycle)

    assert store.list_order_lifecycle_events(selected_request_id) == (selected_lifecycle,)
