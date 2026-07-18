from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

from osca.instrument.api import AssetClass
from osca.market_data.api import (
    DatasetLayer,
    DatasetManifest,
    ManifestState,
    RetrievalRequest,
)
from osca.market_data.application import (
    classify_dates,
    contiguous_missing_ranges,
    preview_cleanup,
    resolve_retrieval,
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


def test_retrieval_reports_fresh_stale_and_exact_pinning() -> None:
    instrument_id = uuid4()
    created_at = datetime(2024, 1, 3, tzinfo=UTC)
    candidate = manifest(DatasetLayer.CANONICAL, protected=True, byte_size=200).model_copy(
        update={
            "instrument_id": instrument_id,
            "start_date": date(2024, 1, 1),
            "end_date_exclusive": date(2024, 1, 3),
            "created_at": created_at,
        }
    )
    request = RetrievalRequest(
        instrument_id=instrument_id,
        start_date=date(2024, 1, 1),
        end_date_exclusive=date(2024, 1, 3),
        maximum_age_seconds=60,
        pinned_revision_id=candidate.manifest_id,
        idempotency_key="retrieval-1",
    )
    fresh = resolve_retrieval(
        request,
        manifests=(candidate,),
        findings=(),
        now=created_at + timedelta(seconds=60),
    )
    assert fresh.state == "fresh"
    assert fresh.revision_id == candidate.manifest_id
    stale = resolve_retrieval(
        request,
        manifests=(candidate,),
        findings=(),
        now=created_at + timedelta(seconds=61),
    )
    assert stale.state == "stale"


def test_retrieval_does_not_substitute_for_missing_pinned_revision() -> None:
    candidate = manifest(DatasetLayer.CANONICAL, protected=True, byte_size=200)
    request = RetrievalRequest(
        instrument_id=candidate.instrument_id,
        start_date=candidate.start_date,
        end_date_exclusive=candidate.end_date_exclusive,
        maximum_age_seconds=60,
        pinned_revision_id=uuid4(),
        idempotency_key="retrieval-2",
    )
    resolution = resolve_retrieval(
        request,
        manifests=(candidate,),
        findings=(),
        now=candidate.created_at,
    )
    assert resolution.state == "unavailable"
    assert resolution.dataset_id is None
