from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

Identifier = Annotated[str, Field(min_length=1, max_length=128)]
Description = Annotated[str, Field(min_length=1, max_length=1024)]
SemanticVersion = Annotated[str, Field(pattern=r"^\d+\.\d+\.\d+([+-][A-Za-z0-9.-]+)?$")]
Digest = Annotated[str, Field(pattern=r"^sha256:[a-fA-F0-9]{64}$")]


class ExtensionCategory(StrEnum):
    METRIC = "metric"
    INDICATOR = "indicator"
    FEATURE = "feature"
    LABEL = "label"
    ANALYSIS = "analysis"
    STRATEGY = "strategy"
    MODEL = "model"
    VISUALIZATION = "visualization"
    DATA_PROVIDER = "data_provider"


class ExtensionTrustTier(StrEnum):
    BUILT_IN = "built_in"
    VERIFIED = "verified"
    LOCAL_TRUSTED = "local_trusted"
    UNTRUSTED = "untrusted"
    QUARANTINED = "quarantined"


class ExtensionActivationState(StrEnum):
    INSTALLED = "installed"
    ACTIVE = "active"
    DISABLED = "disabled"
    QUARANTINED = "quarantined"
    UNINSTALLED = "uninstalled"


class ExtensionPermissionKind(StrEnum):
    NETWORK = "network"
    SECRET = "secret"
    FILESYSTEM = "filesystem"
    SUBPROCESS = "subprocess"
    PROVIDER_DATA = "provider_data"
    MODEL_EXECUTION = "model_execution"


class ExtensionDependency(BaseModel):
    model_config = ConfigDict(frozen=True)
    package_id: Identifier
    version_range: Identifier
    optional: bool = False


class ExtensionPermission(BaseModel):
    model_config = ConfigDict(frozen=True)
    kind: ExtensionPermissionKind
    scope: Identifier
    rationale: Description


class ExtensionSchemaRef(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: Identifier
    schema_family: Identifier
    version: SemanticVersion


class ExtensionEntryPoint(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: Identifier
    contract_family: Identifier
    callable_ref: Identifier


class ExtensionResourceRequirements(BaseModel):
    model_config = ConfigDict(frozen=True)
    max_memory_mb: Annotated[int, Field(gt=0)] | None = None
    max_runtime_seconds: Annotated[int, Field(gt=0)] | None = None
    gpu_required: bool = False


class ExtensionManifest(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.extension.manifest"] = "osca.extension.manifest"
    version: Literal["1.0.0"] = "1.0.0"
    package_id: Identifier
    name: Identifier
    publisher: Identifier
    package_version: SemanticVersion
    category: ExtensionCategory
    entry_points: tuple[ExtensionEntryPoint, ...] = Field(min_length=1)
    osca_compatibility: tuple[Identifier, ...] = Field(min_length=1)
    input_schemas: tuple[ExtensionSchemaRef, ...] = ()
    output_schemas: tuple[ExtensionSchemaRef, ...] = Field(min_length=1)
    parameter_schemas: tuple[ExtensionSchemaRef, ...] = ()
    supported_asset_classes: tuple[Identifier, ...] = ()
    supported_intervals: tuple[Identifier, ...] = ()
    dependencies: tuple[ExtensionDependency, ...] = ()
    permissions: tuple[ExtensionPermission, ...] = ()
    deterministic: bool = True
    random_seed_required: bool = False
    resource_requirements: ExtensionResourceRequirements = Field(
        default_factory=ExtensionResourceRequirements
    )
    integrity_digest: Digest
    signature_ref: Identifier | None = None
    license: Identifier
    provenance: Description
    trust_tier: ExtensionTrustTier = ExtensionTrustTier.UNTRUSTED

    @model_validator(mode="after")
    def validate_manifest(self) -> Self:
        dependency_keys = [
            (dependency.package_id, dependency.version_range)
            for dependency in self.dependencies
        ]
        if len(set(dependency_keys)) != len(dependency_keys):
            raise ValueError("extension dependencies must be unique")
        permission_keys = [
            (permission.kind, permission.scope) for permission in self.permissions
        ]
        if len(set(permission_keys)) != len(permission_keys):
            raise ValueError("extension permissions must be unique")
        return self


class ExtensionInstallationRecord(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.extension.installation"] = "osca.extension.installation"
    version: Literal["1.0.0"] = "1.0.0"
    installation_id: UUID = Field(default_factory=uuid4)
    package_id: Identifier
    package_version: SemanticVersion
    source_uri: Identifier
    integrity_digest: Digest
    resolved_dependencies: tuple[ExtensionDependency, ...] = ()
    granted_permissions: tuple[ExtensionPermission, ...] = ()
    activation_state: ExtensionActivationState = ExtensionActivationState.INSTALLED
    installed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_installed_at(self) -> Self:
        if self.installed_at.tzinfo is None:
            raise ValueError("installed_at must be timezone-aware")
        return self


class ExtensionActivationDecision(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.extension.activation-decision"] = (
        "osca.extension.activation-decision"
    )
    version: Literal["1.0.0"] = "1.0.0"
    decision_id: UUID = Field(default_factory=uuid4)
    installation_id: UUID
    approved: bool
    reasons: tuple[Description, ...] = Field(min_length=1)
    required_permission_approval: bool
    decided_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_decided_at(self) -> Self:
        if self.decided_at.tzinfo is None:
            raise ValueError("decided_at must be timezone-aware")
        return self


class ExtensionImpactReference(BaseModel):
    model_config = ConfigDict(frozen=True)
    reference_type: Identifier
    reference_id: UUID
    summary: Description


class ExtensionImpactPreview(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.extension.impact-preview"] = "osca.extension.impact-preview"
    version: Literal["1.0.0"] = "1.0.0"
    package_id: Identifier
    action: Literal["disable", "uninstall"]
    impacted_references: tuple[ExtensionImpactReference, ...] = ()
    dependent_extension_ids: tuple[Identifier, ...] = ()
    safe_to_apply: bool
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_generated_at(self) -> Self:
        if self.generated_at.tzinfo is None:
            raise ValueError("generated_at must be timezone-aware")
        if self.safe_to_apply and (
            self.impacted_references or self.dependent_extension_ids
        ):
            raise ValueError("safe impact previews cannot contain impacted references")
        return self
