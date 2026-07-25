from uuid import UUID

from osca.backtesting.eventing import PromotionGateDecision
from osca.paper.contracts import (
    ApprovedPaperCandidate,
    ForwardComparisonMetric,
    ForwardComparisonRecord,
    HealthGateStatus,
    MissedRunPolicy,
    PaperControlAction,
    PaperControlDecision,
    PaperFinding,
    PaperFindingSeverity,
    PaperHealthGateDecision,
    PaperRecoveryAction,
    PaperRecoveryDecision,
)


def approve_paper_candidate(gate: PromotionGateDecision) -> ApprovedPaperCandidate:
    if not gate.approved_for_paper_evaluation:
        raise ValueError("paper evaluation requires an approved F2 promotion gate")
    return ApprovedPaperCandidate(
        candidate_id=gate.candidate_id,
        f2_request_id=gate.request_id,
        promotion_gate_id=gate.gate_id,
        approved_at=gate.decided_at,
    )


def evaluate_paper_health_gate(
    *,
    paper_run_id: UUID,
    data_status: HealthGateStatus,
    operational_status: HealthGateStatus,
    findings: tuple[PaperFinding, ...] = (),
) -> PaperHealthGateDecision:
    can_process = (
        data_status is not HealthGateStatus.BLOCKED
        and operational_status is not HealthGateStatus.BLOCKED
        and not any(finding.severity is PaperFindingSeverity.ERROR for finding in findings)
    )
    return PaperHealthGateDecision(
        paper_run_id=paper_run_id,
        data_status=data_status,
        operational_status=operational_status,
        can_process=can_process,
        findings=findings,
    )


def decide_paper_control(
    *,
    paper_account_id: UUID,
    account_paused: bool = False,
    kill_switch_engaged: bool = False,
    reason: str = "paper controls evaluated",
) -> PaperControlDecision:
    if kill_switch_engaged:
        return PaperControlDecision(
            paper_account_id=paper_account_id,
            action=PaperControlAction.KILL_SWITCH,
            can_process=False,
            reason=reason,
        )
    if account_paused:
        return PaperControlDecision(
            paper_account_id=paper_account_id,
            action=PaperControlAction.PAUSE,
            can_process=False,
            reason=reason,
        )
    return PaperControlDecision(
        paper_account_id=paper_account_id,
        action=PaperControlAction.ALLOW,
        can_process=True,
        reason=reason,
    )


def build_forward_comparison(
    *,
    f2_request_id: UUID,
    promotion_gate_id: UUID,
    paper_run_id: UUID,
    metrics: tuple[ForwardComparisonMetric, ...],
    findings: tuple[PaperFinding, ...] = (),
) -> ForwardComparisonRecord:
    return ForwardComparisonRecord(
        f2_request_id=f2_request_id,
        promotion_gate_id=promotion_gate_id,
        paper_run_id=paper_run_id,
        metrics=metrics,
        findings=findings,
    )


def evaluate_paper_recovery(
    *,
    paper_run_id: UUID,
    checkpoint_id: UUID | None,
    missed_run_policy: MissedRunPolicy,
    findings: tuple[PaperFinding, ...] = (),
) -> PaperRecoveryDecision:
    has_error = any(finding.severity is PaperFindingSeverity.ERROR for finding in findings)
    if has_error or missed_run_policy is MissedRunPolicy.BLOCK:
        return PaperRecoveryDecision(
            paper_run_id=paper_run_id,
            checkpoint_id=checkpoint_id,
            action=PaperRecoveryAction.BLOCK,
            can_resume=False,
            findings=findings,
        )
    if missed_run_policy is MissedRunPolicy.SKIP:
        return PaperRecoveryDecision(
            paper_run_id=paper_run_id,
            checkpoint_id=checkpoint_id,
            action=PaperRecoveryAction.SKIP_MISSED,
            can_resume=True,
            findings=findings,
        )
    return PaperRecoveryDecision(
        paper_run_id=paper_run_id,
        checkpoint_id=checkpoint_id,
        action=PaperRecoveryAction.RESUME,
        can_resume=True,
        findings=findings,
    )
