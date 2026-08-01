from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from osca.quantitative_analysis import QuantitativeAnalysisRequest, analyze_dataset

_MAX_ROWS = Query(default=50_000, ge=2, le=50_000)


def quantitative_router() -> APIRouter:
    router = APIRouter()

    @router.get("/api/quantitative-analysis")
    def quantitative_analysis(
        payload_path: Path,
        dataset_revision_id: UUID,
        symbol: str,
        timeframe: str,
        start: datetime | None = None,
        end: datetime | None = None,
        periods_per_year: int = 252,
        risk_free_rate: float = 0.0,
        confidence_level: float = 0.95,
        rsi_window: int = 14,
        atr_window: int = 14,
        bollinger_window: int = 20,
        fast_window: int = 12,
        slow_window: int = 26,
        signal_window: int = 9,
    ) -> dict[str, object]:
        del _MAX_ROWS
        try:
            result = analyze_dataset(
                QuantitativeAnalysisRequest(
                    dataset_revision_id=dataset_revision_id,
                    payload_path=payload_path,
                    symbol=symbol,
                    timeframe=timeframe,
                    start=start,
                    end=end,
                    periods_per_year=periods_per_year,
                    risk_free_rate=risk_free_rate,
                    confidence_level=confidence_level,
                    rsi_window=rsi_window,
                    atr_window=atr_window,
                    bollinger_window=bollinger_window,
                    fast_window=fast_window,
                    slow_window=slow_window,
                    signal_window=signal_window,
                )
            )
        except (FileNotFoundError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return result.model_dump(mode="json")

    return router
