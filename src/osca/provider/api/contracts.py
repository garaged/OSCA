from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from osca.instrument.api import AssetClass

Identifier = Annotated[str, Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$")]


class AuthenticationKind(StrEnum):
    NONE = "none"
    NAMED_SECRET = "named_secret"


class TimestampSemantics(StrEnum):
    UTC_INTERVAL_END = "utc_interval_end"
    VENUE_SESSION_DATE = "venue_session_date"


class AdjustmentSemantics(StrEnum):
    UNADJUSTED = "unadjusted"


class ProviderFailureCode(StrEnum):
    AUTHENTICATION = "authentication"
    POLICY = "policy"
    QUOTA = "quota"
    TRANSPORT = "transport"
    SCHEMA = "schema"
    MAPPING = "mapping"
    QUALITY = "quality"
    COMPATIBILITY = "compatibility"


class AcquisitionRights(BaseModel):
    model_config = ConfigDict(frozen=True)
    retrieval: bool
    retention: bool
    transformation: bool
    export: bool
    backup: bool
    redistribution: bool
    fixture_redistribution: bool
    policy_revision: Identifier


class QuotaProfile(BaseModel):
    model_config = ConfigDict(frozen=True)
    unit: Literal["request"] = "request"
    maximum: int = Field(gt=0)
    window_seconds: int = Field(gt=0)
    retry_after_supported: bool
    maximum_attempts: int = Field(ge=1, le=10)


class ProviderCapability(BaseModel):
    """Machine-readable provider behavior (osca.provider.capability 1.0.0)."""

    model_config = ConfigDict(frozen=True)
    family: Literal["osca.provider.capability"] = "osca.provider.capability"
    version: Literal["1.0.0"] = "1.0.0"
    provider_id: Identifier
    asset_classes: frozenset[AssetClass] = Field(min_length=1)
    intervals: frozenset[Literal["1d"]] = frozenset({"1d"})
    earliest_date: date
    latest_completed_date: date
    timestamp_semantics: TimestampSemantics
    adjustment_semantics: AdjustmentSemantics = AdjustmentSemantics.UNADJUSTED
    authentication: AuthenticationKind
    credential_reference: Identifier | None = None
    quota: QuotaProfile
    rights: AcquisitionRights
    endpoint_hosts: tuple[str, ...] = ()
    healthy: bool = True
    quality_limitations: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_security_profile(self) -> Self:
        if self.earliest_date > self.latest_completed_date:
            raise ValueError("earliest_date must not exceed latest_completed_date")
        if self.authentication is AuthenticationKind.NAMED_SECRET:
            if self.credential_reference is None:
                raise ValueError("named_secret authentication requires credential_reference")
        elif self.credential_reference is not None:
            raise ValueError("credential_reference is allowed only for named_secret authentication")
        return self


class DailyProviderRequest(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.provider.daily-request"] = "osca.provider.daily-request"
    version: Literal["1.0.0"] = "1.0.0"
    request_id: UUID = Field(default_factory=uuid4)
    instrument_id: UUID
    provider_symbol: Identifier
    start_date: date
    end_date_exclusive: date
    interval: Literal["1d"] = "1d"

    @model_validator(mode="after")
    def validate_range(self) -> Self:
        if self.start_date >= self.end_date_exclusive:
            raise ValueError("start_date must precede end_date_exclusive")
        return self


class ProviderDailyObservation(BaseModel):
    model_config = ConfigDict(frozen=True)
    effective_date: date
    source_timestamp: datetime
    complete: bool
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    currency: Identifier
    source_identity: Identifier

    @model_validator(mode="after")
    def validate_numbers(self) -> Self:
        values = (self.open, self.high, self.low, self.close, self.volume)
        if not all(value.is_finite() for value in values):
            raise ValueError("provider observations require finite numbers")
        if self.source_timestamp.tzinfo is None:
            raise ValueError("source_timestamp must be timezone-aware")
        return self


class ProviderFailure(BaseModel):
    model_config = ConfigDict(frozen=True)
    code: ProviderFailureCode
    retryable: bool
    safe_message: Annotated[str, Field(min_length=1, max_length=256)]
    retry_after_seconds: int | None = Field(default=None, ge=0)


class ProviderResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.provider.daily-result"] = "osca.provider.daily-result"
    version: Literal["1.0.0"] = "1.0.0"
    request_id: UUID
    provider_id: Identifier
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    observations: tuple[ProviderDailyObservation, ...] = ()
    failure: ProviderFailure | None = None

    @model_validator(mode="after")
    def validate_outcome(self) -> Self:
        if bool(self.observations) == (self.failure is not None):
            raise ValueError("result must contain exactly observations or failure")
        dates = tuple(item.effective_date for item in self.observations)
        if dates != tuple(sorted(set(dates))):
            raise ValueError("observations must have unique ascending effective dates")
        return self
