from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from osca.workflow.api import (
    DiagnosticCheckpoint,
    DiagnosticResult,
    DiagnosticRun,
    DiagnosticRunError,
    DiagnosticRunState,
)
from osca.workflow.application.handlers import ConcurrentTransition, WorkflowService
from osca.workflow.application.ports import (
    DiagnosticRunRepository,
    NullWorkflowObserver,
    WorkflowEventObserver,
)


class UnsupportedCheckpoint(ValueError):
    pass


class DiagnosticHandler:
    phases = ("validate", "probe", "publish")

    def advance(self, run: DiagnosticRun) -> DiagnosticRun:
        checkpoint = run.checkpoint or DiagnosticCheckpoint(phase=0)
        if (
            checkpoint.family != "osca.workflow.diagnostic-checkpoint"
            or not checkpoint.version.startswith("1.")
        ):
            raise UnsupportedCheckpoint(checkpoint.version)
        if checkpoint.phase >= len(self.phases):
            return run
        name = self.phases[checkpoint.phase]
        completed = checkpoint.completed_phases
        if name not in completed:
            completed += (name,)
        return run.model_copy(
            update={
                "checkpoint": checkpoint.model_copy(
                    update={"phase": checkpoint.phase + 1, "completed_phases": completed}
                )
            }
        )


class EmbeddedExecutor:
    def __init__(
        self,
        repository: DiagnosticRunRepository,
        *,
        owner: str,
        lease_seconds: int = 30,
        max_attempts: int = 3,
        observer: WorkflowEventObserver | None = None,
    ) -> None:
        self._observer = observer or NullWorkflowObserver()
        self._repository, self._service = repository, WorkflowService(repository, self._observer)
        self._handler, self._owner = DiagnosticHandler(), owner
        self._lease_seconds, self._max_attempts, self._stopping = lease_seconds, max_attempts, False

    def stop(self) -> None:
        self._stopping = True

    def claim(self, now: datetime | None = None) -> DiagnosticRun | None:
        current = now or datetime.now(UTC)
        run = self._repository.claim(
            self._owner, current, current + timedelta(seconds=self._lease_seconds)
        )
        if run is not None:
            self._observer.record("claimed", run)
        return run

    def heartbeat(self, run: DiagnosticRun, now: datetime | None = None) -> DiagnosticRun:
        if run.state != DiagnosticRunState.RUNNING or run.lease_owner != self._owner:
            raise ConcurrentTransition("heartbeat requires the active lease")
        current = now or datetime.now(UTC)
        changed = run.model_copy(
            update={
                "lease_expires_at": current + timedelta(seconds=self._lease_seconds),
                "revision": run.revision + 1,
                "updated_at": current,
            }
        )
        if not self._repository.replace(changed, run.revision):
            raise ConcurrentTransition(str(run.run_id.value))
        self._observer.record("heartbeat", changed)
        return changed

    def execute(self, run: DiagnosticRun) -> DiagnosticRun:
        if self._stopping:
            return self._service.transition(run, DiagnosticRunState.INTERRUPTED)
        if run.state == DiagnosticRunState.CANCELLING:
            return self._service.transition(run, DiagnosticRunState.CANCELLED)
        current = run
        try:
            while (current.checkpoint or DiagnosticCheckpoint(phase=0)).phase < len(
                self._handler.phases
            ):
                advanced = self._handler.advance(current).model_copy(
                    update={"revision": current.revision + 1, "updated_at": datetime.now(UTC)}
                )
                if not self._repository.replace(advanced, current.revision):
                    raise ConcurrentTransition(str(run.run_id.value))
                self._observer.record("checkpoint", advanced)
                current = advanced
        except UnsupportedCheckpoint:
            error = DiagnosticRunError(
                code="checkpoint.incompatible",
                message="Checkpoint major version is unsupported",
            )
            return self._service.transition(run, DiagnosticRunState.BLOCKED, error=error)
        with_result = current.model_copy(
            update={"result": DiagnosticResult(result_id=uuid4()), "revision": current.revision + 1}
        )
        if not self._repository.replace(with_result, current.revision):
            raise ConcurrentTransition(str(run.run_id.value))
        return self._service.transition(with_result, DiagnosticRunState.SUCCEEDED)

    def fail(
        self, run: DiagnosticRun, error: DiagnosticRunError, now: datetime | None = None
    ) -> DiagnosticRun:
        current = now or datetime.now(UTC)
        if error.retryable and run.attempt < self._max_attempts:
            interrupted = self._service.transition(run, DiagnosticRunState.INTERRUPTED, error=error)
            pending = self._service.transition(interrupted, DiagnosticRunState.PENDING)
            scheduled = pending.model_copy(
                update={
                    "next_attempt_at": current + timedelta(seconds=2 ** max(run.attempt - 1, 0)),
                    "revision": pending.revision + 1,
                }
            )
            if not self._repository.replace(scheduled, pending.revision):
                raise ConcurrentTransition(str(run.run_id.value))
            self._observer.record("retry_scheduled", scheduled)
            return scheduled
        return self._service.transition(run, DiagnosticRunState.FAILED, error=error)

    def recover_expired(self, now: datetime | None = None) -> tuple[DiagnosticRun, ...]:
        current, recovered = now or datetime.now(UTC), []
        for run in self._repository.list((DiagnosticRunState.RUNNING,), 500):
            if run.lease_expires_at is not None and run.lease_expires_at <= current:
                recovered.append(self._service.transition(run, DiagnosticRunState.INTERRUPTED))
        return tuple(recovered)

    def resume(self, run: DiagnosticRun) -> DiagnosticRun:
        """Apply the local policy decision that makes interrupted work claimable again."""
        if run.state != DiagnosticRunState.INTERRUPTED:
            raise ConcurrentTransition("only interrupted work can be resumed")
        resumed = self._service.transition(run, DiagnosticRunState.PENDING)
        self._observer.record("recovery_resumed", resumed)
        return resumed
