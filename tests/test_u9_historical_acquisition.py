from __future__ import annotations

import json
from pathlib import Path

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
                    [1722384000, "66000", "67000", "65000", "66500", "66300", "10", 50]
                ],
                "last": 1722384000,
            },
        }
    ).encode()


def test_kraken_crypto_acquisition_retains_lineage(tmp_path: Path) -> None:
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
    assert evidence.payload_uri is not None
    assert evidence.payload_sha256 is not None
    assert evidence.ingestion_evidence_uri is not None
    assert evidence.redistribution_enabled is False
    assert evidence.recommendations_enabled is False
    assert evidence.broker_execution_enabled is False
    assert evidence.real_capital_execution_enabled is False
    assert Path(evidence.ingestion_evidence_uri.removeprefix("file://")).exists()


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
    assert payload["redistribution_enabled"] is False
