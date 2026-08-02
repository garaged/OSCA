from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Annotated
from uuid import UUID

import typer

from osca.bootstrap.cli import app
from osca.historical_acquisition import app as historical_data_app

app.add_typer(historical_data_app, name="historical-data")


@app.command("research-pipeline")
def research_pipeline(
    payload_path: Path,
    dataset_revision_id: UUID,
    symbol: str,
    timeframe: str,
    storage_root: Annotated[Path, typer.Option("--storage-root")] = Path(".osca"),
    reviewer: Annotated[str, typer.Option("--reviewer")] = "",
    rationale: Annotated[str, typer.Option("--rationale")] = "",
    approve_local_validation: Annotated[
        bool,
        typer.Option(
            "--approve-local-validation",
            help=(
                "Record explicit human approval for local evidence-only U7 validation. "
                "This never enables recommendations, serving, brokers, or real capital."
            ),
        ),
    ] = False,
    horizon: Annotated[int, typer.Option("--horizon")] = 1,
    feature_window: Annotated[int, typer.Option("--feature-window")] = 20,
    embargo: Annotated[int, typer.Option("--embargo")] = 5,
    iterations: Annotated[int, typer.Option("--iterations")] = 1000,
    calibration_bins: Annotated[int, typer.Option("--calibration-bins")] = 10,
    threshold: Annotated[float, typer.Option("--threshold")] = 0.5,
    transaction_cost_bps: Annotated[
        float, typer.Option("--transaction-cost-bps")
    ] = 5.0,
    slippage_bps: Annotated[float, typer.Option("--slippage-bps")] = 5.0,
    latency_bars: Annotated[int, typer.Option("--latency-bars")] = 1,
    initial_cash: Annotated[float, typer.Option("--initial-cash")] = 10_000.0,
) -> None:
    """Run logistic classification, diagnostics, and human-gated local validation.

    The governed model is ``logistic_classification`` and the task is
    ``classification``. Evidence is retained under STORAGE_ROOT/research-evidence.
    """

    command = [
        sys.executable,
        "-m",
        "osca.research_pipeline",
        str(payload_path),
        str(dataset_revision_id),
        symbol,
        timeframe,
        "--storage-root",
        str(storage_root),
        "--reviewer",
        reviewer,
        "--rationale",
        rationale,
        "--horizon",
        str(horizon),
        "--feature-window",
        str(feature_window),
        "--embargo",
        str(embargo),
        "--iterations",
        str(iterations),
        "--calibration-bins",
        str(calibration_bins),
        "--threshold",
        str(threshold),
        "--transaction-cost-bps",
        str(transaction_cost_bps),
        "--slippage-bps",
        str(slippage_bps),
        "--latency-bars",
        str(latency_bars),
        "--initial-cash",
        str(initial_cash),
    ]
    if approve_local_validation:
        command.append("--approve-local-validation")

    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        raise typer.Exit(completed.returncode)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
