from __future__ import annotations

from datetime import UTC, datetime

from osca.workflow.api import (
    CancelDiagnosticRun,
    DiagnosticRun,
    DiagnosticRunError,
    DiagnosticRunState,
    GetDiagnosticRun,
    ListDiagnosticRuns,
    SubmitDiagnosticRun,
)
from osca.workflow.application.ports import (
    DiagnosticRunRepository,
    NullWorkflowObserver,
    WorkflowEventObserver,
)
from osca.workflow.domain import require_transition


class IdempotencyConflict(ValueError):
    pass


class RunNotFound(LookupError):
    pass


class ConcurrentTransition(RuntimeError):
    pass


class MissingResult(ValueError):
    pass


class WorkflowService:
    def __init__(
        self,
        repository: DiagnosticRunRepository,
        observer: WorkflowEventObserver | None = None,
    ) -> None:
        self._repository = repository
        self._observer = observer or NullWorkflowObserver()

    def submit(self, command: SubmitDiagnosticRun) -> DiagnosticRun:
        existing = self._repository.find_idempotent(command.actor, command.idempotency_key)
        if existing is not None:
            if existing.input.model_dump(mode="json") != command.input.model_dump(mode="json"):
                raise IdempotencyConflict("idempotency key is already bound to different input")
            return existing
        run = DiagnosticRun(
            actor=command.actor,
            correlation_id=command.correlation_id,
            idempotency_key=command.idempotency_key,
            input=command.input,
        )
        self._repository.add(run)
        self._observer.record("submitted", run)
        return run

    def cancel(self, command: CancelDiagnosticRun) -> DiagnosticRun:
        run = self.get(GetDiagnosticRun(run_id=command.run_id))
        if run.state in {
            DiagnosticRunState.SUCCEEDED,
            DiagnosticRunState.FAILED,
            DiagnosticRunState.CANCELLED,
        }:
            return run
        target = (
            DiagnosticRunState.CANCELLED
            if run.state in {DiagnosticRunState.PENDING, DiagnosticRunState.BLOCKED}
            else DiagnosticRunState.CANCELLING
        )
        cancelled = self._transition(run, target)
        self._observer.record("cancellation_requested", cancelled)
        return cancelled

    def get(self, query: GetDiagnosticRun) -> DiagnosticRun:
        run = self._repository.get(query.run_id)
        if run is None:
            raise RunNotFound(str(query.run_id.value))
        return run

    def list(self, query: ListDiagnosticRuns) -> tuple[DiagnosticRun, ...]:
        return self._repository.list(query.states, query.limit)

    def transition(
        self,
        run: DiagnosticRun,
        state: DiagnosticRunState,
        *,
        error: DiagnosticRunError | None = None,
        **updates: object,
    ) -> DiagnosticRun:
        return self._transition(run, state, error=error, **updates)

    def _transition(
        self, run: DiagnosticRun, state: DiagnosticRunState, **updates: object
    ) -> DiagnosticRun:
        if state == DiagnosticRunState.SUCCEEDED and run.result is None:
            raise MissingResult("succeeded requires a durable result reference")
        require_transition(run.state, state)
        changed = run.model_copy(
            update={
                "state": state,
                "revision": run.revision + 1,
                "updated_at": datetime.now(UTC),
                **updates,
            }
        )
        if not self._repository.replace(changed, run.revision):
            raise ConcurrentTransition(str(run.run_id.value))
        outcome = "failed" if state == DiagnosticRunState.FAILED else "succeeded"
        self._observer.record("transition", changed, outcome)
        return changed
