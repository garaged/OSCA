from __future__ import annotations

import json
from pathlib import Path

import pyarrow.parquet as pq
from typer.testing import CliRunner

from osca.cli import app
from osca.historical_acquisition import (
    HistoricalAcquisitionRequest,
    HistoricalAcquisitionStatus,
    HistoricalAssetClass,
    run_historical_acquisition,
)
from osca.production_ingestion.contracts import ProductionProvider

runner = CliRunner()


def _kraken_payload() -> bytes:
    return json.dumps(
        {
            "error": [],
            "result": {
                "XXBTZUSD": [
                    [1722384000, "66000", "67000", "65000", "66500", "66300", "10", 50],
                    [1722470400, "66500", "68000", "66000", "67500", "67100", "12", 55],
                    [1722556800, "67500", "68200", "67000", "67800", "67700", "4", 20],
                ],
                "last": 1722556800,
            },
        }
    ).encode()


def test_kraken_crypto_acquisition_creates_canonical_revision(tmp_path: Path) -> None:
    request = HistoricalAcquisitionRequest(
        provider_id=ProductionProvider.KRAKEN,
        asset_class=HistoricalAssetClass.CRYPTO,
        symbol="XBTUSD",
        timeframe="1d",
        storage_root=str(tmp_path),
        network_access_enabled=True,
    )

    evidence = run_historical_acquisition(request, transport=lambda _: _kraken_payload())

    assert evidence.status is HistoricalAcquisitionStatus.SUCCEEDED
    assert evidence.source_attribution == "Kraken public spot OHLC"
    assert evidence.raw_payload_uri is not None
    assert evidence.raw_payload_sha256 is not None
    assert evidence.dataset_revision_id is not None
    assert evidence.canonical_payload_uri is not None
    assert evidence.canonical_metadata_uri is not None
    assert evidence.canonical_row_count == 2
    assert "current-uncommitted-bar-excluded" in evidence.findings
    assert evidence.ingestion_evidence_uri is not None
    assert evidence.redistribution_enabled is False
    assert evidence.recommendations_enabled is False
    assert evidence.broker_execution_enabled is False
    assert evidence.real_capital_execution_enabled is False

    table = pq.read_table(evidence.canonical_payload_uri)
    assert table.num_rows == 2
    assert table.column_names == ["timestamp", "open", "high", "low", "close", "volume"]
    assert Path(evidence.canonical_metadata_uri).exists()
    assert Path(evidence.ingestion_evidence_uri.removeprefix("file://")).exists()


def test_equivalent_kraken_payload_reuses_dataset_revision(tmp_path: Path) -> None:
    request = HistoricalAcquisitionRequest(
        provider_id=ProductionProvider.KRAKEN,
        asset_class=HistoricalAssetClass.CRYPTO,
        symbol="XBTUSD",
        timeframe="1d",
        storage_root=str(tmp_path),
        network_access_enabled=True,
    )

    first = run_historical_acquisition(request, transport=lambda _: _kraken_payload())
    second = run_historical_acquisition(request, transport=lambda _: _kraken_payload())

    assert first.status is HistoricalAcquisitionStatus.SUCCEEDED
    assert second.status is HistoricalAcquisitionStatus.SUCCEEDED
    assert first.dataset_revision_id == second.dataset_revision_id
    assert first.canonical_payload_uri == second.canonical_payload_uri


def test_network_is_explicit_for_kraken(tmp_path: Path) -> None:
    request = HistoricalAcquisitionRequest(
        provider_id=ProductionProvider.KRAKEN,
        asset_class=HistoricalAssetClass.CRYPTO,
        symbol="XBTUSD",
        timeframe="1d",
        storage_root=str(tmp_path),
    )

    evidence = run_historical_acquisition(request)

    assert evidence.status is HistoricalAcquisitionStatus.POLICY_BLOCKED
    assert "network-access-not-enabled" in evidence.findings
    assert evidence.dataset_revision_id is None


def test_equity_provider_fails_closed_with_csv_fallback(tmp_path: Path) -> None:
    request = HistoricalAcquisitionRequest(
        provider_id=ProductionProvider.TWELVE_DATA,
        asset_class=HistoricalAssetClass.EQUITY,
        symbol="AAPL",
        timeframe="1d",
        storage_root=str(tmp_path),
    )

    evidence = run_historical_acquisition(request)

    assert evidence.status is HistoricalAcquisitionStatus.PROVIDER_UNAVAILABLE
    assert "equity-provider-not-admitted" in evidence.findings
    assert "csv-import-remains-supported" in evidence.findings
    assert evidence.ingestion_evidence_uri is not None
    assert evidence.dataset_revision_id is None


def test_malformed_kraken_payload_fails_without_canonical_revision(tmp_path: Path) -> None:
    request = HistoricalAcquisitionRequest(
        provider_id=ProductionProvider.KRAKEN,
        asset_class=HistoricalAssetClass.CRYPTO,
        symbol="XBTUSD",
        timeframe="1d",
        storage_root=str(tmp_path),
        network_access_enabled=True,
    )

    evidence = run_historical_acquisition(
        request,
        transport=lambda _: json.dumps({"error": [], "result": {"last": 1}}).encode(),
    )

    assert evidence.status is HistoricalAcquisitionStatus.FAILED
    assert "canonical-normalization-failed" in evidence.findings
    assert evidence.raw_payload_uri is not None
    assert evidence.dataset_revision_id is None


def test_primary_cli_lists_historical_data() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "historical-data" in result.stdout


def test_cli_retains_blocked_equity_decision(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "historical-data",
            "fetch",
            "AAPL",
            "equity",
            "twelve_data",
            "--storage-root",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "provider_unavailable"
    assert payload["dataset_revision_id"] is None
    assert payload["redistribution_enabled"] is False
