from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from osca.ml_experiments import (
    ExperimentModel,
    ExperimentTask,
    MLExperimentRequest,
    run_experiment,
)
from osca.model_validation import (
    ModelValidationRequest,
    PromotionDecision,
    ResearchSignalRule,
    validate_model_research,
)
from osca.prediction_lab import DiagnosticStatus, diagnose_experiment


def _write_json(path: Path, value: object) -> None:
    if hasattr(value, "model_dump"):
        payload = value.model_dump(mode="json")
    else:
        payload = value
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run the governed local classification experiment, U6 diagnostic, "
            "and human-gated U7 validation while retaining all evidence under "
            "the configured storage root."
        )
    )
    parser.add_argument("payload_path", type=Path)
    parser.add_argument("dataset_revision_id")
    parser.add_argument("symbol")
    parser.add_argument("timeframe")
    parser.add_argument("--storage-root", type=Path, default=Path(".osca"))
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--rationale", required=True)
    parser.add_argument(
        "--approve-local-validation",
        action="store_true",
        help=(
            "Record explicit human approval for local evidence-only validation. "
            "This never enables recommendations, serving, brokers, or real capital."
        ),
    )
    parser.add_argument("--horizon", type=int, default=1)
    parser.add_argument("--feature-window", type=int, default=20)
    parser.add_argument("--embargo", type=int, default=5)
    parser.add_argument("--iterations", type=int, default=1000)
    parser.add_argument("--calibration-bins", type=int, default=10)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--transaction-cost-bps", type=float, default=5.0)
    parser.add_argument("--slippage-bps", type=float, default=5.0)
    parser.add_argument("--latency-bars", type=int, default=1)
    parser.add_argument("--initial-cash", type=float, default=10_000.0)
    args = parser.parse_args()

    if not args.approve_local_validation:
        parser.error("--approve-local-validation is required for the U7 human gate")
    if not args.payload_path.is_file():
        parser.error(f"payload does not exist: {args.payload_path}")

    run_id = uuid4()
    artifact_root = args.storage_root / "research-evidence" / str(run_id)
    artifact_root.mkdir(parents=True, exist_ok=False)

    experiment = run_experiment(
        MLExperimentRequest(
            dataset_revision_id=args.dataset_revision_id,
            payload_path=args.payload_path,
            symbol=args.symbol,
            timeframe=args.timeframe,
            task=ExperimentTask.CLASSIFICATION,
            model=ExperimentModel.LOGISTIC,
            horizon=args.horizon,
            feature_window=args.feature_window,
            embargo=args.embargo,
            iterations=args.iterations,
        )
    )
    experiment_path = artifact_root / "experiment.json"
    _write_json(experiment_path, experiment)

    diagnostic = diagnose_experiment(
        experiment,
        calibration_bins=args.calibration_bins,
    )
    diagnostic_path = artifact_root / "diagnostic.json"
    _write_json(diagnostic_path, diagnostic)

    if diagnostic.status is not DiagnosticStatus.ELIGIBLE_FOR_F2_VALIDATION:
        manifest = {
            "family": "osca.research-pipeline.manifest",
            "version": "1.0.0",
            "run_id": str(run_id),
            "status": "diagnostic_not_eligible",
            "experiment_id": str(experiment.experiment_id),
            "diagnostic_status": diagnostic.status.value,
            "artifacts": {
                "experiment": str(experiment_path),
                "diagnostic": str(diagnostic_path),
            },
            "automatic_promotion_enabled": False,
            "recommendations_enabled": False,
            "broker_execution_enabled": False,
            "real_capital_execution_enabled": False,
        }
        manifest_path = artifact_root / "manifest.json"
        _write_json(manifest_path, manifest)
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return

    request = ModelValidationRequest(
        experiment=experiment,
        diagnostic=diagnostic,
        promotion=PromotionDecision(
            approved=True,
            reviewer=args.reviewer,
            rationale=args.rationale,
            decided_at=datetime.now(UTC),
        ),
        payload_path=args.payload_path,
        initial_cash=args.initial_cash,
        signal_rule=ResearchSignalRule(
            threshold=args.threshold,
            transaction_cost_bps=args.transaction_cost_bps,
            slippage_bps=args.slippage_bps,
            latency_bars=args.latency_bars,
        ),
    )
    request_path = artifact_root / "validation-request.json"
    _write_json(request_path, request)

    validation = validate_model_research(request)
    validation_path = artifact_root / "validation-result.json"
    _write_json(validation_path, validation)

    manifest = {
        "family": "osca.research-pipeline.manifest",
        "version": "1.0.0",
        "run_id": str(run_id),
        "status": validation.status.value,
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "dataset_revision_id": str(experiment.dataset_revision_id),
        "experiment_id": str(experiment.experiment_id),
        "diagnostic_status": diagnostic.status.value,
        "validation_id": str(validation.validation_id),
        "reviewer": args.reviewer,
        "artifacts": {
            "experiment": str(experiment_path),
            "diagnostic": str(diagnostic_path),
            "validation_request": str(request_path),
            "validation_result": str(validation_path),
        },
        "summary": validation.summary.model_dump(mode="json"),
        "evidence_digest": validation.evidence_digest,
        "event_driven_validation_enabled": validation.event_driven_validation_enabled,
        "live_model_serving_enabled": validation.live_model_serving_enabled,
        "automatic_promotion_enabled": validation.automatic_promotion_enabled,
        "recommendations_enabled": validation.recommendations_enabled,
        "broker_execution_enabled": validation.broker_execution_enabled,
        "real_capital_execution_enabled": validation.real_capital_execution_enabled,
    }
    manifest_path = artifact_root / "manifest.json"
    _write_json(manifest_path, manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
