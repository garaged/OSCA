from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from osca.backtesting.api import OrderIntent

Identifier = Annotated[str, Field(min_length=1, max_length=128)]
Description = Annotated[str, Field(min_length=1, max_length=2048)]
Currency = Annotated[str, Field(min_length=3, max_length=3)]


class F2EventType(StrEnum):
    MARKET_BAR = "market_bar"
    CLOCK = "clock"
    ORDER_LIFECYCLE = "order_lifecycle"
    FILL = "fill"
    RISK_DECISION = "risk_decision"
    JOURNAL = "journal"
    VALUATION = "valuation"


class OrderLifecycleState(StrEnum):
    CREATED = "created"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"


class RiskDecisionAction(StrEnum):
    APPROVE = "approve"
    MODIFY = "modify"
    REJECT = "reject"
    PAUSE = "pause"


class JournalLineSide(StrEnum):
    DEBIT = "debit"
    CREDIT = "credit"


class F2SimulationEvent(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.backtest.event"] = "osca.backtest.event"
    version: Literal["1.0.0"] = "1.0.0"
    event_id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    event_type: F2EventType
    effective_at: datetime
    source_id: Identifier

    @model_validator(mode="after")
    def validate_effective_at(self) -> Self:
        if self.effective_at.tzinfo is None:
            raise ValueError("F2 event effective_at must be timezone-aware")
        return self


class OrderLifecycleEvent(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.backtest.order-lifecycle"] = "osca.backtest.order-lifecycle"
    version: Literal["1.0.0"] = "1.0.0"
    lifecycle_event_id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    order_intent_id: UUID
    decision_id: UUID
    state: OrderLifecycleState
    effective_at: datetime
    rationale: Description

    @classmethod
    def from_order_intent(
        cls,
        *,
        request_id: UUID,
        order_intent: OrderIntent,
        state: OrderLifecycleState,
        rationale: str,
        effective_at: datetime | None = None,
    ) -> "OrderLifecycleEvent":
        return cls(
            request_id=request_id,
            order_intent_id=order_intent.order_intent_id,
            decision_id=order_intent.decision_id,
            state=state,
            effective_at=effective_at or datetime.now(UTC),
            rationale=rationale,
        )

    @model_validator(mode="after")
    def validate_effective_at(self) -> Self:
        if self.effective_at.tzinfo is None:
            raise ValueError("order lifecycle effective_at must be timezone-aware")
        return self


class FillModelMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)
    model_id: Identifier
    version: Identifier
    spread_bps: Annotated[float, Field(ge=0)] = 0
    slippage_bps: Annotated[float, Field(ge=0)] = 0
    latency_seconds: Annotated[float, Field(ge=0)] = 0
    liquidity_limit_quantity: Annotated[float, Field(gt=0)] | None = None


class SimulatedFill(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.backtest.fill"] = "osca.backtest.fill"
    version: Literal["1.0.0"] = "1.0.0"
    fill_id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    order_intent_id: UUID
    market_observation_id: UUID
    fill_model: FillModelMetadata
    filled_quantity: Annotated[float, Field(gt=0)]
    fill_price: Annotated[float, Field(gt=0)]
    fee_amount: Annotated[float, Field(ge=0)] = 0
    fee_currency: Currency = "USD"
    partial_fill: bool = False
    effective_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_fill(self) -> Self:
        if self.effective_at.tzinfo is None:
            raise ValueError("simulated fill effective_at must be timezone-aware")
        if (
            self.fill_model.liquidity_limit_quantity is not None
            and self.filled_quantity > self.fill_model.liquidity_limit_quantity
        ):
            raise ValueError("filled quantity cannot exceed liquidity limit")
        return self


class RiskDecision(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.backtest.risk-decision"] = "osca.backtest.risk-decision"
    version: Literal["1.0.0"] = "1.0.0"
    risk_decision_id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    order_intent_id: UUID | None = None
    policy_id: Identifier
    policy_version: Identifier
    action: RiskDecisionAction
    rationale: Description
    effective_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_effective_at(self) -> Self:
        if self.effective_at.tzinfo is None:
            raise ValueError("risk decision effective_at must be timezone-aware")
        return self


class JournalLine(BaseModel):
    model_config = ConfigDict(frozen=True)
    account: Identifier
    side: JournalLineSide
    amount: Annotated[float, Field(gt=0)]
    currency: Currency
    instrument_id: UUID | None = None


class JournalTransaction(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.backtest.journal-transaction"] = "osca.backtest.journal-transaction"
    version: Literal["1.0.0"] = "1.0.0"
    transaction_id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    source_event_id: UUID
    effective_at: datetime
    description: Description
    lines: tuple[JournalLine, ...] = Field(min_length=2)

    @model_validator(mode="after")
    def validate_transaction(self) -> Self:
        if self.effective_at.tzinfo is None:
            raise ValueError("journal transaction effective_at must be timezone-aware")
        totals: dict[str, float] = {}
        for line in self.lines:
            signed = line.amount if line.side is JournalLineSide.DEBIT else -line.amount
            totals[line.currency] = totals.get(line.currency, 0.0) + signed
        imbalanced = {currency: total for currency, total in totals.items() if abs(total) > 1e-9}
        if imbalanced:
            raise ValueError("journal transaction must balance by currency")
        return self


class ValuationHolding(BaseModel):
    model_config = ConfigDict(frozen=True)
    instrument_id: UUID
    quantity: float
    price: Annotated[float, Field(ge=0)]
    price_currency: Currency
    price_source_id: Identifier
    fx_rate_to_base: Annotated[float, Field(gt=0)] = 1
    fx_source_id: Identifier | None = None

    @model_validator(mode="after")
    def validate_fx_source(self) -> Self:
        if self.price_currency != "USD" and self.fx_source_id is None:
            raise ValueError("non-base valuation holdings require fx_source_id")
        return self


class ValuationSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.backtest.valuation"] = "osca.backtest.valuation"
    version: Literal["1.0.0"] = "1.0.0"
    valuation_id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    base_currency: Currency = "USD"
    effective_at: datetime
    valuation_version: Identifier
    holdings: tuple[ValuationHolding, ...] = ()

    @model_validator(mode="after")
    def validate_effective_at(self) -> Self:
        if self.effective_at.tzinfo is None:
            raise ValueError("valuation effective_at must be timezone-aware")
        return self


class PortfolioProjection(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.backtest.portfolio-projection"] = "osca.backtest.portfolio-projection"
    version: Literal["1.0.0"] = "1.0.0"
    projection_id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    journal_transaction_ids: tuple[UUID, ...] = Field(min_length=1)
    valuation_id: UUID
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_generated_at(self) -> Self:
        if self.generated_at.tzinfo is None:
            raise ValueError("portfolio projection generated_at must be timezone-aware")
        return self


class ReconciliationFinding(BaseModel):
    model_config = ConfigDict(frozen=True)
    code: Identifier
    severity: Literal["info", "warning", "error"]
    message: Description


class PromotionGateDecision(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.backtest.promotion-gate"] = "osca.backtest.promotion-gate"
    version: Literal["1.0.0"] = "1.0.0"
    gate_id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    candidate_id: Identifier
    approved_for_paper_evaluation: bool
    findings: tuple[ReconciliationFinding, ...] = ()
    decided_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_gate(self) -> Self:
        if self.decided_at.tzinfo is None:
            raise ValueError("promotion gate decided_at must be timezone-aware")
        if self.approved_for_paper_evaluation and any(
            finding.severity == "error" for finding in self.findings
        ):
            raise ValueError("promotion gate cannot approve when error findings exist")
        return self
