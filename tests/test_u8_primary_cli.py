from __future__ import annotations

import subprocess
from pathlib import Path
from uuid import uuid4

from typer.testing import CliRunner

from osca.cli import app

runner = CliRunner()


def test_primary_cli_lists_research_pipeline() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "research-pipeline" in result.stdout


def test_research_pipeline_help_discloses_fixed_model_contract() -> None:
    result = runner.invoke(app, ["research-pipeline", "--help"])

    assert result.exit_code == 0
    assert "logistic_classification" in result.stdout
    assert "classification" in result.stdout
    assert "research-evidence" in result.stdout


def test_primary_cli_forwards_human_gate_and_parameters(
    monkeypatch,
    tmp_path: Path,
) -> None:
    payload = tmp_path / "prices.parquet"
    payload.write_bytes(b"fixture")
    calls: list[list[str]] = []

    def fake_run(command: list[str], *, check: bool) -> subprocess.CompletedProcess[str]:
        assert check is False
        calls.append(command)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", fake_run)

    revision = uuid4()
    result = runner.invoke(
        app,
        [
            "research-pipeline",
            str(payload),
            str(revision),
            "AAPL",
            "1d",
            "--storage-root",
            str(tmp_path / "storage"),
            "--reviewer",
            "research-owner",
            "--rationale",
            "Approved for local evidence-only validation.",
            "--approve-local-validation",
            "--feature-window",
            "20",
            "--embargo",
            "5",
        ],
    )

    assert result.exit_code == 0
    assert len(calls) == 1
    command = calls[0]
    assert command[1:3] == ["-m", "osca.research_pipeline"]
    assert "--approve-local-validation" in command
    assert "--reviewer" in command
    assert "research-owner" in command
    assert "--storage-root" in command
