from __future__ import annotations

import argparse
import json
from pathlib import Path

from osca.ml_experiments import MLExperimentResult
from osca.prediction_lab import diagnose_experiment


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnose a retained U5 ML experiment.")
    parser.add_argument("experiment_json", type=Path)
    parser.add_argument("--calibration-bins", type=int, default=10)
    args = parser.parse_args()
    result = MLExperimentResult.model_validate_json(args.experiment_json.read_text())
    diagnostic = diagnose_experiment(result, calibration_bins=args.calibration_bins)
    print(json.dumps(diagnostic.model_dump(mode="json"), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
