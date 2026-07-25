from itertools import pairwise
from uuid import UUID

from datetime import UTC, datetime

from osca.backtesting.api import OrderIntent, OrderIntentSide
from osca.backtesting.eventing.contracts import (
    FillModelMetadata,
    JournalLine,
    JournalLineSide,
    JournalTransaction,
    OrderLifecycleEvent,
    OrderLifecycleState,
    PromotionGateDecision,
    ReconciliationFinding,
    SimulatedFill,
)

_TERMINAL_STATES = {
    OrderLifecycleState.REJECTED,
    OrderLifecycleState.CANCELLED,
    OrderLifecycleState.EXPIRED,
    OrderLifecycleState.FILLED,
}

_ALLOWED_TRANSITIONS: dict[OrderLifecycleState, set[OrderLifecycleState]] = {
    OrderLifecycleState.CREATED: {
        OrderLifecycleState.ACCEPTED,
        OrderLifecycleState.REJECTED,
        OrderLifecycleState.CANCELLED,
        OrderLifecycleState.EXPIRED,
    },
    OrderLifecycleState.ACCEPTED: {
        OrderLifecycleState.PARTIALLY_FILLED,
        OrderLifecycleState.FILLED,
        OrderLifecycleState.CANCELLED,
        OrderLifecycleState.EXPIRED,
    },
    OrderLifecycleState.PARTIALLY_FILLED: {
        OrderLifecycleState.PARTIALLY_FILLED,
        OrderLifecycleState.FILLED,
        OrderLifecycleState.CANCELLED,
        OrderLifecycleState.EXPIRED,
    },
}


def validate_lifecycle_sequence(
    events: tuple[OrderLifecycleEvent, ...],
) -> tuple[ReconciliationFinding, ...]:
    if not events:
        return (
            ReconciliationFinding(
                code="missing_lifecycle_events",
                severity="error",
                message="order lifecycle sequence must contain at least one event",
            ),
        )

    findings: list[ReconciliationFinding] = []
    ordered = tuple(sorted(events, key=lambda event: event.effective_at))
    first = ordered[0]
    if first.state is not OrderLifecycleState.CREATED:
        findings.append(
            ReconciliationFinding(
                code="lifecycle_missing_created",
                severity="error",
                message="order lifecycle must start with created state",
            )
        )

    for previous, current in pairwise(ordered):
        if previous.request_id != current.request_id:
            findings.append(
                ReconciliationFinding(
                    code="lifecycle_request_mismatch",
                    severity="error",
                    message="order lifecycle sequence cannot mix requests",
                )
            )
        if previous.order_intent_id != current.order_intent_id:
            findings.append(
                ReconciliationFinding(
                    code="lifecycle_order_mismatch",
                    severity="error",
                    message="order lifecycle sequence cannot mix order intents",
                )
            )
        if previous.state in _TERMINAL_STATES:
            findings.append(
                ReconciliationFinding(
                    code="lifecycle_terminal_regression",
                    severity="error",
                    message="terminal order lifecycle states cannot transition further",
                )
            )
            continue
        allowed = _ALLOWED_TRANSITIONS.get(previous.state, set())
        if current.state not in allowed:
            findings.append(
                ReconciliationFinding(
                    code="lifecycle_invalid_transition",
                    severity="error",
                    message=(
                        f"invalid lifecycle transition from {previous.state} "
                        f"to {current.state}"
                    ),
                )
            )
    return tuple(findings)


def validate_journal_transaction(
    transaction: JournalTransaction,
) -> tuple[ReconciliationFinding, ...]:
    try:
        JournalTransaction.model_validate(transaction.model_dump(mode="json"))
    except ValueError as exc:
        return (
            ReconciliationFinding(
                code="journal_imbalance",
                severity="error",
                message=str(exc),
            ),
        )
    return ()


def evaluate_promotion_gate(
    *,
    request_id: UUID,
    candidate_id: str,
    findings: tuple[ReconciliationFinding, ...],
) -> PromotionGateDecision:
    approved = not any(finding.severity == "error" for finding in findings)
    return PromotionGateDecision(
        request_id=request_id,
        candidate_id=candidate_id,
        approved_for_paper_evaluation=approved,
        findings=findings,
    )


def build_order_lifecycle_event(
    *,
    request_id: UUID,
    order_intent: OrderIntent,
    state: OrderLifecycleState,
    rationale: str,
    effective_at: datetime | None = None,
) -> OrderLifecycleEvent:
    return OrderLifecycleEvent.from_order_intent(
        request_id=request_id,
        order_intent=order_intent,
        state=state,
        rationale=rationale,
        effective_at=effective_at or datetime.now(UTC),
    )


def simulate_bar_fill(
    *,
    request_id: UUID,
    order_intent: OrderIntent,
    market_observation_id: UUID,
    fill_model: FillModelMetadata,
    observed_price: float,
    effective_at: datetime | None = None,
) -> SimulatedFill:
    quantity = order_intent.quantity
    partial_fill = False
    if (
        fill_model.liquidity_limit_quantity is not None
        and quantity > fill_model.liquidity_limit_quantity
    ):
        quantity = fill_model.liquidity_limit_quantity
        partial_fill = True

    slippage_multiplier = (
        1 + (fill_model.spread_bps + fill_model.slippage_bps) / 10_000
        if order_intent.side is OrderIntentSide.BUY
        else 1 - (fill_model.spread_bps + fill_model.slippage_bps) / 10_000
    )
    fill_price = observed_price * slippage_multiplier
    trade_value = quantity * fill_price
    fee_amount = trade_value * 0.0001

    return SimulatedFill(
        request_id=request_id,
        order_intent_id=order_intent.order_intent_id,
        market_observation_id=market_observation_id,
        fill_model=fill_model,
        filled_quantity=quantity,
        fill_price=fill_price,
        fee_amount=fee_amount,
        partial_fill=partial_fill,
        effective_at=effective_at or datetime.now(UTC),
    )


def build_fill_journal_transaction(
    *,
    request_id: UUID,
    order_intent: OrderIntent,
    fill: SimulatedFill,
    cash_account: str = "cash",
    position_account: str = "positions",
    fee_account: str = "fees",
) -> JournalTransaction:
    trade_value = fill.filled_quantity * fill.fill_price
    if order_intent.side is OrderIntentSide.BUY:
        lines = (
            JournalLine(
                account=position_account,
                side=JournalLineSide.DEBIT,
                amount=trade_value,
                currency=fill.fee_currency,
                instrument_id=order_intent.instrument_id,
            ),
            JournalLine(
                account=fee_account,
                side=JournalLineSide.DEBIT,
                amount=fill.fee_amount,
                currency=fill.fee_currency,
            ),
            JournalLine(
                account=cash_account,
                side=JournalLineSide.CREDIT,
                amount=trade_value + fill.fee_amount,
                currency=fill.fee_currency,
            ),
        )
    else:
        lines = (
            JournalLine(
                account=cash_account,
                side=JournalLineSide.DEBIT,
                amount=trade_value - fill.fee_amount,
                currency=fill.fee_currency,
            ),
            JournalLine(
                account=fee_account,
                side=JournalLineSide.DEBIT,
                amount=fill.fee_amount,
                currency=fill.fee_currency,
            ),
            JournalLine(
                account=position_account,
                side=JournalLineSide.CREDIT,
                amount=trade_value,
                currency=fill.fee_currency,
                instrument_id=order_intent.instrument_id,
            ),
        )
    return JournalTransaction(
        request_id=request_id,
        source_event_id=fill.fill_id,
        effective_at=fill.effective_at,
        description="simulated fill settlement",
        lines=lines,
    )
