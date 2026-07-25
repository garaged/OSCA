from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from osca.ml import (
    DatasetSplit,
    FeatureValueType,
    LabelObjective,
    MLEvaluationReport,
    MLFeatureDefinition,
    MLFinding,
    MLFindingSeverity,
    MLLabelDefinition,
    MLMetric,
    MLModelArtifact,
    MLPromotionDecision,
    MLTrainingWorkflow,
)


def test_feature_definition_requires_point_in_time_safety() -> None:
    with pytest.raises(ValidationError, match="point-in-time-safe"):
        MLFeatureDefinition(
            feature_id="feature.close_return",
            name="close_return",
            value_type=FeatureValueType.FLOAT,
            source_dataset_id=uuid4(),
            point_in_time_safe=False,
            transformation="uses only prior completed bars",
        )


def test_label_definition_requires_leakage_check() -> None:
    with pytest.raises(ValidationError, match="leakage"):
        MLLabelDefinition(
            label_id="label.forward_return",
            objective=LabelObjective.REGRESSION,
            horizon="1d",
            source_dataset_id=uuid4(),
            leakage_checked=False,
        )


def test_training_workflow_requires_unique_features() -> None:
    with pytest.raises(ValidationError, match="unique"):
        MLTrainingWorkflow(
            workflow_id="workflow.duplicate-features",
            trainer_id="trainer.local",
            feature_ids=("feature.a", "feature.a"),
            label_id="label.forward_return",
            split_policy_id="walk-forward.v1",
            parameter_set_id="params.default",
        )


def test_model_artifact_requires_digest_algorithm_prefix() -> None:
    with pytest.raises(ValidationError, match="algorithm prefix"):
        MLModelArtifact(
            experiment_run_id=uuid4(),
            model_family="logistic-regression",
            artifact_uri="models/local/model.bin",
            artifact_digest="abcdef",
        )


def test_evaluation_report_requires_holdout_metrics() -> None:
    with pytest.raises(ValidationError, match="holdout"):
        MLEvaluationReport(
            model_artifact_id=uuid4(),
            experiment_run_id=uuid4(),
            metrics=(
                MLMetric(
                    name="auc",
                    value=0.61,
                    split=DatasetSplit.VALIDATION,
                    methodology="classification.v1",
                ),
            ),
            calibration_methodology="isotonic.v1",
        )


def test_promotion_cannot_approve_with_error_findings() -> None:
    with pytest.raises(ValidationError, match="error findings"):
        MLPromotionDecision(
            model_artifact_id=uuid4(),
            evaluation_report_id=uuid4(),
            approved_for_event_validation=True,
            rationale="blocked",
            findings=(
                MLFinding(
                    code="drift_detected",
                    severity=MLFindingSeverity.ERROR,
                    message="holdout drift exceeds policy",
                ),
            ),
        )


def test_training_workflow_requires_timezone_aware_creation_time() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        MLTrainingWorkflow(
            workflow_id="workflow.naive-time",
            trainer_id="trainer.local",
            feature_ids=("feature.a",),
            label_id="label.forward_return",
            split_policy_id="walk-forward.v1",
            parameter_set_id="params.default",
            created_at=datetime(2026, 1, 1),
        )
