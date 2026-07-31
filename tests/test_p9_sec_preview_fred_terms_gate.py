import json
from collections.abc import Mapping
from pathlib import Path

import pytest
from pydantic import ValidationError

from osca.provider_adapters import ProviderAdapterEndpoint
from osca.provider_preview import (
    FredPreviewRequest,
    ProviderPreviewMode,
    ProviderPreviewOutcome,
    SecFairAccessGate,
    SecPreviewRequest,
    SecPreviewService,
    evaluate_fred_preview,
)
from osca.provider_preview.cli import main


class FakeTransport:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload
        self.calls: list[tuple[str, Mapping[str, str]]] = []

    def get(
        self,
        *,
        url: str,
        headers: Mapping[str, str],
        timeout_seconds: float,
        max_response_bytes: int,
    ) -> bytes:
        assert timeout_seconds == 15.0
        assert max_response_bytes == 5_000_000
        self.calls.append((url, headers))
        return self.payload


def fixture_path() -> Path:
    return Path("tests/fixtures/provider_preview/sec_companyfacts_aapl.json")


def test_sec_fixture_replay_is_network_disabled_and_evidence_only(tmp_path: Path) -> None:
    request = SecPreviewRequest(
        endpoint=ProviderAdapterEndpoint.SEC_COMPANY_FACTS,
        cik="320193",
        fixture_path=fixture_path(),
    )

    evidence = SecPreviewService().run(request, storage_root=tmp_path)

    assert evidence.mode is ProviderPreviewMode.FIXTURE_REPLAY
    assert evidence.outcome is ProviderPreviewOutcome.SUCCEEDED
    assert evidence.record_count == 3
    assert not evidence.network_access_used
    assert not evidence.network_access_enabled
    assert evidence.evidence_only
    assert not evidence.production_ingestion_enabled
    assert not evidence.recommendations_enabled
    assert not evidence.real_capital_orders_enabled


def test_sec_live_preview_requires_explicit_network_and_real_identity() -> None:
    with pytest.raises(ValidationError, match="fixture_path or explicit network"):
        SecPreviewRequest(
            endpoint=ProviderAdapterEndpoint.SEC_COMPANY_FACTS,
            cik="320193",
        )

    with pytest.raises(ValidationError, match="organization and contact email"):
        SecPreviewRequest(
            endpoint=ProviderAdapterEndpoint.SEC_COMPANY_FACTS,
            cik="320193",
            network_access_enabled=True,
            user_agent="OSCA",
        )

    with pytest.raises(ValidationError, match="placeholder identity"):
        SecPreviewRequest(
            endpoint=ProviderAdapterEndpoint.SEC_COMPANY_FACTS,
            cik="320193",
            network_access_enabled=True,
            user_agent="Sample Company admin@example.com",
        )


def test_sec_live_preview_writes_bounded_cache_and_reuses_it(tmp_path: Path) -> None:
    payload = fixture_path().read_bytes()
    transport = FakeTransport(payload)
    service = SecPreviewService(transport=transport)
    request = SecPreviewRequest(
        endpoint=ProviderAdapterEndpoint.SEC_COMPANY_FACTS,
        cik="CIK320193",
        network_access_enabled=True,
        user_agent="OSCA Research admin@garaged.example",
    )

    first = service.run(request, storage_root=tmp_path)
    second = service.run(request, storage_root=tmp_path)

    assert first.outcome is ProviderPreviewOutcome.SUCCEEDED
    assert first.network_access_used
    assert second.outcome is ProviderPreviewOutcome.CACHE_HIT
    assert second.cache_hit
    assert not second.network_access_used
    assert len(transport.calls) == 1
    url, headers = transport.calls[0]
    assert url == (
        "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json"
    )
    assert headers["User-Agent"] == "OSCA Research admin@garaged.example"
    assert first.payload_uri is not None
    assert first.metadata_uri is not None
    assert Path(first.payload_uri.removeprefix("file://")).is_file()
    assert Path(first.metadata_uri.removeprefix("file://")).is_file()


def test_sec_fair_access_gate_stays_below_official_maximum() -> None:
    with pytest.raises(ValueError, match="at most 9 rps"):
        SecFairAccessGate(requests_per_second=10.0)

    moments = iter((0.0, 0.1, 0.5))
    sleeps: list[float] = []
    gate = SecFairAccessGate(
        requests_per_second=2.0,
        monotonic=lambda: next(moments),
        sleeper=sleeps.append,
    )

    gate.wait()
    gate.wait()

    assert sleeps == [pytest.approx(0.4)]


def test_fred_live_preview_is_policy_blocked_without_resolving_secret() -> None:
    request = FredPreviewRequest(
        series_id="CPIAUCSL",
        network_access_enabled=True,
        secret_reference="secret:fred/default",
    )

    evidence = evaluate_fred_preview(request)

    assert evidence.mode is ProviderPreviewMode.POLICY_BLOCKED
    assert evidence.outcome is ProviderPreviewOutcome.BLOCKED
    assert not evidence.network_access_used
    assert not evidence.credential_materialized
    assert evidence.payload_uri is None
    assert "fred-content-retention-not-permitted" in evidence.finding_ids
    assert "fred-secret-reference-not-resolved" in evidence.finding_ids


def test_fred_request_rejects_embedded_secret_values() -> None:
    with pytest.raises(ValidationError, match="named secret references"):
        FredPreviewRequest(series_id="GDP", secret_reference="abcdef")

    with pytest.raises(ValidationError, match="must not contain secret values"):
        FredPreviewRequest(
            series_id="GDP",
            secret_reference="secret:fred/key=abcdef",
        )


def test_module_cli_replays_sec_fixture_and_reports_fred_block(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    sec_exit = main(
        [
            "sec-company-facts",
            "320193",
            "--fixture-file",
            str(fixture_path()),
            "--storage-root",
            str(tmp_path),
        ]
    )
    sec_output = json.loads(capsys.readouterr().out)

    fred_exit = main(["fred-series", "GDP", "--enable-network"])
    fred_output = json.loads(capsys.readouterr().out)

    assert sec_exit == 0
    assert sec_output["mode"] == "fixture_replay"
    assert fred_exit == 2
    assert fred_output["outcome"] == "blocked"
