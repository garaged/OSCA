from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

Identifier = Annotated[str, Field(min_length=1, max_length=128)]
Description = Annotated[str, Field(min_length=1, max_length=2048)]


class LLMCapability(StrEnum):
    SYNTHESIS = "synthesis"
    EXPLANATION = "explanation"
    STRUCTURED_EXTRACTION = "structured_extraction"
    TOOL_ORCHESTRATION = "tool_orchestration"


class LLMPrivacyClass(StrEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    SENSITIVE = "sensitive"


class LLMToolMode(StrEnum):
    READ = "read"
    STATE_CHANGING = "state_changing"


class LLMFindingSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class LLMEvaluationStatus(StrEnum):
    PASSED = "passed"
    DEGRADED = "degraded"
    FAILED = "failed"


class LLMFinding(BaseModel):
    model_config = ConfigDict(frozen=True)
    code: Identifier
    severity: LLMFindingSeverity
    message: Description


class LLMBudget(BaseModel):
    model_config = ConfigDict(frozen=True)
    max_input_tokens: int = Field(gt=0)
    max_output_tokens: int = Field(gt=0)
    max_cost_usd: float = Field(ge=0)
    max_latency_ms: int = Field(gt=0)
    max_tool_calls: int = Field(ge=0)


class LLMProviderCapability(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.llm.provider-capability"] = "osca.llm.provider-capability"
    version: Literal["1.0.0"] = "1.0.0"
    provider_id: Identifier
    model_id: Identifier
    model_version: Identifier
    capabilities: tuple[LLMCapability, ...] = Field(min_length=1)
    supported_privacy_classes: tuple[LLMPrivacyClass, ...] = Field(min_length=1)
    available: bool
    cost_per_1k_input_tokens_usd: float = Field(ge=0)
    cost_per_1k_output_tokens_usd: float = Field(ge=0)
    declared_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_provider(self) -> Self:
        if self.declared_at.tzinfo is None:
            raise ValueError("LLM provider capability declared_at must be timezone-aware")
        if len(set(self.capabilities)) != len(self.capabilities):
            raise ValueError("LLM provider capabilities must be unique")
        if len(set(self.supported_privacy_classes)) != len(self.supported_privacy_classes):
            raise ValueError("LLM provider privacy classes must be unique")
        return self


class LLMToolDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.llm.tool-definition"] = "osca.llm.tool-definition"
    version: Literal["1.0.0"] = "1.0.0"
    tool_id: Identifier
    tool_version: Identifier
    mode: LLMToolMode
    permission_scope: Identifier
    allows_live_orders: bool = False
    requires_confirmation: bool
    declared_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_tool(self) -> Self:
        if self.declared_at.tzinfo is None:
            raise ValueError("LLM tool declared_at must be timezone-aware")
        if self.allows_live_orders:
            raise ValueError("LLM tools cannot allow live-order capabilities")
        if self.mode is LLMToolMode.STATE_CHANGING and not self.requires_confirmation:
            raise ValueError("state-changing LLM tools require explicit confirmation")
        return self


class LLMPromptTemplate(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.llm.prompt-template"] = "osca.llm.prompt-template"
    version: Literal["1.0.0"] = "1.0.0"
    prompt_id: Identifier
    prompt_version: Identifier
    purpose: Identifier
    template_digest: Identifier
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_prompt(self) -> Self:
        if self.created_at.tzinfo is None:
            raise ValueError("LLM prompt created_at must be timezone-aware")
        if ":" not in self.template_digest:
            raise ValueError("LLM prompt template digest must include algorithm prefix")
        return self


class LLMContextPolicy(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.llm.context-policy"] = "osca.llm.context-policy"
    version: Literal["1.0.0"] = "1.0.0"
    context_policy_id: Identifier
    selected_project_id: UUID
    approved_global_reference_ids: tuple[UUID, ...] = ()
    allow_unrelated_project_history: bool = False
    untrusted_content_handling: Identifier
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_context(self) -> Self:
        if self.created_at.tzinfo is None:
            raise ValueError("LLM context policy created_at must be timezone-aware")
        if self.allow_unrelated_project_history:
            raise ValueError("LLM context cannot silently mix unrelated project histories")
        return self


class LLMStructuredOutputContract(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.llm.structured-output-contract"] = "osca.llm.structured-output-contract"
    version: Literal["1.0.0"] = "1.0.0"
    output_contract_id: Identifier
    schema_version: Identifier
    schema_digest: Identifier
    strict_validation: bool

    @model_validator(mode="after")
    def validate_output_contract(self) -> Self:
        if ":" not in self.schema_digest:
            raise ValueError("LLM structured-output schema digest must include algorithm prefix")
        if not self.strict_validation:
            raise ValueError("LLM structured outputs require strict validation")
        return self


class LLMRequestEnvelope(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.llm.request-envelope"] = "osca.llm.request-envelope"
    version: Literal["1.0.0"] = "1.0.0"
    request_id: UUID = Field(default_factory=uuid4)
    requested_capability: LLMCapability
    privacy_class: LLMPrivacyClass
    prompt_template_id: Identifier
    prompt_version: Identifier
    context_policy_id: Identifier
    budget: LLMBudget
    allowed_tool_ids: tuple[Identifier, ...] = ()
    sensitive_disclosure_approved: bool = False
    requested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_request(self) -> Self:
        if self.requested_at.tzinfo is None:
            raise ValueError("LLM request requested_at must be timezone-aware")
        if (
            self.privacy_class is LLMPrivacyClass.SENSITIVE
            and not self.sensitive_disclosure_approved
        ):
            raise ValueError("sensitive LLM disclosure requires explicit approval")
        if len(set(self.allowed_tool_ids)) != len(self.allowed_tool_ids):
            raise ValueError("LLM request allowed tool ids must be unique")
        return self


class LLMRouteDecision(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.llm.route-decision"] = "osca.llm.route-decision"
    version: Literal["1.0.0"] = "1.0.0"
    route_decision_id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    provider_id: Identifier | None
    model_id: Identifier | None
    model_version: Identifier | None
    approved: bool
    rationale: Description
    estimated_cost_usd: float = Field(ge=0)
    findings: tuple[LLMFinding, ...] = ()
    decided_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_route(self) -> Self:
        if self.decided_at.tzinfo is None:
            raise ValueError("LLM route decided_at must be timezone-aware")
        if self.approved and any(
            finding.severity is LLMFindingSeverity.ERROR for finding in self.findings
        ):
            raise ValueError("approved LLM route cannot include error findings")
        if self.approved and (
            self.provider_id is None or self.model_id is None or self.model_version is None
        ):
            raise ValueError("approved LLM route requires exact provider and model identity")
        return self


class LLMEvaluationReport(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.llm.evaluation-report"] = "osca.llm.evaluation-report"
    version: Literal["1.0.0"] = "1.0.0"
    evaluation_report_id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    route_decision_id: UUID
    status: LLMEvaluationStatus
    evaluated_dimensions: tuple[Identifier, ...] = Field(min_length=1)
    findings: tuple[LLMFinding, ...] = ()
    cost_usd: float = Field(ge=0)
    latency_ms: int = Field(ge=0)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_evaluation(self) -> Self:
        if self.evaluated_at.tzinfo is None:
            raise ValueError("LLM evaluation evaluated_at must be timezone-aware")
        if self.status is LLMEvaluationStatus.PASSED and any(
            finding.severity is LLMFindingSeverity.ERROR for finding in self.findings
        ):
            raise ValueError("passed LLM evaluation cannot include error findings")
        return self
