import sqlite3
from pathlib import Path

from osca.ml.contracts import (
    MLEvaluationReport,
    MLExperimentRun,
    MLFeatureDefinition,
    MLLabelDefinition,
    MLModelArtifact,
    MLPromotionDecision,
    MLTrainingWorkflow,
)

_SCHEMA_VERSION = 1


class SQLiteMLLifecycleStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS ml_store_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS ml_records (
                    record_id TEXT PRIMARY KEY,
                    workflow_id TEXT,
                    experiment_run_id TEXT,
                    model_artifact_id TEXT,
                    record_type TEXT NOT NULL,
                    effective_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_ml_records_workflow
                    ON ml_records(workflow_id, record_type, effective_at, record_id);

                CREATE INDEX IF NOT EXISTS idx_ml_records_experiment
                    ON ml_records(experiment_run_id, record_type, effective_at, record_id);

                CREATE INDEX IF NOT EXISTS idx_ml_records_artifact
                    ON ml_records(model_artifact_id, record_type, effective_at, record_id);
                """
            )
            connection.execute(
                """
                INSERT INTO ml_store_metadata(key, value)
                VALUES ('schema_version', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (str(_SCHEMA_VERSION),),
            )

    def save_feature(self, feature: MLFeatureDefinition) -> None:
        self._save_record(
            record_id=feature.feature_id,
            workflow_id=None,
            experiment_run_id=None,
            model_artifact_id=None,
            record_type="feature",
            effective_at=feature.created_at.isoformat(),
            payload_json=feature.model_dump_json(),
        )

    def list_features(self) -> tuple[MLFeatureDefinition, ...]:
        return tuple(
            MLFeatureDefinition.model_validate_json(payload)
            for payload in self._list_payloads_by_type("feature")
        )

    def save_label(self, label: MLLabelDefinition) -> None:
        self._save_record(
            record_id=label.label_id,
            workflow_id=None,
            experiment_run_id=None,
            model_artifact_id=None,
            record_type="label",
            effective_at=label.created_at.isoformat(),
            payload_json=label.model_dump_json(),
        )

    def list_labels(self) -> tuple[MLLabelDefinition, ...]:
        return tuple(
            MLLabelDefinition.model_validate_json(payload)
            for payload in self._list_payloads_by_type("label")
        )

    def save_training_workflow(self, workflow: MLTrainingWorkflow) -> None:
        self._save_record(
            record_id=workflow.workflow_id,
            workflow_id=workflow.workflow_id,
            experiment_run_id=None,
            model_artifact_id=None,
            record_type="training_workflow",
            effective_at=workflow.created_at.isoformat(),
            payload_json=workflow.model_dump_json(),
        )

    def list_training_workflows(self) -> tuple[MLTrainingWorkflow, ...]:
        return tuple(
            MLTrainingWorkflow.model_validate_json(payload)
            for payload in self._list_payloads_by_type("training_workflow")
        )

    def save_experiment_run(self, run: MLExperimentRun) -> None:
        self._save_record(
            record_id=run.experiment_run_id,
            workflow_id=run.workflow_id,
            experiment_run_id=run.experiment_run_id,
            model_artifact_id=None,
            record_type="experiment_run",
            effective_at=run.started_at.isoformat(),
            payload_json=run.model_dump_json(),
        )

    def list_experiment_runs(self, workflow_id: str) -> tuple[MLExperimentRun, ...]:
        return tuple(
            MLExperimentRun.model_validate_json(payload)
            for payload in self._list_payloads_by_workflow(workflow_id, "experiment_run")
        )

    def save_model_artifact(self, artifact: MLModelArtifact) -> None:
        self._save_record(
            record_id=artifact.model_artifact_id,
            workflow_id=None,
            experiment_run_id=artifact.experiment_run_id,
            model_artifact_id=artifact.model_artifact_id,
            record_type="model_artifact",
            effective_at=artifact.created_at.isoformat(),
            payload_json=artifact.model_dump_json(),
        )

    def list_model_artifacts(self, experiment_run_id: str) -> tuple[MLModelArtifact, ...]:
        return tuple(
            MLModelArtifact.model_validate_json(payload)
            for payload in self._list_payloads_by_experiment(experiment_run_id, "model_artifact")
        )

    def save_evaluation_report(self, report: MLEvaluationReport) -> None:
        self._save_record(
            record_id=report.evaluation_report_id,
            workflow_id=None,
            experiment_run_id=report.experiment_run_id,
            model_artifact_id=report.model_artifact_id,
            record_type="evaluation_report",
            effective_at=report.evaluated_at.isoformat(),
            payload_json=report.model_dump_json(),
        )

    def list_evaluation_reports(
        self,
        model_artifact_id: str,
    ) -> tuple[MLEvaluationReport, ...]:
        return tuple(
            MLEvaluationReport.model_validate_json(payload)
            for payload in self._list_payloads_by_artifact(model_artifact_id, "evaluation_report")
        )

    def save_promotion_decision(self, decision: MLPromotionDecision) -> None:
        self._save_record(
            record_id=decision.promotion_decision_id,
            workflow_id=None,
            experiment_run_id=None,
            model_artifact_id=decision.model_artifact_id,
            record_type="promotion_decision",
            effective_at=decision.decided_at.isoformat(),
            payload_json=decision.model_dump_json(),
        )

    def list_promotion_decisions(
        self,
        model_artifact_id: str,
    ) -> tuple[MLPromotionDecision, ...]:
        return tuple(
            MLPromotionDecision.model_validate_json(payload)
            for payload in self._list_payloads_by_artifact(model_artifact_id, "promotion_decision")
        )

    def _save_record(
        self,
        *,
        record_id: object,
        workflow_id: object | None,
        experiment_run_id: object | None,
        model_artifact_id: object | None,
        record_type: str,
        effective_at: str,
        payload_json: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO ml_records(
                    record_id,
                    workflow_id,
                    experiment_run_id,
                    model_artifact_id,
                    record_type,
                    effective_at,
                    payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(record_id) DO UPDATE SET
                    workflow_id = excluded.workflow_id,
                    experiment_run_id = excluded.experiment_run_id,
                    model_artifact_id = excluded.model_artifact_id,
                    record_type = excluded.record_type,
                    effective_at = excluded.effective_at,
                    payload_json = excluded.payload_json
                """,
                (
                    str(record_id),
                    None if workflow_id is None else str(workflow_id),
                    None if experiment_run_id is None else str(experiment_run_id),
                    None if model_artifact_id is None else str(model_artifact_id),
                    record_type,
                    effective_at,
                    payload_json,
                ),
            )

    def _list_payloads_by_type(self, record_type: str) -> tuple[str, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload_json
                FROM ml_records
                WHERE record_type = ?
                ORDER BY effective_at, record_id
                """,
                (record_type,),
            ).fetchall()
        return tuple(str(row[0]) for row in rows)

    def _list_payloads_by_workflow(self, workflow_id: str, record_type: str) -> tuple[str, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload_json
                FROM ml_records
                WHERE workflow_id = ? AND record_type = ?
                ORDER BY effective_at, record_id
                """,
                (workflow_id, record_type),
            ).fetchall()
        return tuple(str(row[0]) for row in rows)

    def _list_payloads_by_experiment(
        self,
        experiment_run_id: str,
        record_type: str,
    ) -> tuple[str, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload_json
                FROM ml_records
                WHERE experiment_run_id = ? AND record_type = ?
                ORDER BY effective_at, record_id
                """,
                (experiment_run_id, record_type),
            ).fetchall()
        return tuple(str(row[0]) for row in rows)

    def _list_payloads_by_artifact(
        self,
        model_artifact_id: str,
        record_type: str,
    ) -> tuple[str, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload_json
                FROM ml_records
                WHERE model_artifact_id = ? AND record_type = ?
                ORDER BY effective_at, record_id
                """,
                (model_artifact_id, record_type),
            ).fetchall()
        return tuple(str(row[0]) for row in rows)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)
