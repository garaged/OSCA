from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from osca.release_acceptance import evaluate_files

app = typer.Typer(help="Evaluate the official OSCA release-candidate acceptance matrix.")


@app.command("evaluate")
def evaluate(
    input_path: Annotated[Path, typer.Option("--input")],
    output_path: Annotated[Path | None, typer.Option("--output")] = None,
) -> None:
    """Evaluate acceptance evidence and the blocking defect threshold."""
    try:
        result = evaluate_files(input_path, output_path)
    except (OSError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "eligible":
        raise typer.Exit(1)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
