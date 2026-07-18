from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from osca.market_data.api import DatasetLayer, DatasetManifest, ManifestState


class CleanupAction(BaseModel):
    model_config = ConfigDict(frozen=True)
    manifest_id: UUID
    object_key: str
    byte_size: int = Field(ge=0)
    reason: str


class CleanupPlan(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.cache.cleanup-plan"] = "osca.cache.cleanup-plan"
    version: Literal["1.0.0"] = "1.0.0"
    plan_id: UUID = Field(default_factory=uuid4)
    actions: tuple[CleanupAction, ...]
    protected_bytes: int = Field(ge=0)
    reclaimable_bytes: int = Field(ge=0)


def preview_cleanup(
    manifests: tuple[DatasetManifest, ...],
    *,
    eligible_manifest_ids: frozenset[UUID],
) -> CleanupPlan:
    actions: list[CleanupAction] = []
    protected_bytes = 0
    for manifest in manifests:
        if manifest.layer is DatasetLayer.CANONICAL or manifest.protected:
            protected_bytes += manifest.byte_size
            continue
        if manifest.manifest_id not in eligible_manifest_ids:
            protected_bytes += manifest.byte_size
            continue
        if manifest.state not in {ManifestState.READY, ManifestState.QUARANTINED}:
            continue
        actions.append(
            CleanupAction(
                manifest_id=manifest.manifest_id,
                object_key=manifest.object_key,
                byte_size=manifest.byte_size,
                reason="retention_policy_eligible_source_or_quarantine",
            )
        )
    return CleanupPlan(
        actions=tuple(actions),
        protected_bytes=protected_bytes,
        reclaimable_bytes=sum(action.byte_size for action in actions),
    )
