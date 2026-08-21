import sqlite3
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID

import pytest

from osca.paper.contracts import PaperRunCheckpoint
from osca.paper.fill_engine import confirm_simulated_order
from osca.paper.order_contracts import (
    ExecutionAssumptions,
    OrderLifecycleEvent,
    OrderSide,
    OrderSourceKind,
    PaperRunBinding,
    SimulatedFill,
    SimulatedOrder,
    SimulatedOrderDraft,
    SimulatedOrderStatus,
    SimulatedOrderType,
)
from osca.paper.order_persistence import OrderConflictError, SQLitePaperOrderStore


RUN_ID = UUID("10000000-0000-0000-0000-000000000001")
ACCOUNT_ID = UUID("20000000-0000-0000-0000-000000000002")
PORTFOLIO_ID = UUID("30000000-0000-0000-0000-000000000003")
ASSUMPTION_ID = UUID("40000000-0000-0000-0000-000000000004")
BAR_ID = UUID("50000000-0000-0000-0000-000000000005")
DATASET_ID = UUID("60000000-0000-0000-0000-000000000006")


def at(hour: int) -> datetime:
    return datetime(2026, 8, 21, hour, tzinfo=UTC)


def store(tmp_path: Path) -> SQLitePaperOrderStore:
    result = SQLitePaperOrderStore(tmp_path / "paper-orders.sqlite")
    result.initialize()
    return result


def assumptions() -> ExecutionAssumptions:
    return ExecutionAssumptions(
        assumption_id=ASSUMPTION_ID,
        max_volume_participation=Decimal("0.10"),
        created_at=at(8),
    )


def draft() -> SimulatedOrderDraft:
    return SimulatedOrderDraft(
        paper_run_id=RUN_ID,
        paper_account_id=ACCOUNT_ID,
        portfolio_id=PORTFOLIO_ID,
        source_kind=OrderSourceKind.MANUAL,
        source_id="manual-order",
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


def prepared(
    tmp_path: Path,
) -> tuple[SQLitePaperOrderStore, SimulatedOrderDraft, SimulatedOrder]:
    persistence = store(tmp_path)
    persistence.append_binding(
        PaperRunBinding(
            paper_run_id=RUN_ID,
            paper_account_id=ACCOUNT_ID,
            portfolio_id=PORTFOLIO_ID,
            created_at=at(8),
        )
    )
    execution = persistence.append_assumptions(assumptions())
    order_draft = persistence.append_draft(draft())
    confirmation, order = confirm_simulated_order(order_draft, execution, confirmed_at=at(9))
    persistence.append_confirmation_and_order(confirmation, order)
    return persistence, order_draft, order


def test_schema_initialization_is_idempotent_and_tables_are_append_only(tmp_path: Path) -> None:
    persistence, _, order = prepared(tmp_path)
    persistence.initialize()
    with sqlite3.connect(persistence.database_path) as connection:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "UPDATE simulated_orders SET paper_run_id = ? WHERE order_id = ?",
                (str(UUID(int=0)), str(order.order_id)),
            )
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "DELETE FROM simulated_orders WHERE order_id = ?",
                (str(order.order_id),),
            )


def test_binding_and_draft_retries_are_idempotent_but_conflicts_fail(tmp_path: Path) -> None:
    persistence = store(tmp_path)
    binding = PaperRunBinding(
        paper_run_id=RUN_ID,
        paper_account_id=ACCOUNT_ID,
        portfolio_id=PORTFOLIO_ID,
        created_at=at(8),
    )
    assert persistence.append_binding(binding) == binding
    assert persistence.append_binding(binding) == binding
    conflicting = binding.model_copy(update={"portfolio_id": UUID(int=9)})
    with pytest.raises(OrderConflictError, match="different content"):
        persistence.append_binding(conflicting)
    order_draft = draft()
    persistence.append_draft(order_draft)
    assert persistence.append_draft(order_draft) == order_draft
    with pytest.raises(OrderConflictError, match="different content"):
        persistence.append_draft(order_draft.model_copy(update={"quantity": Decimal("11")}))


def test_confirmation_and_order_are_atomic_and_retriable(tmp_path: Path) -> None:
    persistence = store(tmp_path)
    execution = persistence.append_assumptions(assumptions())
    order_draft = persistence.append_draft(draft())
    confirmation, order = confirm_simulated_order(order_draft, execution, confirmed_at=at(9))
    first = persistence.append_confirmation_and_order(confirmation, order)
    second = persistence.append_confirmation_and_order(confirmation, order)
    assert first == second
    assert persistence.get_order(order.order_id) == order
    assert persistence.list_orders(RUN_ID) == (order,)


def test_lifecycle_and_fill_sequences_are_append_only_and_source_idempotent(tmp_path: Path) -> None:
    persistence, _, order = prepared(tmp_path)
    lifecycle = OrderLifecycleEvent(
        order_id=order.order_id,
        sequence=persistence.next_lifecycle_sequence(order.order_id),
        status=SimulatedOrderStatus.ACTIVE,
        source_id="activate-1",
        reason="eligible bar available",
        effective_at=at(10),
    )
    assert persistence.append_lifecycle(lifecycle) == lifecycle
    assert persistence.append_lifecycle(lifecycle) == lifecycle
    fill = SimulatedFill(
        order_id=order.order_id,
        paper_run_id=RUN_ID,
        portfolio_id=PORTFOLIO_ID,
        sequence=persistence.next_fill_sequence(order.order_id),
        bar_evidence_id=BAR_ID,
        dataset_revision_id=DATASET_ID,
        assumption_id=ASSUMPTION_ID,
        instrument_id=order.instrument_id,
        side=order.side,
        quantity=Decimal("2"),
        execution_price=Decimal("101"),
        fee=Decimal("0.25"),
        effective_at=at(10),
        source_id="fill-source-1",
    )
    assert persistence.append_fill(fill) == fill
    assert persistence.append_fill(fill) == fill
    assert persistence.next_lifecycle_sequence(order.order_id) == 2
    assert persistence.next_fill_sequence(order.order_id) == 2
    assert persistence.list_lifecycle(order.order_id) == (lifecycle,)
    assert persistence.list_fills(order.order_id) == (fill,)
    with pytest.raises(OrderConflictError, match="different content"):
        persistence.append_fill(fill.model_copy(update={"execution_price": Decimal("102")}))


def test_checkpoints_are_retriable_and_latest_sequence_is_recovered(tmp_path: Path) -> None:
    persistence, _, _ = prepared(tmp_path)
    first = PaperRunCheckpoint(
        paper_run_id=RUN_ID,
        sequence_number=1,
        idempotency_key="checkpoint-1",
        last_processed_at=at(10),
        source_event_ids=(BAR_ID,),
        created_at=at(10),
    )
    second = PaperRunCheckpoint(
        paper_run_id=RUN_ID,
        sequence_number=2,
        idempotency_key="checkpoint-2",
        last_processed_at=at(11),
        source_event_ids=(UUID(int=7),),
        created_at=at(11),
    )
    persistence.append_checkpoint(first)
    persistence.append_checkpoint(first)
    persistence.append_checkpoint(second)
    assert persistence.latest_checkpoint(RUN_ID) == second
