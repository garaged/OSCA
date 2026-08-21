"""D9 orchestration for confirmed simulated orders, fills, risk, and D8 posting."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Literal
from uuid import NAMESPACE_URL, UUID, uuid5

from pydantic import BaseModel, ConfigDict

from osca.paper.accounting import PortfolioAccountingError, PortfolioAccountingService
from osca.paper.accounting_contracts import PortfolioProjection
from osca.paper.contracts import (
    PaperControlDecision,
    PaperHealthGateDecision,
    PaperRunCheckpoint,
)
from osca.paper.fill_engine import confirm_simulated_order, evaluate_fill
from osca.paper.order_contracts import (
    ExecutionAssumptions,
    FillDecision,
    OrderLifecycleEvent,
    OrderSide,
    PaperMarketBar,
    PaperRiskDecision,
    PaperRunBinding,
    RiskDecisionStatus,
    SimulatedFill,
    SimulatedOrder,
    SimulatedOrderConfirmation,
    SimulatedOrderDraft,
    SimulatedOrderStatus,
)
from osca.paper.order_persistence import SQLitePaperOrderStore

_ZERO = Decimal("0")
_TERMINAL = {
    SimulatedOrderStatus.FILLED,
    SimulatedOrderStatus.CANCELLED,
    SimulatedOrderStatus.EXPIRED,
    SimulatedOrderStatus.REJECTED,
}


class ForwardPaperError(ValueError):
    """Raised when D9 processing would violate forward-paper invariants."""


class ConfirmationResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.paper.confirmation-result"] = "osca.paper.confirmation-result"
    confirmation: SimulatedOrderConfirmation
    order: SimulatedOrder
    risk_decision: PaperRiskDecision
    lifecycle: tuple[OrderLifecycleEvent, ...]


class ForwardStepResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.paper.forward-step"] = "osca.paper.forward-step"
    order_id: UUID
    market_evidence_id: UUID
    decision: FillDecision
    risk_decision: PaperRiskDecision | None = None
    fill: SimulatedFill | None = None
    lifecycle_event: OrderLifecycleEvent | None = None
    accounting_event_id: UUID | None = None


class ForwardPaperService:
    """Profile-scoped D9 authority layered over D8 accounting."""

    def __init__(
        self,
        store: SQLitePaperOrderStore,
        accounting: PortfolioAccountingService,
    ) -> None:
        self.store = store
        self.accounting = accounting
        self.store.initialize()

    @classmethod
    def for_profile(cls, profile_root: Path) -> ForwardPaperService:
        return cls(
            SQLitePaperOrderStore(profile_root / "paper-orders.sqlite"),
            PortfolioAccountingService.for_profile(profile_root),
        )

    def bind_run(
        self,
        *,
        paper_run_id: UUID,
        paper_account_id: UUID,
        portfolio_id: UUID,
        approved_candidate_id: UUID | None = None,
        created_at: datetime | None = None,
    ) -> PaperRunBinding:
        self.accounting.get_portfolio(portfolio_id)
        binding = PaperRunBinding(
            paper_run_id=paper_run_id,
            paper_account_id=paper_account_id,
            portfolio_id=portfolio_id,
            approved_candidate_id=approved_candidate_id,
            created_at=_utc(created_at),
        )
        return self.store.append_binding(binding)

    def retain_assumptions(self, assumptions: ExecutionAssumptions) -> ExecutionAssumptions:
        return self.store.append_assumptions(assumptions)

    def retain_draft(self, draft: SimulatedOrderDraft) -> SimulatedOrderDraft:
        binding = self.store.get_binding(draft.paper_run_id)
        if binding.paper_account_id != draft.paper_account_id:
            raise ForwardPaperError("draft paper account does not match run binding")
        if binding.portfolio_id != draft.portfolio_id:
            raise ForwardPaperError("draft portfolio does not match run binding")
        self.store.get_assumptions(draft.assumption_id)
        return self.store.append_draft(draft)

    def confirm_draft(
        self,
        draft: SimulatedOrderDraft,
        *,
        confirmed_at: datetime,
        control_decision: PaperControlDecision,
    ) -> ConfirmationResult:
        self._require_control(draft.paper_account_id, control_decision)
        retained = self.retain_draft(draft)
        assumptions = self.store.get_assumptions(retained.assumption_id)
        confirmation, order = confirm_simulated_order(
            retained,
            assumptions,
            confirmed_at=confirmed_at,
        )
        confirmation, order = self.store.append_confirmation_and_order(confirmation, order)
        confirmed_event = self._ensure_lifecycle(
            order,
            status=SimulatedOrderStatus.CONFIRMED,
            source_id=f"confirmation:{confirmation.confirmation_id}",
            reason="user confirmed simulated-only order draft",
            effective_at=confirmation.confirmed_at,
        )
        risk = self._activation_risk(order)
        self.store.append_risk_decision(risk)
        lifecycle = [confirmed_event]
        if risk.status is RiskDecisionStatus.REJECT:
            lifecycle.append(
                self._ensure_lifecycle(
                    order,
                    status=SimulatedOrderStatus.REJECTED,
                    source_id=f"risk:{risk.risk_decision_id}",
                    reason=risk.reason,
                    effective_at=risk.checked_at,
                )
            )
        return ConfirmationResult(
            confirmation=confirmation,
            order=order,
            risk_decision=risk,
            lifecycle=tuple(lifecycle),
        )

    def cancel_order(
        self,
        order_id: UUID,
        *,
        source_id: str,
        reason: str,
        effective_at: datetime | None = None,
    ) -> OrderLifecycleEvent:
        order = self.store.get_order(order_id)
        status = self.current_status(order_id)
        if status in _TERMINAL:
            raise ForwardPaperError(f"cannot cancel terminal simulated order in {status} state")
        return self._ensure_lifecycle(
            order,
            status=SimulatedOrderStatus.CANCELLED,
            source_id=source_id,
            reason=reason,
            effective_at=_utc(effective_at),
        )

    def current_status(self, order_id: UUID) -> SimulatedOrderStatus:
        order = self.store.get_order(order_id)
        events = self.store.list_lifecycle(order_id)
        return events[-1].status if events else order.status

    def remaining_quantity(self, order_id: UUID) -> Decimal:
        order = self.store.get_order(order_id)
        filled = sum((fill.quantity for fill in self.store.list_fills(order_id)), _ZERO)
        remaining = order.quantity - filled
        if remaining < _ZERO:
            raise ForwardPaperError("retained fills exceed original order quantity")
        return remaining

    def process_bar(
        self,
        order_id: UUID,
        market_bar: PaperMarketBar,
        *,
        control_decision: PaperControlDecision,
        health_gate: PaperHealthGateDecision,
    ) -> ForwardStepResult:
        order = self.store.get_order(order_id)
        self._require_control(order.paper_account_id, control_decision)
        self._require_health(order.paper_run_id, health_gate)
        status = self.current_status(order_id)
        if status in _TERMINAL:
            return ForwardStepResult(
                order_id=order_id,
                market_evidence_id=market_bar.evidence_id,
                decision=FillDecision(
                    can_fill=False,
                    reason=f"simulated order is terminal in {status} state",
                ),
            )
        existing = next(
            (
                fill
                for fill in self.store.list_fills(order_id)
                if fill.bar_evidence_id == market_bar.evidence_id
            ),
            None,
        )
        if existing is not None:
            accounting_event_id = self._post_fill(order, existing)
            replay_lifecycle = self._ensure_fill_lifecycle(order, existing)
            return ForwardStepResult(
                order_id=order_id,
                market_evidence_id=market_bar.evidence_id,
                decision=FillDecision(
                    can_fill=True,
                    reason="retained simulated fill replayed idempotently",
                    quantity=existing.quantity,
                    execution_price=existing.execution_price,
                    fee=existing.fee,
                ),
                fill=existing,
                lifecycle_event=replay_lifecycle,
                accounting_event_id=accounting_event_id,
            )
        assumptions = self.store.get_assumptions(order.assumption_id)
        remaining = self.remaining_quantity(order_id)
        decision = evaluate_fill(
            order,
            assumptions,
            market_bar,
            remaining_quantity=remaining,
        )
        if not decision.can_fill:
            no_fill_lifecycle = self._terminal_no_fill_lifecycle(order, market_bar, decision)
            return ForwardStepResult(
                order_id=order_id,
                market_evidence_id=market_bar.evidence_id,
                decision=decision,
                lifecycle_event=no_fill_lifecycle,
            )
        assert decision.execution_price is not None
        risk, allocations = self._fill_risk(
            order,
            decision,
            assumptions,
            prior_fills=self.store.list_fills(order_id),
            risk_source_id=f"bar:{market_bar.evidence_id}",
            checked_at=market_bar.available_at,
        )
        self.store.append_risk_decision(risk)
        if risk.status is not RiskDecisionStatus.ALLOW:
            risk_lifecycle: OrderLifecycleEvent | None = None
            if risk.status is RiskDecisionStatus.REJECT:
                risk_lifecycle = self._ensure_lifecycle(
                    order,
                    status=SimulatedOrderStatus.REJECTED,
                    source_id=f"risk:{risk.risk_decision_id}",
                    reason=risk.reason,
                    effective_at=market_bar.available_at,
                )
            return ForwardStepResult(
                order_id=order_id,
                market_evidence_id=market_bar.evidence_id,
                decision=FillDecision(can_fill=False, reason=risk.reason),
                risk_decision=risk,
                lifecycle_event=risk_lifecycle,
            )
        fill = self._make_fill(order, market_bar, decision, allocations)
        accounting_event_id = self._post_fill(order, fill)
        fill = self.store.append_fill(fill)
        fill_lifecycle = self._ensure_fill_lifecycle(order, fill)
        return ForwardStepResult(
            order_id=order_id,
            market_evidence_id=market_bar.evidence_id,
            decision=decision,
            risk_decision=risk,
            fill=fill,
            lifecycle_event=fill_lifecycle,
            accounting_event_id=accounting_event_id,
        )

    def checkpoint_run(
        self,
        paper_run_id: UUID,
        *,
        idempotency_key: str,
        last_processed_at: datetime,
        source_event_ids: tuple[UUID, ...],
    ) -> PaperRunCheckpoint:
        existing = self.store.get_checkpoint_by_key(paper_run_id, idempotency_key)
        if existing is not None:
            if (
                existing.last_processed_at != last_processed_at
                or existing.source_event_ids != source_event_ids
            ):
                raise ForwardPaperError(
                    "checkpoint idempotency key already exists with different recovery evidence"
                )
            return existing
        latest = self.store.latest_checkpoint(paper_run_id)
        checkpoint = PaperRunCheckpoint(
            paper_run_id=paper_run_id,
            sequence_number=0 if latest is None else latest.sequence_number + 1,
            idempotency_key=idempotency_key,
            last_processed_at=last_processed_at,
            source_event_ids=source_event_ids,
            created_at=_utc(None),
        )
        return self.store.append_checkpoint(checkpoint)

    def _activation_risk(self, order: SimulatedOrder) -> PaperRiskDecision:
        projection = self.accounting.project(order.portfolio_id)
        source_id = f"activation:{order.confirmation_id}"
        checked_at = order.confirmed_at
        if order.side is OrderSide.SELL:
            matching = [
                lot
                for lot in projection.lots
                if lot.instrument_id == order.instrument_id
                and lot.currency == order.currency
                and lot.quantity > _ZERO
            ]
            available = sum((lot.quantity for lot in matching), _ZERO)
            if available < order.quantity:
                return _risk(
                    order,
                    RiskDecisionStatus.REJECT,
                    "insufficient held quantity",
                    source_id=source_id,
                    checked_at=checked_at,
                )
            if len(matching) > 1 and not order.lot_allocations:
                return _risk(
                    order,
                    RiskDecisionStatus.REJECT,
                    "explicit lot allocations are required for ambiguous simulated disposal",
                    source_id=source_id,
                    checked_at=checked_at,
                )
        return _risk(
            order,
            RiskDecisionStatus.ALLOW,
            "activation risk controls passed",
            source_id=source_id,
            checked_at=checked_at,
        )

    def _fill_risk(
        self,
        order: SimulatedOrder,
        decision: FillDecision,
        assumptions: ExecutionAssumptions,
        *,
        prior_fills: tuple[SimulatedFill, ...],
        risk_source_id: str,
        checked_at: datetime,
    ) -> tuple[PaperRiskDecision, dict[UUID, Decimal]]:
        assert decision.execution_price is not None
        projection = self.accounting.project(order.portfolio_id)
        notional = decision.quantity * decision.execution_price
        order_notional = order.quantity * decision.execution_price
        if (
            assumptions.max_order_notional is not None
            and order_notional > assumptions.max_order_notional
        ):
            return (
                _risk(
                    order,
                    RiskDecisionStatus.REJECT,
                    "maximum simulated order notional exceeded",
                    source_id=risk_source_id,
                    checked_at=checked_at,
                ),
                {},
            )
        if order.side is OrderSide.BUY:
            required = notional + decision.fee
            cash = projection.cash_by_currency.get(order.currency, _ZERO)
            if cash < required:
                return (
                    _risk(
                        order,
                        RiskDecisionStatus.REJECT,
                        "insufficient simulated cash",
                        source_id=risk_source_id,
                        checked_at=checked_at,
                    ),
                    {},
                )
            position_quantity = sum(
                (
                    position.quantity
                    for position in projection.positions
                    if position.instrument_id == order.instrument_id
                    and position.currency == order.currency
                ),
                _ZERO,
            )
            projected_notional = (position_quantity + decision.quantity) * decision.execution_price
            if (
                assumptions.max_position_notional is not None
                and projected_notional > assumptions.max_position_notional
            ):
                return (
                    _risk(
                        order,
                        RiskDecisionStatus.REJECT,
                        "maximum simulated position notional exceeded",
                        source_id=risk_source_id,
                        checked_at=checked_at,
                    ),
                    {},
                )
            return (
                _risk(
                    order,
                    RiskDecisionStatus.ALLOW,
                    "fill risk controls passed",
                    source_id=risk_source_id,
                    checked_at=checked_at,
                ),
                {},
            )
        try:
            allocations = _resolve_fill_allocations(
                order,
                decision.quantity,
                projection,
                prior_fills,
            )
        except ForwardPaperError as exc:
            return (
                _risk(
                    order,
                    RiskDecisionStatus.REJECT,
                    str(exc),
                    source_id=risk_source_id,
                    checked_at=checked_at,
                ),
                {},
            )
        return (
            _risk(
                order,
                RiskDecisionStatus.ALLOW,
                "fill risk controls passed",
                source_id=risk_source_id,
                checked_at=checked_at,
            ),
            allocations,
        )

    def _make_fill(
        self,
        order: SimulatedOrder,
        market_bar: PaperMarketBar,
        decision: FillDecision,
        allocations: dict[UUID, Decimal],
    ) -> SimulatedFill:
        assert decision.execution_price is not None
        fill_id = uuid5(
            NAMESPACE_URL,
            f"osca-paper-fill:{order.order_id}:{market_bar.evidence_id}",
        )
        return SimulatedFill(
            fill_id=fill_id,
            order_id=order.order_id,
            paper_run_id=order.paper_run_id,
            portfolio_id=order.portfolio_id,
            sequence=self.store.next_fill_sequence(order.order_id),
            bar_evidence_id=market_bar.evidence_id,
            dataset_revision_id=market_bar.dataset_revision_id,
            assumption_id=order.assumption_id,
            instrument_id=order.instrument_id,
            side=order.side,
            quantity=decision.quantity,
            execution_price=decision.execution_price,
            fee=decision.fee,
            lot_allocations=allocations,
            effective_at=market_bar.bar_started_at,
            source_id=str(fill_id),
        )

    def _post_fill(self, order: SimulatedOrder, fill: SimulatedFill) -> UUID:
        try:
            if fill.side is OrderSide.BUY:
                event = self.accounting.record_acquisition(
                    order.portfolio_id,
                    instrument_id=order.instrument_id,
                    quantity=fill.quantity,
                    unit_price=fill.execution_price,
                    currency=order.currency,
                    fee=fill.fee,
                    effective_at=fill.effective_at,
                    source_kind="paper.simulated-fill",
                    source_id=str(fill.fill_id),
                )
            else:
                lot_allocations: dict[UUID, Decimal | str | int] | None = None
                if fill.lot_allocations:
                    lot_allocations = {
                        lot_id: quantity
                        for lot_id, quantity in fill.lot_allocations.items()
                    }
                event = self.accounting.record_disposal(
                    order.portfolio_id,
                    instrument_id=order.instrument_id,
                    quantity=fill.quantity,
                    unit_price=fill.execution_price,
                    currency=order.currency,
                    fee=fill.fee,
                    lot_allocations=lot_allocations,
                    effective_at=fill.effective_at,
                    source_kind="paper.simulated-fill",
                    source_id=str(fill.fill_id),
                )
        except PortfolioAccountingError as exc:
            raise ForwardPaperError(f"D8 accounting rejected simulated fill: {exc}") from exc
        return event.event_id

    def _ensure_fill_lifecycle(
        self,
        order: SimulatedOrder,
        fill: SimulatedFill,
    ) -> OrderLifecycleEvent:
        existing = next(
            (
                event
                for event in self.store.list_lifecycle(order.order_id)
                if event.fill_id == fill.fill_id
            ),
            None,
        )
        if existing is not None:
            return existing
        remaining = self.remaining_quantity(order.order_id)
        status = (
            SimulatedOrderStatus.FILLED
            if remaining == _ZERO
            else SimulatedOrderStatus.PARTIALLY_FILLED
        )
        return self._ensure_lifecycle(
            order,
            status=status,
            source_id=f"fill:{fill.fill_id}",
            reason="simulated fill retained and reconciled to D8 accounting",
            effective_at=fill.effective_at,
            fill_id=fill.fill_id,
        )

    def _ensure_lifecycle(
        self,
        order: SimulatedOrder,
        *,
        status: SimulatedOrderStatus,
        source_id: str,
        reason: str,
        effective_at: datetime,
        fill_id: UUID | None = None,
    ) -> OrderLifecycleEvent:
        existing = next(
            (
                event
                for event in self.store.list_lifecycle(order.order_id)
                if event.source_id == source_id
            ),
            None,
        )
        if existing is not None:
            return existing
        event = OrderLifecycleEvent(
            order_id=order.order_id,
            sequence=self.store.next_lifecycle_sequence(order.order_id),
            status=status,
            source_id=source_id,
            reason=reason,
            fill_id=fill_id,
            effective_at=effective_at,
        )
        return self.store.append_lifecycle(event)

    def _terminal_no_fill_lifecycle(
        self,
        order: SimulatedOrder,
        market_bar: PaperMarketBar,
        decision: FillDecision,
    ) -> OrderLifecycleEvent | None:
        if order.expires_at is None or market_bar.bar_started_at < order.expires_at:
            return None
        return self._ensure_lifecycle(
            order,
            status=SimulatedOrderStatus.EXPIRED,
            source_id=f"expiry:{order.expires_at.isoformat()}",
            reason=decision.reason,
            effective_at=market_bar.bar_started_at,
        )

    @staticmethod
    def _require_control(
        paper_account_id: UUID,
        decision: PaperControlDecision,
    ) -> None:
        if decision.paper_account_id != paper_account_id:
            raise ForwardPaperError("paper control decision belongs to another account")
        if not decision.can_process:
            raise ForwardPaperError(f"paper control blocks processing: {decision.reason}")

    @staticmethod
    def _require_health(paper_run_id: UUID, decision: PaperHealthGateDecision) -> None:
        if decision.paper_run_id != paper_run_id:
            raise ForwardPaperError("paper health decision belongs to another run")
        if not decision.can_process:
            raise ForwardPaperError("paper health gate blocks forward processing")


def _resolve_fill_allocations(
    order: SimulatedOrder,
    fill_quantity: Decimal,
    projection: PortfolioProjection,
    prior_fills: tuple[SimulatedFill, ...],
) -> dict[UUID, Decimal]:
    open_lots = {
        lot.lot_id: lot
        for lot in projection.lots
        if lot.instrument_id == order.instrument_id
        and lot.currency == order.currency
        and lot.quantity > _ZERO
    }
    if not open_lots:
        raise ForwardPaperError("no open lots exist for simulated disposal")
    if not order.lot_allocations:
        if len(open_lots) != 1:
            raise ForwardPaperError(
                "explicit lot allocations are required for ambiguous simulated disposal"
            )
        sole_lot_id, sole_lot = next(iter(open_lots.items()))
        if sole_lot.quantity < fill_quantity:
            raise ForwardPaperError("held lot quantity is insufficient for simulated disposal")
        return {sole_lot_id: fill_quantity}
    consumed: dict[UUID, Decimal] = {}
    for fill in prior_fills:
        for lot_id, quantity in fill.lot_allocations.items():
            consumed[lot_id] = consumed.get(lot_id, _ZERO) + quantity
    remaining_to_allocate = fill_quantity
    result: dict[UUID, Decimal] = {}
    for lot_id in sorted(order.lot_allocations, key=str):
        requested = order.lot_allocations[lot_id]
        remaining_order_allocation = requested - consumed.get(lot_id, _ZERO)
        candidate_lot = open_lots.get(lot_id)
        if candidate_lot is None or remaining_order_allocation <= _ZERO:
            continue
        quantity = min(
            remaining_to_allocate,
            remaining_order_allocation,
            candidate_lot.quantity,
        )
        if quantity > _ZERO:
            result[lot_id] = quantity
            remaining_to_allocate -= quantity
        if remaining_to_allocate == _ZERO:
            break
    if remaining_to_allocate != _ZERO:
        raise ForwardPaperError("explicit lot allocations do not cover simulated fill quantity")
    return result


def _risk(
    order: SimulatedOrder,
    status: RiskDecisionStatus,
    reason: str,
    *,
    source_id: str,
    checked_at: datetime,
) -> PaperRiskDecision:
    return PaperRiskDecision(
        risk_decision_id=uuid5(
            NAMESPACE_URL,
            f"osca-paper-risk:{order.order_id}:{source_id}:{status}:{reason}",
        ),
        order_id=order.order_id,
        status=status,
        reason=reason,
        checked_at=_utc(checked_at),
    )


def _utc(value: datetime | None) -> datetime:
    result = value or datetime.now(UTC)
    if result.tzinfo is None or result.utcoffset() is None:
        raise ForwardPaperError("timestamps must be timezone-aware")
    return result
