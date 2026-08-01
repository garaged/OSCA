from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from osca.ml_experiments import MLExperimentResult
from osca.prediction_lab import diagnose_experiment


def prediction_lab_router() -> APIRouter:
    router = APIRouter()

    @router.post("/api/prediction-lab/diagnose")
    def diagnose(
        experiment: MLExperimentResult,
        calibration_bins: int = Query(default=10, ge=2, le=100),
    ) -> dict[str, object]:
        try:
            result = diagnose_experiment(experiment, calibration_bins=calibration_bins)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return result.model_dump(mode="json")

    return router
