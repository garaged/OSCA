from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from urllib.parse import quote

from fastapi.testclient import TestClient

from osca.analyst_workspace.app import create_app
from osca.analyst_workspace.cli import main
from osca.analyst_workspace.contracts import (
    WorkspaceFilter,
    WorkspaceItemStatus,
    WorkspaceSection,
)
from osca.analyst_workspace.evidence import WorkspaceEvidenceService
from osca.analyst_workspace.services import AnalystWorkspaceService


def _write(path: Path, document: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document), encoding="utf-8")


def _evidence_chain(root: Path) -> dict[WorkspaceSection, str]:
    run_root = root / "research-evidence" / "run-1"
    acquisition = root / "historical-acquisition" / "kraken.json"
    experiment = run_root / "experiment.json"
    diagnostic = run_root / "diagnostic.json"
    manifest = run_root / "manifest.json"
    _write(
        acquisition,
        {
            "family": "osca.historical-acquisition.evidence",
            "version": "2.0.0",
            "status": "succeeded",
            "symbol": "XBTUSD",
            "timeframe": "1d",
            "dataset_revision_id": "revision-1",
            "acquisition_id": "acquisition-1",
            "completed_at": "2026-08-02T14:05:59Z",
            "redistribution_enabled": False,
        },
    )
    _write(
        experiment,
        {
            "family": "osca.ml-experiment.result",
            "version": "1.0.0",
            "status": "succeeded",
            "experiment_id": "experiment-1",
            "dataset_revision_id": "revision-1",
            "symbol": "XBTUSD",
            "timeframe": "1d",
            "completed_at": "2026-08-02T14:10:00Z",
        },
    )
    _write(
        diagnostic,
        {
            "family": "osca.prediction-diagnostic.result",
            "version": "1.0.0",
            "status": "review_required",
            "diagnostic_id": "diagnostic-1",
            "experiment_id": "experiment-1",
            "completed_at": "2026-08-02T14:11:00Z",
        },
    )
    _write(
        manifest,
        {
            "family": "osca.research-pipeline.manifest",
            "version": "1.0.0",
            "status": "diagnostic_not_eligible",
            "run_id": "run-1",
            "experiment_id": "experiment-1",
            "completed_at": "2026-08-02T14:12:00Z",
        },
    )
    return {
        WorkspaceSection.ACQUISITIONS: (
            "acquisitions:historical-acquisition/kraken.json"
        ),
        WorkspaceSection.EXPERIMENTS: (
            "experiments:research-evidence/run-1/experiment.json"
        ),
        WorkspaceSection.DIAGNOSTICS: (
            "diagnostics:research-evidence/run-1/diagnostic.json"
        ),
        WorkspaceSection.PIPELINE_RUNS: (
            "pipeline_runs:research-evidence/run-1/manifest.json"
        ),
    }


def test_research_evidence_uses_dedicated_sections(tmp_path: Path) -> None:
    _evidence_chain(tmp_path)
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


def test_detail_lineage_filters_and_portable_export(tmp_path: Path) -> None:
    item_ids = _evidence_chain(tmp_path)
    service = WorkspaceEvidenceService()
    experiment_id = item_ids[WorkspaceSection.EXPERIMENTS]

    detail = service.detail(tmp_path, experiment_id)
    linked_sections = {link.section for link in detail.lineage}
    assert WorkspaceSection.ACQUISITIONS in linked_sections
    assert WorkspaceSection.DIAGNOSTICS in linked_sections
    assert WorkspaceSection.PIPELINE_RUNS in linked_sections
    assert detail.raw_json_download_enabled is True
    assert detail.portable_export_enabled is True

    filtered = service.filtered_snapshot(
        tmp_path,
        WorkspaceFilter(
            section=WorkspaceSection.EXPERIMENTS,
            symbol="XBTUSD",
            timeframe="1d",
        ),
    )
    assert filtered.total_items == 1
    assert filtered.sections[0].items[0].item_id == experiment_id

    payload = service.portable_export(tmp_path, experiment_id)
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        names = archive.namelist()
    assert experiment_id in manifest["included_item_ids"]
    assert item_ids[WorkspaceSection.ACQUISITIONS] in manifest["excluded_item_ids"]
    assert any(name.endswith("experiment.json") for name in names)
    assert all(not name.endswith("kraken.json") for name in names)


def test_api_cli_and_export_use_equivalent_contracts(
    tmp_path: Path,
    capsys: object,
) -> None:
    item_ids = _evidence_chain(tmp_path)
    experiment_id = item_ids[WorkspaceSection.EXPERIMENTS]
    client = TestClient(create_app(storage_root=tmp_path))

    api_snapshot = client.get(
        "/api/evidence",
        params={"section": "experiments", "symbol": "XBTUSD", "timeframe": "1d"},
    )
    assert api_snapshot.status_code == 200
    assert api_snapshot.json()["total_items"] == 1

    exit_code = main(
        [
            "--storage-root",
            str(tmp_path),
            "--snapshot",
            "--section",
            "experiments",
            "--symbol",
            "XBTUSD",
            "--timeframe",
            "1d",
        ]
    )
    assert exit_code == 0
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    assert json.loads(captured.out)["total_items"] == api_snapshot.json()["total_items"]

    encoded = quote(experiment_id, safe="")
    detail = client.get(f"/api/evidence/{encoded}")
    raw = client.get(f"/api/evidence/{encoded}/raw")
    exported = client.get(f"/api/evidence/{encoded}/export")
    assert detail.status_code == 200
    assert raw.status_code == 200
    assert exported.status_code == 200
    assert detail.json()["item"]["item_id"] == experiment_id
    assert json.loads(raw.content)["experiment_id"] == "experiment-1"
    with zipfile.ZipFile(io.BytesIO(exported.content)) as archive:
        assert "manifest.json" in archive.namelist()


def test_incomplete_incompatible_and_orphaned_are_derived(tmp_path: Path) -> None:
    run_root = tmp_path / "research-evidence"
    _write(
        run_root / "missing" / "experiment.json",
        {"family": "osca.ml-experiment.result", "version": "1.0.0"},
    )
    _write(
        run_root / "wrong" / "diagnostic.json",
        {
            "family": "other.diagnostic",
            "version": "9.0.0",
            "experiment_id": "missing-experiment",
        },
    )
    _write(
        run_root / "orphan" / "manifest.json",
        {
            "family": "osca.research-pipeline.manifest",
            "version": "1.0.0",
            "experiment_id": "missing-experiment",
        },
    )

    snapshot = WorkspaceEvidenceService().filtered_snapshot(tmp_path, WorkspaceFilter())
    statuses = {
        item.item_id: item.status
        for section in snapshot.sections
        for item in section.items
    }
    assert statuses["experiments:research-evidence/missing/experiment.json"] is (
        WorkspaceItemStatus.INCOMPLETE
    )
    assert statuses["diagnostics:research-evidence/wrong/diagnostic.json"] is (
        WorkspaceItemStatus.ORPHANED
    )
    assert statuses["pipeline_runs:research-evidence/orphan/manifest.json"] is (
        WorkspaceItemStatus.ORPHANED
    )
    assert snapshot.warnings


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
