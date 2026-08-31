from __future__ import annotations

import csv
import math
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from osca.desktop_api.contracts import DesktopRequest, DesktopResponse
from osca.desktop_api.paper_evaluation import PaperEvaluationDesktopService
from osca.local_data_import import (
    LocalOHLCVImportRequest,
    LocalOHLCVTimeframe,
    import_local_ohlcv,
)
from osca.operator_experience import load_operator_config


def _call(
    service: PaperEvaluationDesktopService,
    method: str,
    params: dict[str, Any],
) -> DesktopResponse:
    return service.handle(DesktopRequest(request_id=f"test-{method}", method=method, params=params))


def _prepared(tmp_path: Path) -> tuple[PaperEvaluationDesktopService, Path]:
    service = PaperEvaluationDesktopService(state_root=tmp_path / "state")
    profile_root = tmp_path / "profile"
    created = _call(service, "profile.create", {"profile_root": str(profile_root)})
    assert created.status == "ok", created.error
    source = tmp_path / "ml-bars.csv"
    start = datetime(2026, 1, 1, tzinfo=UTC)
    close = 100.0
    with source.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=("timestamp", "open", "high", "low", "close", "volume"),
        )
        writer.writeheader()
        for index in range(220):
            close *= 1.0 + 0.002 * math.sin(index / 7) + 0.0004
            writer.writerow(
                {
                    "timestamp": (start + timedelta(days=index)).isoformat(),
                    "open": close - 0.2,
                    "high": close + 0.8,
                    "low": close - 0.8,
                    "close": close,
                    "volume": 10_000 + index,
                }
            )
    config = load_operator_config(profile_root)
    import_local_ohlcv(
        LocalOHLCVImportRequest(
            input_path=str(source),
            storage_root=config.storage_root,
            symbol="AAPL-SYNTHETIC",
            timeframe=LocalOHLCVTimeframe.ONE_DAY,
            source_uri="local-test://d10/aapl",
            revision_salt="d10-test-220-bars",
            calendar_assumption="synthetic-daily-sequence",
        )
    )
    return service, profile_root


def _definition(profile_root: Path, **overrides: Any) -> dict[str, Any]:
    return {
        "profile_root": str(profile_root),
        "name": "D10 deterministic ridge experiment",
        "asset_id": "equity:XNAS:AAPL",
        "timeframe": "1d",
        "task": "regression",
        "model": "ridge_regression",
        "horizon": 2,
        "feature_window": 8,
        "train_fraction": 0.6,
        "validation_fraction": 0.2,
        "embargo": 1,
        "iterations": 300,
        **overrides,
    }


def test_catalog_and_experiment_survive_restart_with_immutable_lineage(tmp_path: Path) -> None:
    service, profile_root = _prepared(tmp_path)
    catalog = _call(service, "ml.catalog.list", {"profile_root": str(profile_root)})
    assert catalog.status == "ok", catalog.error
    assert catalog.result is not None
    assert len(catalog.result["features"]) == 3
    assert all(item["point_in_time_safe"] for item in catalog.result["features"])
    assert all(item["leakage_checked"] for item in catalog.result["labels"])

    created = _call(service, "ml.experiment.create", _definition(profile_root))
    assert created.status == "ok", created.error
    assert created.result is not None
    experiment = created.result["experiment"]
    assert experiment["status"] == "planned"
    definition = experiment["definition"]
    assert definition["payload_sha256"]
    assert definition["split_policy"]["purge_bars"] == 2
    assert definition["split_policy"]["scaler_fit"] == "training_only"
    assert definition["mandatory_baseline"] == "persistence_or_moving_average"
    assert definition["engine_revision"] == "osca.ml_experiments.engine.v1"
    assert str(definition["code_revision"]).startswith("osca-package:")
    assert definition["data_policies"]["missing_data"] == "fail_closed"
    assert "payload_path" not in str(definition)

    run = _call(
        service,
        "ml.experiment.run",
        {
            "profile_root": str(profile_root),
            "experiment_id": experiment["experiment_id"],
        },
    )
    assert run.status == "ok", run.error
    assert run.result is not None
    retained = run.result["experiment"]
    assert retained["status"] in {"completed", "review_required"}
    assert retained["result"]["baseline_test_metrics"]
    assert retained["result"]["point_in_time_safe"] is True
    assert retained["automatic_promotion_enabled"] is False
    assert retained["real_capital_execution_enabled"] is False

    restarted = PaperEvaluationDesktopService(state_root=tmp_path / "restart-state")
    listed = _call(restarted, "ml.experiment.list", {"profile_root": str(profile_root)})
    assert listed.status == "ok", listed.error
    assert listed.result is not None
    assert listed.result["experiments"][0]["output_digest"] == retained["output_digest"]


def test_arbitrary_path_unsafe_policy_and_excess_budget_fail_closed(tmp_path: Path) -> None:
    service, profile_root = _prepared(tmp_path)
    path_attempt = _call(
        service,
        "ml.experiment.create",
        _definition(profile_root, payload_path=str(tmp_path / "attacker.parquet")),
    )
    assert path_attempt.status == "error"
    assert path_attempt.error is not None
    assert path_attempt.error.code == "invalid_parameters"

    unsafe_policy = _call(
        service,
        "ml.experiment.create",
        _definition(profile_root, missing_data_policy="drop_rows"),
    )
    assert unsafe_policy.status == "error"
    assert unsafe_policy.error is not None
    assert unsafe_policy.error.code == "ml_experiment_invalid"

    excessive = _call(
        service,
        "ml.experiment.create",
        _definition(profile_root, iterations=10_001),
    )
    assert excessive.status == "error"
    assert excessive.error is not None
    assert excessive.error.code == "ml_resource_budget_exceeded"


def test_planned_experiment_can_be_cancelled_and_not_run(tmp_path: Path) -> None:
    service, profile_root = _prepared(tmp_path)
    created = _call(service, "ml.experiment.create", _definition(profile_root))
    assert created.result is not None
    experiment_id = created.result["experiment"]["experiment_id"]
    cancelled = _call(
        service,
        "ml.experiment.cancel",
        {"profile_root": str(profile_root), "experiment_id": experiment_id},
    )
    assert cancelled.status == "ok", cancelled.error
    assert cancelled.result is not None
    assert cancelled.result["experiment"]["status"] == "cancelled"
    blocked = _call(
        service,
        "ml.experiment.run",
        {"profile_root": str(profile_root), "experiment_id": experiment_id},
    )
    assert blocked.status == "error"
    assert blocked.error is not None
    assert blocked.error.code == "ml_experiment_cancelled"


def test_interrupted_run_recovers_as_failed_and_newer_schema_is_rejected(tmp_path: Path) -> None:
    service, profile_root = _prepared(tmp_path)
    created = _call(service, "ml.experiment.create", _definition(profile_root))
    assert created.result is not None
    experiment_id = created.result["experiment"]["experiment_id"]
    database = profile_root / ".osca" / "desktop" / "d10-ml-lab.sqlite3"
    with sqlite3.connect(database) as connection:
        connection.execute(
            "UPDATE experiments SET status='running' WHERE experiment_id=?", (experiment_id,)
        )
    restarted = PaperEvaluationDesktopService(state_root=tmp_path / "restart-state")
    recovered = _call(
        restarted,
        "ml.experiment.get",
        {"profile_root": str(profile_root), "experiment_id": experiment_id},
    )
    assert recovered.status == "ok", recovered.error
    assert recovered.result is not None
    assert recovered.result["experiment"]["status"] == "failed"
    assert recovered.result["experiment"]["error"]["code"] == "ml_experiment_interrupted"
    assert recovered.result["experiment"]["events"][-1] == {
        "event_type": "experiment.failed",
        "details": {"code": "ml_experiment_interrupted"},
        "created_at": recovered.result["experiment"]["events"][-1]["created_at"],
    }

    with sqlite3.connect(database) as connection:
        connection.execute("PRAGMA user_version=99")
    rejected = _call(restarted, "ml.catalog.list", {"profile_root": str(profile_root)})
    assert rejected.status == "error"
    assert rejected.error is not None
    assert rejected.error.code == "ml_schema_newer"
