from __future__ import annotations

from collections.abc import Iterator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from osca.bootstrap.authorization import local_authorization_context
from osca.bootstrap.workflow import workflow_service
from osca.security.api import AuthorizationContext
from osca.shared_kernel.api import CorrelationId
from osca.workflow.api import (
    CancelDiagnosticRun,
    DiagnosticInput,
    DiagnosticRun,
    DiagnosticRunId,
    GetDiagnosticRun,
    ListDiagnosticRuns,
    SubmitDiagnosticRun,
)
from osca.workflow.application import WorkflowService
from osca.workflow.application.handlers import AuthorizationDenied, IdempotencyConflict, RunNotFound

router = APIRouter(prefix="/api/v1/diagnostic-runs", tags=["diagnostic-runs"])


def service_dependency() -> Iterator[WorkflowService]:
    with workflow_service() as service:
        yield service


Service = Annotated[WorkflowService, Depends(service_dependency)]
Authorization = Annotated[AuthorizationContext, Depends(local_authorization_context)]


class SubmitDiagnosticRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    idempotency_key: str = Field(min_length=1, max_length=200)
    input: DiagnosticInput


@router.post("", response_model=DiagnosticRun, status_code=201)
def submit(
    request: SubmitDiagnosticRequest,
    service: Service,
    authorization: Authorization,
) -> DiagnosticRun:
    try:
        return service.submit(
            SubmitDiagnosticRun(
                authorization=authorization,
                correlation_id=CorrelationId.new(),
                idempotency_key=request.idempotency_key,
                input=request.input,
            )
        )
    except (AuthorizationDenied, IdempotencyConflict) as error:
        status = 403 if isinstance(error, AuthorizationDenied) else 409
        raise HTTPException(
            status_code=status,
            detail={
                "code": "workflow.authorization_denied"
                if status == 403
                else "workflow.idempotency_conflict"
            },
        ) from error


@router.get("", response_model=list[DiagnosticRun])
def list_runs(
    service: Service, authorization: Authorization, limit: int = 100
) -> tuple[DiagnosticRun, ...]:
    return service.list(ListDiagnosticRuns(authorization=authorization, limit=limit))


@router.get("/{run_id}", response_model=DiagnosticRun)
def get_run(run_id: UUID, service: Service, authorization: Authorization) -> DiagnosticRun:
    try:
        return service.get(
            GetDiagnosticRun(authorization=authorization, run_id=DiagnosticRunId(value=run_id))
        )
    except RunNotFound as error:
        raise HTTPException(status_code=404, detail={"code": "workflow.run_not_found"}) from error


@router.post("/{run_id}/cancel", response_model=DiagnosticRun)
def cancel_run(run_id: UUID, service: Service, authorization: Authorization) -> DiagnosticRun:
    try:
        return service.cancel(
            CancelDiagnosticRun(
                authorization=authorization,
                correlation_id=CorrelationId.new(),
                run_id=DiagnosticRunId(value=run_id),
            )
        )
    except RunNotFound as error:
        raise HTTPException(status_code=404, detail={"code": "workflow.run_not_found"}) from error
