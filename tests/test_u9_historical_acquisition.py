from __future__ import annotations

import csv
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
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
from osca.local_data_import import (
    LocalOHLCVImportRequest,
    LocalOHLCVTimeframe,
    import_local_ohlcv,
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


def _request(tmp_path: Path, *, parser_version: str = "kraken-ohlc-v1"):
    return HistoricalAcquisitionRequest(
        provider_id=ProductionProvider.KRAKEN,
        asset_class=HistoricalAssetClass.CRYPTO,
        symbol="XBTUSD",
        timeframe="1d",
        storage_root=str(tmp_path),
        network_access_enabled=True,
        parser_version=parser_version,
    )


def test_kraken_crypto_acquisition_creates_canonical_revision(tmp_path: Path) -> None:
    evidence = run_historical_acquisition(
        _request(tmp_path),
        transport=lambda _: _kraken_payload(),
    )

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


def test_durable_result_reuse_avoids_second_provider_call(tmp_path: Path) -> None:
    calls = 0

    def transport(_):
        nonlocal calls
        calls += 1
        return _kraken_payload()

    first = run_historical_acquisition(_request(tmp_path), transport=transport)
    second = run_historical_acquisition(_request(tmp_path), transport=transport)

    assert first.status is HistoricalAcquisitionStatus.SUCCEEDED
    assert second.status is HistoricalAcquisitionStatus.SUCCEEDED
    assert first.dataset_revision_id == second.dataset_revision_id
    assert calls == 1


def test_concurrent_equivalent_requests_share_provider_call(tmp_path: Path) -> None:
    calls = 0
    calls_lock = threading.Lock()

    def transport(_):
        nonlocal calls
        with calls_lock:
            calls += 1
        time.sleep(0.05)
        return _kraken_payload()

    request = _request(tmp_path)
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = tuple(
            executor.map(
                lambda _: run_historical_acquisition(request, transport=transport),
                range(2),
            )
        )

    assert all(item.status is HistoricalAcquisitionStatus.SUCCEEDED for item in results)
    assert results[0].dataset_revision_id == results[1].dataset_revision_id
    assert calls == 1


def test_parser_change_creates_new_revision(tmp_path: Path) -> None:
    first = run_historical_acquisition(
        _request(tmp_path, parser_version="kraken-ohlc-v1"),
        transport=lambda _: _kraken_payload(),
    )
    second = run_historical_acquisition(
        _request(tmp_path, parser_version="kraken-ohlc-v2"),
        transport=lambda _: _kraken_payload(),
    )

    assert first.dataset_revision_id is not None
    assert second.dataset_revision_id is not None
    assert first.dataset_revision_id != second.dataset_revision_id


def test_rate_limit_is_retryable_provider_unavailable(tmp_path: Path) -> None:
    payload = json.dumps(
        {"error": ["EAPI:Rate limit exceeded"], "result": {}}
    ).encode()

    evidence = run_historical_acquisition(
        _request(tmp_path),
        transport=lambda _: payload,
    )

    assert evidence.status is HistoricalAcquisitionStatus.PROVIDER_UNAVAILABLE
    assert "rate-limit-exceeded" in evidence.findings
    assert "retry-later" in evidence.findings
    assert evidence.dataset_revision_id is None


def test_csv_fallback_is_canonically_equivalent(tmp_path: Path) -> None:
    acquired = run_historical_acquisition(
        _request(tmp_path / "network"),
        transport=lambda _: _kraken_payload(),
    )
    csv_path = tmp_path / "fallback.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp", "open", "high", "low", "close", "volume"])
        writer.writerow(
            ["2024-07-31T00:00:00+00:00", "66000", "67000", "65000", "66500", "10"]
        )
        writer.writerow(
            ["2024-08-01T00:00:00+00:00", "66500", "68000", "66000", "67500", "12"]
        )
    fallback = import_local_ohlcv(
        LocalOHLCVImportRequest(
            input_path=str(csv_path),
            storage_root=str(tmp_path / "fallback"),
            symbol="XBTUSD",
            timeframe=LocalOHLCVTimeframe.ONE_DAY,
            calendar_assumption="continuous-crypto-market",
        )
    )

    assert acquired.canonical_payload_uri is not None
    acquired_rows = pq.read_table(acquired.canonical_payload_uri).to_pylist()
    fallback_rows = pq.read_table(fallback.payload_uri).to_pylist()
    assert acquired_rows == fallback_rows


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
    evidence = run_historical_acquisition(
        _request(tmp_path),
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
