from uuid import uuid4

import pytest
from pydantic import ValidationError

from osca.ml import (
    DatasetSplit,
    MLDeploymentRole,
    MLDriftMetric,
    MLFinding,
    MLFindingSeverity,
    MLMetric,
    MLModelArtifact,
    MLMonitoringReport,
    MLMonitoringStatus,
    MLPromotionDecision,
    MLRetrainingRecord,
    MLRetrainingTrigger,
    build_evaluation_report,
    build_monitoring_report,
    decide_paper_deployment,
    evaluate_ml_promotion,
    link_model_to_event_validation,
    request_retraining,
)


def test_event_validation_link_requires_approved_promotion() -> None:
    promotion = _approved_promotion(approved=False)

    with pytest.raises(ValueError, match="approved ML promotion"):
        link_model_to_event_validation(
            promotion=promotion,
            f2_request_id=uuid4(),
            f2_promotion_gate_id=uuid4(),
        )


def test_paper_deployment_requires_event_validation_approval() -> None:
    promotion = _approved_promotion(approved=False)

    decision = decide_paper_deployment(
        promotion=promotion,
        paper_account_id=uuid4(),
        paper_run_id=uuid4(),
        role=MLDeploymentRole.CHALLENGER,
    )

    assert decision.approved_for_paper is False


def test_monitoring_report_degrades_on_drift_threshold_breach() -> None:
    report = build_monitoring_report(
        model_artifact_id=uuid4(),
        paper_run_id=uuid4(),
        drift_metrics=(
            MLDriftMetric(
                name="psi",
                value=0.31,
                threshold=0.20,
                methodology="population-stability.v1",
            ),
        ),
    )

    assert report.status is MLMonitoringStatus.DEGRADED


def test_monitoring_report_rejects_healthy_status_with_drift_breach() -> None:
    with pytest.raises(ValidationError, match="healthy"):
        MLMonitoringReport(
            model_artifact_id=uuid4(),
            paper_run_id=uuid4(),
            status=MLMonitoringStatus.HEALTHY,
            drift_metrics=(
                MLDriftMetric(
                    name="psi",
                    value=0.31,
                    threshold=0.20,
                    methodology="population-stability.v1",
                ),
            ),
        )


def test_retraining_record_cannot_request_automatic_promotion() -> None:
    with pytest.raises(ValidationError, match="automatic promotion"):
        MLRetrainingRecord(
            source_model_artifact_id=uuid4(),
            trigger=MLRetrainingTrigger.DRIFT,
            workflow_id="workflow.baseline",
            automatic_promotion_requested=True,
            rationale="drift detected",
        )


def test_request_retraining_keeps_promotion_manual() -> None:
    record = request_retraining(
        source_model_artifact_id=uuid4(),
        trigger=MLRetrainingTrigger.OUTCOME_DEGRADATION,
        workflow_id="workflow.baseline",
        rationale="holdout outcome degraded",
    )

    assert record.automatic_promotion_requested is False


def test_monitoring_report_preserves_outcome_metrics() -> None:
    report = build_monitoring_report(
        model_artifact_id=uuid4(),
        paper_run_id=uuid4(),
        outcome_metrics=(
            MLMetric(
                name="precision",
                value=0.58,
                split=DatasetSplit.HOLDOUT,
                methodology="classification.v1",
            ),
        ),
        findings=(
            MLFinding(
                code="review_required",
                severity=MLFindingSeverity.WARNING,
                message="outcome degraded but remains above block threshold",
            ),
        ),
    )

    assert report.outcome_metrics[0].name == "precision"
    assert report.status is MLMonitoringStatus.HEALTHY

def _approved_promotion(*, approved: bool = True) -> MLPromotionDecision:
    artifact = MLModelArtifact(
        experiment_run_id=uuid4(),
        model_family="logistic-regression",
        artifact_uri="models/local/model.bin",
        artifact_digest="sha256:abcdef",
    )
    report = build_evaluation_report(
        artifact=artifact,
        metrics=(
            MLMetric(
                name="auc",
                value=0.64 if approved else 0.58,
                split=DatasetSplit.HOLDOUT,
                methodology="classification.v1",
            ),
        ),
        calibration_methodology="isotonic.v1",
    )
    return evaluate_ml_promotion(
        report=report,
        artifact=artifact,
        minimum_holdout_metric=0.60,
        holdout_metric_name="auc",
    )
