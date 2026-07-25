from datetime import UTC, datetime
from uuid import uuid4

from osca.backtesting.api import (
    BacktestAssumptionSet,
    BacktestDataAvailability,
    BacktestExecutionMode,
    BacktestFidelityProfile,
    BacktestRequest,
    BacktestWindow,
)
from osca.backtesting.application import plan_backtest_execution, validate_backtest_request


def make_request(
    *,
    profile: BacktestFidelityProfile = BacktestFidelityProfile.F2_EVENT_DRIVEN_BAR,
    mode: BacktestExecutionMode = BacktestExecutionMode.EVENT_DRIVEN,
    data_availability: BacktestDataAvailability = BacktestDataAvailability.POINT_IN_TIME,
) -> BacktestRequest:
    return BacktestRequest(
        project_id=uuid4(),
        strategy_id="strategy.mean-reversion",
        fidelity_profile=profile,
        execution_mode=mode,
        window=BacktestWindow(
            start_at=datetime(2026, 1, 1, tzinfo=UTC),
            end_at=datetime(2026, 1, 31, tzinfo=UTC),
        ),
        dataset_revision_ids=(uuid4(),),
        data_availability=data_availability,
        assumptions=BacktestAssumptionSet(assumption_set_id="base"),
    )


def test_execution_plan_allows_clean_event_driven_bar_request() -> None:
    plan = plan_backtest_execution(make_request())

    assert plan.can_execute is True
    assert not plan.findings
    assert "event_order_lifecycle" in plan.required_checks
    assert "portfolio_accounting_boundary" in plan.required_checks


def test_validation_blocks_vectorized_mode_for_event_driven_profile() -> None:
    findings = validate_backtest_request(
        make_request(mode=BacktestExecutionMode.VECTORIZED)
    )

    assert [finding.code for finding in findings] == ["execution_mode_mismatch"]


def test_validation_blocks_lookahead_data() -> None:
    plan = plan_backtest_execution(
        make_request(data_availability=BacktestDataAvailability.REVISED_AFTER_FACT)
    )

    assert plan.can_execute is False
    assert [finding.code for finding in plan.findings] == ["lookahead_data"]


def test_validation_blocks_provisional_data_for_event_driven_profiles() -> None:
    plan = plan_backtest_execution(
        make_request(data_availability=BacktestDataAvailability.PROVISIONAL)
    )

    assert plan.can_execute is False
    assert [finding.code for finding in plan.findings] == ["provisional_execution_data"]


def test_forward_paper_profile_is_deferred_until_account_authority_exists() -> None:
    plan = plan_backtest_execution(
        make_request(
            profile=BacktestFidelityProfile.F3_FORWARD_PAPER,
            mode=BacktestExecutionMode.FORWARD_PAPER,
        )
    )

    assert plan.can_execute is False
    assert [finding.code for finding in plan.findings] == ["paper_account_deferred"]
