from __future__ import annotations

import json
from pathlib import Path

from osca.production_ingestion import (
    AdmissionStatus,
    IngestionStatus,
    ProductionIngestionRequest,
    ProductionProvider,
    admission_for,
    provider_admission_policy,
    run_production_ingestion,
)
from osca.production_ingestion.cli import main


def _request(tmp_path: Path, provider: ProductionProvider) -> ProductionIngestionRequest:
    if provider is ProductionProvider.SEC_EDGAR:
        return ProductionIngestionRequest(
            provider_id=provider,
            resource_id="company_facts",
            endpoint_url="https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json",
            storage_root=str(tmp_path),
            network_access_enabled=True,
            user_agent="OSCA test contact@example.com",
        )
    return ProductionIngestionRequest(
        provider_id=provider,
        resource_id="spot_ohlc",
        endpoint_url="https://api.kraken.com/0/public/OHLC?pair=XBTUSD&interval=1440",
        storage_root=str(tmp_path),
        network_access_enabled=True,
    )


def test_admission_matrix_approves_only_sec_and_kraken() -> None:
    policy = provider_admission_policy()
    approved = {
        decision.provider_id
        for decision in policy
        if decision.status is AdmissionStatus.APPROVED
    }
    assert approved == {ProductionProvider.SEC_EDGAR, ProductionProvider.KRAKEN}
    assert admission_for(ProductionProvider.FRED).status is AdmissionStatus.POLICY_BLOCKED
    assert admission_for(ProductionProvider.TWELVE_DATA).status is AdmissionStatus.NEEDS_EVIDENCE


def test_network_access_is_explicit(tmp_path: Path) -> None:
    request = _request(tmp_path, ProductionProvider.KRAKEN).model_copy(
        update={"network_access_enabled": False}
    )
    evidence = run_production_ingestion(request, transport=lambda _: b"{}")
    assert evidence.status is IngestionStatus.POLICY_BLOCKED
    assert not evidence.network_used
    assert "network-access-not-enabled" in evidence.findings


def test_non_admitted_provider_fails_closed(tmp_path: Path) -> None:
    request = ProductionIngestionRequest(
        provider_id=ProductionProvider.TWELVE_DATA,
        resource_id="time_series",
        endpoint_url="https://api.twelvedata.com/time_series",
        storage_root=str(tmp_path),
        network_access_enabled=True,
    )
    evidence = run_production_ingestion(request, transport=lambda _: b"{}")
    assert evidence.status is IngestionStatus.PROVIDER_UNAVAILABLE
    assert not evidence.network_used


def test_endpoint_allowlist_blocks_wrong_host(tmp_path: Path) -> None:
    request = _request(tmp_path, ProductionProvider.KRAKEN).model_copy(
        update={"endpoint_url": "https://example.com/0/public/OHLC"}
    )
    evidence = run_production_ingestion(request, transport=lambda _: b"{}")
    assert evidence.status is IngestionStatus.POLICY_BLOCKED
    assert "host-not-allowed" in evidence.findings


def test_success_retains_payload_and_metadata(tmp_path: Path) -> None:
    payload = json.dumps({"error": [], "result": {"XXBTZUSD": []}}).encode()
    evidence = run_production_ingestion(
        _request(tmp_path, ProductionProvider.KRAKEN),
        transport=lambda _: payload,
    )
    assert evidence.status is IngestionStatus.SUCCEEDED
    assert evidence.network_used
    assert evidence.payload_uri is not None
    assert evidence.metadata_uri is not None
    assert Path(evidence.payload_uri.removeprefix("file://")).read_bytes() == payload
    metadata = json.loads(Path(evidence.metadata_uri.removeprefix("file://")).read_text())
    assert metadata["payload_sha256"] == evidence.payload_sha256


def test_invalid_json_retries_then_fails(tmp_path: Path) -> None:
    attempts = 0

    def transport(_: ProductionIngestionRequest) -> bytes:
        nonlocal attempts
        attempts += 1
        return b"not-json"

    request = _request(tmp_path, ProductionProvider.KRAKEN).model_copy(
        update={"max_attempts": 2}
    )
    evidence = run_production_ingestion(request, transport=transport)
    assert evidence.status is IngestionStatus.FAILED
    assert attempts == 2
    assert evidence.attempt_count == 2


def test_response_size_limit_fails_closed(tmp_path: Path) -> None:
    request = _request(tmp_path, ProductionProvider.KRAKEN).model_copy(
        update={"max_response_bytes": 2}
    )
    evidence = run_production_ingestion(request, transport=lambda _: b"{}\n")
    assert evidence.status is IngestionStatus.FAILED
    assert "response-size-limit-exceeded" in evidence.findings


def test_policy_cli_is_network_free(capsys: object) -> None:
    assert main(["policy"]) == 0
    output = capsys.readouterr().out  # type: ignore[attr-defined]
    assert '"sec_edgar"' in output
    assert '"fred"' in output
