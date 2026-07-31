from typing import Any

import pytest
from pydantic import ValidationError

from osca.extensions.api import (
    ExtensionCategory,
    ExtensionDependency,
    ExtensionEntryPoint,
    ExtensionImpactPreview,
    ExtensionImpactReference,
    ExtensionManifest,
    ExtensionPermission,
    ExtensionPermissionKind,
    ExtensionSchemaRef,
    ExtensionTrustTier,
)

DIGEST = "sha256:" + "a" * 64


def manifest(**overrides: object) -> ExtensionManifest:
    values: dict[str, Any] = {
        "package_id": "momentum-extension",
        "name": "Momentum Extension",
        "publisher": "garaged",
        "package_version": "1.0.0",
        "category": ExtensionCategory.ANALYSIS,
        "entry_points": (
            ExtensionEntryPoint(
                name="momentum",
                contract_family="osca.analysis.graph",
                callable_ref="momentum_extension:build",
            ),
        ),
        "osca_compatibility": (">=0.1.0",),
        "output_schemas": (
            ExtensionSchemaRef(
                name="momentum_signal",
                schema_family="osca.analysis.output",
                version="1.0.0",
            ),
        ),
        "dependencies": (
            ExtensionDependency(package_id="core-metrics", version_range="^1.0.0"),
        ),
        "permissions": (
            ExtensionPermission(
                kind=ExtensionPermissionKind.PROVIDER_DATA,
                scope="market-data:read",
                rationale="Read governed bars",
            ),
        ),
        "integrity_digest": DIGEST,
        "license": "Apache-2.0",
        "provenance": "local bundle fixture",
        "trust_tier": ExtensionTrustTier.LOCAL_TRUSTED,
    }
    values.update(overrides)
    return ExtensionManifest(**values)


def test_extension_manifest_captures_package_lifecycle_metadata() -> None:
    package = manifest()

    assert package.family == "osca.extension.manifest"
    assert package.package_id == "momentum-extension"
    assert package.permissions[0].scope == "market-data:read"
    assert package.integrity_digest == DIGEST


def test_extension_manifest_rejects_duplicate_permissions_and_dependencies() -> None:
    permission = ExtensionPermission(
        kind=ExtensionPermissionKind.NETWORK,
        scope="api.example.com",
        rationale="Fetch remote data",
    )

    with pytest.raises(ValidationError):
        manifest(permissions=(permission, permission))

    dependency = ExtensionDependency(package_id="core-metrics", version_range="^1.0.0")
    with pytest.raises(ValidationError):
        manifest(dependencies=(dependency, dependency))


def test_extension_manifest_requires_semantic_version_and_digest() -> None:
    with pytest.raises(ValidationError):
        manifest(package_version="v1")

    with pytest.raises(ValidationError):
        manifest(integrity_digest="sha1:abc")


def test_impact_preview_fails_when_safe_preview_has_impacts() -> None:
    impact = ExtensionImpactReference(
        reference_type="report",
        reference_id=__import__("uuid").uuid4(),
        summary="report depends on extension",
    )

    with pytest.raises(ValidationError):
        ExtensionImpactPreview(
            package_id="momentum-extension",
            action="uninstall",
            impacted_references=(impact,),
            safe_to_apply=True,
        )
