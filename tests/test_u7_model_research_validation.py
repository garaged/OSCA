from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pyarrow as pa
import pyarrow.parquet as pq
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
from osca.model_validation import (
    ModelValidationRequest,
    PromotionDecision,
    ResearchSignalRule,
    ValidationStatus,
    validate_model_research,
)
from osca.prediction_lab import DiagnosticStatus, ExperimentDiagnostic


def _payload(path: Path) -> tuple[Path, datetime]:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    rows = []
    for index in range(60):
        open_price = 100.0 + index
        close_price = open_price + (1.0 if index % 3 else -0.5)
        rows.append(
            {
                "timestamp": start + timedelta(days=index),
                "open": open_price,
                "high": max(open_price, close_price) + 0.5,
                "low": min(open_price, close_price) - 0.5,
                "close": close_price,
                "volume": 1_000.0 + index,
            }
        )
    pq.write_table(pa.Table.from_pylist(rows), path)
    return path, start


def _experiment(
    start: datetime,
    *,
    task: ExperimentTask = ExperimentTask.CLASSIFICATION,
) -> MLExperimentResult:
    predictions = tuple(
        PredictionRecord(
            timestamp=start + timedelta(days=index),
            split="test",
            actual=float(index % 2),
            prediction=float(index % 2),
            probability=0.8 if index % 2 else 0.2,
        )
        for index in range(10, 50)
    )
    metrics = ExperimentMetrics(accuracy=1.0)
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
        feature_names=("lag_return", "rolling_mean_return", "rolling_volatility"),
        label_definition="future direction",
        splits=(
            ExperimentSplit(
                name="test",
                start=predictions[0].timestamp,
                end=predictions[-1].timestamp,
                rows=len(predictions),
            ),
        ),
        predictions=predictions,
        validation_metrics=metrics,
        test_metrics=metrics,
        baseline_test_metrics=ExperimentMetrics(accuracy=0.5),
        parameters={"horizon": 1},
        coefficients=(0.2, 0.1, -0.1),
        intercept=0.0,
        findings=(),
        input_digest="b" * 64,
        output_digest="c" * 64,
    )


def _diagnostic(experiment: MLExperimentResult) -> ExperimentDiagnostic:
    return ExperimentDiagnostic(
        experiment_id=experiment.experiment_id,
        task=experiment.task,
        status=DiagnosticStatus.ELIGIBLE_FOR_F2_VALIDATION,
        predictions=experiment.predictions,
        residuals=tuple(item.prediction - item.actual for item in experiment.predictions),
        absolute_error_quantiles={"p50": 0.0, "p90": 0.0, "p95": 0.0, "maximum": 0.0},
        confusion_matrix={"true_positive": 20, "true_negative": 20},
        calibration=(),
        roc_curve=(),
        precision_recall_curve=(),
        coefficient_evidence={"lag_return": 0.2},
        regime_breakdowns=(),
        findings=(),
        warnings=("not causal",),
        diagnostic_digest="d" * 64,
    )


def _request(path: Path, start: datetime) -> ModelValidationRequest:
    experiment = _experiment(start)
    return ModelValidationRequest(
        experiment=experiment,
        diagnostic=_diagnostic(experiment),
        promotion=PromotionDecision(
            approved=True,
            reviewer="research-owner",
            rationale="Approved for local F2 validation only.",
            decided_at=start,
        ),
        payload_path=path,
        signal_rule=ResearchSignalRule(
            threshold=0.5,
            transaction_cost_bps=5.0,
            slippage_bps=5.0,
            latency_bars=1,
        ),
    )


def test_validation_links_predictions_signals_costs_and_backtest(tmp_path: Path) -> None:
    path, start = _payload(tmp_path / "prices.parquet")
    result = validate_model_research(_request(path, start))

    assert result.status is ValidationStatus.COMPLETED
    assert result.summary.aligned_predictions == 40
    assert result.summary.invested_periods == 20
    assert result.summary.position_changes > 0
    assert result.summary.total_cost_return > 0
    assert result.events[0].execution_timestamp > result.events[0].prediction_timestamp
    assert result.event_driven_validation_enabled is True
    assert result.automatic_promotion_enabled is False
    assert result.broker_execution_enabled is False
    assert result.real_capital_execution_enabled is False


def test_paper_challenger_requires_and_records_human_approval(tmp_path: Path) -> None:
    path, start = _payload(tmp_path / "paper.parquet")
    base = _request(path, start)
    request = base.model_copy(
        update={
            "request_paper_challenger": True,
            "paper_challenger_reviewer": "paper-owner",
            "paper_challenger_rationale": "Approved for local evidence comparison.",
        }
    )
    result = validate_model_research(request)

    assert result.status is ValidationStatus.PAPER_CHALLENGER_APPROVED
    assert result.paper_challenger.approved is True
    assert result.paper_challenger.mode == "local-evidence-only"
    assert result.broker_execution_enabled is False


def test_unapproved_promotion_fails_closed(tmp_path: Path) -> None:
    path, start = _payload(tmp_path / "rejected.parquet")
    request = _request(path, start)
    request = request.model_copy(
        update={"promotion": request.promotion.model_copy(update={"approved": False})}
    )
    with pytest.raises(ValueError, match="approved human promotion"):
        validate_model_research(request)


def test_noneligible_diagnostic_and_regression_fail_closed(tmp_path: Path) -> None:
    path, start = _payload(tmp_path / "invalid.parquet")
    request = _request(path, start)
    exploratory = request.diagnostic.model_copy(
        update={"status": DiagnosticStatus.EXPLORATORY}
    )
    with pytest.raises(ValueError, match="not eligible"):
        validate_model_research(request.model_copy(update={"diagnostic": exploratory}))

    regression = _experiment(start, task=ExperimentTask.REGRESSION)
    regression_request = request.model_copy(
        update={"experiment": regression, "diagnostic": _diagnostic(regression)}
    )
    with pytest.raises(ValueError, match="classification"):
        validate_model_research(regression_request)


def test_workspace_api_returns_traceable_validation(tmp_path: Path) -> None:
    path, start = _payload(tmp_path / "api.parquet")
    request = _request(path, start)
    client = TestClient(create_app(storage_root=tmp_path))
    response = client.post(
        "/api/model-validation/run",
        json=request.model_dump(mode="json"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["experiment_id"] == str(request.experiment.experiment_id)
    assert body["diagnostic_digest"] == request.diagnostic.diagnostic_digest
    assert body["automatic_promotion_enabled"] is False
    assert body["broker_execution_enabled"] is False
