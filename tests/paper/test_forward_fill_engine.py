from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from pydantic import ValidationError
import pytest

from osca.paper.fill_engine import confirm_simulated_order, evaluate_fill
from osca.paper.order_contracts import (
    ExecutionAssumptions,
    OrderSide,
    OrderSourceKind,
    PaperMarketBar,
    SimulatedOrderDraft,
    SimulatedOrderType,
)


RUN_ID = UUID("10000000-0000-0000-0000-000000000001")
ACCOUNT_ID = UUID("20000000-0000-0000-0000-000000000002")
PORTFOLIO_ID = UUID("30000000-0000-0000-0000-000000000003")
ASSUMPTION_ID = UUID("40000000-0000-0000-0000-000000000004")
DATASET_ID = UUID("50000000-0000-0000-0000-000000000005")


def at(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 8, 21, hour, minute, tzinfo=UTC)


def assumptions(**overrides: object) -> ExecutionAssumptions:
    values: dict[str, object] = {
        "assumption_id": ASSUMPTION_ID,
        "spread_bps": Decimal("0"),
        "slippage_bps": Decimal("0"),
        "fee_bps": Decimal("0"),
        "flat_fee": Decimal("0"),
        "max_volume_participation": Decimal("1"),
        "require_volume": True,
    }
    values.update(overrides)
    return ExecutionAssumptions(**values)


def draft(
    order_type: SimulatedOrderType = SimulatedOrderType.MARKET,
    side: OrderSide = OrderSide.BUY,
    **overrides: object,
) -> SimulatedOrderDraft:
    values: dict[str, object] = {
        "paper_run_id": RUN_ID,
        "paper_account_id": ACCOUNT_ID,
        "portfolio_id": PORTFOLIO_ID,
        "source_kind": OrderSourceKind.MANUAL,
        "source_id": "manual-1",
        "instrument_id": "equity:XNAS:AAPL",
        "side": side,
        "order_type": order_type,
        "quantity": Decimal("10"),
        "assumption_id": ASSUMPTION_ID,
        "created_at": at(9),
    }
    values.update(overrides)
    return SimulatedOrderDraft(**values)


def bar(
    start_hour: int,
    *,
    open_price: str = "100",
    high: str = "105",
    low: str = "95",
    close: str = "101",
    volume: str | None = "1000",
    complete: bool = True,
    session_open: bool = True,
) -> PaperMarketBar:
    start = at(start_hour)
    return PaperMarketBar(
        instrument_id="equity:XNAS:AAPL",
        dataset_revision_id=DATASET_ID,
        source_id=f"fixture-{start_hour}",
        timeframe="1h",
        bar_started_at=start,
        bar_ended_at=start + timedelta(hours=1),
        available_at=start + timedelta(hours=1, seconds=1),
        open=Decimal(open_price),
        high=Decimal(high),
        low=Decimal(low),
        close=Decimal(close),
        volume=None if volume is None else Decimal(volume),
        complete=complete,
        market_calendar_id="XNAS",
        session_open=session_open,
    )


def test_order_contracts_reject_unsupported_field_combinations() -> None:
    with pytest.raises(ValidationError, match="market orders cannot have"):
        draft(limit_price=Decimal("100"))
    with pytest.raises(ValidationError, match="limit orders require only limit_price"):
        draft(SimulatedOrderType.LIMIT)
    with pytest.raises(ValidationError, match="scheduled market orders require scheduled_at"):
        draft(SimulatedOrderType.SCHEDULED_MARKET)


def test_confirmation_applies_latency_and_is_simulated_only() -> None:
    execution = assumptions(latency_ms=1500)
    confirmation, order = confirm_simulated_order(
        draft(), execution, confirmed_at=at(9, 30)
    )
    assert confirmation.simulated_only is True
    assert order.eligible_at == at(9, 30) + timedelta(milliseconds=1500)
    assert order.confirmation_id == confirmation.confirmation_id


def test_mid_bar_activation_skips_bar_and_next_market_bar_fills_at_open() -> None:
    execution = assumptions()
    _, order = confirm_simulated_order(draft(), execution, confirmed_at=at(9, 30))
    skipped = evaluate_fill(order, execution, bar(9), remaining_quantity=Decimal("10"))
    accepted = evaluate_fill(order, execution, bar(10), remaining_quantity=Decimal("10"))
    assert skipped.can_fill is False
    assert "before bar start" in skipped.reason
    assert accepted.can_fill is True
    assert accepted.quantity == Decimal("10")
    assert accepted.execution_price == Decimal("100")


def test_incomplete_or_closed_session_bar_never_fills() -> None:
    execution = assumptions()
    _, order = confirm_simulated_order(draft(), execution, confirmed_at=at(8))
    assert evaluate_fill(
        order,
        execution,
        bar(9, complete=False),
        remaining_quantity=Decimal("10"),
    ).can_fill is False
    assert evaluate_fill(
        order,
        execution,
        bar(9, session_open=False),
        remaining_quantity=Decimal("10"),
    ).can_fill is False


def test_limit_uses_better_open_but_never_violates_limit_after_adjustment() -> None:
    execution = assumptions(spread_bps=Decimal("10"), slippage_bps=Decimal("10"))
    _, gap_buy = confirm_simulated_order(
        draft(SimulatedOrderType.LIMIT, limit_price=Decimal("100")),
        execution,
        confirmed_at=at(8),
    )
    better = evaluate_fill(
        gap_buy,
        execution,
        bar(9, open_price="98", high="102", low="97", close="101"),
        remaining_quantity=Decimal("10"),
    )
    assert better.can_fill is True
    assert better.execution_price == Decimal("98.196")
    _, at_limit = confirm_simulated_order(
        draft(SimulatedOrderType.LIMIT, limit_price=Decimal("100")),
        execution,
        confirmed_at=at(8),
    )
    blocked = evaluate_fill(
        at_limit,
        execution,
        bar(9, open_price="101", high="102", low="99", close="100"),
        remaining_quantity=Decimal("10"),
    )
    assert blocked.can_fill is False
    assert "limit protection" in blocked.reason


def test_sell_limit_and_stop_apply_directional_rules() -> None:
    execution = assumptions(spread_bps=Decimal("10"))
    _, limit_order = confirm_simulated_order(
        draft(
            SimulatedOrderType.LIMIT,
            side=OrderSide.SELL,
            limit_price=Decimal("100"),
        ),
        execution,
        confirmed_at=at(8),
    )
    limit_fill = evaluate_fill(
        limit_order,
        execution,
        bar(9, open_price="103", high="104", low="99", close="102"),
        remaining_quantity=Decimal("10"),
    )
    assert limit_fill.can_fill is True
    assert limit_fill.execution_price == Decimal("102.897")
    _, stop_order = confirm_simulated_order(
        draft(
            SimulatedOrderType.STOP,
            side=OrderSide.SELL,
            stop_price=Decimal("100"),
        ),
        execution,
        confirmed_at=at(8),
    )
    stop_fill = evaluate_fill(
        stop_order,
        execution,
        bar(9, open_price="95", high="97", low="90", close="92"),
        remaining_quantity=Decimal("10"),
    )
    assert stop_fill.can_fill is True
    assert stop_fill.execution_price == Decimal("94.905")


def test_stop_gap_uses_open_and_can_fill_worse_than_stop() -> None:
    execution = assumptions(spread_bps=Decimal("20"), slippage_bps=Decimal("30"))
    _, order = confirm_simulated_order(
        draft(SimulatedOrderType.STOP, stop_price=Decimal("100")),
        execution,
        confirmed_at=at(8),
    )
    decision = evaluate_fill(
        order,
        execution,
        bar(9, open_price="105", high="108", low="103", close="106"),
        remaining_quantity=Decimal("10"),
    )
    assert decision.can_fill is True
    assert decision.execution_price == Decimal("105.525")
    assert decision.execution_price > Decimal("100")


def test_volume_participation_creates_deterministic_partial_fill() -> None:
    execution = assumptions(max_volume_participation=Decimal("0.10"))
    _, order = confirm_simulated_order(
        draft(quantity=Decimal("20")), execution, confirmed_at=at(8)
    )
    decision = evaluate_fill(
        order,
        execution,
        bar(9, volume="50"),
        remaining_quantity=Decimal("20"),
    )
    assert decision.can_fill is True
    assert decision.quantity == Decimal("5.0")


def test_missing_required_volume_blocks_without_unlimited_liquidity() -> None:
    execution = assumptions(require_volume=True)
    _, order = confirm_simulated_order(draft(), execution, confirmed_at=at(8))
    decision = evaluate_fill(
        order,
        execution,
        bar(9, volume=None),
        remaining_quantity=Decimal("10"),
    )
    assert decision.can_fill is False
    assert "volume evidence" in decision.reason


def test_fees_and_adverse_adjustments_are_decimal_safe() -> None:
    execution = assumptions(
        spread_bps=Decimal("5"),
        slippage_bps=Decimal("10"),
        fee_bps=Decimal("20"),
        flat_fee=Decimal("1.25"),
    )
    _, order = confirm_simulated_order(
        draft(quantity=Decimal("2")), execution, confirmed_at=at(8)
    )
    decision = evaluate_fill(
        order,
        execution,
        bar(9, open_price="100", high="101", low="99", close="100"),
        remaining_quantity=Decimal("2"),
    )
    assert decision.execution_price == Decimal("100.1500")
    assert decision.fee == Decimal("1.6506000")


def test_scheduled_order_waits_for_schedule_and_latency() -> None:
    execution = assumptions(latency_ms=60_000)
    _, order = confirm_simulated_order(
        draft(SimulatedOrderType.SCHEDULED_MARKET, scheduled_at=at(10)),
        execution,
        confirmed_at=at(8),
    )
    assert order.eligible_at == at(10, 1)
    assert evaluate_fill(
        order,
        execution,
        bar(10),
        remaining_quantity=Decimal("10"),
    ).can_fill is False
    assert evaluate_fill(
        order,
        execution,
        bar(11),
        remaining_quantity=Decimal("10"),
    ).can_fill is True
