from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from osca.extension_conformance import validate_extension_package

app = typer.Typer(help="Validate trusted-local OSCA extension packages without importing code.")


@app.command("validate")
def validate_command(
    manifest: Annotated[Path, typer.Option("--manifest")],
) -> None:
    """Validate a strict extension manifest and all declared artifact digests."""
    result = validate_extension_package(manifest)
    typer.echo(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))
    if result.status == "invalid":
        raise typer.Exit(1)
