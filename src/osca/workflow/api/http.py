from __future__ import annotations

from collections.abc import Iterator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from osca.bootstrap.workflow import workflow_service
from osca.shared_kernel.api import CorrelationId
from osca.workflow.api import (
    CancelDiagnosticRun,
    DiagnosticRun,
    DiagnosticRunId,
    GetDiagnosticRun,
    ListDiagnosticRuns,
    SubmitDiagnosticRun,
)
from osca.workflow.application import WorkflowService
from osca.workflow.application.handlers import IdempotencyConflict, RunNotFound

router = APIRouter(prefix="/api/v1/diagnostic-runs", tags=["diagnostic-runs"])


def service_dependency() -> Iterator[WorkflowService]:
    with workflow_service() as service:
        yield service


Service = Annotated[WorkflowService, Depends(service_dependency)]


@router.post("", response_model=DiagnosticRun, status_code=201)
def submit(command: SubmitDiagnosticRun, service: Service) -> DiagnosticRun:
    try:
        return service.submit(command)
    except IdempotencyConflict as error:
        raise HTTPException(
            status_code=409, detail={"code": "workflow.idempotency_conflict"}
        ) from error


@router.get("", response_model=list[DiagnosticRun])
def list_runs(service: Service, limit: int = 100) -> tuple[DiagnosticRun, ...]:
    return service.list(ListDiagnosticRuns(limit=limit))


@router.get("/{run_id}", response_model=DiagnosticRun)
def get_run(run_id: UUID, service: Service) -> DiagnosticRun:
    try:
        return service.get(GetDiagnosticRun(run_id=DiagnosticRunId(value=run_id)))
    except RunNotFound as error:
        raise HTTPException(status_code=404, detail={"code": "workflow.run_not_found"}) from error


@router.post("/{run_id}/cancel", response_model=DiagnosticRun)
def cancel_run(run_id: UUID, actor: str, service: Service) -> DiagnosticRun:
    try:
        return service.cancel(
            CancelDiagnosticRun(
                actor=actor,
                correlation_id=CorrelationId.new(),
                run_id=DiagnosticRunId(value=run_id),
            )
        )
    except RunNotFound as error:
        raise HTTPException(status_code=404, detail={"code": "workflow.run_not_found"}) from error
