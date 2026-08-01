from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from pathlib import Path
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DerivedSeriesKind(StrEnum):
    SIMPLE_RETURN = "simple_return"
    LOG_RETURN = "log_return"
    SMA = "sma"
    EMA = "ema"
    ROLLING_VOLATILITY = "rolling_volatility"
    ROLLING_VOLUME = "rolling_volume"


class DownsamplingMethod(StrEnum):
    NONE = "none"
    EVENLY_SPACED = "evenly_spaced"


class DerivedSeriesRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    kind: DerivedSeriesKind
    window: int | None = Field(default=None, ge=2, le=10_000)

    @model_validator(mode="after")
    def validate_window(self) -> DerivedSeriesRequest:
        needs_window = self.kind in {
            DerivedSeriesKind.SMA,
            DerivedSeriesKind.EMA,
            DerivedSeriesKind.ROLLING_VOLATILITY,
            DerivedSeriesKind.ROLLING_VOLUME,
        }
        if needs_window and self.window is None:
            raise ValueError(f"{self.kind.value} requires a window")
        if not needs_window and self.window is not None:
            raise ValueError(f"{self.kind.value} does not accept a window")
        return self


class ChartSeriesRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    dataset_revision_id: UUID
    payload_path: Path
    symbol: str
    timeframe: str
    start: datetime | None = None
    end: datetime | None = None
    max_rows: int = Field(default=2_000, ge=2, le=50_000)
    derived: tuple[DerivedSeriesRequest, ...] = ()

    @model_validator(mode="after")
    def validate_range(self) -> ChartSeriesRequest:
        if self.start is not None and self.end is not None and self.start > self.end:
            raise ValueError("start must be less than or equal to end")
        return self


class ChartRow(BaseModel):
    model_config = ConfigDict(frozen=True)

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    complete: bool = True
    derived: dict[str, float | None] = Field(default_factory=dict)


class DerivedSeriesEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    series_id: str
    kind: DerivedSeriesKind
    window: int | None
    warmup_rows: int
    point_in_time_safe: bool
    input_digest: str
    output_digest: str


class ChartSeriesResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    dataset_revision_id: UUID
    payload_path: str
    symbol: str
    timeframe: str
    source_row_count: int
    filtered_row_count: int
    returned_row_count: int
    first_timestamp: datetime
    last_timestamp: datetime
    downsampling_method: DownsamplingMethod
    downsampling_preserves_first_last: bool
    rows: tuple[ChartRow, ...]
    derived_evidence: tuple[DerivedSeriesEvidence, ...]
    payload_sha256: str
    network_used: bool = False
    credentials_used: bool = False
    recommendations_enabled: bool = False
    broker_execution_enabled: bool = False
    real_capital_enabled: bool = False
