from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from osca.historical_acquisition import (
    HistoricalAcquisitionRequest,
    HistoricalAcquisitionStatus,
    HistoricalAssetClass,
    run_historical_acquisition,
)
from osca.production_ingestion.contracts import ProductionProvider
from osca.research_pipeline import main as research_pipeline_main


def _long_kraken_payload() -> bytes:
    rows: list[list[object]] = []
    price = 100.0
    start = 1_704_067_200
    for index in range(422):
        drift = 0.8 if index % 5 else -0.6
        close = price + drift
        rows.append(
            [
                start + index * 86_400,
                f"{price:.4f}",
                f"{max(price, close) + 0.5:.4f}",
                f"{min(price, close) - 0.5:.4f}",
                f"{close:.4f}",
                f"{close:.4f}",
                f"{1000 + index}",
                10,
            ]
        )
        price = close
    return json.dumps(
        {
            "error": [],
            "result": {"XXBTZUSD": rows, "last": rows[-1][0]},
        }
    ).encode()


def test_acquired_revision_runs_through_u8_pipeline(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    storage_root = tmp_path / "storage"
    acquisition = run_historical_acquisition(
        HistoricalAcquisitionRequest(
            provider_id=ProductionProvider.KRAKEN,
            asset_class=HistoricalAssetClass.CRYPTO,
            symbol="XBTUSD",
            timeframe="1d",
            storage_root=str(storage_root),
            network_access_enabled=True,
        ),
        transport=lambda _request: _long_kraken_payload(),
    )

    assert acquisition.status is HistoricalAcquisitionStatus.SUCCEEDED
    assert acquisition.canonical_payload_uri is not None
    assert acquisition.dataset_revision_id is not None

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "osca-research-pipeline",
            acquisition.canonical_payload_uri,
            acquisition.dataset_revision_id,
            "XBTUSD",
            "1d",
            "--storage-root",
            str(storage_root),
            "--reviewer",
            "u9-acceptance",
            "--rationale",
            "Approved for local evidence-only U9 handoff validation.",
            "--approve-local-validation",
            "--feature-window",
            "10",
            "--embargo",
            "2",
            "--iterations",
            "100",
        ],
    )

    research_pipeline_main()

    manifest = json.loads(capsys.readouterr().out)
    assert manifest["dataset_revision_id"] == acquisition.dataset_revision_id
    assert manifest["recommendations_enabled"] is False
    assert manifest["broker_execution_enabled"] is False
    assert manifest["real_capital_execution_enabled"] is False
