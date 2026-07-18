from datetime import date
from uuid import uuid4

from osca.instrument.api import AssetClass
from osca.market_data.api import DatasetLayer, DatasetManifest, ManifestState
from osca.market_data.application import (
    classify_dates,
    contiguous_missing_ranges,
    preview_cleanup,
)


def test_crypto_dates_and_stock_uncertainty_are_conservative() -> None:
    instrument_id = uuid4()
    crypto = classify_dates(
        instrument_id=instrument_id,
        asset_class=AssetClass.CRYPTO_PAIR,
        start_date=date(2024, 1, 1),
        end_date_exclusive=date(2024, 1, 5),
        current_utc_date=date(2024, 1, 4),
        observed=frozenset({date(2024, 1, 1)}),
    )
    assert contiguous_missing_ranges(crypto) == ((date(2024, 1, 2), date(2024, 1, 4)),)
    stock = classify_dates(
        instrument_id=instrument_id,
        asset_class=AssetClass.STOCK,
        start_date=date(2024, 1, 5),
        end_date_exclusive=date(2024, 1, 9),
        current_utc_date=date(2024, 1, 10),
        observed=frozenset(),
        confirmed_stock_sessions=frozenset({date(2024, 1, 5)}),
    )
    assert [finding.classification for finding in stock] == [
        "missing",
        "non_expected",
        "non_expected",
        "unresolved",
    ]


def manifest(layer: DatasetLayer, *, protected: bool, byte_size: int) -> DatasetManifest:
    return DatasetManifest(
        revision=1,
        fingerprint="sha256:" + ("a" if layer is DatasetLayer.CANONICAL else "b") * 64,
        layer=layer,
        state=ManifestState.READY,
        instrument_id=uuid4(),
        provider_id="synthetic",
        source_context="fixture",
        start_date=date(2024, 1, 1),
        end_date_exclusive=date(2024, 1, 2),
        schema_revision="1.0.0",
        row_count=1,
        byte_size=byte_size,
        content_digest="sha256:" + "c" * 64,
        object_key=f"{layer}/object.parquet",
        retention_policy_revision="synthetic-v1",
        backup_permitted=True,
        protected=protected,
    )


def test_cleanup_never_selects_accepted_canonical_history() -> None:
    canonical = manifest(DatasetLayer.CANONICAL, protected=True, byte_size=200)
    source = manifest(DatasetLayer.SOURCE, protected=False, byte_size=100)
    plan = preview_cleanup(
        (canonical, source),
        eligible_manifest_ids=frozenset({canonical.manifest_id, source.manifest_id}),
    )
    assert tuple(action.manifest_id for action in plan.actions) == (source.manifest_id,)
    assert plan.protected_bytes == 200
    assert plan.reclaimable_bytes == 100


def test_cleanup_defaults_are_not_implicit() -> None:
    source = manifest(DatasetLayer.SOURCE, protected=False, byte_size=100)
    plan = preview_cleanup((source,), eligible_manifest_ids=frozenset())
    assert plan.actions == ()
    assert plan.protected_bytes == 100
