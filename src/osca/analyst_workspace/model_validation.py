from __future__ import annotations

from fastapi import APIRouter, HTTPException

from osca.model_validation import ModelValidationRequest, validate_model_research


def model_validation_router() -> APIRouter:
    router = APIRouter()

    @router.post("/api/model-validation/run")
    def run_validation(request: ModelValidationRequest) -> dict[str, object]:
        try:
            result = validate_model_research(request)
        except (FileNotFoundError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return result.model_dump(mode="json")

    return router
