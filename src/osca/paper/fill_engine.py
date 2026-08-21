"""Deterministic completed-bar fill rules for D9 simulated orders."""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

from osca.paper.order_contracts import (
    ExecutionAssumptions,
    FillDecision,
    OrderSide,
    PaperMarketBar,
    SimulatedOrder,
    SimulatedOrderConfirmation,
    SimulatedOrderDraft,
    SimulatedOrderStatus,
    SimulatedOrderType,
)

_BPS = Decimal("10000")


def confirm_simulated_order(
    draft: SimulatedOrderDraft,
    assumptions: ExecutionAssumptions,
    *,
    confirmed_at: datetime,
) -> tuple[SimulatedOrderConfirmation, SimulatedOrder]:
    """Freeze one draft into local simulated-order authority."""
    if draft.assumption_id != assumptions.assumption_id:
        raise ValueError("draft assumption_id does not match execution assumptions")
    if confirmed_at.tzinfo is None or confirmed_at.utcoffset() is None:
        raise ValueError("confirmed_at must be timezone-aware")

    confirmation = SimulatedOrderConfirmation(
        draft_id=draft.draft_id,
        draft_version=draft.draft_version,
        paper_run_id=draft.paper_run_id,
        portfolio_id=draft.portfolio_id,
        assumption_id=draft.assumption_id,
        confirmed_at=confirmed_at,
    )
    activation_floor = confirmed_at
    if draft.scheduled_at is not None and draft.scheduled_at > activation_floor:
        activation_floor = draft.scheduled_at
    eligible_at = activation_floor + timedelta(milliseconds=assumptions.latency_ms)
    order = SimulatedOrder(
        confirmation_id=confirmation.confirmation_id,
        draft_id=draft.draft_id,
        draft_version=draft.draft_version,
        paper_run_id=draft.paper_run_id,
        paper_account_id=draft.paper_account_id,
        portfolio_id=draft.portfolio_id,
        instrument_id=draft.instrument_id,
        side=draft.side,
        order_type=draft.order_type,
        quantity=draft.quantity,
        limit_price=draft.limit_price,
        stop_price=draft.stop_price,
        scheduled_at=draft.scheduled_at,
        expires_at=draft.expires_at,
        assumption_id=draft.assumption_id,
        lot_allocations=draft.lot_allocations,
        confirmed_at=confirmed_at,
        eligible_at=eligible_at,
        status=SimulatedOrderStatus.CONFIRMED,
    )
    return confirmation, order


def evaluate_fill(
    order: SimulatedOrder,
    assumptions: ExecutionAssumptions,
    market_bar: PaperMarketBar,
    *,
    remaining_quantity: Decimal,
) -> FillDecision:
    """Evaluate one complete governed bar without mutating order/accounting state."""
    blocked = _eligibility_reason(order, assumptions, market_bar, remaining_quantity)
    if blocked is not None:
        return FillDecision(can_fill=False, reason=blocked)

    reference_price = _reference_price(order, market_bar)
    if reference_price is None:
        return FillDecision(can_fill=False, reason="order trigger not reached on eligible bar")

    execution_price = _adverse_price(reference_price, order.side, assumptions)
    if order.order_type is SimulatedOrderType.LIMIT:
        assert order.limit_price is not None
        if order.side is OrderSide.BUY and execution_price > order.limit_price:
            return FillDecision(
                can_fill=False,
                reason="limit protection blocks execution above buy limit",
            )
        if order.side is OrderSide.SELL and execution_price < order.limit_price:
            return FillDecision(
                can_fill=False,
                reason="limit protection blocks execution below sell limit",
            )

    quantity = _fillable_quantity(remaining_quantity, assumptions, market_bar)
    if quantity <= Decimal("0"):
        return FillDecision(can_fill=False, reason="eligible bar has no permitted liquidity")

    fee = quantity * execution_price * assumptions.fee_bps / _BPS + assumptions.flat_fee
    return FillDecision(
        can_fill=True,
        reason="deterministic simulated fill available",
        quantity=quantity,
        execution_price=execution_price,
        fee=fee,
    )


def _eligibility_reason(
    order: SimulatedOrder,
    assumptions: ExecutionAssumptions,
    market_bar: PaperMarketBar,
    remaining_quantity: Decimal,
) -> str | None:
    if order.assumption_id != assumptions.assumption_id:
        return "order assumption identity does not match execution assumptions"
    if remaining_quantity <= Decimal("0"):
        return "order has no remaining quantity"
    if remaining_quantity > order.quantity:
        return "remaining quantity cannot exceed original order quantity"
    if market_bar.instrument_id != order.instrument_id:
        return "market evidence instrument does not match order"
    if not market_bar.complete:
        return "incomplete market bar cannot be fill authority"
    if not market_bar.session_open:
        return "market calendar/session does not permit simulated filling"
    if order.expires_at is not None and market_bar.bar_started_at >= order.expires_at:
        return "simulated order expired before eligible bar"
    if order.eligible_at > market_bar.bar_started_at:
        return "order was not eligible before bar start; ambiguous intrabar path skipped"
    if assumptions.require_volume and market_bar.volume is None:
        return "required volume evidence is missing"
    return None


def _reference_price(order: SimulatedOrder, market_bar: PaperMarketBar) -> Decimal | None:
    if order.order_type in {SimulatedOrderType.MARKET, SimulatedOrderType.SCHEDULED_MARKET}:
        return market_bar.open

    if order.order_type is SimulatedOrderType.LIMIT:
        assert order.limit_price is not None
        if order.side is OrderSide.BUY:
            if market_bar.low > order.limit_price:
                return None
            return market_bar.open if market_bar.open < order.limit_price else order.limit_price
        if market_bar.high < order.limit_price:
            return None
        return market_bar.open if market_bar.open > order.limit_price else order.limit_price

    assert order.order_type is SimulatedOrderType.STOP
    assert order.stop_price is not None
    if order.side is OrderSide.BUY:
        if market_bar.high < order.stop_price:
            return None
        return market_bar.open if market_bar.open > order.stop_price else order.stop_price
    if market_bar.low > order.stop_price:
        return None
    return market_bar.open if market_bar.open < order.stop_price else order.stop_price


def _adverse_price(
    reference_price: Decimal,
    side: OrderSide,
    assumptions: ExecutionAssumptions,
) -> Decimal:
    adjustment = (assumptions.spread_bps + assumptions.slippage_bps) / _BPS
    if side is OrderSide.BUY:
        return reference_price * (Decimal("1") + adjustment)
    return reference_price * (Decimal("1") - adjustment)


def _fillable_quantity(
    remaining_quantity: Decimal,
    assumptions: ExecutionAssumptions,
    market_bar: PaperMarketBar,
) -> Decimal:
    if market_bar.volume is None:
        return remaining_quantity
    capacity = market_bar.volume * assumptions.max_volume_participation
    return min(remaining_quantity, capacity)
