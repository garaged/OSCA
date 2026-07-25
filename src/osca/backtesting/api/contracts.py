from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

Identifier = Annotated[str, Field(min_length=1, max_length=128)]
Description = Annotated[str, Field(min_length=1, max_length=2048)]


class BacktestFidelityProfile(StrEnum):
    F0_SIGNAL_STUDY = "f0_signal_study"
    F1_VECTORIZED_PORTFOLIO = "f1_vectorized_portfolio"
    F2_EVENT_DRIVEN_BAR = "f2_event_driven_bar"
    F3_FORWARD_PAPER = "f3_forward_paper"


class BacktestExecutionMode(StrEnum):
    SIGNAL_ONLY = "signal_only"
    VECTORIZED = "vectorized"
    EVENT_DRIVEN = "event_driven"
    FORWARD_PAPER = "forward_paper"


class BacktestDataAvailability(StrEnum):
    POINT_IN_TIME = "point_in_time"
    REVISED_AFTER_FACT = "revised_after_fact"
    PROVISIONAL = "provisional"


class BacktestFindingSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class OrderIntentSide(StrEnum):
    BUY = "buy"
    SELL = "sell"


class OrderIntentType(StrEnum):
    MARKET = "market"
    LIMIT = "limit"


class BacktestStatus(StrEnum):
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class BacktestAssumptionSet(BaseModel):
    model_config = ConfigDict(frozen=True)
    assumption_set_id: Identifier
    fees_bps: Annotated[float, Field(ge=0)] = 0
    slippage_bps: Annotated[float, Field(ge=0)] = 0
    latency_seconds: Annotated[float, Field(ge=0)] = 0
    allow_fractional_quantity: bool = True
    base_currency: Annotated[str, Field(min_length=3, max_length=3)] = "USD"


class BacktestWindow(BaseModel):
    model_config = ConfigDict(frozen=True)
    start_at: datetime
    end_at: datetime

    @model_validator(mode="after")
    def validate_window(self) -> Self:
        if self.start_at.tzinfo is None or self.end_at.tzinfo is None:
            raise ValueError("backtest window timestamps must be timezone-aware")
        if self.end_at <= self.start_at:
            raise ValueError("backtest window end_at must be after start_at")
        return self


class StrategyDecision(BaseModel):
    model_config = ConfigDict(frozen=True)
    decision_id: UUID = Field(default_factory=uuid4)
    strategy_id: Identifier
    effective_at: datetime
    rationale: Description
    confidence: Annotated[float, Field(ge=0, le=1)]
    evidence_ids: tuple[UUID, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_effective_at(self) -> Self:
        if self.effective_at.tzinfo is None:
            raise ValueError("strategy decision effective_at must be timezone-aware")
        return self


class OrderIntent(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.backtest.order-intent"] = "osca.backtest.order-intent"
    version: Literal["1.0.0"] = "1.0.0"
    order_intent_id: UUID = Field(default_factory=uuid4)
    decision_id: UUID
    instrument_id: UUID
    side: OrderIntentSide
    order_type: OrderIntentType
    quantity: Annotated[float, Field(gt=0)]
    limit_price: Annotated[float, Field(gt=0)] | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_order_intent(self) -> Self:
        if self.created_at.tzinfo is None:
            raise ValueError("order intent created_at must be timezone-aware")
        if self.order_type is OrderIntentType.LIMIT and self.limit_price is None:
            raise ValueError("limit order intents require limit_price")
        if self.order_type is OrderIntentType.MARKET and self.limit_price is not None:
            raise ValueError("market order intents cannot declare limit_price")
        return self


class BacktestRequest(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.backtest.request"] = "osca.backtest.request"
    version: Literal["1.0.0"] = "1.0.0"
    request_id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    strategy_id: Identifier
    fidelity_profile: BacktestFidelityProfile
    execution_mode: BacktestExecutionMode
    window: BacktestWindow
    dataset_revision_ids: tuple[UUID, ...] = Field(min_length=1)
    data_availability: BacktestDataAvailability
    assumptions: BacktestAssumptionSet
    random_seed: int | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_created_at(self) -> Self:
        if self.created_at.tzinfo is None:
            raise ValueError("backtest request created_at must be timezone-aware")
        return self


class BacktestValidationFinding(BaseModel):
    model_config = ConfigDict(frozen=True)
    code: Identifier
    severity: BacktestFindingSeverity
    message: Description


class BacktestExecutionPlan(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.backtest.execution-plan"] = "osca.backtest.execution-plan"
    version: Literal["1.0.0"] = "1.0.0"
    request_id: UUID
    can_execute: bool
    required_checks: tuple[Identifier, ...]
    findings: tuple[BacktestValidationFinding, ...] = ()
    planned_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_planned_at(self) -> Self:
        if self.planned_at.tzinfo is None:
            raise ValueError("backtest execution plan planned_at must be timezone-aware")
        if self.can_execute and any(
            finding.severity is BacktestFindingSeverity.ERROR for finding in self.findings
        ):
            raise ValueError("executable plans cannot contain error findings")
        return self


class BacktestMetric(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: Identifier
    value: float
    unit: Identifier
    methodology: Identifier


class BacktestResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.backtest.result"] = "osca.backtest.result"
    version: Literal["1.0.0"] = "1.0.0"
    result_id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    status: BacktestStatus
    metrics: tuple[BacktestMetric, ...] = ()
    unsupported_behaviors: tuple[Description, ...] = ()
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        if self.generated_at.tzinfo is None:
            raise ValueError("backtest result generated_at must be timezone-aware")
        if self.status is BacktestStatus.COMPLETED and not self.metrics:
            raise ValueError("completed backtest results require at least one metric")
        return self
