from __future__ import annotations

import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from osca.research_pipeline import main


def _payload(path: Path) -> Path:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    rows = []
    price = 100.0
    for index in range(420):
        drift = 0.8 if index % 5 else -0.6
        open_price = price
        close_price = open_price + drift
        rows.append(
            {
                "timestamp": start + timedelta(days=index),
                "open": open_price,
                "high": max(open_price, close_price) + 0.5,
                "low": min(open_price, close_price) - 0.5,
                "close": close_price,
                "volume": 1_000.0 + index,
            }
        )
        price = close_price
    pq.write_table(pa.Table.from_pylist(rows), path)
    return path


def test_pipeline_requires_explicit_human_approval(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = _payload(tmp_path / "prices.parquet")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "osca-research-pipeline",
            str(payload),
            str(uuid4()),
            "TEST",
            "1d",
            "--storage-root",
            str(tmp_path / "storage"),
            "--reviewer",
            "research-owner",
            "--rationale",
            "Local evidence-only review.",
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2
    assert not (tmp_path / "storage" / "research-evidence").exists()


def test_pipeline_retains_traceable_evidence_under_storage_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    payload = _payload(tmp_path / "prices.parquet")
    storage_root = tmp_path / "storage"
    revision_id = uuid4()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "osca-research-pipeline",
            str(payload),
            str(revision_id),
            "TEST",
            "1d",
            "--storage-root",
            str(storage_root),
            "--reviewer",
            "research-owner",
            "--rationale",
            "Approved for local evidence-only validation.",
            "--approve-local-validation",
            "--feature-window",
            "10",
            "--embargo",
            "2",
            "--iterations",
            "200",
        ],
    )

    main()

    manifest = json.loads(capsys.readouterr().out)
    artifact_root = storage_root / "research-evidence" / manifest["run_id"]

    assert manifest["dataset_revision_id"] == str(revision_id)
    assert manifest["automatic_promotion_enabled"] is False
    assert manifest["recommendations_enabled"] is False
    assert manifest["broker_execution_enabled"] is False
    assert manifest["real_capital_execution_enabled"] is False
    assert (artifact_root / "experiment.json").is_file()
    assert (artifact_root / "diagnostic.json").is_file()
    assert (artifact_root / "manifest.json").is_file()

    if manifest["status"] == "diagnostic_not_eligible":
        assert not (artifact_root / "validation-result.json").exists()
    else:
        assert (artifact_root / "validation-request.json").is_file()
        assert (artifact_root / "validation-result.json").is_file()
        assert manifest["event_driven_validation_enabled"] is True
