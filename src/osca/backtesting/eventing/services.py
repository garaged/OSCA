from osca.backtesting.eventing.contracts import (
    JournalTransaction,
    OrderLifecycleEvent,
    OrderLifecycleState,
    PromotionGateDecision,
    ReconciliationFinding,
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

    for previous, current in zip(ordered, ordered[1:], strict=False):
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
                    message=f"invalid lifecycle transition from {previous.state} to {current.state}",
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
    request_id,
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
