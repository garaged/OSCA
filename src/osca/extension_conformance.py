from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

SUPPORTED_MANIFEST_VERSION = "1.0.0"
SUPPORTED_API_MAJOR = 1
DEPRECATED_API_VERSIONS = {
    "0.9": (
        "Migrate to extension API 1.0.",
        "0.1.x",
    )
}
SAFE_CAPABILITIES = frozenset(
    {
        "analysis.read",
        "dataset.read",
        "evidence.write-local",
        "metrics.compute",
    }
)
FORBIDDEN_CAPABILITIES = frozenset(
    {
        "broker.connect",
        "exchange.order",
        "network.remote-write",
        "recommendation.publish",
        "capital.execute",
        "model.serve-live",
    }
)
_IDENTIFIER = re.compile(r"^[a-z0-9]+(?:[.-][a-z0-9]+)*$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class ExtensionArtifact(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    path: str
    sha256: str

    @field_validator("path")
    @classmethod
    def validate_relative_path(cls, value: str) -> str:
        candidate = Path(value)
        if candidate.is_absolute() or ".." in candidate.parts or value in {"", "."}:
            raise ValueError("artifact path must be a contained relative path")
        return value

    @field_validator("sha256")
    @classmethod
    def validate_digest(cls, value: str) -> str:
        if not _SHA256.fullmatch(value):
            raise ValueError("artifact sha256 must be 64 lowercase hexadecimal characters")
        return value


class ExtensionManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    family: Literal["osca.extension-manifest"]
    manifest_version: Literal["1.0.0"]
    extension_id: str
    extension_version: str
    api_version: str
    entry_point: str
    trust: Literal["trusted-local"]
    license_spdx: str
    source_repository: str
    source_commit: str
    capabilities: tuple[str, ...] = Field(min_length=1)
    artifacts: tuple[ExtensionArtifact, ...] = Field(min_length=1)
    network_access: Literal[False]
    remote_installation: Literal[False]
    automatic_updates: Literal[False]

    @field_validator("extension_id")
    @classmethod
    def validate_extension_id(cls, value: str) -> str:
        if not _IDENTIFIER.fullmatch(value):
            raise ValueError("extension_id must use lowercase dotted or dashed identifiers")
        return value

    @field_validator("extension_version")
    @classmethod
    def validate_extension_version(cls, value: str) -> str:
        if not re.fullmatch(r"\d+\.\d+\.\d+(?:[a-z0-9.-]+)?", value):
            raise ValueError("extension_version must be an explicit semantic version")
        return value

    @field_validator("api_version")
    @classmethod
    def validate_api_version(cls, value: str) -> str:
        match = re.fullmatch(r"(\d+)\.(\d+)", value)
        if match is None:
            raise ValueError("api_version must use major.minor syntax")
        if int(match.group(1)) == SUPPORTED_API_MAJOR or value in DEPRECATED_API_VERSIONS:
            return value
        raise ValueError(
            f"api_version must use supported major {SUPPORTED_API_MAJOR} "
            f"or deprecated versions {sorted(DEPRECATED_API_VERSIONS)}"
        )

    @field_validator("entry_point")
    @classmethod
    def validate_entry_point(cls, value: str) -> str:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*:[A-Za-z_][A-Za-z0-9_]*", value):
            raise ValueError("entry_point must use module.path:callable syntax")
        return value

    @field_validator("license_spdx")
    @classmethod
    def validate_license(cls, value: str) -> str:
        if not value or any(character.isspace() for character in value):
            raise ValueError("license_spdx must be a non-empty SPDX identifier")
        return value

    @field_validator("source_repository")
    @classmethod
    def validate_repository(cls, value: str) -> str:
        if not value.startswith("https://"):
            raise ValueError("source_repository must use HTTPS")
        return value

    @field_validator("source_commit")
    @classmethod
    def validate_source_commit(cls, value: str) -> str:
        if not re.fullmatch(r"[0-9a-f]{40}", value):
            raise ValueError("source_commit must be a full lowercase Git commit SHA")
        return value

    @field_validator("capabilities")
    @classmethod
    def validate_capabilities(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(set(value)) != len(value):
            raise ValueError("capabilities must not contain duplicates")
        forbidden = sorted(set(value) & FORBIDDEN_CAPABILITIES)
        unknown = sorted(set(value) - SAFE_CAPABILITIES - FORBIDDEN_CAPABILITIES)
        if forbidden:
            raise ValueError(f"forbidden capabilities requested: {forbidden}")
        if unknown:
            raise ValueError(f"unknown capabilities requested: {unknown}")
        return value


class ExtensionValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    status: Literal["valid", "invalid"]
    manifest_path: str
    manifest_sha256: str | None
    extension_id: str | None
    extension_version: str | None
    api_version: str | None
    compatibility_status: Literal["supported", "deprecated", "invalid"]
    deprecation_message: str | None
    last_supported_release_family: str | None
    capabilities: tuple[str, ...]
    verified_artifacts: tuple[str, ...]
    errors: tuple[str, ...]
    code_imported: Literal[False] = False
    execution_enabled: Literal[False] = False


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_extension_package(manifest_path: Path) -> ExtensionValidationResult:
    errors: list[str] = []
    verified: list[str] = []
    manifest_digest: str | None = None
    manifest: ExtensionManifest | None = None

    try:
        manifest_digest = _sha256(manifest_path)
        document = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest = ExtensionManifest.model_validate(document)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        errors.append(str(exc))

    if manifest is not None:
        package_root = manifest_path.parent.resolve()
        declared_paths: set[str] = set()
        for artifact in manifest.artifacts:
            if artifact.path in declared_paths:
                errors.append(f"duplicate artifact declaration: {artifact.path}")
                continue
            declared_paths.add(artifact.path)
            candidate = (package_root / artifact.path).resolve()
            if package_root not in candidate.parents:
                errors.append(f"artifact escapes package root: {artifact.path}")
                continue
            if not candidate.is_file():
                errors.append(f"artifact is missing: {artifact.path}")
                continue
            actual = _sha256(candidate)
            if actual != artifact.sha256:
                errors.append(f"artifact digest mismatch: {artifact.path}")
                continue
            verified.append(artifact.path)

    deprecation = DEPRECATED_API_VERSIONS.get(manifest.api_version) if manifest else None
    compatibility_status: Literal["supported", "deprecated", "invalid"]
    if manifest is None or errors:
        compatibility_status = "invalid"
    elif deprecation is not None:
        compatibility_status = "deprecated"
    else:
        compatibility_status = "supported"

    return ExtensionValidationResult(
        status="invalid" if errors else "valid",
        manifest_path=str(manifest_path),
        manifest_sha256=manifest_digest,
        extension_id=manifest.extension_id if manifest else None,
        extension_version=manifest.extension_version if manifest else None,
        api_version=manifest.api_version if manifest else None,
        compatibility_status=compatibility_status,
        deprecation_message=deprecation[0] if deprecation else None,
        last_supported_release_family=deprecation[1] if deprecation else None,
        capabilities=manifest.capabilities if manifest else (),
        verified_artifacts=tuple(sorted(verified)),
        errors=tuple(errors),
    )
