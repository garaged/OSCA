from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from osca.paper import (
    MissedRunPolicy,
    PaperFinding,
    PaperFindingSeverity,
    PaperRecoveryAction,
    PaperRunCheckpoint,
    PaperSchedule,
    PaperScheduleCadence,
    evaluate_paper_recovery,
)


def test_market_aware_schedule_requires_calendar_identity() -> None:
    with pytest.raises(ValidationError, match="market_calendar_id"):
        PaperSchedule(
            paper_account_id=uuid4(),
            paper_run_id=uuid4(),
            cadence=PaperScheduleCadence.MARKET_OPEN,
            timezone="America/New_York",
            starts_at=datetime(2026, 1, 1, tzinfo=UTC),
        )


def test_paper_checkpoint_requires_timezone_aware_processed_time() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        PaperRunCheckpoint(
            paper_run_id=uuid4(),
            sequence_number=1,
            idempotency_key="paper-run-1:bar-1",
            last_processed_at=datetime(2026, 1, 1),
        )


def test_recovery_blocks_when_missed_run_policy_blocks() -> None:
    decision = evaluate_paper_recovery(
        paper_run_id=uuid4(),
        checkpoint_id=uuid4(),
        missed_run_policy=MissedRunPolicy.BLOCK,
    )

    assert decision.action is PaperRecoveryAction.BLOCK
    assert decision.can_resume is False


def test_recovery_skips_missed_runs_when_policy_allows_skip() -> None:
    decision = evaluate_paper_recovery(
        paper_run_id=uuid4(),
        checkpoint_id=uuid4(),
        missed_run_policy=MissedRunPolicy.SKIP,
    )

    assert decision.action is PaperRecoveryAction.SKIP_MISSED
    assert decision.can_resume is True


def test_recovery_fails_closed_for_error_findings() -> None:
    decision = evaluate_paper_recovery(
        paper_run_id=uuid4(),
        checkpoint_id=uuid4(),
        missed_run_policy=MissedRunPolicy.RUN_ONCE,
        findings=(
            PaperFinding(
                code="checkpoint_gap",
                severity=PaperFindingSeverity.ERROR,
                message="checkpoint sequence has a gap",
            ),
        ),
    )

    assert decision.action is PaperRecoveryAction.BLOCK
    assert decision.can_resume is False
