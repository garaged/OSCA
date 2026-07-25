from uuid import UUID

from osca.operations.contracts import (
    AlertPolicy,
    BackupPackageManifest,
    HealthFindingRecord,
    HealthState,
    OperationsFinding,
    OperationsFindingSeverity,
    RecoveryStatus,
    RestoreVerificationReport,
    RiskDecisionOutcome,
    RiskPolicyDecision,
    WorkflowRunRecord,
    WorkflowRunStatus,
)


def evaluate_restore_verification(
    report: RestoreVerificationReport,
) -> RecoveryStatus:
    if report.active_environment_mutated:
        return RecoveryStatus.BLOCKED
    if not (
        report.integrity_verified
        and report.compatibility_verified
        and report.journal_reconciled
    ):
        return RecoveryStatus.BLOCKED
    if any(finding.severity is OperationsFindingSeverity.ERROR for finding in report.findings):
        return RecoveryStatus.BLOCKED
    if any(
        finding.severity is OperationsFindingSeverity.WARNING for finding in report.findings
    ):
        return RecoveryStatus.DEGRADED
    return RecoveryStatus.HEALTHY


def assess_backup_manifest(manifest: BackupPackageManifest) -> RecoveryStatus:
    if not manifest.encrypted or not manifest.secret_references_only:
        return RecoveryStatus.BLOCKED
    if manifest.profile.value in {"standard", "archival"} and not manifest.off_device_copy_required:
        return RecoveryStatus.DEGRADED
    return RecoveryStatus.HEALTHY


def health_state_from_findings(
    component_id: str,
    *,
    impact: str,
    remediation_uri: str,
    correlation_id: UUID,
    findings: tuple[OperationsFinding, ...],
) -> HealthFindingRecord:
    if any(finding.severity is OperationsFindingSeverity.ERROR for finding in findings):
        state = HealthState.BLOCKED
    elif any(finding.severity is OperationsFindingSeverity.WARNING for finding in findings):
        state = HealthState.DEGRADED
    else:
        state = HealthState.HEALTHY

    return HealthFindingRecord(
        component_id=component_id,
        state=state,
        impact=impact,
        remediation_uri=remediation_uri,
        correlation_id=correlation_id,
        findings=findings,
    )


def should_enqueue_alert(
    policy: AlertPolicy,
    active_findings: tuple[OperationsFinding, ...],
) -> bool:
    if policy.external_delivery_enabled:
        return False
    return any(
        finding.severity in {
            OperationsFindingSeverity.WARNING,
            OperationsFindingSeverity.ERROR,
        }
        for finding in active_findings
    )


def decide_workflow_execution(record: WorkflowRunRecord) -> WorkflowRunStatus:
    if record.approval_required:
        return WorkflowRunStatus.BLOCKED
    if any(finding.severity is OperationsFindingSeverity.ERROR for finding in record.findings):
        return WorkflowRunStatus.DEAD_LETTER
    if any(finding.severity is OperationsFindingSeverity.WARNING for finding in record.findings):
        return WorkflowRunStatus.DEGRADED
    return record.status


def evaluate_risk_policy(decision: RiskPolicyDecision) -> RiskDecisionOutcome:
    strict_breach = any(
        control.strict and control.observed_value > control.limit_value
        for control in decision.controls
    )
    if strict_breach:
        return RiskDecisionOutcome.REJECT
    return decision.outcome