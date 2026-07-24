from typing import Literal, Protocol
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from osca.market_data.api import DatasetLayer, DatasetManifest, ManifestState
from osca.security.api import AuthorizationContext, Capability
from osca.workflow.application.handlers import require_capability


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


class CleanupManifestRepository(Protocol):
    def transition(
        self,
        manifest_id: UUID,
        *,
        expected: ManifestState,
        target: ManifestState,
    ) -> DatasetManifest: ...


class PayloadDeleter(Protocol):
    def delete(self, object_key: str) -> None: ...


def preview_cleanup(
    manifests: tuple[DatasetManifest, ...],
    *,
    eligible_manifest_ids: frozenset[UUID],
    protected_manifest_ids: frozenset[UUID] = frozenset(),
) -> CleanupPlan:
    actions: list[CleanupAction] = []
    protected_bytes = 0
    for manifest in manifests:
        if (
            manifest.layer is DatasetLayer.CANONICAL
            or manifest.protected
            or manifest.manifest_id in protected_manifest_ids
        ):
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


class CleanupService:
    def __init__(
        self,
        repository: CleanupManifestRepository,
        payloads: PayloadDeleter,
    ) -> None:
        self._repository = repository
        self._payloads = payloads

    def preview(
        self,
        authorization: AuthorizationContext,
        manifests: tuple[DatasetManifest, ...],
        *,
        eligible_manifest_ids: frozenset[UUID],
        protected_manifest_ids: frozenset[UUID] = frozenset(),
    ) -> CleanupPlan:
        require_capability(authorization, Capability.MARKET_DATA_CLEANUP_PREVIEW)
        return preview_cleanup(
            manifests,
            eligible_manifest_ids=eligible_manifest_ids,
            protected_manifest_ids=protected_manifest_ids,
        )

    def execute(
        self,
        authorization: AuthorizationContext,
        plan: CleanupPlan,
        current_manifests: tuple[DatasetManifest, ...],
        *,
        eligible_manifest_ids: frozenset[UUID],
        protected_manifest_ids: frozenset[UUID] = frozenset(),
    ) -> tuple[DatasetManifest, ...]:
        require_capability(authorization, Capability.MARKET_DATA_CLEANUP_EXECUTE)
        current = preview_cleanup(
            current_manifests,
            eligible_manifest_ids=eligible_manifest_ids,
            protected_manifest_ids=protected_manifest_ids,
        )
        if (
            current.actions != plan.actions
            or current.protected_bytes != plan.protected_bytes
            or current.reclaimable_bytes != plan.reclaimable_bytes
        ):
            raise ValueError("cleanup inputs changed after preview")
        by_id = {manifest.manifest_id: manifest for manifest in current_manifests}
        deleted: list[DatasetManifest] = []
        for action in plan.actions:
            manifest = by_id[action.manifest_id]
            deleting = self._repository.transition(
                manifest.manifest_id,
                expected=manifest.state,
                target=ManifestState.DELETING,
            )
            self._payloads.delete(deleting.object_key)
            deleted.append(
                self._repository.transition(
                    manifest.manifest_id,
                    expected=ManifestState.DELETING,
                    target=ManifestState.DELETED,
                )
            )
        return tuple(deleted)
