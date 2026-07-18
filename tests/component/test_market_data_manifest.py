from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from osca.market_data.api import (
    CanonicalDailyBar,
    DatasetLayer,
    DatasetManifest,
    ManifestState,
    canonical_fingerprint,
)
from osca.market_data.application import IncompleteObservationError, normalize_daily
from osca.market_data.infrastructure import MarketDataBase, SqliteManifestRepository
from osca.provider.api import ProviderDailyObservation


def observation(*, complete: bool = True) -> ProviderDailyObservation:
    return ProviderDailyObservation(
        effective_date=date(2024, 1, 2),
        source_timestamp=datetime(2024, 1, 3, tzinfo=UTC),
        complete=complete,
        open=Decimal("1.000000000000000001"),
        high=Decimal("2"),
        low=Decimal("0.5"),
        close=Decimal("1.5"),
        volume=Decimal("3.000000000000000001"),
        currency="USD",
        source_identity="fixture-1",
    )


def test_normalization_preserves_decimal_38_18_and_rejects_incomplete() -> None:
    request_id = uuid4()
    bar = normalize_daily(
        observation(),
        instrument_id=uuid4(),
        provider_id="synthetic",
        request_id=request_id,
        volume_unit="units",
        normalization_revision="norm-v1",
    )
    assert bar.open == Decimal("1.000000000000000001")
    assert bar.volume == Decimal("3.000000000000000001")
    with pytest.raises(IncompleteObservationError):
        normalize_daily(
            observation(complete=False),
            instrument_id=uuid4(),
            provider_id="synthetic",
            request_id=request_id,
            volume_unit="units",
            normalization_revision="norm-v1",
        )
    with pytest.raises(ValidationError):
        CanonicalDailyBar.model_validate({**bar.model_dump(), "open": 1.1})


def test_manifest_is_idempotent_by_fingerprint_and_canonical_is_protected() -> None:
    engine = create_engine("sqlite://")
    MarketDataBase.metadata.create_all(engine)
    fingerprint = canonical_fingerprint({"bars": ["fixture-1"], "normalizer": "norm-v1"})
    manifest = DatasetManifest(
        revision=1,
        fingerprint=fingerprint,
        layer=DatasetLayer.CANONICAL,
        state=ManifestState.READY,
        instrument_id=uuid4(),
        provider_id="synthetic",
        source_context="fixture",
        start_date=date(2024, 1, 2),
        end_date_exclusive=date(2024, 1, 3),
        schema_revision="1.0.0",
        row_count=1,
        byte_size=100,
        content_digest="sha256:" + "a" * 64,
        object_key="canonical/aa/object.parquet",
        retention_policy_revision="synthetic-v1",
        backup_permitted=True,
        protected=True,
    )
    with Session(engine) as session, session.begin():
        repository = SqliteManifestRepository(session)
        repository.add(manifest)
        assert repository.by_fingerprint(fingerprint) == manifest
        assert repository.ready(manifest.dataset_id) == (manifest,)
    with pytest.raises(ValidationError):
        DatasetManifest(
            **manifest.model_dump(exclude={"manifest_id", "protected"}),
            protected=False,
        )


def test_manifest_publication_transition_is_compare_and_set() -> None:
    engine = create_engine("sqlite://")
    MarketDataBase.metadata.create_all(engine)
    manifest = DatasetManifest(
        revision=1,
        fingerprint="sha256:" + "b" * 64,
        layer=DatasetLayer.CANONICAL,
        state=ManifestState.STAGING,
        instrument_id=uuid4(),
        provider_id="synthetic",
        source_context="fixture",
        start_date=date(2024, 1, 2),
        end_date_exclusive=date(2024, 1, 3),
        schema_revision="1.0.0",
        row_count=1,
        byte_size=100,
        content_digest="sha256:" + "a" * 64,
        object_key="canonical/aa/staged.parquet",
        retention_policy_revision="synthetic-v1",
        backup_permitted=True,
        protected=True,
    )
    with Session(engine) as session, session.begin():
        repository = SqliteManifestRepository(session)
        repository.add(manifest)
        ready = repository.transition(
            manifest.manifest_id,
            expected=ManifestState.STAGING,
            target=ManifestState.READY,
        )
        assert ready.state is ManifestState.READY
        assert repository.ready(manifest.dataset_id) == (ready,)
        with pytest.raises(ValueError, match="changed"):
            repository.transition(
                manifest.manifest_id,
                expected=ManifestState.STAGING,
                target=ManifestState.READY,
            )
