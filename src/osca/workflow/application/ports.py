from __future__ import annotations

from datetime import datetime
from typing import Protocol

from osca.workflow.api import DiagnosticRun, DiagnosticRunId, DiagnosticRunState


class DiagnosticRunRepository(Protocol):
    def add(self, run: DiagnosticRun) -> None: ...
    def get(self, run_id: DiagnosticRunId) -> DiagnosticRun | None: ...
    def find_idempotent(self, actor: str, key: str) -> DiagnosticRun | None: ...
    def list(
        self, states: tuple[DiagnosticRunState, ...], limit: int
    ) -> tuple[DiagnosticRun, ...]: ...
    def replace(self, run: DiagnosticRun, expected_revision: int) -> bool: ...
    def claim(self, owner: str, now: datetime, lease_until: datetime) -> DiagnosticRun | None: ...


class WorkflowEventObserver(Protocol):
    def record(self, action: str, run: DiagnosticRun, outcome: str = "succeeded") -> None: ...


class NullWorkflowObserver:
    def record(self, action: str, run: DiagnosticRun, outcome: str = "succeeded") -> None:
        pass
