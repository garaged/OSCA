from pathlib import Path
from uuid import uuid4

from osca.operations import (
    BackupPackageManifest,
    BackupProfile,
    HealthState,
    MissedRunPolicy,
    OperationsFinding,
    OperationsFindingSeverity,
    RecoveryClass,
    RiskControl,
    RiskDecisionOutcome,
    RiskPolicyDecision,
    SQLiteOperationsStore,
    WorkflowRunRecord,
    WorkflowRunStatus,
    health_state_from_findings,
)


def build_manifest() -> BackupPackageManifest:
    return BackupPackageManifest(
        profile=BackupProfile.LIGHTWEIGHT,
        recovery_point_id="rp-001",
        encrypted=True,
        off_device_copy_required=False,
        integrity_manifest_digest="sha256:manifest",
        included_recovery_classes=(RecoveryClass.CRITICAL_STATE,),
    )


def test_operations_store_round_trips_backup_manifest(tmp_path: Path) -> None:
    store = SQLiteOperationsStore(tmp_path / "operations.sqlite")
    store.initialize()
    manifest = build_manifest()

    store.save_backup_manifest(manifest)

    assert store.list_backup_manifests() == (manifest,)


def test_operations_store_queries_health_by_component(tmp_path: Path) -> None:
    store = SQLiteOperationsStore(tmp_path / "operations.sqlite")
    store.initialize()
    finding = OperationsFinding(
        code="backup_late",
        severity=OperationsFindingSeverity.WARNING,
        message="backup verification is late",
    )
    record = health_state_from_findings(
        "backup",
        impact="restore confidence is degraded",
        remediation_uri="docs/runbooks/backup.md",
        correlation_id=uuid4(),
        findings=(finding,),
    )
    other = health_state_from_findings(
        "scheduler",
        impact="scheduler is healthy",
        remediation_uri="docs/runbooks/scheduler.md",
        correlation_id=uuid4(),
        findings=(),
    )

    store.save_health_finding(record)
    store.save_health_finding(other)

    assert store.list_health_findings("backup") == (record,)
    assert store.list_health_findings("backup")[0].state is HealthState.DEGRADED


def test_operations_store_queries_workflow_runs(tmp_path: Path) -> None:
    store = SQLiteOperationsStore(tmp_path / "operations.sqlite")
    store.initialize()
    record = WorkflowRunRecord(
        workflow_id="monthly-restore-test",
        trigger_id="monthly",
        status=WorkflowRunStatus.QUEUED,
        missed_run_policy=MissedRunPolicy.SKIP,
        idempotency_key="monthly-restore-test:1",
        correlation_id=uuid4(),
    )

    store.save_workflow_run(record)

    assert store.list_workflow_runs("monthly-restore-test") == (record,)


def test_operations_store_queries_risk_decisions(tmp_path: Path) -> None:
    store = SQLiteOperationsStore(tmp_path / "operations.sqlite")
    store.initialize()
    decision = RiskPolicyDecision(
        policy_id="paper-risk",
        policy_version="1.0.0",
        scope_id="paper-account",
        outcome=RiskDecisionOutcome.REJECT,
        controls=(
            RiskControl(
                control_id="gross-exposure",
                limit_name="max-gross-exposure",
                observed_value=1.2,
                limit_value=1.0,
            ),
        ),
        rationale="strict control breached",
    )

    store.save_risk_policy_decision(decision)

    assert store.list_risk_policy_decisions("paper-risk") == (decision,)
