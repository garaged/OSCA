from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from osca.extensions.api import ExtensionCategory, ExtensionPermission, ExtensionTrustTier

Identifier = Annotated[str, Field(min_length=1, max_length=128)]
Description = Annotated[str, Field(min_length=1, max_length=2048)]
Digest = Annotated[str, Field(pattern=r"^sha256:[a-f0-9]{64}$")]
SemanticVersion = Annotated[str, Field(pattern=r"^\d+\.\d+\.\d+([+-][A-Za-z0-9.-]+)?$")]


class RuntimeExtensionStatus(StrEnum):
    VALIDATED = "validated"
    INSTALLED = "installed"
    ACTIVATED = "activated"
    SUCCEEDED = "succeeded"
    ROLLED_BACK = "rolled_back"
    POLICY_BLOCKED = "policy_blocked"
    INCOMPATIBLE = "incompatible"
    FAILED = "failed"


class RuntimePackManifest(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.runtime-extension-pack"] = "osca.runtime-extension-pack"
    version: Literal["1.0.0"] = "1.0.0"
    package_id: Identifier
    package_version: SemanticVersion
    publisher: Identifier
    category: ExtensionCategory
    executable: Identifier
    arguments: tuple[Identifier, ...] = ()
    osca_min_version: SemanticVersion
    trust_tier: ExtensionTrustTier
    integrity_digest: Digest
    permissions: tuple[ExtensionPermission, ...] = ()
    deterministic: bool = True
    max_runtime_seconds: int = Field(default=60, ge=1, le=3600)
    max_output_bytes: int = Field(default=1_000_000, ge=1, le=10_000_000)


class RuntimePackRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    pack_directory: str
    storage_root: str = ".osca"
    enable_execution: bool = False
    approved_permissions: tuple[ExtensionPermission, ...] = ()
    input_payload: str = "{}"


class RuntimePackEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.runtime-extension-evidence"] = "osca.runtime-extension-evidence"
    version: Literal["1.0.0"] = "1.0.0"
    evidence_id: UUID = Field(default_factory=uuid4)
    package_id: Identifier
    package_version: SemanticVersion
    status: RuntimeExtensionStatus
    manifest_digest: Digest
    approved_permissions: tuple[ExtensionPermission, ...] = ()
    stdout_uri: str | None = None
    stderr_uri: str | None = None
    output_digest: Digest | None = None
    exit_code: int | None = None
    rationale: Description
    findings: tuple[Identifier, ...] = ()
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RuntimePackRollbackEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.runtime-extension-rollback"] = "osca.runtime-extension-rollback"
    version: Literal["1.0.0"] = "1.0.0"
    rollback_id: UUID = Field(default_factory=uuid4)
    package_id: Identifier
    from_version: SemanticVersion
    to_version: SemanticVersion
    status: RuntimeExtensionStatus
    active_pointer_uri: str
    rationale: Description
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
