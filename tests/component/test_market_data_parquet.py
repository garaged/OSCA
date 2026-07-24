from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from osca.market_data.api import CanonicalDailyBar
from osca.market_data.application import CanonicalPublicationIntent, CanonicalPublisher
from osca.market_data.infrastructure import (
    DAILY_BAR_SCHEMA,
    ImmutablePayloadStore,
    MarketDataBase,
    PyArrowCanonicalCodec,
    SqliteManifestRepository,
    deserialize_daily_bars,
    payload_digest,
    serialize_daily_bars,
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


INSTRUMENT_ID = uuid4()


def test_parquet_round_trip_has_exact_governed_schema() -> None:
    original = (bar(2), bar(1))
    payload = serialize_daily_bars(original)
    restored = deserialize_daily_bars(payload)
    assert tuple(item.effective_date for item in restored) == (date(2024, 1, 1), date(2024, 1, 2))
    assert restored[0].open == Decimal("100.100000000000000000")
    metadata = pq.read_metadata(pa.BufferReader(payload))
    assert metadata.schema.to_arrow_schema().equals(DAILY_BAR_SCHEMA, check_metadata=True)


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
        assert first.protected is True
        assert (tmp_path / first.object_key).is_file()
