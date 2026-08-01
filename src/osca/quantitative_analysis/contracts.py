from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class QuantitativeAnalysisRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    dataset_revision_id: UUID
    payload_path: Path
    symbol: str
    timeframe: str
    start: datetime | None = None
    end: datetime | None = None
    periods_per_year: int = Field(default=252, ge=1, le=525_600)
    risk_free_rate: float = 0.0
    confidence_level: float = Field(default=0.95, gt=0.5, lt=1.0)
    rsi_window: int = Field(default=14, ge=2, le=10_000)
    atr_window: int = Field(default=14, ge=2, le=10_000)
    bollinger_window: int = Field(default=20, ge=2, le=10_000)
    bollinger_stddevs: float = Field(default=2.0, gt=0.0, le=10.0)
    fast_window: int = Field(default=12, ge=2, le=10_000)
    slow_window: int = Field(default=26, ge=3, le=10_000)
    signal_window: int = Field(default=9, ge=2, le=10_000)

    @model_validator(mode="after")
    def validate_windows(self) -> QuantitativeAnalysisRequest:
        if self.fast_window >= self.slow_window:
            raise ValueError("fast_window must be less than slow_window")
        if self.start is not None and self.end is not None and self.start > self.end:
            raise ValueError("start must be less than or equal to end")
        return self


class QuantitativeAnalysisPoint(BaseModel):
    model_config = ConfigDict(frozen=True)

    timestamp: datetime
    close: float
    simple_return: float | None
    cumulative_return: float | None
    drawdown: float
    rsi: float | None
    roc: float | None
    macd: float | None
    macd_signal: float | None
    macd_histogram: float | None
    atr: float | None
    bollinger_middle: float | None
    bollinger_upper: float | None
    bollinger_lower: float | None
    obv: float
    trend_regime: str
    volatility_regime: str


class QuantitativeSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    observation_count: int
    return_count: int
    total_return: float | None
    annualized_return: float | None
    annualized_volatility: float | None
    downside_volatility: float | None
    sharpe_ratio: float | None
    sortino_ratio: float | None
    maximum_drawdown: float
    maximum_drawdown_duration: int
    historical_var: float | None
    historical_cvar: float | None
    mean_return: float | None
    median_return: float | None
    standard_deviation: float | None
    skewness: float | None
    excess_kurtosis: float | None
    minimum_return: float | None
    maximum_return: float | None
    q05: float | None
    q25: float | None
    q75: float | None
    q95: float | None
    autocorrelation_lag1: float | None
    outlier_count: int


class QuantitativeAnalysisResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    dataset_revision_id: UUID
    payload_path: str
    payload_sha256: str
    symbol: str
    timeframe: str
    first_timestamp: datetime
    last_timestamp: datetime
    summary: QuantitativeSummary
    points: tuple[QuantitativeAnalysisPoint, ...]
    parameters: dict[str, float | int]
    assumptions: tuple[str, ...]
    findings: tuple[str, ...]
    input_digest: str
    output_digest: str
    point_in_time_safe: bool = True
    network_used: bool = False
    credentials_used: bool = False
    recommendations_enabled: bool = False
    broker_execution_enabled: bool = False
    real_capital_enabled: bool = False


class DatasetComparisonRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    primary: QuantitativeAnalysisRequest
    benchmark: QuantitativeAnalysisRequest
    rolling_window: int = Field(default=20, ge=2, le=10_000)


class DatasetComparisonPoint(BaseModel):
    model_config = ConfigDict(frozen=True)

    timestamp: datetime
    primary_return: float
    benchmark_return: float
    rolling_correlation: float | None


class DatasetComparisonResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    primary_revision_id: UUID
    benchmark_revision_id: UUID
    aligned_return_count: int
    correlation: float | None
    beta: float | None
    points: tuple[DatasetComparisonPoint, ...]
    assumptions: tuple[str, ...]
    input_digest: str
    output_digest: str
    point_in_time_safe: bool = True
