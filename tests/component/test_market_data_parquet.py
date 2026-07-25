from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from osca.market_data.api import CanonicalDailyBar, CanonicalOhlcvBar, MarketDataInterval
from osca.market_data.application import (
    CanonicalPublicationIntent,
    CanonicalPublisher,
    OhlcvPublicationIntent,
    OhlcvPublisher,
)
from osca.market_data.infrastructure import (
    DAILY_BAR_SCHEMA,
    OHLCV_BAR_SCHEMA,
    ImmutablePayloadStore,
    MarketDataBase,
    PyArrowCanonicalCodec,
    PyArrowOhlcvCodec,
    SqliteManifestRepository,
    deserialize_daily_bars,
    deserialize_ohlcv_bars,
    payload_digest,
    serialize_daily_bars,
    serialize_ohlcv_bars,
)


def bar(day: int) -> CanonicalDailyBar:
    return CanonicalDailyBar(
        instrument_id=INSTRUMENT_ID,
        effective_date=date(2024, 1, day),
        source_timestamp=datetime(2024, 1, day + 1, tzinfo=UTC),
        open=Decimal("100.100000000000000000"),
        high=Decimal("103.100000000000000000"),
        low=Decimal("99.100000000000000000"),
        close=Decimal("102.100000000000000000"),
        volume=Decimal("1000.000000000000000000"),
        currency="USD",
        volume_unit="shares",
        provider_id="synthetic",
        source_identity=f"fixture-{day}",
        request_id=uuid4(),
        normalization_revision="1.0.0",
    )


def ohlcv_bar(hour: int, interval: MarketDataInterval = MarketDataInterval.H1) -> CanonicalOhlcvBar:
    starts_at = datetime(2024, 1, 2, hour, tzinfo=UTC)
    seconds = {
        MarketDataInterval.M1: 60,
        MarketDataInterval.M5: 5 * 60,
        MarketDataInterval.M15: 15 * 60,
        MarketDataInterval.M30: 30 * 60,
        MarketDataInterval.H1: 60 * 60,
        MarketDataInterval.H4: 4 * 60 * 60,
        MarketDataInterval.D1: 24 * 60 * 60,
    }[interval]
    return CanonicalOhlcvBar(
        instrument_id=INSTRUMENT_ID,
        interval=interval,
        starts_at=starts_at,
        ends_at=starts_at + timedelta(seconds=seconds),
        effective_date=starts_at.date(),
        open=Decimal("100.100000000000000000"),
        high=Decimal("103.100000000000000000"),
        low=Decimal("99.100000000000000000"),
        close=Decimal("102.100000000000000000"),
        volume=Decimal("1000.000000000000000000"),
        currency="USD",
        volume_unit="shares",
        provider_id="synthetic",
        source_identity=f"fixture-h{hour}",
        request_id=uuid4(),
        normalization_revision="1.0.0",
        calendar_revision="xnys-test-v1",
    )


INSTRUMENT_ID = uuid4()


def test_parquet_round_trip_has_exact_governed_schema() -> None:
    original = (bar(2), bar(1))
    payload = serialize_daily_bars(original)
    restored = deserialize_daily_bars(payload)
    assert tuple(item.effective_date for item in restored) == (date(2024, 1, 1), date(2024, 1, 2))
    assert restored[0].open == Decimal("100.100000000000000000")
    metadata = pq.read_metadata(pa.BufferReader(payload))
    assert metadata.schema.to_arrow_schema().equals(DAILY_BAR_SCHEMA, check_metadata=True)


def test_ohlcv_parquet_round_trip_has_exact_governed_schema() -> None:
    original = (ohlcv_bar(2), ohlcv_bar(1))
    payload = serialize_ohlcv_bars(original)
    restored = deserialize_ohlcv_bars(payload)
    assert tuple(item.starts_at.hour for item in restored) == (1, 2)
    assert restored[0].interval == "1h"
    assert restored[0].calendar_revision == "xnys-test-v1"
    metadata = pq.read_metadata(pa.BufferReader(payload))
    assert metadata.schema.to_arrow_schema().equals(OHLCV_BAR_SCHEMA, check_metadata=True)


def test_immutable_store_is_idempotent_and_rejects_replacement(tmp_path: Path) -> None:
    store = ImmutablePayloadStore(tmp_path)
    payload = serialize_daily_bars((bar(1),))
    destination = store.publish("canonical/instrument/revision.parquet", payload)
    assert store.publish("canonical/instrument/revision.parquet", payload) == destination
    assert payload_digest(destination.read_bytes()) == payload_digest(payload)
    with pytest.raises(FileExistsError):
        store.publish("canonical/instrument/revision.parquet", payload + b"changed")
    with pytest.raises(ValueError):
        store.publish("../escape.parquet", payload)


def test_staged_publisher_is_content_idempotent(tmp_path: Path) -> None:
    engine = create_engine("sqlite://")
    MarketDataBase.metadata.create_all(engine)
    intent = CanonicalPublicationIntent(
        dataset_id=uuid4(),
        revision=1,
        fingerprint="sha256:" + "d" * 64,
        instrument_id=INSTRUMENT_ID,
        provider_id="synthetic",
        source_context="fixture-v1",
        start_date=date(2024, 1, 1),
        end_date_exclusive=date(2024, 1, 2),
        retention_policy_revision="synthetic-v1",
        backup_permitted=True,
    )
    with Session(engine) as session, session.begin():
        publisher = CanonicalPublisher(
            SqliteManifestRepository(session),
            ImmutablePayloadStore(tmp_path),
            PyArrowCanonicalCodec(),
        )
        first = publisher.publish(intent, (bar(1),))
        second = publisher.publish(intent, (bar(1),))
        assert second == first
        assert first.state == "ready"
        assert first.interval == "1d"
        assert first.protected is True
        assert (tmp_path / first.object_key).is_file()


def test_ohlcv_publisher_is_interval_scoped_and_content_idempotent(tmp_path: Path) -> None:
    engine = create_engine("sqlite://")
    MarketDataBase.metadata.create_all(engine)
    intent = OhlcvPublicationIntent(
        dataset_id=uuid4(),
        revision=1,
        fingerprint="sha256:" + "e" * 64,
        instrument_id=INSTRUMENT_ID,
        provider_id="synthetic",
        source_context="fixture-h1-v1",
        interval="1h",
        start_date=date(2024, 1, 2),
        end_date_exclusive=date(2024, 1, 3),
        retention_policy_revision="synthetic-v1",
        backup_permitted=True,
    )
    with Session(engine) as session, session.begin():
        publisher = OhlcvPublisher(
            SqliteManifestRepository(session),
            ImmutablePayloadStore(tmp_path),
            PyArrowOhlcvCodec(),
        )
        first = publisher.publish(intent, (ohlcv_bar(2), ohlcv_bar(1)))
        second = publisher.publish(intent, (ohlcv_bar(2), ohlcv_bar(1)))
        assert second == first
        assert first.state == "ready"
        assert first.interval == "1h"
        assert first.row_count == 2
        assert first.protected is True
        assert "/1h/" in first.object_key
        assert (tmp_path / first.object_key).is_file()


def test_ohlcv_publisher_rejects_mismatched_interval(tmp_path: Path) -> None:
    engine = create_engine("sqlite://")
    MarketDataBase.metadata.create_all(engine)
    intent = OhlcvPublicationIntent(
        dataset_id=uuid4(),
        revision=1,
        fingerprint="sha256:" + "f" * 64,
        instrument_id=INSTRUMENT_ID,
        provider_id="synthetic",
        source_context="fixture-h1-v1",
        interval="1h",
        start_date=date(2024, 1, 2),
        end_date_exclusive=date(2024, 1, 3),
        retention_policy_revision="synthetic-v1",
        backup_permitted=True,
    )
    with Session(engine) as session, session.begin():
        publisher = OhlcvPublisher(
            SqliteManifestRepository(session),
            ImmutablePayloadStore(tmp_path),
            PyArrowOhlcvCodec(),
        )
        with pytest.raises(ValueError, match="declared interval"):
            publisher.publish(intent, (ohlcv_bar(1, MarketDataInterval.M5),))
