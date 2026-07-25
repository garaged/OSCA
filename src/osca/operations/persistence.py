import sqlite3
from pathlib import Path

from osca.operations.contracts import (
    AlertPolicy,
    BackupPackageManifest,
    DisasterRecoveryExerciseRecord,
    HealthFindingRecord,
    RestoreVerificationReport,
    RiskPolicyDecision,
    WorkflowRunRecord,
)

_SCHEMA_VERSION = 1


class SQLiteOperationsStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS operations_store_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS operations_records (
                    record_id TEXT PRIMARY KEY,
                    component_id TEXT,
                    workflow_id TEXT,
                    policy_id TEXT,
                    record_type TEXT NOT NULL,
                    effective_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_operations_records_component
                    ON operations_records(component_id, record_type, effective_at, record_id);

                CREATE INDEX IF NOT EXISTS idx_operations_records_workflow
                    ON operations_records(workflow_id, record_type, effective_at, record_id);

                CREATE INDEX IF NOT EXISTS idx_operations_records_policy
                    ON operations_records(policy_id, record_type, effective_at, record_id);
                """
            )
            connection.execute(
                """
                INSERT INTO operations_store_metadata(key, value)
                VALUES ('schema_version', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (str(_SCHEMA_VERSION),),
            )

    def save_backup_manifest(self, manifest: BackupPackageManifest) -> None:
        self._save_record(
            record_id=manifest.backup_manifest_id,
            component_id=None,
            workflow_id=None,
            policy_id=None,
            record_type="backup_manifest",
            effective_at=manifest.created_at.isoformat(),
            payload_json=manifest.model_dump_json(),
        )

    def list_backup_manifests(self) -> tuple[BackupPackageManifest, ...]:
        return tuple(
            BackupPackageManifest.model_validate_json(payload)
            for payload in self._list_payloads_by_type("backup_manifest")
        )

    def save_restore_verification(self, report: RestoreVerificationReport) -> None:
        self._save_record(
            record_id=report.restore_verification_id,
            component_id=None,
            workflow_id=None,
            policy_id=None,
            record_type="restore_verification",
            effective_at=report.verified_at.isoformat(),
            payload_json=report.model_dump_json(),
        )

    def save_dr_exercise(self, record: DisasterRecoveryExerciseRecord) -> None:
        self._save_record(
            record_id=record.exercise_id,
            component_id=None,
            workflow_id=None,
            policy_id=None,
            record_type="dr_exercise",
            effective_at=record.exercised_at.isoformat(),
            payload_json=record.model_dump_json(),
        )

    def save_health_finding(self, record: HealthFindingRecord) -> None:
        self._save_record(
            record_id=record.health_finding_id,
            component_id=record.component_id,
            workflow_id=None,
            policy_id=None,
            record_type="health_finding",
            effective_at=record.observed_at.isoformat(),
            payload_json=record.model_dump_json(),
        )

    def list_health_findings(self, component_id: str) -> tuple[HealthFindingRecord, ...]:
        return tuple(
            HealthFindingRecord.model_validate_json(payload)
            for payload in self._list_payloads_by_component(component_id, "health_finding")
        )

    def save_alert_policy(self, policy: AlertPolicy) -> None:
        self._save_record(
            record_id=policy.alert_policy_id,
            component_id=None,
            workflow_id=None,
            policy_id=policy.alert_policy_id,
            record_type="alert_policy",
            effective_at="0001-01-01T00:00:00+00:00",
            payload_json=policy.model_dump_json(),
        )

    def save_workflow_run(self, record: WorkflowRunRecord) -> None:
        self._save_record(
            record_id=record.workflow_run_id,
            component_id=None,
            workflow_id=record.workflow_id,
            policy_id=None,
            record_type="workflow_run",
            effective_at=record.started_at.isoformat(),
            payload_json=record.model_dump_json(),
        )

    def list_workflow_runs(self, workflow_id: str) -> tuple[WorkflowRunRecord, ...]:
        return tuple(
            WorkflowRunRecord.model_validate_json(payload)
            for payload in self._list_payloads_by_workflow(workflow_id, "workflow_run")
        )

    def save_risk_policy_decision(self, decision: RiskPolicyDecision) -> None:
        self._save_record(
            record_id=decision.risk_decision_id,
            component_id=None,
            workflow_id=None,
            policy_id=decision.policy_id,
            record_type="risk_policy_decision",
            effective_at=decision.decided_at.isoformat(),
            payload_json=decision.model_dump_json(),
        )

    def list_risk_policy_decisions(self, policy_id: str) -> tuple[RiskPolicyDecision, ...]:
        return tuple(
            RiskPolicyDecision.model_validate_json(payload)
            for payload in self._list_payloads_by_policy(policy_id, "risk_policy_decision")
        )

    def _save_record(
        self,
        *,
        record_id: object,
        component_id: object | None,
        workflow_id: object | None,
        policy_id: object | None,
        record_type: str,
        effective_at: str,
        payload_json: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO operations_records(
                    record_id,
                    component_id,
                    workflow_id,
                    policy_id,
                    record_type,
                    effective_at,
                    payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(record_id) DO UPDATE SET
                    component_id = excluded.component_id,
                    workflow_id = excluded.workflow_id,
                    policy_id = excluded.policy_id,
                    record_type = excluded.record_type,
                    effective_at = excluded.effective_at,
                    payload_json = excluded.payload_json
                """,
                (
                    str(record_id),
                    None if component_id is None else str(component_id),
                    None if workflow_id is None else str(workflow_id),
                    None if policy_id is None else str(policy_id),
                    record_type,
                    effective_at,
                    payload_json,
                ),
            )

    def _list_payloads_by_type(self, record_type: str) -> tuple[str, ...]:
        return self._list_payloads("record_type = ?", (record_type,))

    def _list_payloads_by_component(self, component_id: str, record_type: str) -> tuple[str, ...]:
        return self._list_payloads(
            "component_id = ? AND record_type = ?",
            (component_id, record_type),
        )

    def _list_payloads_by_workflow(self, workflow_id: str, record_type: str) -> tuple[str, ...]:
        return self._list_payloads(
            "workflow_id = ? AND record_type = ?",
            (workflow_id, record_type),
        )

    def _list_payloads_by_policy(self, policy_id: str, record_type: str) -> tuple[str, ...]:
        return self._list_payloads(
            "policy_id = ? AND record_type = ?",
            (policy_id, record_type),
        )

    def _list_payloads(self, where_clause: str, parameters: tuple[str, ...]) -> tuple[str, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT payload_json
                FROM operations_records
                WHERE {where_clause}
                ORDER BY effective_at, record_id
                """,
                parameters,
            ).fetchall()
        return tuple(str(row[0]) for row in rows)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)
