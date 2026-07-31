from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from osca.analyst_workspace import (
    AnalystWorkspaceService,
    WorkspaceItemStatus,
    WorkspaceSection,
    create_app,
)
from osca.analyst_workspace.cli import main


def _write_dataset_metadata(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    payload = root / "payloads" / "aapl.parquet"
    payload.parent.mkdir(parents=True, exist_ok=True)
    payload.write_bytes(b"PAR1")
    database = root / "osca-local-data.sqlite"
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            CREATE TABLE local_ohlcv_imports (
                dataset_revision_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                row_count INTEGER NOT NULL,
                first_timestamp TEXT NOT NULL,
                last_timestamp TEXT NOT NULL,
                payload_uri TEXT NOT NULL,
                quality_findings_json TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            INSERT INTO local_ohlcv_imports VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "dataset-aapl",
                "AAPL",
                "1d",
                10,
                "2026-01-01T00:00:00+00:00",
                "2026-01-10T00:00:00+00:00",
                str(payload),
                "[]",
            ),
        )
    return payload


def test_empty_workspace_has_all_sections_and_safety_boundaries(tmp_path: Path) -> None:
    snapshot = AnalystWorkspaceService().snapshot(tmp_path)

    assert snapshot.total_items == 0
    assert tuple(section.section for section in snapshot.sections) == tuple(WorkspaceSection)
    assert snapshot.read_only is True
    assert snapshot.network_access_enabled is False
    assert snapshot.credential_materialization_enabled is False
    assert snapshot.real_capital_orders_enabled is False


def test_workspace_discovers_local_dataset_and_reports(tmp_path: Path) -> None:
    payload = _write_dataset_metadata(tmp_path)
    (tmp_path / "demo-research.md").write_text("# Research", encoding="utf-8")
    (tmp_path / "backtest-paper.md").write_text("# Backtest", encoding="utf-8")

    snapshot = AnalystWorkspaceService().snapshot(tmp_path)
    sections = {section.section: section for section in snapshot.sections}

    dataset = sections[WorkspaceSection.DATASETS].items[0]
    assert dataset.title == "AAPL 1d"
    assert dataset.status is WorkspaceItemStatus.AVAILABLE
    assert dataset.artifact_uri == str(payload)
    assert sections[WorkspaceSection.REPORTS].item_count == 1
    assert sections[WorkspaceSection.BACKTESTS].item_count == 1


def test_workspace_discovers_sec_enrichment_and_filters_secret_fields(
    tmp_path: Path,
) -> None:
    metadata = (
        tmp_path
        / "provider-preview"
        / "sec-edgar"
        / "sec_company_facts"
        / "CIK0000320193.metadata.json"
    )
    metadata.parent.mkdir(parents=True)
    metadata.write_text(
        json.dumps(
            {
                "provider_id": "sec_edgar",
                "resource_id": "CIK0000320193",
                "outcome": "succeeded",
                "rationale": "fixture evidence",
                "secret_reference": "secret:must-not-surface",
            }
        ),
        encoding="utf-8",
    )

    result = AnalystWorkspaceService().section(tmp_path, WorkspaceSection.ENRICHMENT)

    assert result.item_count == 1
    assert result.items[0].status is WorkspaceItemStatus.AVAILABLE
    assert "secret_reference" not in result.items[0].metadata


def test_workspace_preserves_policy_blocked_routing_status(tmp_path: Path) -> None:
    decision = tmp_path / "runtime-routing" / "fred.decision.json"
    decision.parent.mkdir(parents=True)
    decision.write_text(
        json.dumps(
            {
                "provider_id": "fred",
                "resource_id": "GDP",
                "status": "policy_blocked",
                "rationale": "FRED remains gated.",
            }
        ),
        encoding="utf-8",
    )

    result = AnalystWorkspaceService().section(tmp_path, WorkspaceSection.ROUTING)

    assert result.items[0].status is WorkspaceItemStatus.POLICY_BLOCKED
    assert result.items[0].summary == "FRED remains gated."


def test_workspace_api_and_html_are_read_only(tmp_path: Path) -> None:
    _write_dataset_metadata(tmp_path)
    client = TestClient(create_app(storage_root=tmp_path))

    page = client.get("/")
    snapshot = client.get("/api/workspace")
    health = client.get("/health")

    assert page.status_code == 200
    assert "OSCA Analyst Workspace" in page.text
    assert snapshot.status_code == 200
    assert snapshot.json()["read_only"] is True
    assert health.json()["network_access_enabled"] is False
    assert client.post("/api/workspace").status_code == 405


def test_unknown_workspace_section_returns_404(tmp_path: Path) -> None:
    client = TestClient(create_app(storage_root=tmp_path))

    response = client.get("/api/workspace/not-a-section")

    assert response.status_code == 404


def test_snapshot_cli_outputs_json(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _write_dataset_metadata(tmp_path)

    result = main(["--storage-root", str(tmp_path), "--snapshot"])

    assert result == 0
    document = json.loads(capsys.readouterr().out)
    assert document["read_only"] is True
    assert document["total_items"] == 1


def test_workspace_server_rejects_non_loopback_binding(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = main(
        ["--storage-root", str(tmp_path), "--host", "0.0.0.0", "--port", "8000"]
    )

    assert result == 2
    assert "loopback" in capsys.readouterr().err
