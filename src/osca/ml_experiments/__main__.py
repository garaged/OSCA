from __future__ import annotations

import argparse
import json
from pathlib import Path
from uuid import UUID

from osca.ml_experiments import (
    ExperimentModel,
    ExperimentTask,
    MLExperimentRequest,
    run_experiment,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a governed local ML experiment.")
    parser.add_argument("payload_path", type=Path)
    parser.add_argument("dataset_revision_id", type=UUID)
    parser.add_argument("symbol")
    parser.add_argument("timeframe")
    parser.add_argument("--task", type=ExperimentTask, default=ExperimentTask.REGRESSION)
    parser.add_argument("--model", type=ExperimentModel, default=ExperimentModel.RIDGE)
    parser.add_argument("--horizon", type=int, default=1)
    parser.add_argument("--feature-window", type=int, default=5)
    parser.add_argument("--embargo", type=int, default=0)
    parser.add_argument("--ridge-alpha", type=float, default=1.0)
    parser.add_argument("--iterations", type=int, default=500)
    args = parser.parse_args()
    result = run_experiment(
        MLExperimentRequest(
            dataset_revision_id=args.dataset_revision_id,
            payload_path=args.payload_path,
            symbol=args.symbol,
            timeframe=args.timeframe,
            task=args.task,
            model=args.model,
            horizon=args.horizon,
            feature_window=args.feature_window,
            embargo=args.embargo,
            ridge_alpha=args.ridge_alpha,
            iterations=args.iterations,
        )
    )
    print(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
