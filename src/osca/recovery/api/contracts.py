import hashlib
import json
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from osca.configuration.api import ValidatedConfiguration
from osca.security.api import AuthorizationContext, SecretReference
from osca.shared_kernel.api import CorrelationId


def canonical_digest(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


class RecoveryAvailability(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    REJECTED = "rejected"


class ManifestEntry(BaseModel):
    model_config = ConfigDict(frozen=True)
    path: str
    size: int = Field(ge=0)
    digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    media_type: str

    @model_validator(mode="after")
    def safe_relative_path(self) -> "ManifestEntry":
        path = PurePosixPath(self.path)
        if path.is_absolute() or ".." in path.parts or self.path != path.as_posix():
            raise ValueError("manifest entry path must be normalized and relative")
        if not path.parts or any(part in {"", "."} for part in path.parts):
            raise ValueError("manifest entry path is invalid")
        return self


class BackupManifest(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.recovery.backup-manifest"] = "osca.recovery.backup-manifest"
    version: Literal["1.0.0"] = "1.0.0"
    backup_id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source_build: str
    source_schema: str
    configuration_revision: UUID
    container: Literal["age/v1+x25519"] = "age/v1+x25519"
    recipient_fingerprints: tuple[str, ...] = Field(min_length=1)
    entries: tuple[ManifestEntry, ...]
    exclusions: tuple[str, ...]
    integrity_digest: str = ""

    @model_validator(mode="after")
    def unique_allowlisted_entries(self) -> "BackupManifest":
        paths = tuple(entry.path for entry in self.entries)
        if len(paths) != len(set(paths)):
            raise ValueError("manifest entry paths must be unique")
        allowed = {"state/osca.db", "configuration/snapshot.json", "exclusions.json"}
        if set(paths) != allowed:
            raise ValueError("manifest must contain exactly the M1 allowlisted entries")
        return self

    def with_integrity(self) -> "BackupManifest":
        return self.model_copy(
            update={
                "integrity_digest": canonical_digest(
                    self.model_dump(mode="json", exclude={"integrity_digest"})
                )
            }
        )

    def verify_integrity(self) -> bool:
        return self.integrity_digest == canonical_digest(
            self.model_dump(mode="json", exclude={"integrity_digest"})
        )


class BackupRecord(BaseModel):
    model_config = ConfigDict(frozen=True)
    record_id: UUID = Field(default_factory=uuid4)
    backup_id: UUID
    correlation_id: CorrelationId
    registered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source_build: str
    source_schema: str
    configuration_revision: UUID
    package_digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    manifest_digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    availability: RecoveryAvailability = RecoveryAvailability.AVAILABLE
    retention: Literal["protected_backup"] = "protected_backup"
    revision: int = 1


class RestoreValidation(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str
    passed: bool
    safe_detail: str


class RestorePlan(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.recovery.restore-plan"] = "osca.recovery.restore-plan"
    version: Literal["1.0.0"] = "1.0.0"
    plan_id: UUID = Field(default_factory=uuid4)
    backup_id: UUID
    package_digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    destination: str
    operations: tuple[str, ...]
    conflicts: tuple[str, ...]
    required_validations: tuple[str, ...]
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    integrity_digest: str = ""

    @property
    def executable(self) -> bool:
        return not self.conflicts

    def with_integrity(self) -> "RestorePlan":
        return self.model_copy(
            update={
                "integrity_digest": canonical_digest(
                    self.model_dump(mode="json", exclude={"integrity_digest"})
                )
            }
        )

    def verify_integrity(self) -> bool:
        return self.integrity_digest == canonical_digest(
            self.model_dump(mode="json", exclude={"integrity_digest"})
        )


class RestoreRecord(BaseModel):
    model_config = ConfigDict(frozen=True)
    record_id: UUID = Field(default_factory=uuid4)
    plan_id: UUID
    backup_id: UUID
    correlation_id: CorrelationId
    destination: str
    validations: tuple[RestoreValidation, ...]
    availability: RecoveryAvailability
    registered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CreateBackup(BaseModel):
    model_config = ConfigDict(frozen=True)
    authorization: AuthorizationContext
    correlation_id: CorrelationId
    destination: str
    recipient: str
    recipient_fingerprint: str
    configuration_snapshot: ValidatedConfiguration
    configuration_revision: UUID
    source_build: str
    source_schema: str


class VerifyBackup(BaseModel):
    model_config = ConfigDict(frozen=True)
    authorization: AuthorizationContext
    correlation_id: CorrelationId
    package: str
    identity_reference: SecretReference


class PreviewRestore(VerifyBackup):
    destination: str


class ExecuteRestore(BaseModel):
    model_config = ConfigDict(frozen=True)
    authorization: AuthorizationContext
    correlation_id: CorrelationId
    package: str
    identity_reference: SecretReference
    plan: RestorePlan
