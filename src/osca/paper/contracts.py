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
