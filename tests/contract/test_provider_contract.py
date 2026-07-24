from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from osca.instrument.api import AssetClass
from osca.provider.api import (
    AcquisitionRights,
    AuthenticationKind,
    DailyProviderRequest,
    ProviderCapability,
    ProviderDailyObservation,
    ProviderFailureCode,
    QuotaProfile,
    TimestampSemantics,
)
from osca.provider.application import DailyProviderAdapter, DailyProviderRouter
from osca.provider.infrastructure import SyntheticDailyProvider


def capability(asset_class: AssetClass, provider_id: str) -> ProviderCapability:
    return ProviderCapability(
        provider_id=provider_id,
        asset_classes=frozenset({asset_class}),
        earliest_date=date(2024, 1, 1),
        latest_completed_date=date(2024, 1, 3),
        timestamp_semantics=(
            TimestampSemantics.VENUE_SESSION_DATE
            if asset_class is AssetClass.STOCK
            else TimestampSemantics.UTC_INTERVAL_END
        ),
        authentication=AuthenticationKind.NONE,
        quota=QuotaProfile(
            maximum=10,
            window_seconds=60,
            retry_after_supported=False,
            maximum_attempts=1,
        ),
        rights=AcquisitionRights(
            retrieval=True,
            retention=True,
            transformation=True,
            export=True,
            backup=True,
            redistribution=True,
            fixture_redistribution=True,
            policy_revision="synthetic-v1",
        ),
    )


def observations(prefix: str) -> tuple[ProviderDailyObservation, ...]:
    return tuple(
        ProviderDailyObservation(
            effective_date=date(2024, 1, day),
            source_timestamp=datetime(2024, 1, day, 23, tzinfo=UTC),
            complete=True,
            open=Decimal("100.10") + day,
            high=Decimal("103.10") + day,
            low=Decimal("99.10") + day,
            close=Decimal("102.10") + day,
            volume=Decimal("1000") + day,
            currency="USD",
            source_identity=f"{prefix}-{day}",
        )
        for day in (1, 2, 3)
    )


@pytest.mark.parametrize(
    ("asset_class", "provider_id", "symbol"),
    [
        (AssetClass.STOCK, "synthetic-stock", "ACME"),
        (AssetClass.CRYPTO_PAIR, "synthetic-crypto", "BTCUSD"),
    ],
)
def test_stock_and_crypto_adapters_pass_one_contract(
    asset_class: AssetClass, provider_id: str, symbol: str
) -> None:
    adapter: DailyProviderAdapter = SyntheticDailyProvider(
        capability(asset_class, provider_id), observations(provider_id)
    )
    request = DailyProviderRequest(
        instrument_id=uuid4(),
        provider_symbol=symbol,
        start_date=date(2024, 1, 2),
        end_date_exclusive=date(2024, 1, 4),
    )
    result = adapter.retrieve_daily(request)
    assert result.failure is None
    assert tuple(item.effective_date for item in result.observations) == (
        date(2024, 1, 2),
        date(2024, 1, 3),
    )
    assert result.model_validate_json(result.model_dump_json()) == result


def test_policy_uncertainty_fails_closed() -> None:
    blocked = capability(AssetClass.STOCK, "synthetic-stock").model_copy(
        update={
            "rights": AcquisitionRights(
                retrieval=False,
                retention=False,
                transformation=False,
                export=False,
                backup=False,
                redistribution=False,
                fixture_redistribution=False,
                policy_revision="unknown",
            )
        }
    )
    adapter = SyntheticDailyProvider(blocked, observations("blocked"))
    result = adapter.retrieve_daily(
        DailyProviderRequest(
            instrument_id=uuid4(),
            provider_symbol="ACME",
            start_date=date(2024, 1, 1),
            end_date_exclusive=date(2024, 1, 2),
        )
    )
    assert result.failure is not None
    assert result.failure.code is ProviderFailureCode.POLICY
    assert result.observations == ()


def test_routing_fallback_is_visible_and_never_merges_series() -> None:
    unavailable_capability = capability(AssetClass.STOCK, "first").model_copy(
        update={"healthy": False}
    )
    first = SyntheticDailyProvider(unavailable_capability, observations("first"))
    second = SyntheticDailyProvider(
        capability(AssetClass.STOCK, "second"), observations("second")
    )
    router = DailyProviderRouter({"first": first, "second": second})
    provider_request = DailyProviderRequest(
        instrument_id=uuid4(),
        provider_symbol="ACME",
        start_date=date(2024, 1, 1),
        end_date_exclusive=date(2024, 1, 2),
    )
    routed = router.retrieve(
        provider_request,
        asset_class=AssetClass.STOCK,
        ordered_provider_ids=("first", "second"),
    )
    assert routed.result.provider_id == "second"
    assert routed.attempted_provider_ids == ("first", "second")
    assert routed.transitions == ("first:transport",)
    assert all(
        item.source_identity.startswith("second") for item in routed.result.observations
    )
