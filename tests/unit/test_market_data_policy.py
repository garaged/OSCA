from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from osca.instrument.api import AssetClass
from osca.market_data.api import (
    CanonicalDailyBar,
    DatasetLayer,
    DatasetManifest,
    ManifestState,
    RetrievalRequest,
)
from osca.market_data.application import (
    classify_dates,
    contiguous_missing_ranges,
    inspect_storage,
    preview_cleanup,
    resolve_retrieval,
    validate_daily_series,
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


def test_cleanup_protects_explicit_pins_and_inspection_accounts_usage() -> None:
    source = manifest(DatasetLayer.SOURCE, protected=False, byte_size=100)
    intraday = source.model_copy(
        update={
            "manifest_id": uuid4(),
            "dataset_id": uuid4(),
            "fingerprint": "sha256:" + "d" * 64,
            "interval": "5m",
            "object_key": "source/intraday.parquet",
        }
    )
    plan = preview_cleanup(
        (source,),
        eligible_manifest_ids=frozenset({source.manifest_id}),
        protected_manifest_ids=frozenset({source.manifest_id}),
    )
    assert plan.actions == ()
    assert plan.protected_bytes == 100
    inspection = inspect_storage((source, intraday))
    assert [usage.interval for usage in inspection.usage] == ["1d", "5m"]
    assert [usage.object_count for usage in inspection.usage] == [1, 1]
    assert {item.manifest_id for item in inspection.manifests} == {
        source.manifest_id,
        intraday.manifest_id,
    }


def test_series_quality_finds_duplicates_and_identity_mismatch() -> None:
    instrument_id = uuid4()
    other_instrument_id = uuid4()
    request_id = uuid4()

    def bar(bar_instrument_id: UUID) -> CanonicalDailyBar:
        return CanonicalDailyBar(
            instrument_id=bar_instrument_id,
            effective_date=date(2024, 1, 1),
            source_timestamp=datetime(2024, 1, 2, tzinfo=UTC),
            open=Decimal("10"),
            high=Decimal("12"),
            low=Decimal("9"),
            close=Decimal("11"),
            volume=Decimal("100"),
            currency="USD",
            volume_unit="shares",
            provider_id="synthetic",
            source_identity="source-1",
            request_id=request_id,
            normalization_revision="1.0.0",
        )

    findings = validate_daily_series(
        (bar(instrument_id), bar(other_instrument_id)),
        instrument_id=instrument_id,
        start_date=date(2024, 1, 1),
        end_date_exclusive=date(2024, 1, 2),
    )
    assert {finding.classification for finding in findings} == {"duplicate", "invalid"}


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
    intraday = candidate.model_copy(
        update={
            "manifest_id": uuid4(),
            "dataset_id": uuid4(),
            "fingerprint": "sha256:" + "e" * 64,
            "interval": "5m",
            "object_key": "canonical/intraday.parquet",
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
        manifests=(candidate, intraday),
        findings=(),
        now=created_at + timedelta(seconds=60),
    )
    assert fresh.state == "fresh"
    assert fresh.revision_id == candidate.manifest_id
    stale = resolve_retrieval(
        request,
        manifests=(candidate, intraday),
        findings=(),
        now=created_at + timedelta(seconds=61),
    )
    assert stale.state == "stale"

    intraday_request = RetrievalRequest(
        instrument_id=instrument_id,
        start_date=date(2024, 1, 1),
        end_date_exclusive=date(2024, 1, 3),
        interval="5m",
        maximum_age_seconds=60,
        pinned_revision_id=intraday.manifest_id,
        idempotency_key="retrieval-1-5m",
    )
    intraday_resolution = resolve_retrieval(
        intraday_request,
        manifests=(candidate, intraday),
        findings=(),
        now=created_at + timedelta(seconds=60),
    )
    assert intraday_resolution.state == "fresh"
    assert intraday_resolution.revision_id == intraday.manifest_id


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
