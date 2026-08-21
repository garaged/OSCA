"""Decimal-safe virtual-portfolio accounting contracts for D8."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def utc_now() -> datetime:
    """Return an aware UTC timestamp."""
    return datetime.now(UTC)


def _aware(value: datetime, name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value


def _currency(value: str) -> str:
    normalized = value.strip().upper()
    if len(normalized) != 3 or not normalized.isalpha():
        raise ValueError("currency must be a three-letter alphabetic code")
    return normalized


class PortfolioStatus(StrEnum):
    ACTIVE = "active"
    CLOSED = "closed"


class AccountingEventType(StrEnum):
    FUNDING = "funding"
    WITHDRAWAL = "withdrawal"
    ACQUISITION = "acquisition"
    DISPOSAL = "disposal"
    FEE = "fee"
    DIVIDEND = "dividend"
    SPLIT = "split"
    FORK = "fork"
    FX_CONVERSION = "fx_conversion"
    MANUAL_ADJUSTMENT = "manual_adjustment"
    REVERSAL = "reversal"
    CLONE_OPENING = "clone_opening"
    RESET_OPENING = "reset_opening"


class PostingSide(StrEnum):
    DEBIT = "debit"
    CREDIT = "credit"


class ProjectionHealth(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"


class VirtualPortfolio(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: str = "osca.virtual-portfolio"
    version: str = "1.0.0"
    portfolio_id: UUID = Field(default_factory=uuid4)
    name: str
    base_currency: str = "USD"
    status: PortfolioStatus = PortfolioStatus.ACTIVE
    created_at: datetime = Field(default_factory=utc_now)
    source_portfolio_id: UUID | None = None
    source_revision: int | None = Field(default=None, ge=0)
    lineage_kind: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized or len(normalized) > 120:
            raise ValueError("name must be between 1 and 120 characters")
        return normalized

    @field_validator("base_currency")
    @classmethod
    def validate_base_currency(cls, value: str) -> str:
        return _currency(value)

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, value: datetime) -> datetime:
        return _aware(value, "created_at")

    @model_validator(mode="after")
    def validate_lineage(self) -> Self:
        has_source = self.source_portfolio_id is not None
        if has_source != (self.source_revision is not None):
            raise ValueError("source_portfolio_id and source_revision must be provided together")
        if has_source and not self.lineage_kind:
            raise ValueError("lineage_kind is required when source lineage is present")
        if self.lineage_kind is not None and not has_source:
            raise ValueError("lineage_kind requires source lineage")
        return self


class AccountingEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: str = "osca.accounting-event"
    version: str = "1.0.0"
    event_id: UUID
    portfolio_id: UUID
    sequence: int = Field(ge=1)
    event_type: AccountingEventType
    effective_at: datetime
    recorded_at: datetime = Field(default_factory=utc_now)
    source_kind: str
    source_id: str
    payload: dict[str, str]
    content_digest: str = Field(min_length=64, max_length=64)

    @field_validator("effective_at", "recorded_at")
    @classmethod
    def validate_times(cls, value: datetime) -> datetime:
        return _aware(value, "event timestamp")

    @field_validator("source_kind", "source_id")
    @classmethod
    def validate_source_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized or len(normalized) > 200:
            raise ValueError("source identifiers must be between 1 and 200 characters")
        return normalized


class JournalPosting(BaseModel):
    model_config = ConfigDict(frozen=True)

    posting_id: UUID
    account_code: str
    side: PostingSide
    currency: str
    amount: Decimal = Field(ge=Decimal("0"))
    instrument_id: str | None = None

    @field_validator("account_code")
    @classmethod
    def validate_account_code(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized or len(normalized) > 120:
            raise ValueError("account_code must be between 1 and 120 characters")
        return normalized

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        return _currency(value)

    @field_validator("instrument_id")
    @classmethod
    def validate_instrument_id(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized or len(normalized) > 200:
            raise ValueError("instrument_id must be between 1 and 200 characters")
        return normalized


class JournalTransaction(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: str = "osca.accounting-journal"
    version: str = "1.0.0"
    transaction_id: UUID
    portfolio_id: UUID
    event_id: UUID
    effective_at: datetime
    postings: tuple[JournalPosting, ...] = Field(min_length=2)

    @field_validator("effective_at")
    @classmethod
    def validate_effective_at(cls, value: datetime) -> datetime:
        return _aware(value, "effective_at")

    @model_validator(mode="after")
    def validate_balance(self) -> Self:
        balances: dict[str, Decimal] = {}
        for posting in self.postings:
            signed = posting.amount if posting.side is PostingSide.DEBIT else -posting.amount
            balances[posting.currency] = balances.get(posting.currency, Decimal("0")) + signed
        unbalanced = {
            currency: amount for currency, amount in balances.items() if amount != Decimal("0")
        }
        if unbalanced:
            raise ValueError(f"journal transaction is not balanced by currency: {unbalanced}")
        return self


class ValuationObservation(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: str = "osca.portfolio-valuation-observation"
    version: str = "1.0.0"
    observation_id: UUID = Field(default_factory=uuid4)
    portfolio_id: UUID
    asset_id: str
    quantity: Decimal
    unit_price: Decimal = Field(gt=Decimal("0"))
    price_currency: str
    price_source: str
    price_effective_at: datetime
    fx_rate_to_base: Decimal | None = Field(default=None, gt=Decimal("0"))
    fx_source: str | None = None
    fx_effective_at: datetime | None = None
    valuation_revision: str
    recorded_at: datetime = Field(default_factory=utc_now)

    @field_validator("asset_id", "price_source", "valuation_revision")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized or len(normalized) > 200:
            raise ValueError("valuation identifiers must be between 1 and 200 characters")
        return normalized

    @field_validator("price_currency")
    @classmethod
    def validate_price_currency(cls, value: str) -> str:
        return _currency(value)

    @field_validator("price_effective_at", "recorded_at")
    @classmethod
    def validate_observation_times(cls, value: datetime) -> datetime:
        return _aware(value, "valuation timestamp")

    @model_validator(mode="after")
    def validate_fx_evidence(self) -> Self:
        supplied = (
            self.fx_rate_to_base is not None,
            self.fx_source is not None,
            self.fx_effective_at is not None,
        )
        if any(supplied) and not all(supplied):
            raise ValueError("FX rate, source, and effective time must be supplied together")
        if self.fx_effective_at is not None:
            _aware(self.fx_effective_at, "fx_effective_at")
        if self.fx_source is not None and not self.fx_source.strip():
            raise ValueError("fx_source cannot be blank")
        return self


class LotState(BaseModel):
    model_config = ConfigDict(frozen=True)

    lot_id: UUID
    instrument_id: str
    acquired_at: datetime
    quantity: Decimal
    book_cost: Decimal
    currency: str

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        return _currency(value)


class PositionState(BaseModel):
    model_config = ConfigDict(frozen=True)

    instrument_id: str
    quantity: Decimal
    book_cost: Decimal
    currency: str

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        return _currency(value)


class PortfolioProjection(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: str = "osca.virtual-portfolio-projection"
    version: str = "1.0.0"
    portfolio_id: UUID
    revision: int = Field(ge=0)
    base_currency: str
    cash_by_currency: dict[str, Decimal]
    positions: tuple[PositionState, ...]
    lots: tuple[LotState, ...]
    realized_pnl_by_currency: dict[str, Decimal]
    income_by_currency: dict[str, Decimal]
    fees_by_currency: dict[str, Decimal]
    health: ProjectionHealth
    missing_evidence: tuple[str, ...] = ()
    equity_base: Decimal | None = None
    unrealized_pnl_base: Decimal | None = None
    gross_exposure_base: Decimal | None = None
    net_exposure_base: Decimal | None = None
    allocation_by_asset: dict[str, Decimal] = Field(default_factory=dict)

    @field_validator("base_currency")
    @classmethod
    def validate_base_currency(cls, value: str) -> str:
        return _currency(value)
