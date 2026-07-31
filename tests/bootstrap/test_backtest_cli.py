import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from typer.testing import CliRunner

from osca.backtesting.api import (
    BacktestAssumptionSet,
    BacktestDataAvailability,
    BacktestExecutionMode,
    BacktestFidelityProfile,
    BacktestRequest,
    BacktestWindow,
)
from osca.bootstrap.cli import app

runner = CliRunner()


def make_request() -> BacktestRequest:
    return BacktestRequest(
        project_id=uuid4(),
        strategy_id="strategy.mean-reversion",
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


def test_backtest_plan_persists_request_and_plan(tmp_path: Path) -> None:
    request = make_request()
    request_file = tmp_path / "request.json"
    database = tmp_path / "backtests.sqlite"
    request_file.write_text(request.model_dump_json(), encoding="utf-8")

    result = runner.invoke(
        app,
        ["backtest-plan", str(request_file), "--database", str(database)],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["request_id"] == str(request.request_id)
    assert payload["can_execute"] is True


def test_backtest_list_filters_persisted_requests(tmp_path: Path) -> None:
    request = make_request()
    request_file = tmp_path / "request.json"
    database = tmp_path / "backtests.sqlite"
    request_file.write_text(request.model_dump_json(), encoding="utf-8")
    runner.invoke(app, ["backtest-plan", str(request_file), "--database", str(database)])

    result = runner.invoke(
        app,
        [
            "backtest-list",
            "--database",
            str(database),
            "--strategy-id",
            request.strategy_id,
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert [record["request_id"] for record in payload] == [str(request.request_id)]
