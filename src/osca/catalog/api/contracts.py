import hashlib
import json
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from osca.shared_kernel.api import CorrelationId


class MetadataAvailability(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class RetentionClass(StrEnum):
    MILESTONE_EVIDENCE = "milestone_evidence"
    PROTECTED_BACKUP = "protected_backup"


class CatalogResultReference(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.catalog.result-reference"] = "osca.catalog.result-reference"
    version: Literal["1.0.0"] = "1.0.0"
    result_id: UUID = Field(default_factory=uuid4)
    producing_run_id: UUID
    correlation_id: CorrelationId
    producer_build: str
    lineage: tuple[UUID, ...]
    availability: MetadataAvailability = MetadataAvailability.AVAILABLE
    retention: RetentionClass = RetentionClass.MILESTONE_EVIDENCE
    revision: int = 1
    integrity_digest: str = ""
    media_type: str = "application/json"
    registered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def verify_integrity(self) -> bool:
        return self.integrity_digest == metadata_digest(
            self.model_dump(mode="json", exclude={"integrity_digest"})
        )


class RecoveryRecordKind(StrEnum):
    BACKUP = "backup"
    RESTORE = "restore"


class CatalogRecoveryReference(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.catalog.recovery-reference"] = "osca.catalog.recovery-reference"
    version: Literal["1.0.0"] = "1.0.0"
    record_id: UUID = Field(default_factory=uuid4)
    kind: RecoveryRecordKind
    subject_id: UUID
    correlation_id: CorrelationId
    producer_build: str
    source_schema: str
    configuration_revision: UUID
    lineage: tuple[UUID, ...]
    availability: MetadataAvailability
    retention: RetentionClass = RetentionClass.PROTECTED_BACKUP
    revision: int = 1
    integrity_digest: str = ""
    registered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def verify_integrity(self) -> bool:
        return self.integrity_digest == metadata_digest(
            self.model_dump(mode="json", exclude={"integrity_digest"})
        )


def metadata_digest(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()
