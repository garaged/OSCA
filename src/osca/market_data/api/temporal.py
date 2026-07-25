from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Decimal38x18 = Annotated[Decimal, Field(max_digits=38, decimal_places=18)]
Identifier = Annotated[str, Field(min_length=1, max_length=128)]


class MarketDataInterval(StrEnum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"


INTERVAL_SECONDS: dict[MarketDataInterval, int] = {
    MarketDataInterval.M1: 60,
    MarketDataInterval.M5: 5 * 60,
    MarketDataInterval.M15: 15 * 60,
    MarketDataInterval.M30: 30 * 60,
    MarketDataInterval.H1: 60 * 60,
    MarketDataInterval.H4: 4 * 60 * 60,
    MarketDataInterval.D1: 24 * 60 * 60,
}


class MarketDomain(StrEnum):
    STOCK = "stock"
    CRYPTO = "crypto"


class SessionState(StrEnum):
    OPEN = "open"
    CLOSED = "closed"
    HOLIDAY = "holiday"
    EARLY_CLOSE = "early_close"


class TemporalGapState(StrEnum):
    OBSERVED = "observed"
    MISSING = "missing"
    UNRESOLVED = "unresolved"
    NON_EXPECTED = "non_expected"
    INCOMPLETE = "incomplete"


class ExchangeSession(BaseModel):
    model_config = ConfigDict(frozen=True)
    session_date: date
    opens_at: datetime
    closes_at: datetime
    state: SessionState = SessionState.OPEN
    venue: Identifier
    calendar_revision: Identifier

    @model_validator(mode="after")
    def validate_session(self) -> Self:
        if self.opens_at.tzinfo is None or self.closes_at.tzinfo is None:
            raise ValueError("session boundaries must be timezone-aware")
        if self.opens_at.utcoffset() != UTC.utcoffset(self.opens_at):
            raise ValueError("session open must be expressed in UTC")
        if self.closes_at.utcoffset() != UTC.utcoffset(self.closes_at):
            raise ValueError("session close must be expressed in UTC")
        if self.opens_at >= self.closes_at:
            raise ValueError("session open must precede close")
        return self


class CryptoUtcDay(BaseModel):
    model_config = ConfigDict(frozen=True)
    session_date: date
    opens_at: datetime
    closes_at: datetime
    calendar_revision: Literal["crypto-utc-day-v1"] = "crypto-utc-day-v1"

    @classmethod
    def for_date(cls, session_date: date) -> "CryptoUtcDay":
        start = datetime.combine(session_date, time.min, tzinfo=UTC)
        return cls(session_date=session_date, opens_at=start, closes_at=start + timedelta(days=1))


class CompletedBarWindow(BaseModel):
    model_config = ConfigDict(frozen=True)
    interval: MarketDataInterval
    starts_at: datetime
    ends_at: datetime

    @model_validator(mode="after")
    def validate_window(self) -> Self:
        if self.starts_at.tzinfo is None or self.ends_at.tzinfo is None:
            raise ValueError("bar window boundaries must be timezone-aware")
        if self.starts_at.utcoffset() != UTC.utcoffset(self.starts_at):
            raise ValueError("bar window start must be UTC")
        if self.ends_at.utcoffset() != UTC.utcoffset(self.ends_at):
            raise ValueError("bar window end must be UTC")
        if self.starts_at >= self.ends_at:
            raise ValueError("bar window must be non-empty")
        expected = timedelta(seconds=INTERVAL_SECONDS[self.interval])
        if self.ends_at - self.starts_at != expected:
            raise ValueError("bar window duration must match interval")
        return self


class CanonicalOhlcvBar(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.market-data.ohlcv-bar"] = "osca.market-data.ohlcv-bar"
    version: Literal["1.0.0"] = "1.0.0"
    bar_id: UUID = Field(default_factory=uuid4)
    instrument_id: UUID
    interval: MarketDataInterval
    starts_at: datetime
    ends_at: datetime
    effective_date: date
    complete: Literal[True] = True
    open: Decimal38x18
    high: Decimal38x18
    low: Decimal38x18
    close: Decimal38x18
    volume: Decimal38x18
    currency: Identifier
    volume_unit: Identifier
    provider_id: Identifier
    source_identity: Identifier
    request_id: UUID
    normalization_revision: Identifier
    calendar_revision: Identifier

    @field_validator("open", "high", "low", "close", "volume", mode="before")
    @classmethod
    def reject_binary_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("canonical decimals cannot originate from binary float")
        return value

    @model_validator(mode="after")
    def validate_semantics(self) -> Self:
        CompletedBarWindow(interval=self.interval, starts_at=self.starts_at, ends_at=self.ends_at)
        if self.volume < 0:
            raise ValueError("volume must be non-negative")
        if min(self.open, self.close, self.low) < 0:
            raise ValueError("prices must be non-negative")
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("high must not be below OHLC values")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("low must not be above OHLC values")
        return self


class TemporalGap(BaseModel):
    model_config = ConfigDict(frozen=True)
    instrument_id: UUID
    interval: MarketDataInterval
    starts_at: datetime
    ends_at: datetime
    state: TemporalGapState
    reason: Identifier
    repair_eligible: bool
    calendar_revision: Identifier


class ResampleLineage(BaseModel):
    model_config = ConfigDict(frozen=True)
    output_bar_id: UUID
    source_bar_ids: tuple[UUID, ...] = Field(min_length=1)
    source_interval: MarketDataInterval
    target_interval: MarketDataInterval
    calendar_revision: Identifier
    method_revision: Literal["ohlcv-resample-v1"] = "ohlcv-resample-v1"

    @model_validator(mode="after")
    def validate_direction(self) -> Self:
        if INTERVAL_SECONDS[self.source_interval] >= INTERVAL_SECONDS[self.target_interval]:
            raise ValueError("resampling lineage must go from lower to higher interval")
        return self
