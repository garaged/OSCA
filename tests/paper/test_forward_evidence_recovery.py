from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from uuid import UUID

import pytest

from osca.paper.contracts import HealthGateStatus
from osca.paper.forward_evidence import ForwardEvidenceError, append_completed_bar_mark
from osca.paper.forward_service import ForwardPaperError, ForwardPaperService
from osca.paper.order_contracts import (
    ExecutionAssumptions,
    OrderSide,
    OrderSourceKind,
    PaperMarketBar,
    SimulatedOrderDraft,
    SimulatedOrderType,
)
from osca.paper.services import decide_paper_control, evaluate_paper_health_gate

RUN_ID = UUID("71000000-0000-0000-0000-000000000001")
ACCOUNT_ID = UUID("72000000-0000-0000-0000-000000000002")
ASSUMPTION_ID = UUID("73000000-0000-0000-0000-000000000003")
DATASET_ID = UUID("74000000-0000-0000-0000-000000000004")


def at(hour: int) -> datetime:
    return datetime(2026, 8, 21, hour, tzinfo=UTC)


def bar(hour: int, *, close: str = "110", complete: bool = True) -> PaperMarketBar:
    start = at(hour)
    return PaperMarketBar(
        evidence_id=UUID(int=1000 + hour),
        instrument_id="equity:XNAS:AAPL",
        dataset_revision_id=DATASET_ID,
        source_id=f"governed-forward-{hour}",
        timeframe="1h",
        bar_started_at=start,
        bar_ended_at=start + timedelta(hours=1),
        available_at=start + timedelta(hours=1, seconds=1),
        open=Decimal("108"),
        high=Decimal("112"),
        low=Decimal("107"),
        close=Decimal(close),
        volume=Decimal("1000"),
        complete=complete,
        market_calendar_id="XNAS",
        session_open=True,
    )


def prepared(tmp_path: Path) -> tuple[ForwardPaperService, UUID]:
    service = ForwardPaperService.for_profile(tmp_path)
    portfolio = service.accounting.create_portfolio(
        name="D9 recovery evidence",
        starting_cash="10000",
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
            max_volume_participation=Decimal("1"),
            created_at=at(8),
        )
    )
    return service, portfolio.portfolio_id


def confirmed_order(service: ForwardPaperService, portfolio_id: UUID):
    order_draft = SimulatedOrderDraft(
        paper_run_id=RUN_ID,
        paper_account_id=ACCOUNT_ID,
        portfolio_id=portfolio_id,
        source_kind=OrderSourceKind.MANUAL,
        source_id="restart-order",
        instrument_id="equity:XNAS:AAPL",
        timeframe="1h",
        currency="USD",
        dataset_revision_id=DATASET_ID,
        side=OrderSide.BUY,
        order_type=SimulatedOrderType.MARKET,
        quantity=Decimal("10"),
        assumption_id=ASSUMPTION_ID,
        created_at=at(8),
    )
    control = decide_paper_control(paper_account_id=ACCOUNT_ID)
    return service.confirm_draft(order_draft, confirmed_at=at(9), control_decision=control)


def healthy_gate():
    return evaluate_paper_health_gate(
        paper_run_id=RUN_ID,
        data_status=HealthGateStatus.HEALTHY,
        operational_status=HealthGateStatus.HEALTHY,
    )


def test_completed_bar_mark_is_replay_safe_and_separate_from_fill_price(tmp_path: Path) -> None:
    service, portfolio_id = prepared(tmp_path)
    service.accounting.record_acquisition(
        portfolio_id,
        instrument_id="equity:XNAS:AAPL",
        quantity="10",
        unit_price="100",
        currency="USD",
        effective_at=at(9),
        source_id="seed-position",
    )
    market_bar = bar(10, close="110")

    first = append_completed_bar_mark(
        service.accounting,
        portfolio_id=portfolio_id,
        market_bar=market_bar,
        price_currency="USD",
    )
    second = append_completed_bar_mark(
        service.accounting,
        portfolio_id=portfolio_id,
        market_bar=market_bar,
        price_currency="USD",
    )

    assert second == first
    assert first.unit_price == Decimal("110")
    assert first.price_effective_at == market_bar.bar_ended_at
    assert first.recorded_at == market_bar.available_at
    assert first.price_source == "paper-bar:governed-forward-10"
    assert str(DATASET_ID) in first.valuation_revision
    projection = service.accounting.project(portfolio_id)
    assert projection.equity_base == Decimal("10100")
    assert projection.unrealized_pnl_base == Decimal("100")


def test_incomplete_bar_or_missing_position_cannot_be_silently_marked(tmp_path: Path) -> None:
    service, portfolio_id = prepared(tmp_path)
    with pytest.raises(ForwardEvidenceError, match="incomplete"):
        append_completed_bar_mark(
            service.accounting,
            portfolio_id=portfolio_id,
            market_bar=bar(10, complete=False),
            price_currency="USD",
        )
    with pytest.raises(ForwardEvidenceError, match="no open matching position"):
        append_completed_bar_mark(
            service.accounting,
            portfolio_id=portfolio_id,
            market_bar=bar(10),
            price_currency="USD",
        )


def test_checkpoint_retry_is_idempotent_and_conflicts_fail(tmp_path: Path) -> None:
    service, _ = prepared(tmp_path)
    source_ids = (UUID(int=501), UUID(int=502))

    first = service.checkpoint_run(
        RUN_ID,
        idempotency_key="after-bar-10",
        last_processed_at=at(10),
        source_event_ids=source_ids,
    )
    retry = service.checkpoint_run(
        RUN_ID,
        idempotency_key="after-bar-10",
        last_processed_at=at(10),
        source_event_ids=source_ids,
    )
    second = service.checkpoint_run(
        RUN_ID,
        idempotency_key="after-bar-11",
        last_processed_at=at(11),
        source_event_ids=(UUID(int=503),),
    )

    assert retry == first
    assert second.sequence_number == first.sequence_number + 1
    with pytest.raises(ForwardPaperError, match="different recovery evidence"):
        service.checkpoint_run(
            RUN_ID,
            idempotency_key="after-bar-10",
            last_processed_at=at(11),
            source_event_ids=source_ids,
        )


def test_restart_replays_fill_without_duplicate_accounting(tmp_path: Path) -> None:
    service, portfolio_id = prepared(tmp_path)
    confirmed = confirmed_order(service, portfolio_id)
    market_bar = bar(10, close="100")
    control = decide_paper_control(paper_account_id=ACCOUNT_ID)

    first = service.process_bar(
        confirmed.order.order_id,
        market_bar,
        control_decision=control,
        health_gate=healthy_gate(),
    )
    assert first.fill is not None
    first_projection = service.accounting.project(portfolio_id)

    restarted = ForwardPaperService.for_profile(tmp_path)
    replay = restarted.process_bar(
        confirmed.order.order_id,
        market_bar,
        control_decision=control,
        health_gate=healthy_gate(),
    )
    replay_projection = restarted.accounting.project(portfolio_id)

    assert replay.fill == first.fill
    assert replay.accounting_event_id == first.accounting_event_id
    assert replay_projection.revision == first_projection.revision
    assert replay_projection.positions == first_projection.positions
