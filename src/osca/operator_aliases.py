from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Annotated

import typer


def _run_primary(command: list[str]) -> None:
    completed = subprocess.run([sys.executable, "-m", "osca.cli", *command], check=False)
    if completed.returncode != 0:
        raise typer.Exit(completed.returncode)


def import_data_command(
    input_file: Path,
    symbol: str,
    timeframe: str,
    storage_root: Annotated[Path, typer.Option("--storage-root")] = Path(".osca/data"),
    input_format: Annotated[str | None, typer.Option("--input-format")] = None,
    calendar_assumption: Annotated[
        str, typer.Option("--calendar-assumption")
    ] = "source-provided",
) -> None:
    """Import governed local OHLCV evidence through the canonical U11 command."""
    command = [
        "local-ohlcv-import",
        str(input_file),
        symbol,
        timeframe,
        "--storage-root",
        str(storage_root),
        "--calendar-assumption",
        calendar_assumption,
    ]
    if input_format is not None:
        command.extend(["--input-format", input_format])
    _run_primary(command)


def analyze_command(
    payload_file: Path,
    symbol: str,
    timeframe: str,
    output_file: Annotated[Path | None, typer.Option("--output-file")] = None,
    report_format: Annotated[str, typer.Option("--report-format")] = "markdown",
    project_name: Annotated[str, typer.Option("--project-name")] = "first-demo-research",
) -> None:
    """Run deterministic local analysis through the canonical U11 command."""
    command = [
        "demo-research-report",
        str(payload_file),
        symbol,
        timeframe,
        "--report-format",
        report_format,
        "--project-name",
        project_name,
    ]
    if output_file is not None:
        command.extend(["--output-file", str(output_file)])
    _run_primary(command)


def backtest_command(
    payload_file: Path,
    symbol: str,
    timeframe: str,
    output_file: Annotated[Path | None, typer.Option("--output-file")] = None,
    report_format: Annotated[str, typer.Option("--report-format")] = "markdown",
    initial_cash: Annotated[float, typer.Option("--initial-cash")] = 10_000.0,
    project_name: Annotated[
        str, typer.Option("--project-name")
    ] = "p8-backtest-paper-happy-path",
) -> None:
    """Run built-in backtest-to-paper evidence through the canonical U11 command."""
    command = [
        "backtest-paper-run",
        str(payload_file),
        symbol,
        timeframe,
        "--report-format",
        report_format,
        "--initial-cash",
        str(initial_cash),
        "--project-name",
        project_name,
    ]
    if output_file is not None:
        command.extend(["--output-file", str(output_file)])
    _run_primary(command)
