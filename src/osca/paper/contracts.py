from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

Identifier = Annotated[str, Field(min_length=1, max_length=128)]
Description = Annotated[str, Field(min_length=1, max_length=2048)]
Currency = Annotated[str, Field(min_length=3, max_length=3)]


class PaperAccountStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


class PaperEvaluationStatus(StrEnum):
    REQUESTED = "requested"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class HealthGateStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    BLOCKED = "blocked"


class PaperControlAction(StrEnum):
    ALLOW = "allow"
    PAUSE = "pause"
    KILL_SWITCH = "kill_switch"


class PaperFindingSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class PaperAccount(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.paper.account"] = "osca.paper.account"
    version: Literal["1.0.0"] = "1.0.0"
    paper_account_id: UUID = Field(default_factory=uuid4)
    name: Identifier
    base_currency: Currency = "USD"
    status: PaperAccountStatus = PaperAccountStatus.ACTIVE
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_created_at(self) -> Self:
        if self.created_at.tzinfo is None:
            raise ValueError("paper account created_at must be timezone-aware")
        return self


class ApprovedPaperCandidate(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.paper.approved-candidate"] = "osca.paper.approved-candidate"
    version: Literal["1.0.0"] = "1.0.0"
    approved_candidate_id: UUID = Field(default_factory=uuid4)
    candidate_id: Identifier
    f2_request_id: UUID
    promotion_gate_id: UUID
    approved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_approved_at(self) -> Self:
        if self.approved_at.tzinfo is None:
            raise ValueError("approved candidate approved_at must be timezone-aware")
        return self


class PaperDataRequirement(BaseModel):
    model_config = ConfigDict(frozen=True)
    dataset_revision_id: UUID
    freshness_policy_id: Identifier
    allow_provisional_data: bool = False


class PaperEvaluationRequest(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.paper.evaluation-request"] = "osca.paper.evaluation-request"
    version: Literal["1.0.0"] = "1.0.0"
    paper_run_id: UUID = Field(default_factory=uuid4)
    paper_account_id: UUID
    approved_candidate_id: UUID
    candidate_id: Identifier
    promotion_gate_id: UUID
    data_requirements: tuple[PaperDataRequirement, ...] = Field(min_length=1)
    schedule_id: Identifier | None = None
    status: PaperEvaluationStatus = PaperEvaluationStatus.REQUESTED
    requested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_request(self) -> Self:
        if self.requested_at.tzinfo is None:
            raise ValueError("paper evaluation requested_at must be timezone-aware")
        if any(requirement.allow_provisional_data for requirement in self.data_requirements):
            raise ValueError("paper evaluation cannot allow provisional data")
        return self


class PaperFinding(BaseModel):
    model_config = ConfigDict(frozen=True)
    code: Identifier
    severity: PaperFindingSeverity
    message: Description


class PaperHealthGateDecision(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.paper.health-gate"] = "osca.paper.health-gate"
    version: Literal["1.0.0"] = "1.0.0"
    health_gate_id: UUID = Field(default_factory=uuid4)
    paper_run_id: UUID
    data_status: HealthGateStatus
    operational_status: HealthGateStatus
    can_process: bool
    findings: tuple[PaperFinding, ...] = ()
    checked_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_gate(self) -> Self:
        if self.checked_at.tzinfo is None:
            raise ValueError("paper health gate checked_at must be timezone-aware")
        blocked = (
            self.data_status is HealthGateStatus.BLOCKED
            or self.operational_status is HealthGateStatus.BLOCKED
            or any(finding.severity is PaperFindingSeverity.ERROR for finding in self.findings)
        )
        if self.can_process and blocked:
            raise ValueError("paper health gate cannot process blocked or error state")
        return self


class PaperControlDecision(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.paper.control-decision"] = "osca.paper.control-decision"
    version: Literal["1.0.0"] = "1.0.0"
    control_decision_id: UUID = Field(default_factory=uuid4)
    paper_account_id: UUID
    action: PaperControlAction
    can_process: bool
    reason: Description
    effective_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_control(self) -> Self:
        if self.effective_at.tzinfo is None:
            raise ValueError("paper control effective_at must be timezone-aware")
        if self.action is not PaperControlAction.ALLOW and self.can_process:
            raise ValueError("pause and kill-switch controls must block processing")
        return self


class ForwardComparisonMetric(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: Identifier
    f2_value: float
    f3_value: float
    unit: Identifier
    methodology: Identifier


class ForwardComparisonRecord(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.paper.forward-comparison"] = "osca.paper.forward-comparison"
    version: Literal["1.0.0"] = "1.0.0"
    comparison_id: UUID = Field(default_factory=uuid4)
    f2_request_id: UUID
    promotion_gate_id: UUID
    paper_run_id: UUID
    metrics: tuple[ForwardComparisonMetric, ...] = Field(min_length=1)
    findings: tuple[PaperFinding, ...] = ()
    compared_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_compared_at(self) -> Self:
        if self.compared_at.tzinfo is None:
            raise ValueError("forward comparison compared_at must be timezone-aware")
        return self


class PaperScheduleCadence(StrEnum):
    HOURLY = "hourly"
    DAILY = "daily"
    MARKET_OPEN = "market_open"
    MARKET_CLOSE = "market_close"


class MissedRunPolicy(StrEnum):
    SKIP = "skip"
    RUN_ONCE = "run_once"
    BLOCK = "block"


class PaperScheduleStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class PaperRecoveryAction(StrEnum):
    RESUME = "resume"
    SKIP_MISSED = "skip_missed"
    BLOCK = "block"


class PaperSchedule(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.paper.schedule"] = "osca.paper.schedule"
    version: Literal["1.0.0"] = "1.0.0"
    schedule_id: UUID = Field(default_factory=uuid4)
    paper_account_id: UUID
    paper_run_id: UUID
    cadence: PaperScheduleCadence
    timezone: Identifier
    market_calendar_id: Identifier | None = None
    missed_run_policy: MissedRunPolicy = MissedRunPolicy.BLOCK
    status: PaperScheduleStatus = PaperScheduleStatus.ACTIVE
    starts_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_schedule(self) -> Self:
        if self.starts_at.tzinfo is None:
            raise ValueError("paper schedule starts_at must be timezone-aware")
        if self.cadence in {
            PaperScheduleCadence.MARKET_OPEN,
            PaperScheduleCadence.MARKET_CLOSE,
        } and self.market_calendar_id is None:
            raise ValueError("market-aware paper schedules require market_calendar_id")
        return self


class PaperRunCheckpoint(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.paper.run-checkpoint"] = "osca.paper.run-checkpoint"
    version: Literal["1.0.0"] = "1.0.0"
    checkpoint_id: UUID = Field(default_factory=uuid4)
    paper_run_id: UUID
    sequence_number: Annotated[int, Field(ge=0)]
    idempotency_key: Identifier
    last_processed_at: datetime
    source_event_ids: tuple[UUID, ...] = ()
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_checkpoint(self) -> Self:
        if self.last_processed_at.tzinfo is None or self.created_at.tzinfo is None:
            raise ValueError("paper checkpoint timestamps must be timezone-aware")
        return self


class PaperRecoveryDecision(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.paper.recovery-decision"] = "osca.paper.recovery-decision"
    version: Literal["1.0.0"] = "1.0.0"
    recovery_decision_id: UUID = Field(default_factory=uuid4)
    paper_run_id: UUID
    checkpoint_id: UUID | None = None
    action: PaperRecoveryAction
    can_resume: bool
    findings: tuple[PaperFinding, ...] = ()
    decided_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_recovery(self) -> Self:
        if self.decided_at.tzinfo is None:
            raise ValueError("paper recovery decided_at must be timezone-aware")
        has_error = any(finding.severity is PaperFindingSeverity.ERROR for finding in self.findings)
        if self.can_resume and (self.action is PaperRecoveryAction.BLOCK or has_error):
            raise ValueError("paper recovery cannot resume from blocked or error state")
        return self


class PaperNotificationSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class PaperNotificationStatus(StrEnum):
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    SUPPRESSED = "suppressed"


class DeliveryAttemptStatus(StrEnum):
    PLANNED = "planned"
    SENT = "sent"
    FAILED = "failed"
    SKIPPED = "skipped"


class PaperNotification(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.paper.notification"] = "osca.paper.notification"
    version: Literal["1.0.0"] = "1.0.0"
    notification_id: UUID = Field(default_factory=uuid4)
    paper_run_id: UUID
    severity: PaperNotificationSeverity
    title: Identifier
    message: Description
    source_record_id: UUID | None = None
    status: PaperNotificationStatus = PaperNotificationStatus.NEW
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_created_at(self) -> Self:
        if self.created_at.tzinfo is None:
            raise ValueError("paper notification created_at must be timezone-aware")
        return self


class PaperNotificationDigest(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.paper.notification-digest"] = "osca.paper.notification-digest"
    version: Literal["1.0.0"] = "1.0.0"
    digest_id: UUID = Field(default_factory=uuid4)
    paper_run_id: UUID
    notification_ids: tuple[UUID, ...] = Field(min_length=1)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_generated_at(self) -> Self:
        if self.generated_at.tzinfo is None:
            raise ValueError("paper notification digest generated_at must be timezone-aware")
        return self


class DeliveryAdapterDeclaration(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.paper.delivery-adapter"] = "osca.paper.delivery-adapter"
    version: Literal["1.0.0"] = "1.0.0"
    adapter_id: Identifier
    adapter_kind: Identifier
    configured: bool = False
    enabled: bool = False

    @model_validator(mode="after")
    def validate_adapter(self) -> Self:
        if self.enabled and not self.configured:
            raise ValueError("delivery adapter cannot be enabled before configuration")
        return self


class PaperDeliveryAttempt(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.paper.delivery-attempt"] = "osca.paper.delivery-attempt"
    version: Literal["1.0.0"] = "1.0.0"
    delivery_attempt_id: UUID = Field(default_factory=uuid4)
    digest_id: UUID
    adapter_id: Identifier
    status: DeliveryAttemptStatus
    attempted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    error_message: Description | None = None

    @model_validator(mode="after")
    def validate_attempt(self) -> Self:
        if self.attempted_at.tzinfo is None:
            raise ValueError("paper delivery attempted_at must be timezone-aware")
        if self.status is DeliveryAttemptStatus.FAILED and self.error_message is None:
            raise ValueError("failed delivery attempts require error_message")
        return self
