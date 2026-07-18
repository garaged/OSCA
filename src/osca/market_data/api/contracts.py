import hashlib
import json
from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Any, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Decimal38x18 = Annotated[Decimal, Field(max_digits=38, decimal_places=18)]
Identifier = Annotated[str, Field(min_length=1, max_length=128)]


class DatasetLayer(StrEnum):
    SOURCE = "source"
    CANONICAL = "canonical"


class ManifestState(StrEnum):
    STAGING = "staging"
    READY = "ready"
    QUARANTINED = "quarantined"
    DELETING = "deleting"
    DELETED = "deleted"


class ResolutionState(StrEnum):
    FRESH = "fresh"
    STALE = "stale"
    PARTIAL = "partial"
    INVALID = "invalid"
    CORRUPT = "corrupt"
    UNAVAILABLE = "unavailable"
    REFRESHING = "refreshing"
    QUOTA_BLOCKED = "quota_blocked"
    POLICY_BLOCKED = "policy_blocked"


class DateClassification(StrEnum):
    OBSERVED = "observed"
    MISSING = "missing"
    UNRESOLVED = "unresolved"
    NON_EXPECTED = "non_expected"
    INCOMPLETE = "incomplete"
    INVALID = "invalid"
    DUPLICATE = "duplicate"


class RetrievalRequest(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.market-data.retrieval-request"] = (
        "osca.market-data.retrieval-request"
    )
    version: Literal["1.0.0"] = "1.0.0"
    request_id: UUID = Field(default_factory=uuid4)
    instrument_id: UUID
    start_date: date
    end_date_exclusive: date
    interval: Literal["1d"] = "1d"
    maximum_age_seconds: int = Field(ge=0)
    require_complete: bool = True
    provider_ids: tuple[Identifier, ...] = ()
    pinned_revision_id: UUID | None = None
    idempotency_key: Identifier

    @model_validator(mode="after")
    def validate_range(self) -> Self:
        if self.start_date >= self.end_date_exclusive:
            raise ValueError("retrieval range must be non-empty")
        return self


class RetrievalResolution(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.market-data.resolution"] = "osca.market-data.resolution"
    version: Literal["1.0.0"] = "1.0.0"
    request_id: UUID
    state: ResolutionState
    dataset_id: UUID | None = None
    revision_id: UUID | None = None
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    safe_remediation: Annotated[str, Field(min_length=1, max_length=256)]
    findings: tuple[UUID, ...] = ()

    @model_validator(mode="after")
    def validate_dataset_identity(self) -> Self:
        identities = (self.dataset_id, self.revision_id)
        if (identities[0] is None) != (identities[1] is None):
            raise ValueError("dataset and revision identities must be present together")
        if self.state is ResolutionState.FRESH and self.dataset_id is None:
            raise ValueError("fresh resolution requires an exact dataset revision")
        return self


class RepairRange(BaseModel):
    model_config = ConfigDict(frozen=True)
    start_date: date
    end_date_exclusive: date

    @model_validator(mode="after")
    def validate_range(self) -> Self:
        if self.start_date >= self.end_date_exclusive:
            raise ValueError("repair range must be non-empty")
        return self


class RepairRequest(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.market-data.repair-request"] = "osca.market-data.repair-request"
    version: Literal["1.0.0"] = "1.0.0"
    request_id: UUID = Field(default_factory=uuid4)
    instrument_id: UUID
    ranges: tuple[RepairRange, ...] = Field(min_length=1)
    provider_ids: tuple[Identifier, ...] = ()
    idempotency_key: Identifier

    @model_validator(mode="after")
    def validate_disjoint_ranges(self) -> Self:
        ordered = tuple(sorted(self.ranges, key=lambda item: item.start_date))
        if any(
            current.start_date < previous.end_date_exclusive
            for previous, current in zip(ordered, ordered[1:], strict=False)
        ):
            raise ValueError("repair ranges must not overlap")
        return self


class DateFinding(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.data-quality.finding"] = "osca.data-quality.finding"
    version: Literal["1.0.0"] = "1.0.0"
    finding_id: UUID = Field(default_factory=uuid4)
    instrument_id: UUID
    effective_date: date
    classification: DateClassification
    reason: Identifier
    repair_eligible: bool


class CanonicalDailyBar(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.market-data.daily-bar"] = "osca.market-data.daily-bar"
    version: Literal["1.0.0"] = "1.0.0"
    instrument_id: UUID
    interval: Literal["1d"] = "1d"
    effective_date: date
    source_timestamp: datetime
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

    @field_validator("open", "high", "low", "close", "volume", mode="before")
    @classmethod
    def reject_binary_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("canonical decimals cannot originate from binary float")
        return value

    @model_validator(mode="after")
    def validate_semantics(self) -> Self:
        if self.source_timestamp.tzinfo is None:
            raise ValueError("source_timestamp must be timezone-aware")
        if self.source_timestamp.utcoffset() != UTC.utcoffset(self.source_timestamp):
            raise ValueError("source_timestamp must be UTC")
        if self.volume < 0:
            raise ValueError("volume must be non-negative")
        if min(self.open, self.close, self.low) < 0:
            raise ValueError("prices must be non-negative")
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("high must not be below OHLC values")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("low must not be above OHLC values")
        return self


class DatasetManifest(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.market-data.dataset-manifest"] = (
        "osca.market-data.dataset-manifest"
    )
    version: Literal["1.0.0"] = "1.0.0"
    manifest_id: UUID = Field(default_factory=uuid4)
    dataset_id: UUID = Field(default_factory=uuid4)
    revision: int = Field(ge=1)
    fingerprint: Annotated[str, Field(pattern=r"^sha256:[0-9a-f]{64}$")]
    layer: DatasetLayer
    state: ManifestState = ManifestState.STAGING
    instrument_id: UUID
    provider_id: Identifier
    source_context: Identifier
    start_date: date
    end_date_exclusive: date
    schema_revision: Identifier
    row_count: int = Field(ge=0)
    byte_size: int = Field(ge=0)
    content_digest: Annotated[str, Field(pattern=r"^sha256:[0-9a-f]{64}$")]
    object_key: Annotated[str, Field(min_length=1, max_length=512)]
    source_evidence: tuple[UUID, ...] = ()
    previous_revisions: tuple[UUID, ...] = ()
    retention_policy_revision: Identifier
    backup_permitted: bool
    protected: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_range_and_protection(self) -> Self:
        if self.start_date >= self.end_date_exclusive:
            raise ValueError("manifest range must be non-empty")
        if self.layer is DatasetLayer.CANONICAL and not self.protected:
            raise ValueError("accepted canonical history must be protected in M2")
        return self


def canonical_fingerprint(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()
