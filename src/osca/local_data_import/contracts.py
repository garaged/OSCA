from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Identifier = Annotated[str, Field(min_length=1, max_length=128)]
Description = Annotated[str, Field(min_length=1, max_length=2048)]


class LocalOHLCVTimeframe(StrEnum):
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"
    ONE_DAY = "1d"


class LocalOHLCVImportFormat(StrEnum):
    CSV = "csv"
    PARQUET = "parquet"


class LocalOHLCVQualitySeverity(StrEnum):
    WARNING = "warning"
    ERROR = "error"


class LocalOHLCVQualityFinding(BaseModel):
    model_config = ConfigDict(frozen=True)

    finding_id: Identifier
    severity: LocalOHLCVQualitySeverity
    message: Description
    row_number: int | None = Field(default=None, ge=1)


class LocalOHLCVBar(BaseModel):
    model_config = ConfigDict(frozen=True)

    timestamp: datetime
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: float = Field(ge=0)

    @field_validator("timestamp")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("OHLCV timestamps must include timezone information")
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def validate_ohlc_relationship(self) -> Self:
        if self.high < max(self.open, self.low, self.close):
            raise ValueError("OHLCV high must be greater than or equal to open, low, and close")
        if self.low > min(self.open, self.high, self.close):
            raise ValueError("OHLCV low must be less than or equal to open, high, and close")
        return self


class LocalOHLCVImportRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.local-ohlcv-import.request"] = "osca.local-ohlcv-import.request"
    version: Literal["1.0.0"] = "1.0.0"
    request_id: UUID = Field(default_factory=uuid4)
    input_path: Identifier
    storage_root: Identifier
    symbol: Identifier
    timeframe: LocalOHLCVTimeframe
    input_format: LocalOHLCVImportFormat | None = None
    source_uri: Identifier = "local-file://user-supplied"
    calendar_assumption: Identifier = "source-provided"
    network_access_enabled: Literal[False] = False


class LocalOHLCVImportResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.local-ohlcv-import.result"] = "osca.local-ohlcv-import.result"
    version: Literal["1.0.0"] = "1.0.0"
    dataset_revision_id: UUID
    symbol: Identifier
    timeframe: LocalOHLCVTimeframe
    input_format: LocalOHLCVImportFormat
    row_count: int = Field(ge=1)
    first_timestamp: datetime
    last_timestamp: datetime
    source_sha256: Annotated[str, Field(min_length=64, max_length=64)]
    payload_uri: Identifier
    metadata_uri: Identifier
    calendar_assumption: Identifier
    quality_findings: tuple[LocalOHLCVQualityFinding, ...] = ()
    network_access_enabled: Literal[False] = False
    deferred_boundaries: dict[str, bool]
