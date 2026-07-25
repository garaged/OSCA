from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from osca.market_data.api.temporal import (
    CanonicalOhlcvBar,
    ExchangeSession,
    MarketDataInterval,
    SessionState,
)
from osca.market_data.application.temporal import (
    classify_temporal_gaps,
    completed_bar_window,
    crypto_expected_windows,
    resample_ohlcv,
    stock_expected_windows,
    temporal_repair_windows,
)


def test_approved_intervals_are_exact_and_completed_bar_semantics_use_cutoff() -> None:
    assert [item.value for item in MarketDataInterval] == [
        "1m",
        "5m",
        "15m",
        "30m",
        "1h",
        "4h",
        "1d",
    ]
    window = completed_bar_window(
        moment=datetime(2024, 1, 2, 10, 7, 30, tzinfo=UTC),
        interval=MarketDataInterval.M5,
        publication_lag=timedelta(seconds=30),
    )
    assert window.starts_at == datetime(2024, 1, 2, 10, 0, tzinfo=UTC)
    assert window.ends_at == datetime(2024, 1, 2, 10, 5, tzinfo=UTC)


def test_stock_sessions_drive_expected_windows_and_gap_repair() -> None:
    instrument_id = uuid4()
    session = ExchangeSession(
        session_date=date(2024, 1, 2),
        opens_at=datetime(2024, 1, 2, 14, 30, tzinfo=UTC),
        closes_at=datetime(2024, 1, 2, 14, 45, tzinfo=UTC),
        state=SessionState.OPEN,
        venue="XNYS",
        calendar_revision="xnys-test-v1",
    )
    windows = stock_expected_windows(session=session, interval=MarketDataInterval.M5)
    assert len(windows) == 3
    gaps = classify_temporal_gaps(
        instrument_id=instrument_id,
        interval=MarketDataInterval.M5,
        expected_windows=windows,
        observed_windows=frozenset({(windows[0].starts_at, windows[0].ends_at)}),
        current_completed_end=datetime(2024, 1, 2, 14, 45, tzinfo=UTC),
        calendar_revision=session.calendar_revision,
    )
    assert [gap.state for gap in gaps] == ["observed", "missing", "missing"]
    assert [gap.repair_eligible for gap in gaps] == [False, True, True]
    assert temporal_repair_windows(gaps) == windows[1:]


def test_unknown_stock_calendar_is_unresolved_not_missing() -> None:
    gaps = classify_temporal_gaps(
        instrument_id=uuid4(),
        interval=MarketDataInterval.H1,
        expected_windows=None,
        observed_windows=frozenset(),
        current_completed_end=datetime(2024, 1, 2, 15, tzinfo=UTC),
        calendar_revision="xnys-unresolved",
    )
    assert len(gaps) == 1
    assert gaps[0].state == "unresolved"
    assert gaps[0].repair_eligible is False
    assert temporal_repair_windows(gaps) == ()


def test_crypto_utc_day_boundaries_are_interval_aware() -> None:
    windows = crypto_expected_windows(
        day_start=datetime.combine(date(2024, 1, 2), time.min, tzinfo=UTC),
        interval=MarketDataInterval.H4,
    )
    assert len(windows) == 6
    assert windows[0].starts_at == datetime(2024, 1, 2, tzinfo=UTC)
    assert windows[-1].ends_at == datetime(2024, 1, 3, tzinfo=UTC)


def bar(start_hour: int, close: str) -> CanonicalOhlcvBar:
    start = datetime(2024, 1, 2, start_hour, tzinfo=UTC)
    return CanonicalOhlcvBar(
        instrument_id=INSTRUMENT_ID,
        interval=MarketDataInterval.H1,
        starts_at=start,
        ends_at=start + timedelta(hours=1),
        effective_date=start.date(),
        open=Decimal("10"),
        high=Decimal("15"),
        low=Decimal("9"),
        close=Decimal(close),
        volume=Decimal("100"),
        currency="USD",
        volume_unit="shares",
        provider_id="synthetic",
        source_identity=f"h{start_hour}",
        request_id=uuid4(),
        normalization_revision="1.0.0",
        calendar_revision="xnys-test-v1",
    )


INSTRUMENT_ID = uuid4()


def test_resampling_requires_complete_lower_interval_lineage() -> None:
    output = resample_ohlcv(
        (bar(0, "11"), bar(1, "12"), bar(2, "13"), bar(3, "14")),
        target_interval=MarketDataInterval.H4,
        request_id=uuid4(),
    )
    assert len(output) == 1
    resampled, lineage = output[0]
    assert resampled.interval == "4h"
    assert resampled.open == Decimal("10")
    assert resampled.close == Decimal("14")
    assert resampled.volume == Decimal("400")
    assert lineage.source_interval == "1h"
    assert lineage.target_interval == "4h"
    assert len(lineage.source_bar_ids) == 4

    assert (
        resample_ohlcv((bar(0, "11"), bar(1, "12")), target_interval=MarketDataInterval.H4)
        == ()
    )


def test_intraday_bar_contract_rejects_float_and_wrong_duration() -> None:
    with pytest.raises(ValidationError):
        CanonicalOhlcvBar(
            instrument_id=uuid4(),
            interval=MarketDataInterval.M5,
            starts_at=datetime(2024, 1, 2, 10, tzinfo=UTC),
            ends_at=datetime(2024, 1, 2, 10, 6, tzinfo=UTC),
            effective_date=date(2024, 1, 2),
            open=Decimal("1"),
            high=Decimal("2"),
            low=Decimal("1"),
            close=1.5,
            volume=Decimal("10"),
            currency="USD",
            volume_unit="shares",
            provider_id="synthetic",
            source_identity="bad",
            request_id=uuid4(),
            normalization_revision="1.0.0",
            calendar_revision="test-v1",
        )
