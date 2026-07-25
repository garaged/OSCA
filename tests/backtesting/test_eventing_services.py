from datetime import UTC, datetime, timedelta
from uuid import uuid4

from osca.backtesting.eventing import (
    JournalLine,
    JournalLineSide,
    JournalTransaction,
    OrderLifecycleEvent,
    OrderLifecycleState,
    ReconciliationFinding,
    evaluate_promotion_gate,
    validate_journal_transaction,
    validate_lifecycle_sequence,
)


def lifecycle_event(state: OrderLifecycleState, offset_seconds: int = 0) -> OrderLifecycleEvent:
    return OrderLifecycleEvent(
        request_id=REQUEST_ID,
        order_intent_id=ORDER_ID,
        decision_id=DECISION_ID,
        state=state,
        effective_at=datetime(2026, 1, 1, tzinfo=UTC) + timedelta(seconds=offset_seconds),
        rationale=f"state {state}",
    )


REQUEST_ID = uuid4()
ORDER_ID = uuid4()
DECISION_ID = uuid4()


def test_lifecycle_sequence_accepts_valid_fill_path() -> None:
    findings = validate_lifecycle_sequence(
        (
            lifecycle_event(OrderLifecycleState.CREATED),
            lifecycle_event(OrderLifecycleState.ACCEPTED, 1),
            lifecycle_event(OrderLifecycleState.PARTIALLY_FILLED, 2),
            lifecycle_event(OrderLifecycleState.FILLED, 3),
        )
    )

    assert findings == ()


def test_lifecycle_sequence_rejects_terminal_regression() -> None:
    findings = validate_lifecycle_sequence(
        (
            lifecycle_event(OrderLifecycleState.CREATED),
            lifecycle_event(OrderLifecycleState.FILLED, 1),
            lifecycle_event(OrderLifecycleState.CANCELLED, 2),
        )
    )

    assert [finding.code for finding in findings] == ["lifecycle_terminal_regression"]


def test_journal_validation_accepts_balanced_transaction() -> None:
    transaction = JournalTransaction(
        request_id=uuid4(),
        source_event_id=uuid4(),
        effective_at=datetime(2026, 1, 1, tzinfo=UTC),
        description="settlement",
        lines=(
            JournalLine(account="positions", side=JournalLineSide.DEBIT, amount=10, currency="USD"),
            JournalLine(account="cash", side=JournalLineSide.CREDIT, amount=10, currency="USD"),
        ),
    )

    assert validate_journal_transaction(transaction) == ()


def test_promotion_gate_blocks_error_findings_without_activating_paper() -> None:
    request_id = uuid4()
    gate = evaluate_promotion_gate(
        request_id=request_id,
        candidate_id="candidate.mean-reversion",
        findings=(
            ReconciliationFinding(
                code="journal_imbalance",
                severity="error",
                message="journal did not balance",
            ),
        ),
    )

    assert gate.request_id == request_id
    assert gate.approved_for_paper_evaluation is False


def test_promotion_gate_allows_clean_f2_evidence_only() -> None:
    gate = evaluate_promotion_gate(
        request_id=uuid4(),
        candidate_id="candidate.mean-reversion",
        findings=(),
    )

    assert gate.approved_for_paper_evaluation is True
    assert gate.family == "osca.backtest.promotion-gate"
