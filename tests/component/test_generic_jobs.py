from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from osca.market_data.api import RetrievalRequest
from osca.market_data.application import MarketDataJobService
from osca.operations.api import AuditRecord, WorkflowJobEvent
from osca.security.api import AuthorizationContext, Capability
from osca.shared_kernel.api import CorrelationId
from osca.workflow.api import CancelJob, JobResultReference, JobState, SubmitJob
from osca.workflow.application import JobService
from osca.workflow.application.handlers import IdempotencyConflict
from osca.workflow.infrastructure import SqliteJobRepository, WorkflowBase


def authorization(*capabilities: Capability) -> AuthorizationContext:
    return AuthorizationContext(
        actor="local-owner",
        capabilities=frozenset(capabilities),
        authentication_method="local-os-user",
    )


class RecordingAudit:
    def __init__(self) -> None:
        self.records: list[AuditRecord] = []

    def add(self, record: AuditRecord) -> None:
        self.records.append(record)


class RecordingEvents:
    def __init__(self) -> None:
        self.events: list[WorkflowJobEvent] = []

    def add(self, event: WorkflowJobEvent) -> None:
        self.events.append(event)


def submit_command(payload: dict[str, object]) -> SubmitJob:
    return SubmitJob(
        authorization=authorization(Capability.JOB_SUBMIT),
        correlation_id=CorrelationId.new(),
        kind="market-data.retrieve",
        idempotency_key="retrieve-1",
        input_family="osca.market-data.retrieval-request",
        input_version="1.0.0",
        input_payload=payload,
    )


def test_generic_job_is_durable_idempotent_claimable_and_completable() -> None:
    engine = create_engine("sqlite://")
    WorkflowBase.metadata.create_all(engine)
    with Session(engine) as session, session.begin():
        repository = SqliteJobRepository(session)
        service = JobService(repository)
        command = submit_command({"instrument_id": "fixture", "range": "2024-01"})
        submitted = service.submit(command)
        assert submitted.verify_input()
        assert service.submit(command) == submitted
        with pytest.raises(IdempotencyConflict):
            service.submit(submit_command({"instrument_id": "different"}))
        now = datetime.now(UTC)
        claimed = repository.claim_job("worker-1", now, now + timedelta(seconds=30))
        assert claimed is not None
        assert claimed.state is JobState.RUNNING
        assert claimed.attempt == 1
        completed = service.transition(
            claimed,
            JobState.SUCCEEDED,
            result=JobResultReference(
                family="osca.market-data.dataset-manifest",
                reference_id=claimed.job_id,
            ),
        )
        assert completed.state is JobState.SUCCEEDED


def test_pending_job_can_be_cancelled_without_execution() -> None:
    engine = create_engine("sqlite://")
    WorkflowBase.metadata.create_all(engine)
    with Session(engine) as session, session.begin():
        service = JobService(SqliteJobRepository(session))
        submitted = service.submit(submit_command({"instrument_id": "fixture"}))
        cancelled = service.cancel(
            CancelJob(
                authorization=authorization(Capability.JOB_CANCEL),
                job_id=submitted.job_id,
            )
        )
        assert cancelled.state is JobState.CANCELLED


def test_market_data_submission_requires_domain_and_generic_job_capabilities() -> None:
    engine = create_engine("sqlite://")
    WorkflowBase.metadata.create_all(engine)
    request = RetrievalRequest(
        instrument_id=uuid4(),
        start_date=date(2024, 1, 1),
        end_date_exclusive=date(2024, 1, 2),
        maximum_age_seconds=3600,
        idempotency_key="market-retrieve-1",
    )
    with Session(engine) as session, session.begin():
        audit = RecordingAudit()
        events = RecordingEvents()
        service = MarketDataJobService(
            JobService(SqliteJobRepository(session)), audit, events
        )
        context = authorization(Capability.JOB_SUBMIT, Capability.MARKET_DATA_RETRIEVE)
        job = service.submit_retrieval(context, CorrelationId.new(), request)
        assert job.kind == "market-data.retrieve"
        assert job.input_family == request.family
        assert audit.records[0].target_id == str(job.job_id)
        assert events.events[0].run_id == job.job_id
        assert events.events[0].action == "market-data.retrieve.submit"
