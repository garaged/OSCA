from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PreviewKind(StrEnum):
    LOCAL_TREND = "local_trend"
    LLM_ANALYSIS = "llm_analysis"


class PreviewStatus(StrEnum):
    SUCCEEDED = "succeeded"
    POLICY_BLOCKED = "policy_blocked"
    BUDGET_EXCEEDED = "budget_exceeded"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    REVIEW_REQUIRED = "review_required"


class ReviewStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class PreviewBudget(BaseModel):
    model_config = ConfigDict(frozen=True)

    max_input_records: int = Field(gt=1, le=100_000)
    max_output_characters: int = Field(gt=0, le=100_000)
    max_cost_usd: float = Field(ge=0, le=1000)
    max_latency_ms: int = Field(gt=0, le=300_000)


class LocalTrendRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.model-preview.local-trend-request"] = (
        "osca.model-preview.local-trend-request"
    )
    version: Literal["1.0.0"] = "1.0.0"
    request_id: UUID = Field(default_factory=uuid4)
    values: tuple[float, ...] = Field(min_length=3)
    budget: PreviewBudget
    requested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_request(self) -> LocalTrendRequest:
        if self.requested_at.tzinfo is None:
            raise ValueError("requested_at must be timezone-aware")
        return self


class LLMAnalysisRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.model-preview.llm-analysis-request"] = (
        "osca.model-preview.llm-analysis-request"
    )
    version: Literal["1.0.0"] = "1.0.0"
    request_id: UUID = Field(default_factory=uuid4)
    input_text: str = Field(min_length=1, max_length=50_000)
    prompt_id: str = Field(min_length=1, max_length=128)
    prompt_version: str = Field(min_length=1, max_length=64)
    provider_id: str = Field(min_length=1, max_length=128)
    model_id: str = Field(min_length=1, max_length=128)
    model_version: str = Field(min_length=1, max_length=128)
    budget: PreviewBudget
    fixture_response: str | None = Field(default=None, max_length=100_000)
    network_access_enabled: bool = False
    requested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_request(self) -> LLMAnalysisRequest:
        if self.requested_at.tzinfo is None:
            raise ValueError("requested_at must be timezone-aware")
        if self.network_access_enabled and self.fixture_response is not None:
            raise ValueError("fixture and network modes cannot be combined")
        return self


class ModelPreviewEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.model-preview.evidence"] = "osca.model-preview.evidence"
    version: Literal["1.0.0"] = "1.0.0"
    preview_id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    kind: PreviewKind
    status: PreviewStatus
    review_status: ReviewStatus = ReviewStatus.PENDING
    provider_id: str
    model_id: str
    model_version: str
    input_digest: str
    prompt_id: str | None = None
    prompt_version: str | None = None
    output: str | None = None
    metrics: dict[str, float | int | str | bool] = Field(default_factory=dict)
    findings: tuple[str, ...] = ()
    estimated_cost_usd: float = Field(ge=0)
    latency_ms: int = Field(ge=0)
    network_access_used: bool = False
    recommendations_enabled: bool = False
    real_capital_orders_enabled: bool = False
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_evidence(self) -> ModelPreviewEvidence:
        if self.generated_at.tzinfo is None:
            raise ValueError("generated_at must be timezone-aware")
        if self.recommendations_enabled or self.real_capital_orders_enabled:
            raise ValueError("P12 previews cannot enable recommendations or real orders")
        return self
