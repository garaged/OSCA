from uuid import uuid4

import pytest
from osca.extensions.api import (
    ExtensionActivationState,
    ExtensionCategory,
    ExtensionEntryPoint,
    ExtensionManifest,
    ExtensionPermission,
    ExtensionPermissionKind,
    ExtensionSchemaRef,
    ExtensionTrustTier,
)
from osca.extensions.application import (
    create_installation_record,
    decide_activation,
    preview_extension_impact,
    validate_extension_manifest,
)


DIGEST = "sha256:" + "b" * 64


def manifest(*, trust_tier: ExtensionTrustTier) -> ExtensionManifest:
    return ExtensionManifest(
        package_id="table-visualization",
        name="Table Visualization",
        publisher="garaged",
        package_version="1.0.0",
        category=ExtensionCategory.VISUALIZATION,
        entry_points=(
            ExtensionEntryPoint(
                name="table",
                contract_family="osca.visualization.specification",
                callable_ref="table_visualization:render",
            ),
        ),
        osca_compatibility=(">=0.1.0",),
        output_schemas=(
            ExtensionSchemaRef(
                name="table",
                schema_family="osca.visualization.specification",
                version="1.0.0",
            ),
        ),
        permissions=(
            ExtensionPermission(
                kind=ExtensionPermissionKind.FILESYSTEM,
                scope="exports:write",
                rationale="Write user-requested visualization exports",
            ),
        ),
        integrity_digest=DIGEST,
        license="Apache-2.0",
        provenance="local bundle fixture",
        trust_tier=trust_tier,
    )


def test_validate_manifest_accepts_complete_manifest() -> None:
    findings = validate_extension_manifest(
        manifest(trust_tier=ExtensionTrustTier.LOCAL_TRUSTED)
    )

    assert findings == ()


def test_create_installation_record_preserves_manifest_identity() -> None:
    package = manifest(trust_tier=ExtensionTrustTier.LOCAL_TRUSTED)
    record = create_installation_record(
        package,
        source_uri="file:///extensions/table-visualization.oscaext",
        granted_permissions=package.permissions,
    )

    assert record.package_id == package.package_id
    assert record.package_version == package.package_version
    assert record.integrity_digest == package.integrity_digest
    assert record.activation_state is ExtensionActivationState.INSTALLED


def test_create_installation_record_rejects_undeclared_permissions() -> None:
    package = manifest(trust_tier=ExtensionTrustTier.LOCAL_TRUSTED)
    undeclared = ExtensionPermission(
        kind=ExtensionPermissionKind.NETWORK,
        scope="api.example.com",
        rationale="Not declared by manifest",
    )

    with pytest.raises(ValueError, match="declared by the manifest"):
        create_installation_record(
            package,
            source_uri="file:///extensions/table-visualization.oscaext",
            granted_permissions=(undeclared,),
        )


def test_activation_fails_closed_for_untrusted_and_permission_changes() -> None:
    package = manifest(trust_tier=ExtensionTrustTier.UNTRUSTED)
    record = create_installation_record(
        package,
        source_uri="file:///extensions/table-visualization.oscaext",
        granted_permissions=(),
    )

    decision = decide_activation(
        package,
        record,
        requested_permissions=package.permissions,
    )

    assert not decision.approved
    assert decision.required_permission_approval
    assert any("trust tier" in reason for reason in decision.reasons)
    assert any("permission changes" in reason for reason in decision.reasons)


def test_activation_approves_trusted_unchanged_permissions() -> None:
    package = manifest(trust_tier=ExtensionTrustTier.VERIFIED)
    record = create_installation_record(
        package,
        source_uri="file:///extensions/table-visualization.oscaext",
        granted_permissions=package.permissions,
    )

    decision = decide_activation(
        package,
        record,
        requested_permissions=package.permissions,
    )

    assert decision.approved
    assert decision.reasons == ("activation approved",)


def test_preview_extension_impact_lists_retained_references() -> None:
    retained_id = uuid4()
    preview = preview_extension_impact(
        package_id="table-visualization",
        action="uninstall",
        retained_reference_ids=(retained_id,),
        dependent_extension_ids=("dashboard-pack",),
    )

    assert not preview.safe_to_apply
    assert preview.impacted_references[0].reference_id == retained_id
    assert preview.dependent_extension_ids == ("dashboard-pack",)
