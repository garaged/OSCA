import hashlib
from collections.abc import Sequence
from datetime import date
from typing import Annotated, Protocol, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from osca.market_data.api import (
    CanonicalDailyBar,
    DatasetLayer,
    DatasetManifest,
    ManifestState,
)

Digest = Annotated[str, Field(pattern=r"^sha256:[0-9a-f]{64}$")]


class CanonicalPublicationIntent(BaseModel):
    model_config = ConfigDict(frozen=True)
    dataset_id: UUID
    revision: int = Field(ge=1)
    fingerprint: Digest
    instrument_id: UUID
    provider_id: Annotated[str, Field(min_length=1, max_length=128)]
    source_context: Annotated[str, Field(min_length=1, max_length=128)]
    start_date: date
    end_date_exclusive: date
    source_evidence: tuple[UUID, ...] = ()
    previous_revisions: tuple[UUID, ...] = ()
    retention_policy_revision: Annotated[str, Field(min_length=1, max_length=128)]
    backup_permitted: bool

    @model_validator(mode="after")
    def validate_range(self) -> Self:
        if self.start_date >= self.end_date_exclusive:
            raise ValueError("publication range must be non-empty")
        return self


class CanonicalCodec(Protocol):
    def encode(self, bars: Sequence[CanonicalDailyBar]) -> bytes: ...


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
        digest = "sha256:" + hashlib.sha256(payload).hexdigest()
        manifest = DatasetManifest(
            dataset_id=intent.dataset_id,
            revision=intent.revision,
            fingerprint=intent.fingerprint,
            layer=DatasetLayer.CANONICAL,
            state=ManifestState.STAGING,
            instrument_id=intent.instrument_id,
            provider_id=intent.provider_id,
            source_context=intent.source_context,
            start_date=intent.start_date,
            end_date_exclusive=intent.end_date_exclusive,
            schema_revision="1.0.0",
            row_count=len(ordered),
            byte_size=len(payload),
            content_digest=digest,
            object_key=_object_key(intent),
            source_evidence=intent.source_evidence,
            previous_revisions=intent.previous_revisions,
            retention_policy_revision=intent.retention_policy_revision,
            backup_permitted=intent.backup_permitted,
            protected=True,
        )
        self._repository.add(manifest)
        try:
            self._store.publish(manifest.object_key, payload)
        except Exception:
            self._repository.transition(
                manifest.manifest_id,
                expected=ManifestState.STAGING,
                target=ManifestState.QUARANTINED,
            )
            raise
        return self._repository.transition(
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
