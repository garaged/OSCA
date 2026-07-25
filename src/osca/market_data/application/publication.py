import hashlib
from collections.abc import Sequence
from datetime import UTC, date, datetime, time
from typing import Annotated, Protocol, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from osca.market_data.api import (
    CanonicalDailyBar,
    CanonicalOhlcvBar,
    DatasetLayer,
    DatasetManifest,
    ManifestState,
)
from osca.market_data.api.contracts import ApprovedInterval

Digest = Annotated[str, Field(pattern=r"^sha256:[0-9a-f]{64}$")]
Identifier = Annotated[str, Field(min_length=1, max_length=128)]


class CanonicalPublicationIntent(BaseModel):
    model_config = ConfigDict(frozen=True)
    dataset_id: UUID
    revision: int = Field(ge=1)
    fingerprint: Digest
    instrument_id: UUID
    provider_id: Identifier
    source_context: Identifier
    start_date: date
    end_date_exclusive: date
    source_evidence: tuple[UUID, ...] = ()
    previous_revisions: tuple[UUID, ...] = ()
    retention_policy_revision: Identifier
    backup_permitted: bool

    @model_validator(mode="after")
    def validate_range(self) -> Self:
        if self.start_date >= self.end_date_exclusive:
            raise ValueError("publication range must be non-empty")
        return self


class OhlcvPublicationIntent(BaseModel):
    model_config = ConfigDict(frozen=True)
    dataset_id: UUID
    revision: int = Field(ge=1)
    fingerprint: Digest
    instrument_id: UUID
    provider_id: Identifier
    source_context: Identifier
    interval: ApprovedInterval
    start_date: date
    end_date_exclusive: date
    source_evidence: tuple[UUID, ...] = ()
    previous_revisions: tuple[UUID, ...] = ()
    retention_policy_revision: Identifier
    backup_permitted: bool

    @model_validator(mode="after")
    def validate_range_and_interval(self) -> Self:
        if self.start_date >= self.end_date_exclusive:
            raise ValueError("publication range must be non-empty")
        if self.interval == "1d":
            raise ValueError("daily publications must use CanonicalPublicationIntent")
        return self


class CanonicalCodec(Protocol):
    def encode(self, bars: Sequence[CanonicalDailyBar]) -> bytes: ...


class OhlcvCodec(Protocol):
    def encode(self, bars: Sequence[CanonicalOhlcvBar]) -> bytes: ...


class PayloadStore(Protocol):
    def publish(self, object_key: str, payload: bytes) -> object: ...


class PublicationManifestRepository(Protocol):
    def add(self, manifest: DatasetManifest) -> None: ...
    def by_fingerprint(self, fingerprint: str) -> DatasetManifest | None: ...
    def transition(
        self,
        manifest_id: UUID,
        *,
        expected: ManifestState,
        target: ManifestState,
    ) -> DatasetManifest: ...


class CanonicalPublisher:
    def __init__(
        self,
        repository: PublicationManifestRepository,
        store: PayloadStore,
        codec: CanonicalCodec,
    ) -> None:
        self._repository = repository
        self._store = store
        self._codec = codec

    def publish(
        self,
        intent: CanonicalPublicationIntent,
        bars: Sequence[CanonicalDailyBar],
    ) -> DatasetManifest:
        existing = self._repository.by_fingerprint(intent.fingerprint)
        if existing is not None:
            if existing.state is ManifestState.READY:
                return existing
            raise ValueError("equivalent publication is already unresolved")
        ordered = tuple(sorted(bars, key=lambda bar: bar.effective_date))
        if not ordered or any(bar.instrument_id != intent.instrument_id for bar in ordered):
            raise ValueError("publication bars must match one canonical instrument")
        if ordered[0].effective_date < intent.start_date:
            raise ValueError("publication contains observations before its declared range")
        if ordered[-1].effective_date >= intent.end_date_exclusive:
            raise ValueError("publication contains observations after its declared range")
        payload = self._codec.encode(ordered)
        manifest = _staged_manifest(
            intent=intent,
            interval="1d",
            payload=payload,
            row_count=len(ordered),
            object_key=_object_key(intent),
        )
        return _publish_staged_manifest(
            repository=self._repository,
            store=self._store,
            manifest=manifest,
            payload=payload,
        )


class OhlcvPublisher:
    def __init__(
        self,
        repository: PublicationManifestRepository,
        store: PayloadStore,
        codec: OhlcvCodec,
    ) -> None:
        self._repository = repository
        self._store = store
        self._codec = codec

    def publish(
        self,
        intent: OhlcvPublicationIntent,
        bars: Sequence[CanonicalOhlcvBar],
    ) -> DatasetManifest:
        existing = self._repository.by_fingerprint(intent.fingerprint)
        if existing is not None:
            if existing.state is ManifestState.READY:
                return existing
            raise ValueError("equivalent publication is already unresolved")
        ordered = tuple(sorted(bars, key=lambda bar: (bar.starts_at, str(bar.bar_id))))
        if not ordered or any(bar.instrument_id != intent.instrument_id for bar in ordered):
            raise ValueError("publication bars must match one canonical instrument")
        if any(bar.interval != intent.interval for bar in ordered):
            raise ValueError("publication bars must match the declared interval")
        range_start = datetime.combine(intent.start_date, time.min, tzinfo=UTC)
        range_end = datetime.combine(intent.end_date_exclusive, time.min, tzinfo=UTC)
        if ordered[0].starts_at < range_start:
            raise ValueError("publication contains observations before its declared range")
        if ordered[-1].ends_at > range_end:
            raise ValueError("publication contains observations after its declared range")
        payload = self._codec.encode(ordered)
        manifest = _staged_manifest(
            intent=intent,
            interval=intent.interval,
            payload=payload,
            row_count=len(ordered),
            object_key=_interval_object_key(intent),
        )
        return _publish_staged_manifest(
            repository=self._repository,
            store=self._store,
            manifest=manifest,
            payload=payload,
        )


def _staged_manifest(
    *,
    intent: CanonicalPublicationIntent | OhlcvPublicationIntent,
    interval: ApprovedInterval,
    payload: bytes,
    row_count: int,
    object_key: str,
) -> DatasetManifest:
    digest = "sha256:" + hashlib.sha256(payload).hexdigest()
    return DatasetManifest(
        dataset_id=intent.dataset_id,
        revision=intent.revision,
        fingerprint=intent.fingerprint,
        layer=DatasetLayer.CANONICAL,
        state=ManifestState.STAGING,
        instrument_id=intent.instrument_id,
        provider_id=intent.provider_id,
        source_context=intent.source_context,
        interval=interval,
        start_date=intent.start_date,
        end_date_exclusive=intent.end_date_exclusive,
        schema_revision="1.0.0",
        row_count=row_count,
        byte_size=len(payload),
        content_digest=digest,
        object_key=object_key,
        source_evidence=intent.source_evidence,
        previous_revisions=intent.previous_revisions,
        retention_policy_revision=intent.retention_policy_revision,
        backup_permitted=intent.backup_permitted,
        protected=True,
    )


def _publish_staged_manifest(
    *,
    repository: PublicationManifestRepository,
    store: PayloadStore,
    manifest: DatasetManifest,
    payload: bytes,
) -> DatasetManifest:
    repository.add(manifest)
    try:
        store.publish(manifest.object_key, payload)
    except Exception:
        repository.transition(
            manifest.manifest_id,
            expected=ManifestState.STAGING,
            target=ManifestState.QUARANTINED,
        )
        raise
    return repository.transition(
        manifest.manifest_id,
        expected=ManifestState.STAGING,
        target=ManifestState.READY,
    )


def _object_key(intent: CanonicalPublicationIntent) -> str:
    provider = hashlib.sha256(intent.provider_id.encode()).hexdigest()[:16]
    context = hashlib.sha256(intent.source_context.encode()).hexdigest()[:16]
    bounded_range = f"{intent.start_date.isoformat()}_{intent.end_date_exclusive.isoformat()}"
    return (
        f"canonical/{intent.instrument_id}/{provider}/{context}/{intent.dataset_id}/"
        f"r{intent.revision}/{bounded_range}.parquet"
    )


def _interval_object_key(intent: OhlcvPublicationIntent) -> str:
    provider = hashlib.sha256(intent.provider_id.encode()).hexdigest()[:16]
    context = hashlib.sha256(intent.source_context.encode()).hexdigest()[:16]
    bounded_range = f"{intent.start_date.isoformat()}_{intent.end_date_exclusive.isoformat()}"
    return (
        f"canonical/{intent.instrument_id}/{intent.interval}/{provider}/{context}/"
        f"{intent.dataset_id}/r{intent.revision}/{bounded_range}.parquet"
    )
