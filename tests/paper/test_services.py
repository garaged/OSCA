from datetime import UTC, datetime
from uuid import uuid4

import pytest

from osca.backtesting.eventing import PromotionGateDecision, ReconciliationFinding
from osca.paper import (
    ForwardComparisonMetric,
    HealthGateStatus,
    PaperControlAction,
    PaperFinding,
    PaperFindingSeverity,
    approve_paper_candidate,
    build_forward_comparison,
    decide_paper_control,
    evaluate_paper_health_gate,
)


def test_paper_candidate_requires_approved_f2_gate() -> None:
    blocked_gate = PromotionGateDecision(
        request_id=uuid4(),
        candidate_id="candidate.mean-reversion",
        approved_for_paper_evaluation=False,
        findings=(
            ReconciliationFinding(
                code="journal_imbalance",
                severity="error",
                message="journal did not balance",
            ),
        ),
    )

    with pytest.raises(ValueError, match="approved F2 promotion gate"):
        approve_paper_candidate(blocked_gate)


def test_approved_paper_candidate_preserves_f2_gate_lineage() -> None:
    gate = PromotionGateDecision(
        request_id=uuid4(),
        candidate_id="candidate.mean-reversion",
        approved_for_paper_evaluation=True,
        decided_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    candidate = approve_paper_candidate(gate)

    assert candidate.candidate_id == gate.candidate_id
    assert candidate.f2_request_id == gate.request_id
    assert candidate.promotion_gate_id == gate.gate_id
    assert candidate.approved_at == gate.decided_at


def test_paper_health_gate_fails_closed_for_blocked_data() -> None:
    gate = evaluate_paper_health_gate(
        paper_run_id=uuid4(),
        data_status=HealthGateStatus.BLOCKED,
        operational_status=HealthGateStatus.HEALTHY,
    )

    assert gate.can_process is False


def test_paper_health_gate_fails_closed_for_error_findings() -> None:
    gate = evaluate_paper_health_gate(
        paper_run_id=uuid4(),
        data_status=HealthGateStatus.HEALTHY,
        operational_status=HealthGateStatus.HEALTHY,
        findings=(
            PaperFinding(
                code="provider_unavailable",
                severity=PaperFindingSeverity.ERROR,
                message="provider is unavailable",
            ),
        ),
    )

    assert gate.can_process is False


def test_paper_controls_prioritize_kill_switch_over_pause() -> None:
    decision = decide_paper_control(
        paper_account_id=uuid4(),
        account_paused=True,
        kill_switch_engaged=True,
        reason="system-wide paper stop",
    )

    assert decision.action is PaperControlAction.KILL_SWITCH
    assert decision.can_process is False


def test_forward_comparison_builder_retains_metric_methodology() -> None:
    comparison = build_forward_comparison(
        f2_request_id=uuid4(),
        promotion_gate_id=uuid4(),
        paper_run_id=uuid4(),
        metrics=(
            ForwardComparisonMetric(
                name="return",
                f2_value=0.05,
                f3_value=0.03,
                unit="ratio",
                methodology="m8.forward-comparison.v1",
            ),
        ),
    )

    assert comparison.metrics[0].methodology == "m8.forward-comparison.v1"
