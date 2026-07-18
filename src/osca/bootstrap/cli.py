from __future__ import annotations

import json

import typer

from osca.bootstrap.runtime import readiness_snapshot

app = typer.Typer(no_args_is_help=True, help="OSCA operator command line.")


@app.command()
def readiness() -> None:
    """Report the validated local readiness snapshot."""

    typer.echo(json.dumps(readiness_snapshot().model_dump(mode="json"), indent=2))


def main() -> None:
    app()


if __name__ == "__main__":
    main()

