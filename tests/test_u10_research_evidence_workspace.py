from __future__ import annotations

import json
from pathlib import Path

from osca.analyst_workspace.contracts import WorkspaceItemStatus, WorkspaceSection
from osca.analyst_workspace.services import AnalystWorkspaceService


def _write(path: Path, document: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document), encoding="utf-8")


def test_research_evidence_uses_dedicated_sections(tmp_path: Path) -> None:
    run_root = tmp_path / "research-evidence" / "run-1"
    _write(
        tmp_path / "historical-acquisition" / "kraken.json",
        {
            "family": "osca.historical-acquisition.evidence",
            "status": "succeeded",
            "symbol": "XBTUSD",
            "dataset_revision_id": "revision-1",
        },
    )
    _write(
        run_root / "experiment.json",
        {
            "family": "osca.ml-experiment.result",
            "status": "succeeded",
            "experiment_id": "experiment-1",
            "dataset_revision_id": "revision-1",
        },
    )
    _write(
        run_root / "diagnostic.json",
        {
            "family": "osca.prediction-diagnostic.result",
            "status": "review_required",
            "diagnostic_id": "diagnostic-1",
            "experiment_id": "experiment-1",
        },
    )
    _write(
        run_root / "manifest.json",
        {
            "family": "osca.research-pipeline.manifest",
            "status": "diagnostic_not_eligible",
            "run_id": "run-1",
            "experiment_id": "experiment-1",
        },
    )

    snapshot = AnalystWorkspaceService().snapshot(tmp_path)
    sections = {section.section: section for section in snapshot.sections}

    assert sections[WorkspaceSection.ACQUISITIONS].item_count == 1
    assert sections[WorkspaceSection.EXPERIMENTS].item_count == 1
    assert sections[WorkspaceSection.DIAGNOSTICS].item_count == 1
    assert sections[WorkspaceSection.VALIDATIONS].item_count == 0
    assert sections[WorkspaceSection.PIPELINE_RUNS].item_count == 1
    assert sections[WorkspaceSection.DIAGNOSTICS].items[0].status is (
        WorkspaceItemStatus.REVIEW_REQUIRED
    )
    assert sections[WorkspaceSection.PIPELINE_RUNS].items[0].status is (
        WorkspaceItemStatus.NOT_ELIGIBLE
    )
    assert all(
        "/research-evidence/" not in str(item.artifact_uri)
        and "/historical-acquisition/" not in str(item.artifact_uri)
        for item in sections[WorkspaceSection.REPORTS].items
    )
    assert snapshot.read_only is True
    assert snapshot.network_access_enabled is False
    assert snapshot.recommendations_enabled is False
    assert snapshot.broker_connections_enabled is False
    assert snapshot.real_capital_orders_enabled is False


def test_corrupt_research_evidence_is_not_healthy(tmp_path: Path) -> None:
    path = tmp_path / "research-evidence" / "run-2" / "diagnostic.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("not-json", encoding="utf-8")

    snapshot = AnalystWorkspaceService().snapshot(tmp_path)
    diagnostics = next(
        section
        for section in snapshot.sections
        if section.section is WorkspaceSection.DIAGNOSTICS
    )

    assert diagnostics.item_count == 1
    assert diagnostics.items[0].status is WorkspaceItemStatus.CORRUPT
    assert snapshot.warnings
