from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from osca.analyst_workspace.app import create_app
from osca.ml_experiments import (
    ExperimentMetrics,
    ExperimentModel,
    ExperimentSplit,
    ExperimentStatus,
    ExperimentTask,
    MLExperimentResult,
    PredictionRecord,
)
from osca.prediction_lab import DiagnosticStatus, compare_experiments, diagnose_experiment


def _result(*, task: ExperimentTask, score: float = 0.8) -> MLExperimentResult:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    predictions = []
    for index in range(40):
        actual = float(index % 2) if task is ExperimentTask.CLASSIFICATION else index / 100
        prediction = actual if index / 40 < score else 1.0 - actual
        predictions.append(
            PredictionRecord(
                timestamp=start + timedelta(days=index),
                split="test",
                actual=actual,
                prediction=prediction,
                probability=prediction if task is ExperimentTask.CLASSIFICATION else None,
            )
        )
    test_metrics = (
        ExperimentMetrics(accuracy=score)
        if task is ExperimentTask.CLASSIFICATION
        else ExperimentMetrics(mean_absolute_error=1.0 - score)
    )
    baseline_metrics = (
        ExperimentMetrics(accuracy=0.5)
        if task is ExperimentTask.CLASSIFICATION
        else ExperimentMetrics(mean_absolute_error=0.4)
    )
    return MLExperimentResult(
        experiment_id=uuid4(),
        status=ExperimentStatus.COMPLETED,
        dataset_revision_id=uuid4(),
        payload_sha256="a" * 64,
        symbol="TEST",
        timeframe="1d",
        task=task,
        model=(
            ExperimentModel.LOGISTIC
            if task is ExperimentTask.CLASSIFICATION
            else ExperimentModel.RIDGE
        ),
        feature_names=("lag_return", "rolling_mean"),
        label_definition="future target",
        splits=(ExperimentSplit(name="test", start=start, end=start + timedelta(days=39), rows=40),),
        predictions=tuple(predictions),
        validation_metrics=test_metrics,
        test_metrics=test_metrics,
        baseline_test_metrics=baseline_metrics,
        parameters={"horizon": 1},
        coefficients=(0.3, -0.1),
        intercept=0.0,
        findings=(),
        input_digest="b" * 64,
        output_digest="c" * 64,
    )


def test_regression_diagnostic_contains_residuals_and_regime_breakdowns() -> None:
    diagnostic = diagnose_experiment(_result(task=ExperimentTask.REGRESSION))
    assert diagnostic.status is DiagnosticStatus.ELIGIBLE_FOR_F2_VALIDATION
    assert len(diagnostic.residuals) == 40
    assert diagnostic.absolute_error_quantiles["p95"] >= 0
    assert {item.regime for item in diagnostic.regime_breakdowns} == {"early_test", "late_test"}
    assert "not causal" in diagnostic.warnings[0]
    assert diagnostic.automatic_promotion_enabled is False


def test_classification_diagnostic_contains_confusion_calibration_and_curves() -> None:
    diagnostic = diagnose_experiment(_result(task=ExperimentTask.CLASSIFICATION))
    assert sum(diagnostic.confusion_matrix.values()) == 40
    assert diagnostic.calibration
    assert diagnostic.roc_curve
    assert diagnostic.precision_recall_curve
    assert diagnostic.recommendations_enabled is False
    assert diagnostic.real_capital_execution_enabled is False


def test_comparison_ranks_baseline_relative_performance() -> None:
    stronger = _result(task=ExperimentTask.CLASSIFICATION, score=0.9)
    weaker = _result(task=ExperimentTask.CLASSIFICATION, score=0.6)
    comparison = compare_experiments((weaker, stronger))
    assert comparison.ordered_experiment_ids[0] == stronger.experiment_id
    assert comparison.ranking_metric == "test_accuracy_improvement_over_baseline"


def test_mixed_task_comparison_fails_closed() -> None:
    with pytest.raises(ValueError, match="same task"):
        compare_experiments(
            (
                _result(task=ExperimentTask.CLASSIFICATION),
                _result(task=ExperimentTask.REGRESSION),
            )
        )


def test_prediction_lab_api_returns_diagnostics() -> None:
    experiment = _result(task=ExperimentTask.CLASSIFICATION)
    client = TestClient(create_app())
    response = client.post(
        "/api/prediction-lab/diagnose?calibration_bins=5",
        json=experiment.model_dump(mode="json"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["experiment_id"] == str(experiment.experiment_id)
    assert body["confusion_matrix"]
    assert body["automatic_promotion_enabled"] is False
    assert body["broker_execution_enabled"] is False
