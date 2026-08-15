from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, cast

import pytest

from osca.desktop_api.contracts import DesktopRequest, DesktopResponse
from osca.desktop_api.d7_service import D7DesktopApplicationService


def _call(
    service: D7DesktopApplicationService,
    method: str,
    params: dict[str, Any] | None = None,
) -> DesktopResponse:
    return service.handle(
        DesktopRequest(
            request_id=f"test-{method}",
            method=method,
            params=params or {},
        )
    )


def _profile_with_sample(tmp_path: Path) -> tuple[D7DesktopApplicationService, Path]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    service = D7DesktopApplicationService(state_root=tmp_path / "state")
    profile_root = tmp_path / "profile"
    assert _call(service, "profile.create", {"profile_root": str(profile_root)}).status == "ok"
    assert _call(service, "sample.import", {"profile_root": str(profile_root)}).status == "ok"
    return service, profile_root


def _dsl() -> dict[str, Any]:
    return {
        "family": "osca.strategy.dsl",
        "version": "1.0.0",
        "entry": {"type": "close_above_sma", "window": 3},
        "exit": {"type": "close_below_sma", "window": 3},
        "sizing": {"type": "fixed_fraction", "fraction": 1.0},
        "risk": {"max_position_fraction": 1.0},
        "costs": {"fees_bps": 1.0, "slippage_bps": 2.0},
    }


def _strategy(service: D7DesktopApplicationService, profile_root: Path) -> dict[str, Any]:
    response = _call(
        service,
        "strategy.create",
        {
            "profile_root": str(profile_root),
            "name": "AAPL SMA trend",
            "objective": "Evaluate a local-only SMA trend rule.",
            "asset_id": "equity:XNAS:AAPL",
            "timeframe": "1d",
            "dsl": _dsl(),
        },
    )
    assert response.status == "ok", response.error
    assert response.result is not None
    return cast(dict[str, Any], response.result["strategy"])


def test_strategy_lifecycle_versions_survive_restart(tmp_path: Path) -> None:
    service, profile_root = _profile_with_sample(tmp_path)
    strategy = _strategy(service, profile_root)
    strategy_id = strategy["strategy_id"]
    first_version = strategy["current_version"]
    assert strategy["version_count"] == 1
    assert first_version["version_number"] == 1
    assert first_version["dsl_digest"]
    assert first_version["validation"]["can_execute"] is True

    updated_dsl = {**_dsl(), "entry": {"type": "close_above_sma", "window": 4}}
    versioned = _call(
        service,
        "strategy.version.create",
        {
            "profile_root": str(profile_root),
            "strategy_id": strategy_id,
            "dsl": updated_dsl,
            "summary": "Use a four-day SMA entry rule.",
        },
    )
    assert versioned.status == "ok", versioned.error
    assert versioned.result is not None
    assert versioned.result["strategy"]["version_count"] == 2
    assert versioned.result["strategy_version"]["version_number"] == 2
    assert versioned.result["strategy_version"]["dsl_digest"] != first_version["dsl_digest"]

    restarted = D7DesktopApplicationService(state_root=tmp_path / "state-restarted")
    fetched = _call(
        restarted,
        "strategy.get",
        {"profile_root": str(profile_root), "strategy_id": strategy_id},
    )
    assert fetched.status == "ok"
    assert fetched.result is not None
    versions = fetched.result["strategy"]["versions"]
    assert [version["version_number"] for version in versions] == [1, 2]


def test_strategy_validation_blocks_executable_and_future_data(tmp_path: Path) -> None:
    service, profile_root = _profile_with_sample(tmp_path)

    executable = _call(
        service,
        "strategy.validate",
        {
            "profile_root": str(profile_root),
            "dsl": {
                **_dsl(),
                "entry": {"type": "close_above_sma", "window": 3, "python": "import os"},
            },
        },
    )
    assert executable.status == "ok"
    assert executable.result is not None
    assert executable.result["validation"]["can_execute"] is False
    assert [finding["code"] for finding in executable.result["validation"]["findings"]] == [
        "executable_field"
    ]

    future = _call(
        service,
        "strategy.validate",
        {
            "profile_root": str(profile_root),
            "dsl": {**_dsl(), "filter": {"type": "future_close_above", "window": 1}},
        },
    )
    assert future.result is not None
    assert future.result["validation"]["can_execute"] is False
    assert [finding["code"] for finding in future.result["validation"]["findings"]] == [
        "lookahead_rule"
    ]


def test_backtest_run_is_deterministic_and_retains_evidence(tmp_path: Path) -> None:
    service, profile_root = _profile_with_sample(tmp_path)
    strategy = _strategy(service, profile_root)

    first = _call(
        service,
        "backtest.run",
        {
            "profile_root": str(profile_root),
            "strategy_id": strategy["strategy_id"],
            "strategy_version_id": strategy["current_version"]["version_id"],
            "initial_cash": 10_000,
        },
    )
    second = _call(
        service,
        "backtest.run",
        {
            "profile_root": str(profile_root),
            "strategy_id": strategy["strategy_id"],
            "strategy_version_id": strategy["current_version"]["version_id"],
            "initial_cash": 10_000,
        },
    )

    assert first.status == "ok", first.error
    assert second.status == "ok", second.error
    assert first.result is not None
    assert second.result is not None
    first_result = first.result["result"]
    second_result = second.result["result"]
    assert first_result["status"] == "completed"
    assert first_result["result_digest"] == second_result["result_digest"]
    assert first_result["metrics"]["bars_processed"] == 10
    assert first_result["metrics"]["trade_count"] == 3
    assert first_result["metrics"]["final_equity"] == pytest.approx(10_759.54287546964)
    assert first_result["assumptions"]["fees_bps"] == 1.0
    assert first_result["assumptions"]["slippage_bps"] == 2.0
    assert first_result["network_access_enabled"] is False
    assert first_result["recommendations_enabled"] is False
    assert first_result["real_capital_execution_enabled"] is False
    assert Path(first_result["evidence_path"]).is_file()
    evidence = json.loads(Path(first_result["evidence_path"]).read_text(encoding="utf-8"))
    assert evidence["result_digest"] == first_result["result_digest"]
    assert evidence["source_dataset"]["asset_id"] == "equity:XNAS:AAPL"
    assert evidence["fidelity_level"] == "vectorized_research"


def test_backtest_export_and_project_pin_reference_thin_evidence(tmp_path: Path) -> None:
    service, profile_root = _profile_with_sample(tmp_path)
    strategy = _strategy(service, profile_root)
    run = _call(
        service,
        "backtest.run",
        {
            "profile_root": str(profile_root),
            "strategy_id": strategy["strategy_id"],
            "strategy_version_id": strategy["current_version"]["version_id"],
        },
    )
    assert run.result is not None
    result_id = run.result["result"]["result_id"]

    exported = _call(
        service,
        "backtest.export.prepare",
        {"profile_root": str(profile_root), "result_id": result_id},
    )
    assert exported.status == "ok", exported.error
    assert exported.result is not None
    assert exported.result["thin_manifest"] is True
    assert exported.result["provider_datasets_embedded"] is False
    assert len(exported.result["data_paths"]) == 2
    manifest = json.loads(Path(exported.result["manifest_path"]).read_text(encoding="utf-8"))
    assert manifest["result"]["result_id"] == result_id
    assert manifest["provider_datasets_embedded"] is False
    assert manifest["data_paths"] == exported.result["data_paths"]
    equity_csv, trades_csv = [Path(path) for path in exported.result["data_paths"]]
    assert equity_csv.read_text(encoding="utf-8").splitlines()[0] == (
        "timestamp,close,equity,drawdown,signal"
    )
    assert len(equity_csv.read_text(encoding="utf-8").splitlines()) == 11
    assert trades_csv.read_text(encoding="utf-8").splitlines()[0] == (
        "timestamp,side,fill_price,quantity,fees,research_assumption"
    )

    project = _call(
        service,
        "project.create",
        {
            "profile_root": str(profile_root),
            "name": "AAPL strategy research",
            "objective": "Collect D7 evidence.",
        },
    )
    assert project.result is not None
    pin = _call(
        service,
        "project.pin.add",
        {
            "profile_root": str(profile_root),
            "project_id": project.result["project"]["project_id"],
            "pin_type": "backtest_result",
            "source_id": f"backtest:{result_id}",
            "label": "AAPL SMA trend result",
            "metadata": {"result_digest": run.result["result"]["result_digest"]},
        },
    )
    assert pin.status == "ok", pin.error
    assert pin.result is not None
    assert pin.result["pin"]["pin_type"] == "backtest_result"


def test_sensitivity_and_walkforward_retain_bounded_evidence(tmp_path: Path) -> None:
    service, profile_root = _profile_with_sample(tmp_path)
    strategy = _strategy(service, profile_root)

    sensitivity = _call(
        service,
        "backtest.sensitivity.run",
        {
            "profile_root": str(profile_root),
            "strategy_id": strategy["strategy_id"],
            "strategy_version_id": strategy["current_version"]["version_id"],
            "parameter": "entry.window",
            "values": [2, 3, 4],
        },
    )
    assert sensitivity.status == "ok", sensitivity.error
    assert sensitivity.result is not None
    sweep = sensitivity.result["evaluation"]
    assert sweep["evaluation_type"] == "sensitivity"
    assert sweep["budget"]["max_scenarios"] == 12
    assert sweep["budget"]["requested_scenarios"] == 3
    assert sweep["budget"]["cancellation_supported"] is True
    assert [row["value"] for row in sweep["rows"]] == [2, 3, 4]
    assert all(row["status"] == "completed" for row in sweep["rows"])
    assert "overfit" in sweep["warnings"][0].lower()
    assert Path(sweep["evidence_path"]).is_file()

    too_large = _call(
        service,
        "backtest.sensitivity.run",
        {
            "profile_root": str(profile_root),
            "strategy_id": strategy["strategy_id"],
            "strategy_version_id": strategy["current_version"]["version_id"],
            "parameter": "entry.window",
            "values": list(range(2, 15)),
        },
    )
    assert too_large.status == "error"
    assert too_large.error is not None
    assert too_large.error.code == "sensitivity_budget_exceeded"

    walkforward = _call(
        service,
        "backtest.walkforward.run",
        {
            "profile_root": str(profile_root),
            "strategy_id": strategy["strategy_id"],
            "strategy_version_id": strategy["current_version"]["version_id"],
            "train_fraction": 0.5,
        },
    )
    assert walkforward.status == "ok", walkforward.error
    assert walkforward.result is not None
    evaluation = walkforward.result["evaluation"]
    assert evaluation["evaluation_type"] == "walkforward"
    partition = evaluation["partitions"][0]
    assert partition["train_rows"] == 5
    assert partition["test_rows"] == 5
    assert partition["train_end"] < partition["test_start"]
    assert evaluation["rows"][0]["metrics"]["bars_processed"] == 5
    assert "test partition" in evaluation["warnings"][0]

    cancelled = _call(
        service,
        "backtest.cancel",
        {"profile_root": str(profile_root), "evaluation_id": evaluation["evaluation_id"]},
    )
    assert cancelled.status == "ok"
    assert cancelled.result is not None
    assert cancelled.result["evaluation"]["cancelled"] is False
    assert cancelled.result["evaluation"]["status"] == "completed"


def test_backtest_blocks_invalid_strategy_and_missing_governed_data(tmp_path: Path) -> None:
    service, profile_root = _profile_with_sample(tmp_path)
    invalid = _call(
        service,
        "strategy.create",
        {
            "profile_root": str(profile_root),
            "name": "Invalid",
            "objective": "Cannot run.",
            "asset_id": "equity:XNAS:AAPL",
            "timeframe": "1d",
            "dsl": {**_dsl(), "entry": {"type": "future_close_above", "window": 1}},
        },
    )
    assert invalid.status == "ok"
    assert invalid.result is not None
    blocked = _call(
        service,
        "backtest.run",
        {
            "profile_root": str(profile_root),
            "strategy_id": invalid.result["strategy"]["strategy_id"],
            "strategy_version_id": invalid.result["strategy"]["current_version"]["version_id"],
        },
    )
    assert blocked.status == "error"
    assert blocked.error is not None
    assert blocked.error.code == "strategy_validation_failed"

    missing = _call(
        service,
        "strategy.create",
        {
            "profile_root": str(profile_root),
            "name": "Missing data",
            "objective": "Cannot resolve dataset.",
            "asset_id": "crypto:KRAKEN:XBTUSD",
            "timeframe": "1d",
            "dsl": _dsl(),
        },
    )
    assert missing.result is not None
    unavailable = _call(
        service,
        "backtest.run",
        {
            "profile_root": str(profile_root),
            "strategy_id": missing.result["strategy"]["strategy_id"],
            "strategy_version_id": missing.result["strategy"]["current_version"]["version_id"],
        },
    )
    assert unavailable.status == "error"
    assert unavailable.error is not None
    assert unavailable.error.code == "workbench_data_unavailable"


def test_strategy_profile_isolation_and_newer_schema_rejection(tmp_path: Path) -> None:
    service, first = _profile_with_sample(tmp_path / "first")
    strategy = _strategy(service, first)
    second_parent = tmp_path / "second"
    second_parent.mkdir(parents=True, exist_ok=True)
    second = second_parent / "profile"
    assert _call(service, "profile.create", {"profile_root": str(second)}).status == "ok"

    other = _call(service, "strategy.list", {"profile_root": str(second)})
    assert other.result is not None
    assert other.result["strategies"] == []

    database = first / ".osca" / "desktop" / "d7-strategies.sqlite3"
    assert database.is_file()
    with sqlite3.connect(database) as connection:
        connection.execute("PRAGMA user_version=99")

    response = _call(
        service,
        "strategy.get",
        {"profile_root": str(first), "strategy_id": strategy["strategy_id"]},
    )
    assert response.status == "error"
    assert response.error is not None
    assert response.error.code == "strategy_schema_newer"
