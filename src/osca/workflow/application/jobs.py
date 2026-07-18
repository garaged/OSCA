from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from osca.catalog.api import metadata_digest
from osca.security.api import Capability
from osca.workflow.api import CancelJob, GetJob, JobRun, JobState, SubmitJob
from osca.workflow.application.handlers import (
    AuthorizationDenied,
    ConcurrentTransition,
    IdempotencyConflict,
    RunNotFound,
    require_capability,
)


class JobRepository(Protocol):
    def add_job(self, job: JobRun) -> None: ...
    def get_job(self, job_id: UUID) -> JobRun | None: ...
    def find_job_idempotent(self, actor: str, kind: str, key: str) -> JobRun | None: ...
    def replace_job(self, job: JobRun, expected_revision: int) -> bool: ...


class JobService:
    def __init__(self, repository: JobRepository) -> None:
        self._repository = repository

    def submit(self, command: SubmitJob) -> JobRun:
        require_capability(command.authorization, Capability.JOB_SUBMIT)
        actor = command.authorization.actor
        existing = self._repository.find_job_idempotent(
            actor, command.kind, command.idempotency_key
        )
        digest = metadata_digest(command.input_payload)
        if existing is not None:
            if (
                existing.input_family != command.input_family
                or existing.input_version != command.input_version
                or existing.input_digest != digest
            ):
                raise IdempotencyConflict("job idempotency key is bound to different input")
            return existing
        job = JobRun(
            correlation_id=command.correlation_id,
            actor=actor,
            kind=command.kind,
            idempotency_key=command.idempotency_key,
            input_family=command.input_family,
            input_version=command.input_version,
            input_payload=command.input_payload,
            input_digest=digest,
        )
        self._repository.add_job(job)
        return job

    def get(self, query: GetJob) -> JobRun:
        require_capability(query.authorization, Capability.JOB_READ)
        return self._get(query.job_id)

    def cancel(self, command: CancelJob) -> JobRun:
        require_capability(command.authorization, Capability.JOB_CANCEL)
        job = self._get(command.job_id)
        if job.state in {JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED}:
            return job
        target = (
            JobState.CANCELLED
            if job.state in {JobState.PENDING, JobState.BLOCKED}
            else JobState.CANCELLING
        )
        return self.transition(job, target)

    def transition(self, job: JobRun, target: JobState, **updates: object) -> JobRun:
        _require_job_transition(job.state, target)
        changed = job.model_copy(
            update={
                "state": target,
                "revision": job.revision + 1,
                "updated_at": datetime.now(UTC),
                **updates,
            }
        )
        changed = JobRun.model_validate(changed)
        if not self._repository.replace_job(changed, job.revision):
            raise ConcurrentTransition(str(job.job_id))
        return changed

    def _get(self, job_id: UUID) -> JobRun:
        job = self._repository.get_job(job_id)
        if job is None:
            raise RunNotFound(str(job_id))
        return job


_JOB_TRANSITIONS: dict[JobState, frozenset[JobState]] = {
    JobState.PENDING: frozenset({JobState.RUNNING, JobState.CANCELLED}),
    JobState.RUNNING: frozenset(
        {
            JobState.BLOCKED,
            JobState.SUCCEEDED,
            JobState.FAILED,
            JobState.CANCELLING,
            JobState.INTERRUPTED,
        }
    ),
    JobState.BLOCKED: frozenset({JobState.PENDING, JobState.CANCELLED}),
    JobState.CANCELLING: frozenset({JobState.CANCELLED, JobState.INTERRUPTED}),
    JobState.INTERRUPTED: frozenset(
        {JobState.PENDING, JobState.FAILED, JobState.CANCELLED}
    ),
    JobState.SUCCEEDED: frozenset(),
    JobState.FAILED: frozenset(),
    JobState.CANCELLED: frozenset(),
}


def _require_job_transition(source: JobState, target: JobState) -> None:
    if target not in _JOB_TRANSITIONS[source]:
        raise ValueError(f"job transition {source.value}->{target.value} is prohibited")


__all__ = ["AuthorizationDenied", "JobRepository", "JobService"]
