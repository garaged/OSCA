from datetime import date
from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from osca.market_data.api import DatasetLayer, DatasetManifest, ManifestState
from osca.market_data.application import CleanupService
from osca.market_data.infrastructure import (
    ImmutablePayloadStore,
    MarketDataBase,
    SqliteManifestRepository,
)
from osca.security.api import AuthorizationContext, Capability


def authorization(capability: Capability) -> AuthorizationContext:
    return AuthorizationContext(
        actor="local-owner",
        capabilities=frozenset({capability}),
        authentication_method="local-os-user",
    )


def source_manifest() -> DatasetManifest:
    return DatasetManifest(
        revision=1,
        fingerprint="sha256:" + "b" * 64,
        layer=DatasetLayer.SOURCE,
        state=ManifestState.READY,
        instrument_id=uuid4(),
        provider_id="synthetic",
        source_context="fixture",
        start_date=date(2024, 1, 1),
        end_date_exclusive=date(2024, 1, 2),
        schema_revision="1.0.0",
        row_count=1,
        byte_size=7,
        content_digest="sha256:" + "c" * 64,
        object_key="source/fixture/object.parquet",
        retention_policy_revision="synthetic-v1",
        backup_permitted=False,
    )


def test_cleanup_execution_revalidates_plan_and_deletes_only_selected_payload(
    tmp_path: Path,
) -> None:
    engine = create_engine("sqlite://")
    MarketDataBase.metadata.create_all(engine)
    manifest = source_manifest()
    store = ImmutablePayloadStore(tmp_path)
    destination = store.publish(manifest.object_key, b"payload")
    with Session(engine) as session, session.begin():
        repository = SqliteManifestRepository(session)
        repository.add(manifest)
        service = CleanupService(repository, store)
        eligible = frozenset({manifest.manifest_id})
        plan = service.preview(
            authorization(Capability.MARKET_DATA_CLEANUP_PREVIEW),
            (manifest,),
            eligible_manifest_ids=eligible,
        )
        deleted = service.execute(
            authorization(Capability.MARKET_DATA_CLEANUP_EXECUTE),
            plan,
            (manifest,),
            eligible_manifest_ids=eligible,
        )
        assert deleted[0].state is ManifestState.DELETED
        assert not destination.exists()
