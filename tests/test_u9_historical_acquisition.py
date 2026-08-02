from __future__ import annotations

import csv
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

import pyarrow.parquet as pq
import pytest
from typer.testing import CliRunner

from osca.cli import app
from osca.historical_acquisition import (
    AcquisitionJobRecord,
    AcquisitionJobStatus,
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


def _kraken_payload(*, errors: list[str] | None = None) -> bytes:
    return json.dumps(
        {
            "error": errors or [],
            "result": {
                "XXBTZUSD": [
                    [
                        1722384000,
                        "66000",
                        "67000",
                        "65000",
                        "66500",
                        "66300",
                        "10",
                        50,
                    ],
                    [
                        1722470400,
                        "66500",
                        "68000",
                        "66000",
                        "67500",
                        "67100",
                        "12",
                        55,
                    ],
                    [
                        1722556800,
                        "67500",
                        "68200",
                        "67000",
                        "67800",
                        "67700",
                        "4",
                        20,
                    ],
                ],
                "last": 1722556800,
            },
        }
    ).encode()


def _request(
    tmp_path: Path,
    *,
    parser_version: str = "kraken-ohlc-v1",
    normalizer_version: str = "canonical-ohlcv-v1",
    **updates: object,
) -> HistoricalAcquisitionRequest:
    values: dict[str, object] = {
        "provider_id": ProductionProvider.KRAKEN,
        "asset_class": HistoricalAssetClass.CRYPTO,
        "symbol": "XBTUSD",
        "timeframe": "1d",
        "storage_root": str(tmp_path),
        "network_access_enabled": True,
        "expected_pair_key": "XXBTZUSD",
        "parser_version": parser_version,
        "normalizer_version": normalizer_version,
    }
    values.update(updates)
    return HistoricalAcquisitionRequest(**values)


def test_kraken_acquisition_retains_full_lineage_and_job_evidence(
    tmp_path: Path,
) -> None:
    evidence = run_historical_acquisition(
        _request(tmp_path),
        transport=lambda _: _kraken_payload(),
    )

    assert evidence.status is HistoricalAcquisitionStatus.SUCCEEDED
    assert evidence.job_status is AcquisitionJobStatus.SUCCEEDED
    assert evidence.provider_pair_key == "XXBTZUSD"
    assert evidence.raw_payload_uri is not None
    assert evidence.raw_payload_sha256 is not None
    assert evidence.normalized_sha256 is not None
    assert evidence.dataset_revision_id is not None
    assert evidence.canonical_payload_uri is not None
    assert evidence.canonical_metadata_uri is not None
    assert evidence.canonical_row_count == 2
    assert evidence.request_id != evidence.correlation_id
    assert evidence.attempts
    assert evidence.progress_percent == 100
    assert evidence.ingestion_evidence_uri is not None
    assert evidence.job_evidence_uri is not None
    assert evidence.redistribution_enabled is False
    assert evidence.recommendations_enabled is False
    assert evidence.broker_execution_enabled is False
    assert evidence.real_capital_execution_enabled is False

    table = pq.read_table(evidence.canonical_payload_uri)
    assert table.num_rows == 2
    job_path = Path(evidence.job_evidence_uri.removeprefix("file://"))
    job = AcquisitionJobRecord.model_validate_json(
        job_path.read_text(encoding="utf-8")
    )
    assert job.status is AcquisitionJobStatus.SUCCEEDED
    assert job.progress_percent == 100


def test_bounded_range_filters_rows_and_retains_mapping(tmp_path: Path) -> None:
    evidence = run_historical_acquisition(
        _request(
            tmp_path,
            start_at=datetime(2024, 8, 1, tzinfo=UTC),
            end_at=datetime(2024, 8, 2, tzinfo=UTC),
            require_complete_range=True,
        ),
        transport=lambda _: _kraken_payload(),
    )

    assert evidence.status is HistoricalAcquisitionStatus.SUCCEEDED
    assert evidence.canonical_row_count == 1
    assert evidence.start_at == datetime(2024, 8, 1, tzinfo=UTC)
    assert evidence.end_at == datetime(2024, 8, 2, tzinfo=UTC)
    assert evidence.provider_pair_key == "XXBTZUSD"


def test_invalid_range_and_mapping_fail_before_acceptance(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="start_at"):
        _request(
            tmp_path,
            start_at=datetime(2024, 8, 2, tzinfo=UTC),
            end_at=datetime(2024, 8, 1, tzinfo=UTC),
        )

    evidence = run_historical_acquisition(
        _request(tmp_path, expected_pair_key="WRONG"),
        transport=lambda _: _kraken_payload(),
    )
    assert evidence.status is HistoricalAcquisitionStatus.INVALID
    assert evidence.dataset_revision_id is None


def test_durable_result_reuse_avoids_second_provider_call(tmp_path: Path) -> None:
    calls = 0

    def transport(_: object) -> bytes:
        nonlocal calls
        calls += 1
        return _kraken_payload()

    first = run_historical_acquisition(_request(tmp_path), transport=transport)
    second = run_historical_acquisition(_request(tmp_path), transport=transport)

    assert first.dataset_revision_id == second.dataset_revision_id
    assert second.reuse_state == "reused"
    assert calls == 1


def test_concurrent_equivalent_requests_share_provider_call(tmp_path: Path) -> None:
    calls = 0
    calls_lock = threading.Lock()

    def transport(_: object) -> bytes:
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

    assert results[0].dataset_revision_id == results[1].dataset_revision_id
    assert calls == 1


def test_interrupted_job_is_recovered_and_cancel_can_fail_closed(
    tmp_path: Path,
) -> None:
    request = _request(tmp_path)
    first = run_historical_acquisition(
        request,
        transport=lambda _: _kraken_payload(),
    )
    assert first.job_evidence_uri is not None
    assert first.ingestion_evidence_uri is not None
    job_path = Path(first.job_evidence_uri.removeprefix("file://"))
    job = AcquisitionJobRecord.model_validate_json(
        job_path.read_text(encoding="utf-8")
    )
    interrupted = job.model_copy(
        update={
            "status": AcquisitionJobStatus.RUNNING,
            "stage": "provider-retrieval",
        }
    )
    job_path.write_text(interrupted.model_dump_json(indent=2), encoding="utf-8")
    Path(first.ingestion_evidence_uri.removeprefix("file://")).unlink()

    recovered = run_historical_acquisition(
        request,
        transport=lambda _: _kraken_payload(),
    )
    assert recovered.reuse_state == "recovered"

    cancelled = run_historical_acquisition(
        _request(tmp_path / "cancel", cancel_requested=True)
    )
    assert cancelled.status is HistoricalAcquisitionStatus.CANCELLED
    assert cancelled.job_status is AcquisitionJobStatus.CANCELLED
    assert "cancelled-before-network" in cancelled.findings


def test_parser_or_normalizer_change_links_predecessor_revision(
    tmp_path: Path,
) -> None:
    first = run_historical_acquisition(
        _request(tmp_path),
        transport=lambda _: _kraken_payload(),
    )
    second = run_historical_acquisition(
        _request(tmp_path, parser_version="kraken-ohlc-v2"),
        transport=lambda _: _kraken_payload(),
    )

    assert first.dataset_revision_id != second.dataset_revision_id
    assert second.predecessor_revision_id == first.dataset_revision_id
    assert second.supersedes_revision_id == first.dataset_revision_id
    assert second.correction_reason == "parser-or-provider-correction"


def test_quota_service_corrupt_and_invalid_outcomes_are_distinct(
    tmp_path: Path,
) -> None:
    quota = run_historical_acquisition(
        _request(tmp_path / "quota"),
        transport=lambda _: _kraken_payload(
            errors=["EAPI:Rate limit exceeded"]
        ),
    )
    assert quota.status is HistoricalAcquisitionStatus.QUOTA_BLOCKED
    assert quota.quota_state == "exhausted"
    assert quota.retry_after_seconds == 60

    service = run_historical_acquisition(
        _request(tmp_path / "service"),
        transport=lambda _: _kraken_payload(errors=["EService:Unavailable"]),
    )
    assert service.status is HistoricalAcquisitionStatus.PROVIDER_UNAVAILABLE

    corrupt = run_historical_acquisition(
        _request(tmp_path / "corrupt"),
        transport=lambda _: b"not-json",
    )
    assert corrupt.status is HistoricalAcquisitionStatus.CORRUPT

    invalid = run_historical_acquisition(
        _request(tmp_path / "invalid"),
        transport=lambda _: json.dumps(
            {"error": [], "result": {"last": 1}}
        ).encode(),
    )
    assert invalid.status is HistoricalAcquisitionStatus.INVALID


def test_partial_and_stale_statuses_are_machine_readable(tmp_path: Path) -> None:
    partial = run_historical_acquisition(
        _request(tmp_path / "partial", minimum_rows=5),
        transport=lambda _: _kraken_payload(),
    )
    assert partial.status is HistoricalAcquisitionStatus.PARTIAL
    assert partial.remediation

    stale = run_historical_acquisition(
        _request(tmp_path / "stale", freshness_max_age_seconds=1),
        transport=lambda _: _kraken_payload(),
    )
    assert stale.status is HistoricalAcquisitionStatus.STALE


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
            [
                "2024-07-31T00:00:00+00:00",
                "66000",
                "67000",
                "65000",
                "66500",
                "10",
            ]
        )
        writer.writerow(
            [
                "2024-08-01T00:00:00+00:00",
                "66500",
                "68000",
                "66000",
                "67500",
                "12",
            ]
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


def test_network_and_equity_policy_fail_closed(tmp_path: Path) -> None:
    network = run_historical_acquisition(
        _request(tmp_path, network_access_enabled=False)
    )
    assert network.status is HistoricalAcquisitionStatus.POLICY_BLOCKED

    equity = run_historical_acquisition(
        HistoricalAcquisitionRequest(
            provider_id=ProductionProvider.TWELVE_DATA,
            asset_class=HistoricalAssetClass.EQUITY,
            symbol="AAPL",
            timeframe="1d",
            storage_root=str(tmp_path / "equity"),
        )
    )
    assert equity.status is HistoricalAcquisitionStatus.POLICY_BLOCKED
    assert "csv-import-remains-supported" in equity.findings
    assert equity.dataset_revision_id is None


def test_primary_cli_help_and_blocked_equity_output(tmp_path: Path) -> None:
    help_result = runner.invoke(
        app,
        ["historical-data", "fetch", "--help"],
        color=False,
        terminal_width=200,
    )
    assert help_result.exit_code == 0
    for option in (
        "--start-at",
        "--end-at",
        "--expected-pair-key",
        "--minimum-rows",
        "--freshness-max-age-seconds",
        "--cancel-requested",
    ):
        assert option in help_result.stdout

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
    assert payload["status"] == "policy_blocked"
    assert payload["dataset_revision_id"] is None
    assert payload["redistribution_enabled"] is False
