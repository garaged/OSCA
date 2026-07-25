from uuid import uuid4

from osca.ml import (
    DatasetSplit,
    MLFinding,
    MLFindingSeverity,
    MLMetric,
    MLModelArtifact,
    build_evaluation_report,
    evaluate_ml_promotion,
)


def test_evaluate_ml_promotion_approves_holdout_threshold_without_errors() -> None:
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
                value=0.64,
                split=DatasetSplit.HOLDOUT,
                methodology="classification.v1",
            ),
        ),
        calibration_methodology="isotonic.v1",
    )

    decision = evaluate_ml_promotion(
        report=report,
        artifact=artifact,
        minimum_holdout_metric=0.60,
        holdout_metric_name="auc",
    )

    assert decision.model_artifact_id == artifact.model_artifact_id
    assert decision.evaluation_report_id == report.evaluation_report_id
    assert decision.approved_for_event_validation is True
    assert decision.approved_for_paper_challenger is False


def test_evaluate_ml_promotion_blocks_missing_threshold() -> None:
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
                value=0.58,
                split=DatasetSplit.HOLDOUT,
                methodology="classification.v1",
            ),
        ),
        calibration_methodology="isotonic.v1",
    )

    decision = evaluate_ml_promotion(
        report=report,
        artifact=artifact,
        minimum_holdout_metric=0.60,
        holdout_metric_name="auc",
    )

    assert decision.approved_for_event_validation is False


def test_evaluate_ml_promotion_blocks_error_findings() -> None:
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
                value=0.70,
                split=DatasetSplit.HOLDOUT,
                methodology="classification.v1",
            ),
        ),
        calibration_methodology="isotonic.v1",
    )

    decision = evaluate_ml_promotion(
        report=report,
        artifact=artifact,
        minimum_holdout_metric=0.60,
        holdout_metric_name="auc",
        findings=(
            MLFinding(
                code="data_drift",
                severity=MLFindingSeverity.ERROR,
                message="feature distribution changed materially",
            ),
        ),
    )

    assert decision.approved_for_event_validation is False
