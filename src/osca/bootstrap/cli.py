from __future__ import annotations

import json
from uuid import UUID

import typer

from osca.bootstrap.runtime import readiness_snapshot
from osca.bootstrap.workflow import workflow_service
from osca.shared_kernel.api import CorrelationId
from osca.workflow.api import (
    CancelDiagnosticRun,
    DiagnosticInput,
    DiagnosticRunId,
    GetDiagnosticRun,
    ListDiagnosticRuns,
    SubmitDiagnosticRun,
)

app = typer.Typer(no_args_is_help=True, help="OSCA operator command line.")


@app.callback()
def cli() -> None:
    """Operate and inspect a local or personal-server OSCA installation."""


@app.command()
def readiness() -> None:
    """Report the validated local readiness snapshot."""

    typer.echo(json.dumps(readiness_snapshot().model_dump(mode="json"), indent=2))


@app.command("diagnostic-submit")
def diagnostic_submit(probe: str, idempotency_key: str, actor: str = "operator") -> None:
    """Submit a durable versioned diagnostic run."""
    command = SubmitDiagnosticRun(
        actor=actor,
        correlation_id=CorrelationId.new(),
        idempotency_key=idempotency_key,
        input=DiagnosticInput(probe=probe),
    )
    with workflow_service() as service:
        run = service.submit(command)
    typer.echo(run.model_dump_json(indent=2))


@app.command("diagnostic-get")
def diagnostic_get(run_id: UUID) -> None:
    """Get a durable diagnostic run."""
    with workflow_service() as service:
        run = service.get(GetDiagnosticRun(run_id=DiagnosticRunId(value=run_id)))
    typer.echo(run.model_dump_json(indent=2))


@app.command("diagnostic-list")
def diagnostic_list(limit: int = 100) -> None:
    """List durable diagnostic runs."""
    with workflow_service() as service:
        runs = service.list(ListDiagnosticRuns(limit=limit))
    typer.echo(json.dumps([run.model_dump(mode="json") for run in runs], indent=2))


@app.command("diagnostic-cancel")
def diagnostic_cancel(run_id: UUID, actor: str = "operator") -> None:
    """Request cancellation of a durable diagnostic run."""
    command = CancelDiagnosticRun(
        actor=actor, correlation_id=CorrelationId.new(), run_id=DiagnosticRunId(value=run_id)
    )
    with workflow_service() as service:
        run = service.cancel(command)
    typer.echo(run.model_dump_json(indent=2))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
