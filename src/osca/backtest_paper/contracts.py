from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from osca.local_data_import import LocalOHLCVTimeframe

Identifier = Annotated[str, Field(min_length=1, max_length=128)]
LocalPath = Annotated[str, Field(min_length=1, max_length=4096)]
Description = Annotated[str, Field(min_length=1, max_length=4096)]


class BacktestPaperReportFormat(StrEnum):
    JSON = "json"
    MARKDOWN = "markdown"


class BuiltInStrategyId(StrEnum):
    SMA_TREND_LONG_ONLY = "sma-trend-long-only"


class StrategyHypothesis(BaseModel):
    model_config = ConfigDict(frozen=True)

    strategy_id: BuiltInStrategyId = BuiltInStrategyId.SMA_TREND_LONG_ONLY
    description: Description = (
        "Long-only trend-following strategy that enters when close is above SMA 3 "
        "and SMA 3 is above SMA 5, then exits to cash when the condition is false."
    )
    short_window: int = Field(default=3, ge=2)
    long_window: int = Field(default=5, ge=3)

    @model_validator(mode="after")
    def require_ordered_windows(
        self,
    ) -> StrategyHypothesis:
        if self.short_window >= self.long_window:
            raise ValueError("short_window must be less than long_window")
        return self


class BacktestPaperRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.backtest-paper.request"] = "osca.backtest-paper.request"
    version: Literal["1.0.0"] = "1.0.0"
    request_id: UUID = Field(default_factory=uuid4)
    project_name: Identifier = "p8-backtest-paper-happy-path"
    payload_path: LocalPath
    symbol: Identifier
    timeframe: LocalOHLCVTimeframe
    initial_cash: float = Field(default=10_000.0, gt=0)
    report_format: BacktestPaperReportFormat = BacktestPaperReportFormat.MARKDOWN
    output_path: LocalPath | None = None
    strategy: StrategyHypothesis = Field(default_factory=StrategyHypothesis)
    enable_live_paper_broker: Literal[False] = False
    enable_autonomous_execution: Literal[False] = False
    enable_real_orders: Literal[False] = False
    include_recommendations: Literal[False] = False


class BacktestTrade(BaseModel):
    model_config = ConfigDict(frozen=True)

    timestamp: datetime
    action: Literal["buy", "sell"]
    price: float = Field(gt=0)
    units: float = Field(gt=0)
    cash_after: float = Field(ge=0)
    position_units_after: float = Field(ge=0)
    reason: Description


class BacktestSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    strategy_id: BuiltInStrategyId
    bars_processed: int = Field(ge=1)
    signal_bar_count: int = Field(ge=0)
    initial_cash: float = Field(gt=0)
    final_equity: float = Field(ge=0)
    total_return: float
    max_drawdown: float
    trade_count: int = Field(ge=0)
    exposure_bar_count: int = Field(ge=0)
    buy_and_hold_return: float
    trades: tuple[BacktestTrade, ...]


class PaperEvaluationRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    paper_run_id: UUID = Field(default_factory=uuid4)
    linked_request_id: UUID
    approved_for_forward_paper: Literal[True] = True
    paper_account_mode: Literal["local-evidence-only"] = "local-evidence-only"
    broker_integration_enabled: Literal[False] = False
    autonomous_execution_enabled: Literal[False] = False
    real_orders_enabled: Literal[False] = False
    comparison_summary: Description
    retained_evidence_uris: tuple[LocalPath, ...] = ()


class BacktestPaperReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.backtest-paper.report"] = "osca.backtest-paper.report"
    version: Literal["1.0.0"] = "1.0.0"
    request_id: UUID
    project_name: Identifier
    symbol: Identifier
    timeframe: LocalOHLCVTimeframe
    strategy: StrategyHypothesis
    backtest: BacktestSummary
    paper_evaluation: PaperEvaluationRecord
    observations: tuple[Description, ...]
    output_uri: LocalPath | None = None
    evidence_only: Literal[True] = True
    not_financial_advice: Literal[True] = True
    deferred_boundaries: dict[str, bool]
