from pathlib import Path
from uuid import uuid4

from osca.ml import (
    DatasetSplit,
    FeatureValueType,
    LabelObjective,
    MLExperimentRun,
    MLFeatureDefinition,
    MLLabelDefinition,
    MLMetric,
    MLModelArtifact,
    MLTrainingWorkflow,
    SQLiteMLLifecycleStore,
    build_evaluation_report,
    evaluate_ml_promotion,
)


def test_sqlite_ml_lifecycle_store_round_trips_records(tmp_path: Path) -> None:
    store = SQLiteMLLifecycleStore(tmp_path / "ml.sqlite")
    store.initialize()

    feature = MLFeatureDefinition(
        feature_id="feature.close_return",
        name="close_return",
        value_type=FeatureValueType.FLOAT,
        source_dataset_id=uuid4(),
        point_in_time_safe=True,
        transformation="uses only prior completed bars",
    )
    label = MLLabelDefinition(
        label_id="label.forward_return",
        objective=LabelObjective.REGRESSION,
        horizon="1d",
        source_dataset_id=uuid4(),
        leakage_checked=True,
    )
    workflow = MLTrainingWorkflow(
        workflow_id="workflow.baseline",
        trainer_id="trainer.local",
        feature_ids=(feature.feature_id,),
        label_id=label.label_id,
        split_policy_id="walk-forward.v1",
        parameter_set_id="params.default",
    )
    run = MLExperimentRun(
        workflow_id=workflow.workflow_id,
        dataset_revision_id=uuid4(),
        code_revision="git:abc123",
    )
    artifact = MLModelArtifact(
        experiment_run_id=run.experiment_run_id,
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

    store.save_feature(feature)
    store.save_label(label)
    store.save_training_workflow(workflow)
    store.save_experiment_run(run)
    store.save_model_artifact(artifact)
    store.save_evaluation_report(report)
    store.save_promotion_decision(decision)

    assert store.list_features() == (feature,)
    assert store.list_labels() == (label,)
    assert store.list_training_workflows() == (workflow,)
    assert store.list_experiment_runs(workflow.workflow_id) == (run,)
    assert store.list_model_artifacts(str(run.experiment_run_id)) == (artifact,)
    assert store.list_evaluation_reports(str(artifact.model_artifact_id)) == (report,)
    assert store.list_promotion_decisions(str(artifact.model_artifact_id)) == (decision,)
