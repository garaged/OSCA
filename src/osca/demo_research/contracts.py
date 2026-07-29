from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from osca.local_data_import import LocalOHLCVTimeframe

Identifier = Annotated[str, Field(min_length=1, max_length=128)]
LocalPath = Annotated[str, Field(min_length=1, max_length=4096)]
Description = Annotated[str, Field(min_length=1, max_length=4096)]


class DemoResearchReportFormat(StrEnum):
    JSON = "json"
    MARKDOWN = "markdown"


class DemoWatchlistItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    symbol: Identifier
    timeframe: LocalOHLCVTimeframe


class DemoResearchRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.demo-research.request"] = "osca.demo-research.request"
    version: Literal["1.0.0"] = "1.0.0"
    request_id: UUID = Field(default_factory=uuid4)
    project_name: Identifier = "first-demo-research"
    payload_path: LocalPath
    symbol: Identifier
    timeframe: LocalOHLCVTimeframe
    report_format: DemoResearchReportFormat = DemoResearchReportFormat.MARKDOWN
    output_path: LocalPath | None = None
    include_ml: Literal[False] = False
    include_llm: Literal[False] = False
    include_live_provider_data: Literal[False] = False
    include_recommendations: Literal[False] = False


class DemoResearchMetricSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    bar_count: int = Field(ge=1)
    first_timestamp: datetime
    last_timestamp: datetime
    first_close: float
    latest_close: float
    total_return: float
    mean_period_return: float
    volatility: float
    max_drawdown: float
    simple_moving_average_3: float | None = None
    simple_moving_average_5: float | None = None


class DemoResearchQualitySummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    accepted_bar_count: int = Field(ge=1)
    rejected_bar_count: int = Field(default=0, ge=0)
    quality_findings: tuple[Description, ...] = ()


class DemoResearchReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.demo-research.report"] = "osca.demo-research.report"
    version: Literal["1.0.0"] = "1.0.0"
    request_id: UUID
    project_name: Identifier
    watchlist: tuple[DemoWatchlistItem, ...]
    metrics: DemoResearchMetricSummary
    quality_summary: DemoResearchQualitySummary
    observations: tuple[Description, ...]
    output_uri: LocalPath | None = None
    evidence_only: Literal[True] = True
    not_financial_advice: Literal[True] = True
    deferred_boundaries: dict[str, bool]
