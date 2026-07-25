import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

from osca.backtesting.api import (
    BacktestAssumptionSet,
    BacktestDataAvailability,
    BacktestExecutionMode,
    BacktestFidelityProfile,
    BacktestMetric,
    BacktestRequest,
    BacktestResult,
    BacktestStatus,
    BacktestWindow,
)
from osca.backtesting.application import plan_backtest_execution
from osca.backtesting.persistence import SQLiteBacktestLifecycleStore


def make_request(*, project_id=None, strategy_id: str = "strategy.mean-reversion") -> BacktestRequest:
    return BacktestRequest(
        project_id=project_id or uuid4(),
        strategy_id=strategy_id,
        fidelity_profile=BacktestFidelityProfile.F2_EVENT_DRIVEN_BAR,
        execution_mode=BacktestExecutionMode.EVENT_DRIVEN,
        window=BacktestWindow(
            start_at=datetime(2026, 1, 1, tzinfo=UTC),
            end_at=datetime(2026, 1, 31, tzinfo=UTC),
        ),
        dataset_revision_ids=(uuid4(),),
        data_availability=BacktestDataAvailability.POINT_IN_TIME,
        assumptions=BacktestAssumptionSet(assumption_set_id="base"),
    )


def make_store(tmp_path: Path) -> SQLiteBacktestLifecycleStore:
    store = SQLiteBacktestLifecycleStore(tmp_path / "backtests.sqlite")
    store.initialize()
    return store


def test_backtest_store_round_trips_request_plan_and_result(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    request = make_request()
    plan = plan_backtest_execution(request)
    result = BacktestResult(
        request_id=request.request_id,
        status=BacktestStatus.COMPLETED,
        metrics=(
            BacktestMetric(
                name="total_return",
                value=0.18,
                unit="ratio",
                methodology="simple",
            ),
        ),
    )

    store.save_request(request)
    store.save_execution_plan(plan)
    store.save_result(result)

    assert store.get_request(request.request_id) == request
    assert store.get_execution_plan(request.request_id) == plan
    assert store.get_result(result.result_id) == result
    assert store.list_results_for_request(request.request_id) == (result,)


def test_backtest_store_filters_requests_by_project_and_strategy(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    project_id = uuid4()
    selected = make_request(project_id=project_id, strategy_id="strategy.a")
    other_project = make_request(strategy_id="strategy.a")
    other_strategy = make_request(project_id=project_id, strategy_id="strategy.b")

    for request in (selected, other_project, other_strategy):
        store.save_request(request)

    assert store.list_requests(project_id=project_id, strategy_id="strategy.a") == (selected,)
    assert store.list_requests(project_id=project_id) == (selected, other_strategy)
    assert store.list_requests(strategy_id="strategy.a") == (selected, other_project)


def test_backtest_store_requires_request_before_plan_or_result(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    request = make_request()
    plan = plan_backtest_execution(request)
    result = BacktestResult(request_id=request.request_id, status=BacktestStatus.BLOCKED)

    with pytest.raises(sqlite3.IntegrityError):
        store.save_execution_plan(plan)

    with pytest.raises(sqlite3.IntegrityError):
        store.save_result(result)
