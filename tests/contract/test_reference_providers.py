from datetime import UTC, date, datetime
from typing import Any
from uuid import uuid4

import pytest

from osca.instrument.api import AssetClass
from osca.provider.api import (
    AcquisitionRights,
    AuthenticationKind,
    DailyProviderRequest,
    ProviderCapability,
    QuotaProfile,
    TimestampSemantics,
)
from osca.provider.application.ports import DailyProviderAdapter
from osca.provider.infrastructure import KrakenDailyProvider, TwelveDataDailyProvider


def capability(provider_id: str, asset_class: AssetClass) -> ProviderCapability:
    return ProviderCapability(
        provider_id=provider_id,
        asset_classes=frozenset({asset_class}),
        earliest_date=date(2020, 1, 1),
        latest_completed_date=date(2024, 1, 2),
        timestamp_semantics=(
            TimestampSemantics.VENUE_SESSION_DATE
            if asset_class is AssetClass.STOCK
            else TimestampSemantics.UTC_INTERVAL_END
        ),
        authentication=(
            AuthenticationKind.NAMED_SECRET
            if provider_id == "twelve-data"
            else AuthenticationKind.NONE
        ),
        credential_reference=(
            "provider.twelve-data.api-key" if provider_id == "twelve-data" else None
        ),
        quota=QuotaProfile(
            maximum=8,
            window_seconds=60,
            retry_after_supported=True,
            maximum_attempts=2,
        ),
        rights=AcquisitionRights(
            retrieval=True,
            retention=True,
            transformation=True,
            export=False,
            backup=False,
            redistribution=False,
            fixture_redistribution=False,
            policy_revision="evaluation-fixture-v1",
        ),
    )


def request(symbol: str) -> DailyProviderRequest:
    return DailyProviderRequest(
        instrument_id=uuid4(),
        provider_symbol=symbol,
        start_date=date(2024, 1, 1),
        end_date_exclusive=date(2024, 1, 4),
    )


@pytest.mark.parametrize("adapter_name", ["twelve-data", "kraken"])
def test_reference_adapters_emit_one_governed_contract(adapter_name: str) -> None:
    adapter: DailyProviderAdapter
    if adapter_name == "twelve-data":
        payload: dict[str, Any] = {
            "values": [
                {
                    "datetime": "2024-01-02",
                    "open": "10.1",
                    "high": "12.0",
                    "low": "9.8",
                    "close": "11.5",
                    "volume": "1000",
                },
                {
                    "datetime": "2024-01-01",
                    "open": "9.1",
                    "high": "10.2",
                    "low": "8.9",
                    "close": "10.0",
                    "volume": "900",
                },
            ]
        }
        adapter = TwelveDataDailyProvider(
            capability("twelve-data", AssetClass.STOCK), lambda _: payload, "USD"
        )
        provider_request = request("ACME")
    else:
        first = int(datetime(2024, 1, 1, tzinfo=UTC).timestamp())
        payload = {
            "error": [],
            "result": {
                "XXBTZUSD": [
                    [first, "9.1", "10.2", "8.9", "10.0", "9.8", "900", 2],
                    [first + 86400, "10.1", "12.0", "9.8", "11.5", "11", "1000", 3],
                ],
                "last": first + 86400,
            },
        }
        adapter = KrakenDailyProvider(
            capability("kraken", AssetClass.CRYPTO_PAIR), lambda _: payload, "USD"
        )
        provider_request = request("XBTUSD")
    result = adapter.retrieve_daily(provider_request)
    assert result.failure is None
    assert tuple(item.effective_date for item in result.observations) == (
        date(2024, 1, 1),
        date(2024, 1, 2),
    )
    assert all(item.complete for item in result.observations)
