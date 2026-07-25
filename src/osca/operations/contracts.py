from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

Identifier = Annotated[str, Field(min_length=1, max_length=128)]
Description = Annotated[str, Field(min_length=1, max_length=2048)]


class BackupProfile(StrEnum):
    LIGHTWEIGHT = "lightweight"
    STANDARD = "standard"
    ARCHIVAL = "archival"


class RecoveryClass(StrEnum):
    CRITICAL_STATE = "critical_state"
    ACTIVE_RESEARCH = "active_research"
    PROTECTED_ARTIFACTS = "protected_artifacts"
    RECONSTRUCTABLE_DATA = "reconstructable_data"
    EPHEMERAL = "ephemeral"


class RecoveryStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    BLOCKED = "blocked"


class OperationsFindingSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class HealthState(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    BLOCKED = "blocked"
    RECOVERING = "recovering"
    UNAVAILABLE = "unavailable"


class WorkflowRunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    DEGRADED = "degraded"
    BLOCKED = "blocked"
    DEAD_LETTER = "dead_letter"


class MissedRunPolicy(StrEnum):
    SKIP = "skip"
    RUN_ONCE = "run_once"
    BOUNDED_CATCH_UP = "bounded_catch_up"
    REQUIRE_APPROVAL = "require_approval"


class RiskDecisionOutcome(StrEnum):
    APPROVE = "approve"
    MODIFY = "modify"
    REJECT = "reject"
    PAUSE = "pause"


class OperationsFinding(BaseModel):
    model_config = ConfigDict(frozen=True)
    code: Identifier
    severity: OperationsFindingSeverity
    message: Description


class RecoveryObjective(BaseModel):
    model_config = ConfigDict(frozen=True)
    recovery_class: RecoveryClass
    rpo_minutes: int | None = Field(ge=0)
    rto_minutes: int | None = Field(ge=0)
    payload_guaranteed: bool = True

    @model_validator(mode="after")
    def validate_objective(self) -> Self:
        if self.recovery_class is RecoveryClass.EPHEMERAL and (
            self.rpo_minutes is not None or self.rto_minutes is not None
        ):
            raise ValueError("ephemeral recovery class cannot declare RPO or RTO objectives")
        if (
            self.recovery_class is not RecoveryClass.EPHEMERAL
            and self.rpo_minutes is None
            and self.payload_guaranteed
        ):
            raise ValueError("guaranteed recovery classes require an RPO objective")
        return self


class BackupPackageManifest(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.operations.backup-package-manifest"] = (
        "osca.operations.backup-package-manifest"
    )
    version: Literal["1.0.0"] = "1.0.0"
    backup_manifest_id: UUID = Field(default_factory=uuid4)
    profile: BackupProfile
    recovery_point_id: Identifier
    encrypted: bool
    off_device_copy_required: bool
    integrity_manifest_digest: Identifier
    included_recovery_classes: tuple[RecoveryClass, ...] = Field(min_length=1)
    excluded_content: tuple[Identifier, ...] = ()
    secret_references_only: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_manifest(self) -> Self:
        if self.created_at.tzinfo is None:
            raise ValueError("backup manifest created_at must be timezone-aware")
        if not self.encrypted:
            raise ValueError("backup packages must be encrypted")
        if not self.secret_references_only:
            raise ValueError("backup packages must exclude secret values")
        if len(set(self.included_recovery_classes)) != len(self.included_recovery_classes):
            raise ValueError("backup recovery classes must be unique")
        return self


class RestoreVerificationReport(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.operations.restore-verification"] = (
        "osca.operations.restore-verification"
    )
    version: Literal["1.0.0"] = "1.0.0"
    restore_verification_id: UUID = Field(default_factory=uuid4)
    backup_manifest_id: UUID
    isolated_target_uri: Identifier
    integrity_verified: bool
    compatibility_verified: bool
    journal_reconciled: bool
    active_environment_mutated: bool = False
    status: RecoveryStatus
    findings: tuple[OperationsFinding, ...] = ()
    verified_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_restore_report(self) -> Self:
        if self.verified_at.tzinfo is None:
            raise ValueError("restore verification verified_at must be timezone-aware")
        if self.active_environment_mutated:
            raise ValueError("restore verification cannot mutate the active environment")
        has_error = any(
            finding.severity is OperationsFindingSeverity.ERROR for finding in self.findings
        )
        complete = (
            self.integrity_verified
            and self.compatibility_verified
            and self.journal_reconciled
        )
        if complete and not has_error and self.status is RecoveryStatus.BLOCKED:
            raise ValueError("blocked restore verification requires a blocking failure")
        if (not complete or has_error) and self.status is RecoveryStatus.HEALTHY:
            raise ValueError("restore verification cannot be healthy with failed checks")
        return self


class DisasterRecoveryExerciseRecord(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.operations.dr-exercise"] = "osca.operations.dr-exercise"
    version: Literal["1.0.0"] = "1.0.0"
    exercise_id: UUID = Field(default_factory=uuid4)
    scenario_id: Identifier
    recovery_objectives: tuple[RecoveryObjective, ...] = Field(min_length=1)
    restore_verification_id: UUID
    duration_minutes: int = Field(ge=0)
    status: RecoveryStatus
    findings: tuple[OperationsFinding, ...] = ()
    exercised_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_exercise(self) -> Self:
        if self.exercised_at.tzinfo is None:
            raise ValueError("DR exercise exercised_at must be timezone-aware")
        if len({objective.recovery_class for objective in self.recovery_objectives}) != len(
            self.recovery_objectives
        ):
            raise ValueError("DR exercise recovery objectives must be unique by class")
        if self.status is RecoveryStatus.HEALTHY and any(
            finding.severity is OperationsFindingSeverity.ERROR for finding in self.findings
        ):
            raise ValueError("healthy DR exercise cannot contain error findings")
        return self


class HealthFindingRecord(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.operations.health-finding"] = "osca.operations.health-finding"
    version: Literal["1.0.0"] = "1.0.0"
    health_finding_id: UUID = Field(default_factory=uuid4)
    component_id: Identifier
    state: HealthState
    impact: Description
    remediation_uri: Identifier
    correlation_id: UUID
    findings: tuple[OperationsFinding, ...] = ()
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_health(self) -> Self:
        if self.observed_at.tzinfo is None:
            raise ValueError("health finding observed_at must be timezone-aware")
        if self.state in {HealthState.BLOCKED, HealthState.UNAVAILABLE} and not self.findings:
            raise ValueError("blocked or unavailable health states require findings")
        return self


class AlertPolicy(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.operations.alert-policy"] = "osca.operations.alert-policy"
    version: Literal["1.0.0"] = "1.0.0"
    alert_policy_id: Identifier
    threshold_id: Identifier
    dedupe_window_minutes: int = Field(gt=0)
    destinations: tuple[Identifier, ...] = Field(min_length=1)
    escalation_required: bool = False
    external_delivery_enabled: bool = False

    @model_validator(mode="after")
    def validate_policy(self) -> Self:
        if self.external_delivery_enabled:
            raise ValueError("M12 alert policies record metadata only; delivery is deferred")
        if len(set(self.destinations)) != len(self.destinations):
            raise ValueError("alert policy destinations must be unique")
        return self


class WorkflowRunRecord(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.operations.workflow-run"] = "osca.operations.workflow-run"
    version: Literal["1.0.0"] = "1.0.0"
    workflow_run_id: UUID = Field(default_factory=uuid4)
    workflow_id: Identifier
    trigger_id: Identifier
    status: WorkflowRunStatus
    missed_run_policy: MissedRunPolicy
    financially_meaningful: bool = False
    approval_required: bool = False
    idempotency_key: Identifier
    correlation_id: UUID
    findings: tuple[OperationsFinding, ...] = ()
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_workflow_run(self) -> Self:
        if self.started_at.tzinfo is None:
            raise ValueError("workflow run started_at must be timezone-aware")
        unsafe_replay = (
            self.financially_meaningful
            and self.missed_run_policy is not MissedRunPolicy.REQUIRE_APPROVAL
        )
        if unsafe_replay:
            raise ValueError("financially meaningful missed runs require approval")
        if self.approval_required and self.status is WorkflowRunStatus.SUCCEEDED:
            raise ValueError("workflow run cannot succeed while approval is still required")
        return self


class RiskControl(BaseModel):
    model_config = ConfigDict(frozen=True)
    control_id: Identifier
    limit_name: Identifier
    observed_value: float
    limit_value: float
    strict: bool = True


class RiskPolicyDecision(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.operations.risk-policy-decision"] = (
        "osca.operations.risk-policy-decision"
    )
    version: Literal["1.0.0"] = "1.0.0"
    risk_decision_id: UUID = Field(default_factory=uuid4)
    policy_id: Identifier
    policy_version: Identifier
    scope_id: Identifier
    outcome: RiskDecisionOutcome
    controls: tuple[RiskControl, ...] = Field(min_length=1)
    rationale: Description
    override_authority_id: Identifier | None = None
    findings: tuple[OperationsFinding, ...] = ()
    decided_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_decision(self) -> Self:
        if self.decided_at.tzinfo is None:
            raise ValueError("risk decision decided_at must be timezone-aware")
        breached = any(
            control.strict and control.observed_value > control.limit_value
            for control in self.controls
        )
        if breached and self.outcome is RiskDecisionOutcome.APPROVE:
            raise ValueError("risk decision cannot approve breached strict controls")
        if self.outcome is RiskDecisionOutcome.MODIFY and self.override_authority_id is None:
            raise ValueError("modified risk decisions require override authority")
        return self
