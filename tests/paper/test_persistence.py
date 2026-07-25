from datetime import UTC, datetime
from uuid import uuid4

from osca.backtesting.eventing import PromotionGateDecision
from osca.paper import (
    ForwardComparisonMetric,
    HealthGateStatus,
    MissedRunPolicy,
    PaperAccount,
    PaperDataRequirement,
    PaperEvaluationRequest,
    PaperSchedule,
    PaperScheduleCadence,
    SQLitePaperEvaluationStore,
    approve_paper_candidate,
    build_forward_comparison,
    decide_paper_control,
    evaluate_paper_health_gate,
    evaluate_paper_recovery,
)


def test_paper_evaluation_store_round_trips_metadata_records(tmp_path) -> None:
    account = PaperAccount(name="mean-reversion-paper", created_at=datetime(2026, 1, 1, tzinfo=UTC))
    gate = PromotionGateDecision(
        request_id=uuid4(),
        candidate_id="candidate.mean-reversion",
        approved_for_paper_evaluation=True,
        decided_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    candidate = approve_paper_candidate(gate)
    request = PaperEvaluationRequest(
        paper_account_id=account.paper_account_id,
        approved_candidate_id=candidate.approved_candidate_id,
        candidate_id=candidate.candidate_id,
        promotion_gate_id=candidate.promotion_gate_id,
        data_requirements=(
            PaperDataRequirement(
                dataset_revision_id=uuid4(),
                freshness_policy_id="forward.strict",
            ),
        ),
        requested_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    health = evaluate_paper_health_gate(
        paper_run_id=request.paper_run_id,
        data_status=HealthGateStatus.HEALTHY,
        operational_status=HealthGateStatus.HEALTHY,
    )
    control = decide_paper_control(paper_account_id=account.paper_account_id)
    schedule = PaperSchedule(
        paper_account_id=account.paper_account_id,
        paper_run_id=request.paper_run_id,
        cadence=PaperScheduleCadence.DAILY,
        timezone="UTC",
        missed_run_policy=MissedRunPolicy.SKIP,
        starts_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    recovery = evaluate_paper_recovery(
        paper_run_id=request.paper_run_id,
        checkpoint_id=None,
        missed_run_policy=MissedRunPolicy.SKIP,
    )
    comparison = build_forward_comparison(
        f2_request_id=candidate.f2_request_id,
        promotion_gate_id=candidate.promotion_gate_id,
        paper_run_id=request.paper_run_id,
        metrics=(
            ForwardComparisonMetric(
                name="return",
                f2_value=0.04,
                f3_value=0.03,
                unit="ratio",
                methodology="m8.forward-comparison.v1",
            ),
        ),
    )

    store = SQLitePaperEvaluationStore(tmp_path / "paper.sqlite")
    store.initialize()
    store.save_paper_account(account)
    store.save_approved_candidate(candidate)
    store.save_evaluation_request(request)
    store.save_health_gate(health)
    store.save_control_decision(control)
    store.save_schedule(schedule)
    store.save_recovery_decision(recovery)
    store.save_forward_comparison(comparison)

    assert store.list_paper_accounts() == (account,)
    assert store.list_approved_candidates() == (candidate,)
    assert store.list_evaluation_requests(account.paper_account_id) == (request,)
    assert store.list_health_gates(request.paper_run_id) == (health,)
    assert store.list_control_decisions(account.paper_account_id) == (control,)
    assert store.list_schedules(request.paper_run_id) == (schedule,)
    assert store.list_recovery_decisions(request.paper_run_id) == (recovery,)
    assert store.list_forward_comparisons(request.paper_run_id) == (comparison,)


def test_paper_evaluation_store_filters_by_account_and_run(tmp_path) -> None:
    selected_account = PaperAccount(name="selected")
    other_account = PaperAccount(name="other")
    selected_request = PaperEvaluationRequest(
        paper_account_id=selected_account.paper_account_id,
        approved_candidate_id=uuid4(),
        candidate_id="candidate.selected",
        promotion_gate_id=uuid4(),
        data_requirements=(
            PaperDataRequirement(dataset_revision_id=uuid4(), freshness_policy_id="forward.strict"),
        ),
    )
    other_request = PaperEvaluationRequest(
        paper_account_id=other_account.paper_account_id,
        approved_candidate_id=uuid4(),
        candidate_id="candidate.other",
        promotion_gate_id=uuid4(),
        data_requirements=(
            PaperDataRequirement(dataset_revision_id=uuid4(), freshness_policy_id="forward.strict"),
        ),
    )

    store = SQLitePaperEvaluationStore(tmp_path / "paper.sqlite")
    store.initialize()
    store.save_paper_account(selected_account)
    store.save_paper_account(other_account)
    store.save_evaluation_request(selected_request)
    store.save_evaluation_request(other_request)

    assert store.list_evaluation_requests(selected_account.paper_account_id) == (selected_request,)
