"""Immutable Decimal-safe contracts for D9 forward paper evaluation."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def utc_now() -> datetime:
    return datetime.now(UTC)


def _aware(value: datetime, name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value


def _text(value: str, name: str, *, limit: int = 200) -> str:
    normalized = value.strip()
    if not normalized or len(normalized) > limit:
        raise ValueError(f"{name} must be between 1 and {limit} characters")
    return normalized


class OrderSide(StrEnum):
    BUY = "buy"
    SELL = "sell"


class SimulatedOrderType(StrEnum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    SCHEDULED_MARKET = "scheduled_market"


class OrderSourceKind(StrEnum):
    MANUAL = "manual"
    APPROVED_STRATEGY = "approved_strategy"


class SimulatedOrderStatus(StrEnum):
    CONFIRMED = "confirmed"
    PENDING = "pending"
    ACTIVE = "active"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    REJECTED = "rejected"


class RiskDecisionStatus(StrEnum):
    ALLOW = "allow"
    BLOCK = "block"
    REJECT = "reject"


class PaperRunBinding(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.paper.run-binding"] = "osca.paper.run-binding"
    version: Literal["1.0.0"] = "1.0.0"
    binding_id: UUID = Field(default_factory=uuid4)
    paper_run_id: UUID
    paper_account_id: UUID
    portfolio_id: UUID
    approved_candidate_id: UUID | None = None
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, value: datetime) -> datetime:
        return _aware(value, "created_at")


class ExecutionAssumptions(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.paper.execution-assumptions"] = "osca.paper.execution-assumptions"
    version: Literal["1.0.0"] = "1.0.0"
    assumption_id: UUID = Field(default_factory=uuid4)
    revision: int = Field(default=1, ge=1)
    spread_bps: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    slippage_bps: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    fee_bps: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    flat_fee: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    latency_ms: int = Field(default=0, ge=0)
    max_volume_participation: Decimal = Field(
        default=Decimal("1"),
        gt=Decimal("0"),
        le=Decimal("1"),
    )
    require_volume: bool = True
    max_order_notional: Decimal | None = Field(default=None, gt=Decimal("0"))
    max_position_notional: Decimal | None = Field(default=None, gt=Decimal("0"))
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, value: datetime) -> datetime:
        return _aware(value, "created_at")


class SimulatedOrderDraft(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.paper.order-draft"] = "osca.paper.order-draft"
    version: Literal["1.0.0"] = "1.0.0"
    draft_id: UUID = Field(default_factory=uuid4)
    draft_version: int = Field(default=1, ge=1)
    paper_run_id: UUID
    paper_account_id: UUID
    portfolio_id: UUID
    source_kind: OrderSourceKind
    source_id: str
    approved_candidate_id: UUID | None = None
    instrument_id: str
    side: OrderSide
    order_type: SimulatedOrderType
    quantity: Decimal = Field(gt=Decimal("0"))
    limit_price: Decimal | None = Field(default=None, gt=Decimal("0"))
    stop_price: Decimal | None = Field(default=None, gt=Decimal("0"))
    scheduled_at: datetime | None = None
    expires_at: datetime | None = None
    assumption_id: UUID
    lot_allocations: dict[UUID, Decimal] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("source_id")
    @classmethod
    def validate_source_id(cls, value: str) -> str:
        return _text(value, "source_id")

    @field_validator("instrument_id")
    @classmethod
    def validate_instrument_id(cls, value: str) -> str:
        return _text(value, "instrument_id")

    @field_validator("scheduled_at", "expires_at", "created_at")
    @classmethod
    def validate_times(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        return _aware(value, "order timestamp")

    @field_validator("lot_allocations")
    @classmethod
    def validate_lot_allocations(cls, value: dict[UUID, Decimal]) -> dict[UUID, Decimal]:
        if any(quantity <= Decimal("0") for quantity in value.values()):
            raise ValueError("lot allocations must be positive")
        return value

    @model_validator(mode="after")
    def validate_order_shape(self) -> Self:
        if self.source_kind is OrderSourceKind.APPROVED_STRATEGY:
            if self.approved_candidate_id is None:
                raise ValueError("approved strategy drafts require approved_candidate_id")
        elif self.approved_candidate_id is not None:
            raise ValueError("manual drafts cannot claim approved_candidate_id")

        if self.order_type is SimulatedOrderType.MARKET:
            if self.limit_price is not None or self.stop_price is not None:
                raise ValueError("market orders cannot have limit or stop prices")
            if self.scheduled_at is not None:
                raise ValueError("market orders cannot have scheduled_at")
        elif self.order_type is SimulatedOrderType.LIMIT:
            if self.limit_price is None or self.stop_price is not None:
                raise ValueError("limit orders require only limit_price")
            if self.scheduled_at is not None:
                raise ValueError("limit orders cannot have scheduled_at")
        elif self.order_type is SimulatedOrderType.STOP:
            if self.stop_price is None or self.limit_price is not None:
                raise ValueError("stop orders require only stop_price")
            if self.scheduled_at is not None:
                raise ValueError("stop orders cannot have scheduled_at")
        else:
            if self.scheduled_at is None:
                raise ValueError("scheduled market orders require scheduled_at")
            if self.limit_price is not None or self.stop_price is not None:
                raise ValueError("scheduled market orders cannot have trigger prices")

        if self.expires_at is not None and self.expires_at <= self.created_at:
            raise ValueError("expires_at must be after created_at")
        if self.scheduled_at is not None and self.expires_at is not None:
            if self.expires_at <= self.scheduled_at:
                raise ValueError("expires_at must be after scheduled_at")
        if self.side is OrderSide.BUY and self.lot_allocations:
            raise ValueError("buy orders cannot carry disposal lot allocations")
        if sum(self.lot_allocations.values(), Decimal("0")) > self.quantity:
            raise ValueError("lot allocations cannot exceed order quantity")
        return self


class SimulatedOrderConfirmation(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.paper.order-confirmation"] = "osca.paper.order-confirmation"
    version: Literal["1.0.0"] = "1.0.0"
    confirmation_id: UUID = Field(default_factory=uuid4)
    draft_id: UUID
    draft_version: int = Field(ge=1)
    paper_run_id: UUID
    portfolio_id: UUID
    assumption_id: UUID
    simulated_only: Literal[True] = True
    confirmed_at: datetime = Field(default_factory=utc_now)

    @field_validator("confirmed_at")
    @classmethod
    def validate_confirmed_at(cls, value: datetime) -> datetime:
        return _aware(value, "confirmed_at")


class SimulatedOrder(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.paper.simulated-order"] = "osca.paper.simulated-order"
    version: Literal["1.0.0"] = "1.0.0"
    order_id: UUID = Field(default_factory=uuid4)
    confirmation_id: UUID
    draft_id: UUID
    draft_version: int = Field(ge=1)
    paper_run_id: UUID
    paper_account_id: UUID
    portfolio_id: UUID
    instrument_id: str
    side: OrderSide
    order_type: SimulatedOrderType
    quantity: Decimal = Field(gt=Decimal("0"))
    limit_price: Decimal | None = Field(default=None, gt=Decimal("0"))
    stop_price: Decimal | None = Field(default=None, gt=Decimal("0"))
    scheduled_at: datetime | None = None
    expires_at: datetime | None = None
    assumption_id: UUID
    lot_allocations: dict[UUID, Decimal] = Field(default_factory=dict)
    confirmed_at: datetime
    eligible_at: datetime
    status: SimulatedOrderStatus = SimulatedOrderStatus.CONFIRMED

    @field_validator("instrument_id")
    @classmethod
    def validate_instrument_id(cls, value: str) -> str:
        return _text(value, "instrument_id")

    @field_validator("scheduled_at", "expires_at", "confirmed_at", "eligible_at")
    @classmethod
    def validate_times(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        return _aware(value, "order timestamp")

    @model_validator(mode="after")
    def validate_eligibility(self) -> Self:
        floor = self.confirmed_at
        if self.scheduled_at is not None and self.scheduled_at > floor:
            floor = self.scheduled_at
        if self.eligible_at < floor:
            raise ValueError("eligible_at cannot precede confirmation/schedule")
        return self


class PaperMarketBar(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.paper.market-bar"] = "osca.paper.market-bar"
    version: Literal["1.0.0"] = "1.0.0"
    evidence_id: UUID = Field(default_factory=uuid4)
    instrument_id: str
    dataset_revision_id: UUID
    source_id: str
    timeframe: str
    bar_started_at: datetime
    bar_ended_at: datetime
    available_at: datetime
    open: Decimal = Field(gt=Decimal("0"))
    high: Decimal = Field(gt=Decimal("0"))
    low: Decimal = Field(gt=Decimal("0"))
    close: Decimal = Field(gt=Decimal("0"))
    volume: Decimal | None = Field(default=None, ge=Decimal("0"))
    complete: bool = True
    market_calendar_id: str | None = None
    session_open: bool = True

    @field_validator("instrument_id", "source_id", "timeframe")
    @classmethod
    def validate_text(cls, value: str) -> str:
        return _text(value, "market bar identifier")

    @field_validator("market_calendar_id")
    @classmethod
    def validate_calendar(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _text(value, "market_calendar_id")

    @field_validator("bar_started_at", "bar_ended_at", "available_at")
    @classmethod
    def validate_times(cls, value: datetime) -> datetime:
        return _aware(value, "bar timestamp")

    @model_validator(mode="after")
    def validate_bar(self) -> Self:
        if not self.bar_started_at < self.bar_ended_at <= self.available_at:
            raise ValueError("bar timestamps must satisfy start < end <= available_at")
        if self.low > self.high:
            raise ValueError("bar low cannot exceed high")
        if not self.low <= self.open <= self.high:
            raise ValueError("bar open must be within low/high")
        if not self.low <= self.close <= self.high:
            raise ValueError("bar close must be within low/high")
        return self


class SimulatedFill(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.paper.simulated-fill"] = "osca.paper.simulated-fill"
    version: Literal["1.0.0"] = "1.0.0"
    fill_id: UUID = Field(default_factory=uuid4)
    order_id: UUID
    paper_run_id: UUID
    portfolio_id: UUID
    sequence: int = Field(ge=1)
    bar_evidence_id: UUID
    dataset_revision_id: UUID
    assumption_id: UUID
    instrument_id: str
    side: OrderSide
    quantity: Decimal = Field(gt=Decimal("0"))
    execution_price: Decimal = Field(gt=Decimal("0"))
    fee: Decimal = Field(ge=Decimal("0"))
    effective_at: datetime
    source_id: str

    @field_validator("instrument_id", "source_id")
    @classmethod
    def validate_text(cls, value: str) -> str:
        return _text(value, "fill identifier")

    @field_validator("effective_at")
    @classmethod
    def validate_effective_at(cls, value: datetime) -> datetime:
        return _aware(value, "effective_at")


class FillDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    can_fill: bool
    reason: str
    quantity: Decimal = Decimal("0")
    execution_price: Decimal | None = None
    fee: Decimal = Decimal("0")

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        return _text(value, "reason", limit=500)

    @model_validator(mode="after")
    def validate_fill_shape(self) -> Self:
        if self.can_fill:
            if self.quantity <= Decimal("0") or self.execution_price is None:
                raise ValueError("fillable decisions require positive quantity and execution_price")
        elif self.quantity != Decimal("0") or self.execution_price is not None:
            raise ValueError("non-fill decisions cannot contain fill quantity/price")
        return self


class PaperRiskDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.paper.risk-decision"] = "osca.paper.risk-decision"
    version: Literal["1.0.0"] = "1.0.0"
    risk_decision_id: UUID = Field(default_factory=uuid4)
    order_id: UUID
    status: RiskDecisionStatus
    reason: str
    checked_at: datetime = Field(default_factory=utc_now)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        return _text(value, "reason", limit=500)

    @field_validator("checked_at")
    @classmethod
    def validate_checked_at(cls, value: datetime) -> datetime:
        return _aware(value, "checked_at")


class OrderLifecycleEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.paper.order-lifecycle"] = "osca.paper.order-lifecycle"
    version: Literal["1.0.0"] = "1.0.0"
    event_id: UUID = Field(default_factory=uuid4)
    order_id: UUID
    sequence: int = Field(ge=1)
    status: SimulatedOrderStatus
    source_id: str
    reason: str
    fill_id: UUID | None = None
    effective_at: datetime = Field(default_factory=utc_now)

    @field_validator("source_id")
    @classmethod
    def validate_source_id(cls, value: str) -> str:
        return _text(value, "source_id")

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        return _text(value, "reason", limit=500)

    @field_validator("effective_at")
    @classmethod
    def validate_effective_at(cls, value: datetime) -> datetime:
        return _aware(value, "effective_at")
