from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Annotated
from uuid import UUID

import typer

from osca.analytical_data import (
    ChartSeriesRequest,
    DerivedSeriesKind,
    DerivedSeriesRequest,
    build_chart_series,
)

app = typer.Typer(no_args_is_help=True, help="Query governed OHLCV chart and derived series.")


@app.command("query")
def query(
    payload_file: Path,
    dataset_revision_id: UUID,
    symbol: str,
    timeframe: str,
    start: Annotated[datetime | None, typer.Option("--start")] = None,
    end: Annotated[datetime | None, typer.Option("--end")] = None,
    max_rows: Annotated[int, typer.Option("--max-rows")] = 2_000,
    derived: Annotated[list[str] | None, typer.Option("--derived")] = None,
) -> None:
    """Return bounded chart-ready OHLCV data and optional derived series as JSON."""

    definitions = tuple(_parse_derived(item) for item in (derived or []))
    result = build_chart_series(
        ChartSeriesRequest(
            dataset_revision_id=dataset_revision_id,
            payload_path=payload_file,
            symbol=symbol,
            timeframe=timeframe,
            start=start,
            end=end,
            max_rows=max_rows,
            derived=definitions,
        )
    )
    typer.echo(json.dumps(result.model_dump(mode="json"), indent=2))


def _parse_derived(value: str) -> DerivedSeriesRequest:
    name, separator, raw_window = value.partition(":")
    try:
        kind = DerivedSeriesKind(name)
    except ValueError as exc:
        allowed = ", ".join(item.value for item in DerivedSeriesKind)
        raise typer.BadParameter(f"derived series must be one of: {allowed}") from exc
    window = int(raw_window) if separator else None
    return DerivedSeriesRequest(kind=kind, window=window)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
