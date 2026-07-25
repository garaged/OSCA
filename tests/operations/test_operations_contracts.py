from uuid import uuid4

import pytest
from pydantic import ValidationError

from osca.operations import (
    AlertPolicy,
    BackupPackageManifest,
    BackupProfile,
    HealthState,
    MissedRunPolicy,
    OperationsFinding,
    OperationsFindingSeverity,
    RecoveryClass,
    RecoveryObjective,
    RecoveryStatus,
    RestoreVerificationReport,
    RiskControl,
    RiskDecisionOutcome,
    RiskPolicyDecision,
    WorkflowRunRecord,
    WorkflowRunStatus,
    assess_backup_manifest,
    decide_workflow_execution,
    evaluate_restore_verification,
    evaluate_risk_policy,
    health_state_from_findings,
    should_enqueue_alert,
)


def error_finding() -> OperationsFinding:
    return OperationsFinding(
        code="blocked",
        severity=OperationsFindingSeverity.ERROR,
        message="blocking condition",
    )


def warning_finding() -> OperationsFinding:
    return OperationsFinding(
        code="degraded",
        severity=OperationsFindingSeverity.WARNING,
        message="degraded condition",
    )


def build_manifest() -> BackupPackageManifest:
    return BackupPackageManifest(
        profile=BackupProfile.STANDARD,
        recovery_point_id="rp-001",
        encrypted=True,
        off_device_copy_required=True,
        integrity_manifest_digest="sha256:manifest",
        included_recovery_classes=(RecoveryClass.CRITICAL_STATE,),
    )


def test_backup_manifest_requires_encryption_and_secret_exclusion() -> None:
    with pytest.raises(ValidationError, match="encrypted"):
        BackupPackageManifest(
            profile=BackupProfile.LIGHTWEIGHT,
            recovery_point_id="rp-001",
            encrypted=False,
            off_device_copy_required=False,
            integrity_manifest_digest="sha256:manifest",
            included_recovery_classes=(RecoveryClass.CRITICAL_STATE,),
        )


def test_restore_verification_fails_closed_for_active_mutation() -> None:
    with pytest.raises(ValidationError, match="active environment"):
        RestoreVerificationReport(
            backup_manifest_id=uuid4(),
            isolated_target_uri="restore://isolated",
            integrity_verified=True,
            compatibility_verified=True,
            journal_reconciled=True,
            active_environment_mutated=True,
            status=RecoveryStatus.HEALTHY,
        )


def test_restore_verification_status_blocks_failed_checks() -> None:
    report = RestoreVerificationReport(
        backup_manifest_id=uuid4(),
        isolated_target_uri="restore://isolated",
        integrity_verified=True,
        compatibility_verified=False,
        journal_reconciled=True,
        status=RecoveryStatus.BLOCKED,
        findings=(error_finding(),),
    )

    assert evaluate_restore_verification(report) is RecoveryStatus.BLOCKED


def test_recovery_objective_rejects_ephemeral_rpo() -> None:
    with pytest.raises(ValidationError, match="ephemeral"):
        RecoveryObjective(
            recovery_class=RecoveryClass.EPHEMERAL,
            rpo_minutes=60,
            rto_minutes=None,
        )


def test_health_state_from_findings_preserves_remediation_and_correlation() -> None:
    correlation_id = uuid4()

    record = health_state_from_findings(
        "backup",
        impact="backup verification is degraded",
        remediation_uri="docs/runbooks/backup.md",
        correlation_id=correlation_id,
        findings=(warning_finding(),),
    )

    assert record.state is HealthState.DEGRADED
    assert record.correlation_id == correlation_id


def test_alert_policy_records_metadata_without_external_delivery() -> None:
    with pytest.raises(ValidationError, match="delivery is deferred"):
        AlertPolicy(
            alert_policy_id="backup-alerts",
            threshold_id="backup-failure",
            dedupe_window_minutes=30,
            destinations=("inbox",),
            external_delivery_enabled=True,
        )


def test_alert_enqueue_is_local_metadata_only() -> None:
    policy = AlertPolicy(
        alert_policy_id="backup-alerts",
        threshold_id="backup-failure",
        dedupe_window_minutes=30,
        destinations=("inbox",),
    )

    assert should_enqueue_alert(policy, (warning_finding(),)) is True


def test_financially_meaningful_missed_runs_require_approval() -> None:
    with pytest.raises(ValidationError, match="require approval"):
        WorkflowRunRecord(
            workflow_id="paper-run",
            trigger_id="missed-close",
            status=WorkflowRunStatus.QUEUED,
            missed_run_policy=MissedRunPolicy.BOUNDED_CATCH_UP,
            financially_meaningful=True,
            idempotency_key="paper-run:1",
            correlation_id=uuid4(),
        )


def test_workflow_execution_blocks_when_approval_is_required() -> None:
    record = WorkflowRunRecord(
        workflow_id="restore-test",
        trigger_id="monthly",
        status=WorkflowRunStatus.QUEUED,
        missed_run_policy=MissedRunPolicy.SKIP,
        approval_required=True,
        idempotency_key="restore-test:1",
        correlation_id=uuid4(),
    )

    assert decide_workflow_execution(record) is WorkflowRunStatus.BLOCKED


def test_risk_policy_rejects_breached_strict_controls() -> None:
    with pytest.raises(ValidationError, match="breached strict controls"):
        RiskPolicyDecision(
            policy_id="paper-risk",
            policy_version="1.0.0",
            scope_id="paper-account",
            outcome=RiskDecisionOutcome.APPROVE,
            controls=(
                RiskControl(
                    control_id="gross-exposure",
                    limit_name="max-gross-exposure",
                    observed_value=1.2,
                    limit_value=1.0,
                ),
            ),
            rationale="unsafe approval",
        )


def test_risk_policy_service_rejects_breaches() -> None:
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

    assert evaluate_risk_policy(decision) is RiskDecisionOutcome.REJECT


def test_standard_backup_without_off_device_copy_is_degraded() -> None:
    manifest = build_manifest().model_copy(update={"off_device_copy_required": False})

    assert assess_backup_manifest(manifest) is RecoveryStatus.DEGRADED
