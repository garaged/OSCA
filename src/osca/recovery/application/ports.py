from pathlib import Path
from typing import Protocol
from uuid import UUID

from osca.catalog.api import (
    CatalogRecoveryReference,
    MetadataAvailability,
    RecoveryRecordKind,
)
from osca.shared_kernel.api import CorrelationId


class EncryptionContainer(Protocol):
    container_id: str

    def encrypt(self, cleartext: Path, destination: Path, recipient: str) -> None: ...

    def decrypt(self, package: Path, cleartext: Path, identity: bytes) -> None: ...


class RecoveryCatalog(Protocol):
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
