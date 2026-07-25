from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from osca.paper import (
    ForwardComparisonMetric,
    ForwardComparisonRecord,
    HealthGateStatus,
    PaperAccount,
    PaperControlAction,
    PaperControlDecision,
    PaperDataRequirement,
    PaperEvaluationRequest,
    PaperFinding,
    PaperFindingSeverity,
    PaperHealthGateDecision,
)


def test_paper_account_requires_timezone_aware_creation_time() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        PaperAccount(name="candidate-paper", created_at=datetime(2026, 1, 1))


def test_paper_evaluation_request_rejects_provisional_data() -> None:
    with pytest.raises(ValidationError, match="provisional"):
        PaperEvaluationRequest(
            paper_account_id=uuid4(),
            approved_candidate_id=uuid4(),
            candidate_id="candidate.mean-reversion",
            promotion_gate_id=uuid4(),
            data_requirements=(
                PaperDataRequirement(
                    dataset_revision_id=uuid4(),
                    freshness_policy_id="forward.strict",
                    allow_provisional_data=True,
                ),
            ),
        )


def test_health_gate_blocks_error_findings() -> None:
    with pytest.raises(ValidationError, match="blocked or error"):
        PaperHealthGateDecision(
            paper_run_id=uuid4(),
            data_status=HealthGateStatus.HEALTHY,
            operational_status=HealthGateStatus.HEALTHY,
            can_process=True,
            findings=(
                PaperFinding(
                    code="data_stale",
                    severity=PaperFindingSeverity.ERROR,
                    message="forward data is stale",
                ),
            ),
        )


def test_pause_and_kill_switch_controls_cannot_allow_processing() -> None:
    with pytest.raises(ValidationError, match="must block"):
        PaperControlDecision(
            paper_account_id=uuid4(),
            action=PaperControlAction.KILL_SWITCH,
            can_process=True,
            reason="system paper kill switch engaged",
        )


def test_forward_comparison_preserves_f2_and_f3_identities() -> None:
    f2_request_id = uuid4()
    gate_id = uuid4()
    paper_run_id = uuid4()

    comparison = ForwardComparisonRecord(
        f2_request_id=f2_request_id,
        promotion_gate_id=gate_id,
        paper_run_id=paper_run_id,
        metrics=(
            ForwardComparisonMetric(
                name="max_drawdown",
                f2_value=-0.03,
                f3_value=-0.04,
                unit="ratio",
                methodology="m8.forward-comparison.v1",
            ),
        ),
        compared_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    assert comparison.f2_request_id == f2_request_id
    assert comparison.promotion_gate_id == gate_id
    assert comparison.paper_run_id == paper_run_id
