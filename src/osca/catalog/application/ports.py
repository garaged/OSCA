from typing import Protocol
from uuid import UUID

from osca.catalog.api import (
    CatalogRecoveryReference,
    CatalogResultReference,
    MetadataAvailability,
    RecoveryRecordKind,
)
from osca.shared_kernel.api import CorrelationId


class ResultCatalog(Protocol):
    def register(
        self,
        producing_run_id: UUID,
        correlation_id: CorrelationId,
        producer_build: str,
        media_type: str = "application/json",
    ) -> CatalogResultReference: ...

    def register_recovery(
        self,
        *,
        kind: RecoveryRecordKind,
        subject_id: UUID,
        correlation_id: CorrelationId,
        producer_build: str,
        source_schema: str,
        configuration_revision: UUID,
        lineage: tuple[UUID, ...],
        availability: MetadataAvailability,
    ) -> CatalogRecoveryReference: ...
