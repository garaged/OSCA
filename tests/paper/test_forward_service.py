from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from pytest import raises

from osca.paper.contracts import HealthGateStatus
from osca.paper.forward_service import ForwardPaperError, ForwardPaperService
from osca.paper.order_contracts import (
    ExecutionAssumptions,
    OrderSide,
    OrderSourceKind,
    PaperMarketBar,
    SimulatedOrderDraft,
    SimulatedOrderStatus,
    SimulatedOrderType,
)
from osca.paper.services import decide_paper_control, evaluate_paper_health_gate

RUN_ID = UUID("10000000-0000-0000-0000-000000000001")
ACCOUNT_ID = UUID("20000000-0000-0000-0000-000000000002")
ASSUMPTION_ID = UUID("30000000-0000-0000-0000-000000000003")
DATASET_ID = UUID("40000000-0000-0000-0000-000000000004")


def at(hour: int) -> datetime:
    return datetime(2026, 8, 21, hour, tzinfo=UTC)


def prepared(
    tmp_path: Path,
    *,
    starting_cash: str = "10000",
    participation: str = "0.10",
) -> tuple[ForwardPaperService, UUID]:
    service = ForwardPaperService.for_profile(tmp_path)
    portfolio = service.accounting.create_portfolio(
        name="D9 paper portfolio",
        starting_cash=starting_cash,
        created_at=at(8),
    )
    service.bind_run(
        paper_run_id=RUN_ID,
        paper_account_id=ACCOUNT_ID,
        portfolio_id=portfolio.portfolio_id,
        created_at=at(8),
    )
    service.retain_assumptions(
        ExecutionAssumptions(
            assumption_id=ASSUMPTION_ID,
            max_volume_participation=Decimal(participation),
            created_at=at(8),
        )
    )
    return service, portfolio.portfolio_id


def draft(
    portfolio_id: UUID,
    *,
    quantity: str = "10",
    side: OrderSide = OrderSide.BUY,
) -> SimulatedOrderDraft:
    return SimulatedOrderDraft(
        paper_run_id=RUN_ID,
        paper_account_id=ACCOUNT_ID,
        portfolio_id=portfolio_id,
        source_kind=OrderSourceKind.MANUAL,
        source_id="manual-forward-order",
        instrument_id="equity:XNAS:AAPL",
        timeframe="1h",
        currency="USD",
        dataset_revision_id=DATASET_ID,
        side=side,
        order_type=SimulatedOrderType.MARKET,
        quantity=Decimal(quantity),
        assumption_id=ASSUMPTION_ID,
        created_at=at(8),
    )


def bar(hour: int, *, volume: str = "50", price: str = "100") -> PaperMarketBar:
    started = at(hour)
    return PaperMarketBar(
        evidence_id=UUID(int=hour),
        instrument_id="equity:XNAS:AAPL",
        dataset_revision_id=DATASET_ID,
        source_id=f"governed-bar-{hour}",
        timeframe="1h",
        bar_started_at=started,
        bar_ended_at=started + timedelta(hours=1),
        available_at=started + timedelta(hours=1, seconds=1),
        open=Decimal(price),
        high=Decimal(price) + Decimal("1"),
        low=Decimal(price) - Decimal("1"),
        close=Decimal(price),
        volume=Decimal(volume),
        market_calendar_id="XNAS",
        session_open=True,
    )


def control():
    return decide_paper_control(paper_account_id=ACCOUNT_ID)


def health():
    return evaluate_paper_health_gate(
        paper_run_id=RUN_ID,
        data_status=HealthGateStatus.HEALTHY,
        operational_status=HealthGateStatus.HEALTHY,
    )


def test_confirmation_retry_reuses_immutable_confirmation_order_and_risk(tmp_path: Path) -> None:
    service, portfolio_id = prepared(tmp_path)
    order_draft = draft(portfolio_id)

    first = service.confirm_draft(order_draft, confirmed_at=at(9), control_decision=control())
    second = service.confirm_draft(order_draft, confirmed_at=at(9), control_decision=control())

    assert second.confirmation == first.confirmation
    assert second.order == first.order
    assert second.risk_decision == first.risk_decision
    assert second.lifecycle == first.lifecycle
    assert service.store.list_orders(RUN_ID) == (first.order,)


def test_partial_fills_post_once_to_d8_and_replay_one_bar_idempotently(tmp_path: Path) -> None:
    service, portfolio_id = prepared(tmp_path)
    confirmed = service.confirm_draft(
        draft(portfolio_id),
        confirmed_at=at(9),
        control_decision=control(),
    )

    first = service.process_bar(
        confirmed.order.order_id,
        bar(10),
        control_decision=control(),
        health_gate=health(),
    )
    assert first.fill is not None
    assert first.fill.quantity == Decimal("5.0")
    assert service.current_status(confirmed.order.order_id) is SimulatedOrderStatus.PARTIALLY_FILLED
    after_first = service.accounting.project(portfolio_id)
    assert after_first.positions[0].quantity == Decimal("5.0")

    replay = service.process_bar(
        confirmed.order.order_id,
        bar(10),
        control_decision=control(),
        health_gate=health(),
    )
    after_replay = service.accounting.project(portfolio_id)
    assert replay.fill == first.fill
    assert replay.accounting_event_id == first.accounting_event_id
    assert after_replay.revision == after_first.revision
    assert after_replay.positions[0].quantity == Decimal("5.0")

    second = service.process_bar(
        confirmed.order.order_id,
        bar(11),
        control_decision=control(),
        health_gate=health(),
    )
    assert second.fill is not None
    assert second.fill.quantity == Decimal("5.0")
    assert service.current_status(confirmed.order.order_id) is SimulatedOrderStatus.FILLED
    final = service.accounting.project(portfolio_id)
    assert final.positions[0].quantity == Decimal("10.0")
    assert len(service.store.list_fills(confirmed.order.order_id)) == 2


def test_fill_risk_rejects_insufficient_cash_without_accounting_mutation(tmp_path: Path) -> None:
    service, portfolio_id = prepared(tmp_path, starting_cash="100")
    confirmed = service.confirm_draft(
        draft(portfolio_id, quantity="2"),
        confirmed_at=at(9),
        control_decision=control(),
    )
    before = service.accounting.project(portfolio_id)

    result = service.process_bar(
        confirmed.order.order_id,
        bar(10, price="100"),
        control_decision=control(),
        health_gate=health(),
    )

    assert result.fill is None
    assert result.risk_decision is not None
    assert "insufficient simulated cash" in result.risk_decision.reason
    assert service.current_status(confirmed.order.order_id) is SimulatedOrderStatus.REJECTED
    after = service.accounting.project(portfolio_id)
    assert after.revision == before.revision
    assert not after.positions


def test_cancelled_order_never_processes_a_later_fill(tmp_path: Path) -> None:
    service, portfolio_id = prepared(tmp_path)
    confirmed = service.confirm_draft(
        draft(portfolio_id),
        confirmed_at=at(9),
        control_decision=control(),
    )
    service.cancel_order(
        confirmed.order.order_id,
        source_id="user-cancel",
        reason="operator cancelled simulated order",
        effective_at=at(10),
    )

    result = service.process_bar(
        confirmed.order.order_id,
        bar(11),
        control_decision=control(),
        health_gate=health(),
    )

    assert result.fill is None
    assert "terminal" in result.decision.reason
    assert not service.store.list_fills(confirmed.order.order_id)


def test_pause_and_blocked_health_fail_closed_before_forward_processing(tmp_path: Path) -> None:
    service, portfolio_id = prepared(tmp_path)
    order_draft = draft(portfolio_id)
    paused = decide_paper_control(
        paper_account_id=ACCOUNT_ID,
        account_paused=True,
        reason="paper account paused",
    )
    with raises(ForwardPaperError, match="paper control blocks"):
        service.confirm_draft(order_draft, confirmed_at=at(9), control_decision=paused)

    confirmed = service.confirm_draft(
        order_draft,
        confirmed_at=at(9),
        control_decision=control(),
    )
    blocked = evaluate_paper_health_gate(
        paper_run_id=RUN_ID,
        data_status=HealthGateStatus.BLOCKED,
        operational_status=HealthGateStatus.HEALTHY,
    )
    with raises(ForwardPaperError, match="health gate blocks"):
        service.process_bar(
            confirmed.order.order_id,
            bar(10),
            control_decision=control(),
            health_gate=blocked,
        )
