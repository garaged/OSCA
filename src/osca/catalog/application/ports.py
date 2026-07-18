from typing import Protocol
from uuid import UUID

from osca.catalog.api import CatalogResultReference
from osca.shared_kernel.api import CorrelationId


class ResultCatalog(Protocol):
    def register(
        self,
        producing_run_id: UUID,
        correlation_id: CorrelationId,
        producer_build: str,
        media_type: str = "application/json",
    ) -> CatalogResultReference: ...
