from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from osca.runtime_routing import (
    RuntimeRouter,
    RuntimeRoutingBatchOutcome,
    RuntimeRoutingCapability,
    RuntimeRoutingRequest,
    RuntimeRoutingSource,
    RuntimeRoutingStatus,
    routing_policy,
)
from osca.runtime_routing.cli import main


def test_local_ohlcv_payload_is_selected(tmp_path: Path) -> None:
    payload = tmp_path / "aapl.parquet"
    payload.write_bytes(b"governed-local-payload")

    decision = RuntimeRouter().route(
        RuntimeRoutingRequest(
            capability=RuntimeRoutingCapability.OHLCV,
            resource_id="AAPL",
            local_payload_uri=str(payload),
            timeframe="1d",
        ),
        storage_root=tmp_path,
    )

    assert decision.status is RuntimeRoutingStatus.SELECTED
    assert decision.selected_source is RuntimeRoutingSource.LOCAL_OHLCV
    assert decision.payload_uri == payload.resolve().as_uri()
    assert decision.network_access_used is False


def test_stale_local_payload_fails_closed_unless_allowed(tmp_path: Path) -> None:
    payload = tmp_path / "aapl.parquet"
    payload.write_bytes(b"governed-local-payload")
    requested_at = datetime(2100, 1, 1, tzinfo=UTC)

    blocked = RuntimeRouter().route(
        RuntimeRoutingRequest(
            capability=RuntimeRoutingCapability.OHLCV,
            resource_id="AAPL",
            local_payload_uri=str(payload),
            max_age_seconds=60,
            requested_at=requested_at,
        ),
        storage_root=tmp_path,
    )
    allowed = RuntimeRouter().route(
        RuntimeRoutingRequest(
            capability=RuntimeRoutingCapability.OHLCV,
            resource_id="AAPL",
            local_payload_uri=str(payload),
            max_age_seconds=60,
            allow_stale=True,
            requested_at=requested_at,
        ),
        storage_root=tmp_path,
    )

    assert blocked.status is RuntimeRoutingStatus.PROVIDER_UNAVAILABLE
    assert blocked.finding_ids == ("local-ohlcv-payload-stale",)
    assert allowed.status is RuntimeRoutingStatus.SELECTED
    assert allowed.stale is True
    assert allowed.finding_ids == ("selected-source-stale",)


def test_sec_company_facts_fixture_is_selected(tmp_path: Path) -> None:
    fixture = Path(
        "tests/fixtures/provider_preview/sec_companyfacts_aapl.json"
    )

    decision = RuntimeRouter().route(
        RuntimeRoutingRequest(
            capability=RuntimeRoutingCapability.COMPANY_FACTS,
            resource_id="320193",
            fixture_path=fixture,
        ),
        storage_root=tmp_path,
    )

    assert decision.status is RuntimeRoutingStatus.SELECTED
    assert decision.selected_source is RuntimeRoutingSource.SEC_EDGAR_FIXTURE
    assert decision.provider_id is not None
    assert decision.network_access_used is False


def test_sec_request_without_explicit_source_is_unavailable(tmp_path: Path) -> None:
    decision = RuntimeRouter().route(
        RuntimeRoutingRequest(
            capability=RuntimeRoutingCapability.FILINGS,
            resource_id="320193",
        ),
        storage_root=tmp_path,
    )

    assert decision.status is RuntimeRoutingStatus.PROVIDER_UNAVAILABLE
    assert decision.finding_ids == ("sec-source-not-supplied",)


def test_fred_macro_request_is_policy_blocked_without_secret_resolution(
    tmp_path: Path,
) -> None:
    decision = RuntimeRouter().route(
        RuntimeRoutingRequest(
            capability=RuntimeRoutingCapability.MACRO_SERIES,
            resource_id="CPIAUCSL",
            preferred_provider="fred",
            network_access_enabled=True,
            secret_reference="secret:fred-api-key",
        ),
        storage_root=tmp_path,
    )

    assert decision.status is RuntimeRoutingStatus.POLICY_BLOCKED
    assert decision.selected_source is None
    assert decision.payload_uri is None
    assert decision.network_access_used is False
    assert decision.credential_materialized is False


def test_unapproved_macro_provider_is_unavailable(tmp_path: Path) -> None:
    decision = RuntimeRouter().route(
        RuntimeRoutingRequest(
            capability=RuntimeRoutingCapability.MACRO_SERIES,
            resource_id="GDP",
            preferred_provider="unconfigured-macro-source",
        ),
        storage_root=tmp_path,
    )

    assert decision.status is RuntimeRoutingStatus.PROVIDER_UNAVAILABLE
    assert decision.finding_ids == ("macro-provider-unavailable",)


def test_macro_block_does_not_stop_non_macro_batch(tmp_path: Path) -> None:
    payload = tmp_path / "aapl.parquet"
    payload.write_bytes(b"governed-local-payload")

    result = RuntimeRouter().route_many(
        (
            RuntimeRoutingRequest(
                capability=RuntimeRoutingCapability.OHLCV,
                resource_id="AAPL",
                local_payload_uri=str(payload),
            ),
            RuntimeRoutingRequest(
                capability=RuntimeRoutingCapability.MACRO_SERIES,
                resource_id="CPIAUCSL",
            ),
        ),
        storage_root=tmp_path,
    )

    assert result.outcome is RuntimeRoutingBatchOutcome.PARTIAL
    assert result.selected_count == 1
    assert result.policy_blocked_count == 1
    assert result.non_macro_continued is True


def test_capability_options_reject_silent_source_blending() -> None:
    with pytest.raises(ValidationError, match="cannot combine fixture and live"):
        RuntimeRoutingRequest(
            capability=RuntimeRoutingCapability.COMPANY_FACTS,
            resource_id="320193",
            fixture_path=Path("fixture.json"),
            network_access_enabled=True,
            user_agent="OSCA Team ops@garaged.dev",
        )


def test_policy_surface_declares_macro_block_and_local_independence() -> None:
    policy = {entry["capability"]: entry for entry in routing_policy()}

    assert policy["ohlcv"]["source_precedence"] == ("local_ohlcv",)
    assert policy["macro_series"]["source_precedence"] == ()
    assert policy["macro_series"]["missing_source_status"] == "policy_blocked"


def test_macro_cli_returns_structured_policy_block(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["macro-series", "CPIAUCSL"])
    output = capsys.readouterr().out

    assert exit_code == 2
    assert '"status": "policy_blocked"' in output
    assert '"network_access_used": false' in output
