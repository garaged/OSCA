from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from osca.onboarding import inspect_first_run

app = typer.Typer(no_args_is_help=True, help="Inspect and prepare a first-run OSCA workspace.")


@app.command("check")
def check(
    storage_root: Annotated[Path, typer.Option("--storage-root")] = Path(".osca"),
    prepare: Annotated[bool, typer.Option("--prepare")] = False,
) -> None:
    """Run deterministic first-run checks and optionally create the storage root."""

    report = inspect_first_run(storage_root, prepare=prepare)
    typer.echo(json.dumps(report.model_dump(mode="json"), indent=2))
    if report.status.value == "failed":
        raise typer.Exit(code=2)
    if report.status.value == "action_required":
        raise typer.Exit(code=1)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
