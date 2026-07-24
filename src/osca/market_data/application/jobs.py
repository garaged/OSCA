from typing import Protocol

from osca.market_data.api import RepairRequest, RetrievalRequest
from osca.operations.api import AuditOutcome, AuditRecord, WorkflowJobEvent
from osca.security.api import AuthorizationContext, Capability
from osca.shared_kernel.api import CorrelationId
from osca.workflow.api import JobRun, SubmitJob
from osca.workflow.application import JobService
from osca.workflow.application.handlers import require_capability


class AuditSink(Protocol):
    def add(self, record: AuditRecord) -> None: ...


class EventSink(Protocol):
    def add(self, event: WorkflowJobEvent) -> None: ...


class MarketDataJobService:
    def __init__(
        self,
        jobs: JobService,
        audit: AuditSink,
        events: EventSink | None = None,
    ) -> None:
        self._jobs = jobs
        self._audit = audit
        self._events = events

    def submit_retrieval(
        self,
        authorization: AuthorizationContext,
        correlation_id: CorrelationId,
        request: RetrievalRequest,
    ) -> JobRun:
        require_capability(authorization, Capability.MARKET_DATA_RETRIEVE)
        job = self._jobs.submit(
            SubmitJob(
                authorization=authorization,
                correlation_id=correlation_id,
                kind="market-data.retrieve",
                idempotency_key=request.idempotency_key,
                input_family=request.family,
                input_version=request.version,
                input_payload=request.model_dump(mode="json"),
            )
        )
        self._record(authorization, correlation_id, job, "market-data.retrieve.submit")
        self._event(correlation_id, job, "market-data.retrieve.submit")
        return job

    def submit_repair(
        self,
        authorization: AuthorizationContext,
        correlation_id: CorrelationId,
        request: RepairRequest,
    ) -> JobRun:
        require_capability(authorization, Capability.MARKET_DATA_REPAIR)
        job = self._jobs.submit(
            SubmitJob(
                authorization=authorization,
                correlation_id=correlation_id,
                kind="market-data.repair",
                idempotency_key=request.idempotency_key,
                input_family=request.family,
                input_version=request.version,
                input_payload=request.model_dump(mode="json"),
            )
        )
        self._record(authorization, correlation_id, job, "market-data.repair.submit")
        self._event(correlation_id, job, "market-data.repair.submit")
        return job

    def _record(
        self,
        authorization: AuthorizationContext,
        correlation_id: CorrelationId,
        job: JobRun,
        action: str,
    ) -> None:
        self._audit.add(
            AuditRecord(
                correlation_id=correlation_id,
                actor=authorization.actor,
                action=action,
                target_type="workflow.job-run",
                target_id=str(job.job_id),
                outcome=AuditOutcome.SUCCEEDED,
                code="market_data_job_submitted",
                policy_version="ADR-0028",
            )
        )

    def _event(
        self,
        correlation_id: CorrelationId,
        job: JobRun,
        action: str,
    ) -> None:
        if self._events is None:
            return
        self._events.add(
            WorkflowJobEvent(
                correlation_id=correlation_id,
                run_id=job.job_id,
                action=action,
                state=job.state.value,
                attempt=job.attempt,
                outcome="succeeded",
            )
        )
