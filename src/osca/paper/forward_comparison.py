"""Descriptive D9 comparison evidence between retained backtests and forward runs."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ComparisonMetric(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    backtest_value: Decimal
    forward_value: Decimal
    unit: str
    methodology: str

    @field_validator("name", "unit", "methodology")
    @classmethod
    def validate_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized or len(normalized) > 300:
            raise ValueError("comparison metric text must be between 1 and 300 characters")
        return normalized

    @property
    def delta(self) -> Decimal:
        return self.forward_value - self.backtest_value


class ForwardBacktestComparison(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.paper.backtest-forward-comparison"] = (
        "osca.paper.backtest-forward-comparison"
    )
    version: Literal["1.0.0"] = "1.0.0"
    comparison_id: UUID = Field(default_factory=uuid4)
    backtest_result_id: int = Field(ge=1)
    paper_run_id: UUID
    strategy_version_id: int = Field(ge=1)
    assumption_id: UUID
    backtest_started_at: datetime
    backtest_ended_at: datetime
    forward_started_at: datetime
    forward_ended_at: datetime
    metrics: tuple[ComparisonMetric, ...] = Field(min_length=1)
    methodology_differences: tuple[str, ...] = Field(min_length=1)
    research_only: Literal[True] = True
    compared_at: datetime

    @field_validator(
        "backtest_started_at",
        "backtest_ended_at",
        "forward_started_at",
        "forward_ended_at",
        "compared_at",
    )
    @classmethod
    def validate_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("comparison timestamps must be timezone-aware")
        return value

    @field_validator("methodology_differences")
    @classmethod
    def validate_methodology(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(item.strip() for item in value)
        if any(not item or len(item) > 500 for item in normalized):
            raise ValueError("methodology differences must be non-empty bounded text")
        return normalized

    @model_validator(mode="after")
    def validate_windows(self) -> Self:
        if self.backtest_started_at >= self.backtest_ended_at:
            raise ValueError("backtest comparison window must have positive duration")
        if self.forward_started_at >= self.forward_ended_at:
            raise ValueError("forward comparison window must have positive duration")
        if self.compared_at < self.forward_ended_at:
            raise ValueError("comparison cannot predate the retained forward window")
        return self


def build_forward_backtest_comparison(
    *,
    backtest_result_id: int,
    paper_run_id: UUID,
    strategy_version_id: int,
    assumption_id: UUID,
    backtest_started_at: datetime,
    backtest_ended_at: datetime,
    forward_started_at: datetime,
    forward_ended_at: datetime,
    metrics: tuple[ComparisonMetric, ...],
    methodology_differences: tuple[str, ...],
    compared_at: datetime,
) -> ForwardBacktestComparison:
    """Create explicit, non-prescriptive comparison evidence."""
    return ForwardBacktestComparison(
        backtest_result_id=backtest_result_id,
        paper_run_id=paper_run_id,
        strategy_version_id=strategy_version_id,
        assumption_id=assumption_id,
        backtest_started_at=backtest_started_at,
        backtest_ended_at=backtest_ended_at,
        forward_started_at=forward_started_at,
        forward_ended_at=forward_ended_at,
        metrics=metrics,
        methodology_differences=methodology_differences,
        compared_at=compared_at,
    )
