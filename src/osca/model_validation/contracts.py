from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from osca.ml_experiments import MLExperimentResult
from osca.prediction_lab import ExperimentDiagnostic


class MissingPredictionPolicy(StrEnum):
    HOLD_CASH = "hold_cash"


class ValidationStatus(StrEnum):
    REJECTED = "rejected"
    COMPLETED = "completed"
    PAPER_CHALLENGER_APPROVED = "paper_challenger_approved"


class PromotionDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    decision_id: UUID = Field(default_factory=uuid4)
    approved: bool
    reviewer: str = Field(min_length=1, max_length=128)
    rationale: str = Field(min_length=1, max_length=4096)
    decided_at: datetime


class ResearchSignalRule(BaseModel):
    model_config = ConfigDict(frozen=True)

    version: Literal["1.0.0"] = "1.0.0"
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    long_only: Literal[True] = True
    missing_prediction_policy: MissingPredictionPolicy = MissingPredictionPolicy.HOLD_CASH
    transaction_cost_bps: float = Field(default=5.0, ge=0.0, le=1_000.0)
    slippage_bps: float = Field(default=5.0, ge=0.0, le=1_000.0)
    latency_bars: int = Field(default=1, ge=1, le=20)


class ModelValidationRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    experiment: MLExperimentResult
    diagnostic: ExperimentDiagnostic
    promotion: PromotionDecision
    payload_path: Path
    initial_cash: float = Field(default=10_000.0, gt=0.0)
    signal_rule: ResearchSignalRule = Field(default_factory=ResearchSignalRule)
    request_paper_challenger: bool = False
    paper_challenger_reviewer: str | None = Field(default=None, max_length=128)
    paper_challenger_rationale: str | None = Field(default=None, max_length=4096)

    @model_validator(mode="after")
    def validate_paper_challenger(self) -> ModelValidationRequest:
        if self.request_paper_challenger and (
            not self.paper_challenger_reviewer or not self.paper_challenger_rationale
        ):
            raise ValueError(
                "paper challenger designation requires reviewer and rationale"
            )
        return self


class ResearchSignalEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    prediction_timestamp: datetime
    execution_timestamp: datetime
    prediction: float
    probability: float | None = None
    position: Literal[0, 1]
    execution_price: float = Field(gt=0.0)
    exit_price: float = Field(gt=0.0)
    gross_return: float
    cost_return: float = Field(ge=0.0)
    net_return: float


class ValidationSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    aligned_predictions: int = Field(ge=0)
    skipped_predictions: int = Field(ge=0)
    invested_periods: int = Field(ge=0)
    position_changes: int = Field(ge=0)
    initial_cash: float = Field(gt=0.0)
    final_equity: float = Field(ge=0.0)
    total_return: float
    buy_and_hold_return: float
    baseline_excess_return: float
    maximum_drawdown: float
    total_cost_return: float = Field(ge=0.0)


class PaperChallengerEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    requested: bool
    approved: bool
    reviewer: str | None = None
    rationale: str | None = None
    mode: Literal["local-evidence-only"] = "local-evidence-only"


class ModelValidationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    validation_id: UUID = Field(default_factory=uuid4)
    status: ValidationStatus
    experiment_id: UUID
    diagnostic_digest: str
    promotion_decision_id: UUID
    dataset_revision_id: UUID
    payload_sha256: str
    symbol: str
    timeframe: str
    signal_rule: ResearchSignalRule
    events: tuple[ResearchSignalEvent, ...]
    summary: ValidationSummary
    paper_challenger: PaperChallengerEvidence
    findings: tuple[str, ...]
    assumptions: tuple[str, ...]
    evidence_digest: str
    event_driven_validation_enabled: bool = True
    live_model_serving_enabled: bool = False
    automatic_promotion_enabled: bool = False
    recommendations_enabled: bool = False
    broker_execution_enabled: bool = False
    real_capital_execution_enabled: bool = False
