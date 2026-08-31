"""Build the disposable, deterministic desktop acceptance profile.

This is deliberately an application-service client rather than a second data path.
It exercises the D5--D10 critical workflow with the same typed methods used by the
desktop sidecar, then leaves the profile ready for a short visual review.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from osca.desktop_api.contracts import DesktopRequest, DesktopResponse
from osca.desktop_api.paper_evaluation import PaperEvaluationDesktopService

DSL: dict[str, Any] = {
    "family": "osca.strategy.dsl",
    "version": "1.0.0",
    "entry": {"type": "close_above_sma", "window": 3},
    "exit": {"type": "close_below_sma", "window": 3},
    "sizing": {"type": "fixed_fraction", "fraction": 1.0},
    "risk": {"max_position_fraction": 1.0},
    "costs": {"fees_bps": 1.0, "slippage_bps": 2.0},
}


def call(
    service: PaperEvaluationDesktopService,
    method: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    response: DesktopResponse = service.handle(
        DesktopRequest(request_id=f"desktop-acceptance-{method}", method=method, params=params)
    )
    if response.status != "ok" or response.result is None:
        detail = response.error.message if response.error else "missing result"
        raise RuntimeError(f"{method} failed: {detail}")
    return response.result


def prepare(root: Path, *, reset: bool) -> dict[str, Any]:
    """Create the profile and retain a machine-readable D5--D10 smoke manifest."""

    root = root.resolve()
    if root.name != "desktop-acceptance" or ".osca" not in root.parts:
        raise ValueError("acceptance root must be a .osca/.../desktop-acceptance directory")
    if reset and root.exists():
        shutil.rmtree(root)
    profile_root = root / "profile"
    evidence_root = root / "evidence"
    evidence_root.mkdir(parents=True, exist_ok=True)
    service = PaperEvaluationDesktopService(state_root=root / "state")
    profile = str(profile_root)

    call(service, "profile.create", {"profile_root": profile})
    imported = call(service, "sample.import", {"profile_root": profile})
    ml_source = evidence_root / "d10-synthetic-aapl-daily.csv"
    _write_ml_sample(ml_source, phase=0.0)
    ml_import = call(
        service,
        "local.import",
        {
            "profile_root": profile,
            "input_path": str(ml_source),
            "symbol": "AAPL-SYNTHETIC",
            "timeframe": "1d",
            "source_uri": "bundled-synthetic://osca/d10/aapl-daily-v1",
            "revision_salt": "d10-acceptance-aapl-220-bars",
            "calendar_assumption": "synthetic-daily-sequence",
        },
    )
    comparison_source = evidence_root / "d10-synthetic-msft-daily.csv"
    _write_ml_sample(comparison_source, phase=1.5)
    call(
        service,
        "local.import",
        {
            "profile_root": profile,
            "input_path": str(comparison_source),
            "symbol": "MSFT-SYNTHETIC",
            "timeframe": "1d",
            "source_uri": "bundled-synthetic://osca/d10/msft-daily-v1",
            "revision_salt": "d10-acceptance-msft-220-bars",
            "calendar_assumption": "synthetic-daily-sequence",
        },
    )
    comparison = call(
        service,
        "workbench.comparison.get",
        {
            "profile_root": profile,
            "primary_asset_id": "equity:XNAS:AAPL",
            "comparison_asset_id": "equity:XNAS:MSFT",
            "timeframe": "1d",
            "rolling_window": 3,
            "max_rows": 10,
        },
    )
    strategy = call(
        service,
        "strategy.create",
        {
            "profile_root": profile,
            "name": "Acceptance AAPL SMA trend",
            "objective": "Deterministic offline D7 acceptance evidence.",
            "asset_id": "equity:XNAS:AAPL",
            "timeframe": "1d",
            "dsl": DSL,
        },
    )["strategy"]
    version_id = strategy["current_version"]["version_id"]
    backtest = call(
        service,
        "backtest.run",
        {
            "profile_root": profile,
            "strategy_id": strategy["strategy_id"],
            "strategy_version_id": version_id,
            "initial_cash": 10_000,
        },
    )["result"]
    sensitivity = call(
        service,
        "backtest.sensitivity.run",
        {
            "profile_root": profile,
            "strategy_id": strategy["strategy_id"],
            "strategy_version_id": version_id,
            "parameter": "entry.window",
            "values": [2, 3, 4],
        },
    )["evaluation"]
    walkforward = call(
        service,
        "backtest.walkforward.run",
        {
            "profile_root": profile,
            "strategy_id": strategy["strategy_id"],
            "strategy_version_id": version_id,
            "train_fraction": 0.5,
        },
    )["evaluation"]
    project = call(
        service,
        "project.create",
        {
            "profile_root": profile,
            "name": "Desktop acceptance evidence",
            "objective": "Inspect deterministic D5--D7 local evidence.",
        },
    )["project"]
    pin = call(
        service,
        "project.pin.add",
        {
            "profile_root": profile,
            "project_id": project["project_id"],
            "pin_type": "backtest_result",
            "source_id": f"backtest:{backtest['result_id']}",
            "label": "Acceptance AAPL SMA result",
            "metadata": {"result_digest": backtest["result_digest"]},
        },
    )["pin"]
    ml_plan = call(
        service,
        "ml.experiment.create",
        {
            "profile_root": profile,
            "name": "Acceptance AAPL ridge baseline",
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
        },
    )["experiment"]
    ml_experiment = call(
        service,
        "ml.experiment.run",
        {"profile_root": profile, "experiment_id": ml_plan["experiment_id"]},
    )["experiment"]
    ml_pin = call(
        service,
        "project.pin.add",
        {
            "profile_root": profile,
            "project_id": project["project_id"],
            "pin_type": "ml_experiment",
            "source_id": f"ml-experiment:{ml_experiment['experiment_id']}",
            "label": "Acceptance AAPL ridge experiment",
            "metadata": {"output_digest": ml_experiment["output_digest"]},
        },
    )["pin"]
    manifest = {
        "family": "osca.desktop-acceptance.manifest",
        "version": "1.0.0",
        "profile_root": profile,
        "network_access_enabled": False,
        "recommendations_enabled": False,
        "real_capital_execution_enabled": False,
        "sample_import": {"symbols": [item["symbol"] for item in imported["imports"]]},
        "ml_sample_import": {
            "dataset_revision_id": ml_import["import"]["dataset_revision_id"],
            "canonical_row_count": ml_import["import"]["row_count"],
        },
        "workbench": {"aligned_return_count": comparison["aligned_return_count"]},
        "strategy": {"strategy_id": strategy["strategy_id"], "version_id": version_id},
        "backtest": {
            "result_id": backtest["result_id"],
            "bars_processed": backtest["metrics"]["bars_processed"],
            "trade_count": backtest["metrics"]["trade_count"],
        },
        "evaluations": {
            "sensitivity_id": sensitivity["evaluation_id"],
            "walkforward_id": walkforward["evaluation_id"],
        },
        "project": {
            "project_id": project["project_id"],
            "pin_id": pin["pin_id"],
            "ml_pin_id": ml_pin["pin_id"],
        },
        "ml_experiment": {
            "experiment_id": ml_experiment["experiment_id"],
            "status": ml_experiment["status"],
            "output_digest": ml_experiment["output_digest"],
            "automatic_promotion_enabled": False,
        },
    }
    (evidence_root / "acceptance-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def _write_ml_sample(path: Path, *, phase: float) -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    close = 100.0
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=("timestamp", "open", "high", "low", "close", "volume"),
        )
        writer.writeheader()
        for index in range(220):
            close *= 1.0 + 0.002 * math.sin(index / 7 + phase) + 0.0004
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    print(json.dumps(prepare(args.root, reset=args.reset), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
