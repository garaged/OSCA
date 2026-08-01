from __future__ import annotations

from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, HTTPException

from osca.ml_experiments import (
    ExperimentModel,
    ExperimentTask,
    MLExperimentRequest,
    run_experiment,
)


def ml_experiment_router() -> APIRouter:
    router = APIRouter()

    @router.get("/api/ml-experiment")
    def ml_experiment(
        payload_path: Path,
        dataset_revision_id: UUID,
        symbol: str,
        timeframe: str,
        task: ExperimentTask = ExperimentTask.REGRESSION,
        model: ExperimentModel = ExperimentModel.RIDGE,
        horizon: int = 1,
        feature_window: int = 5,
        embargo: int = 0,
        ridge_alpha: float = 1.0,
        iterations: int = 500,
    ) -> dict[str, object]:
        try:
            result = run_experiment(
                MLExperimentRequest(
                    dataset_revision_id=dataset_revision_id,
                    payload_path=payload_path,
                    symbol=symbol,
                    timeframe=timeframe,
                    task=task,
                    model=model,
                    horizon=horizon,
                    feature_window=feature_window,
                    embargo=embargo,
                    ridge_alpha=ridge_alpha,
                    iterations=iterations,
                )
            )
        except (FileNotFoundError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return result.model_dump(mode="json")

    return router
