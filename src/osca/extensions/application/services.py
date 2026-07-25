from uuid import UUID

from pydantic import BaseModel, ConfigDict

from osca.extensions.api import (
    ExtensionActivationDecision,
    ExtensionActivationState,
    ExtensionImpactPreview,
    ExtensionImpactReference,
    ExtensionInstallationRecord,
    ExtensionManifest,
    ExtensionPermission,
    ExtensionTrustTier,
)


class ExtensionValidationFinding(BaseModel):
    model_config = ConfigDict(frozen=True)
    code: str
    message: str


def validate_extension_manifest(
    manifest: ExtensionManifest,
) -> tuple[ExtensionValidationFinding, ...]:
    findings: list[ExtensionValidationFinding] = []
    if not manifest.entry_points:
        findings.append(
            ExtensionValidationFinding(
                code="missing_entry_point",
                message="extension manifest requires at least one entry point",
            )
        )
    if not manifest.osca_compatibility:
        findings.append(
            ExtensionValidationFinding(
                code="missing_compatibility",
                message="extension manifest requires OSCA compatibility metadata",
            )
        )
    if not manifest.integrity_digest:
        findings.append(
            ExtensionValidationFinding(
                code="missing_integrity",
                message="extension manifest requires an integrity digest",
            )
        )
    dependency_keys = [
        (dependency.package_id, dependency.version_range)
        for dependency in manifest.dependencies
    ]
    if len(set(dependency_keys)) != len(dependency_keys):
        findings.append(
            ExtensionValidationFinding(
                code="duplicate_dependency",
                message="extension dependencies must be unique",
            )
        )
    permission_keys = [
        (permission.kind, permission.scope) for permission in manifest.permissions
    ]
    if len(set(permission_keys)) != len(permission_keys):
        findings.append(
            ExtensionValidationFinding(
                code="duplicate_permission",
                message="extension permissions must be unique",
            )
        )
    return tuple(findings)


def create_installation_record(
    manifest: ExtensionManifest,
    *,
    source_uri: str,
    granted_permissions: tuple[ExtensionPermission, ...],
) -> ExtensionInstallationRecord:
    findings = validate_extension_manifest(manifest)
    if findings:
        codes = ", ".join(finding.code for finding in findings)
        raise ValueError(f"extension manifest is invalid: {codes}")
    requested = {(permission.kind, permission.scope) for permission in manifest.permissions}
    granted = {(permission.kind, permission.scope) for permission in granted_permissions}
    if not granted.issubset(requested):
        raise ValueError("granted permissions must be declared by the manifest")
    return ExtensionInstallationRecord(
        package_id=manifest.package_id,
        package_version=manifest.package_version,
        source_uri=source_uri,
        integrity_digest=manifest.integrity_digest,
        resolved_dependencies=manifest.dependencies,
        granted_permissions=granted_permissions,
    )


def decide_activation(
    manifest: ExtensionManifest,
    installation: ExtensionInstallationRecord,
    *,
    requested_permissions: tuple[ExtensionPermission, ...],
) -> ExtensionActivationDecision:
    reasons: list[str] = []
    if manifest.trust_tier in {
        ExtensionTrustTier.UNTRUSTED,
        ExtensionTrustTier.QUARANTINED,
    }:
        reasons.append(f"trust tier cannot activate: {manifest.trust_tier}")
    if installation.activation_state is ExtensionActivationState.QUARANTINED:
        reasons.append("installation is quarantined")
    granted = {
        (permission.kind, permission.scope)
        for permission in installation.granted_permissions
    }
    requested = {
        (permission.kind, permission.scope) for permission in requested_permissions
    }
    permission_approval_required = requested != granted
    if permission_approval_required:
        reasons.append("permission changes require renewed approval")
    if manifest.package_id != installation.package_id:
        reasons.append("manifest package does not match installation")
    if manifest.package_version != installation.package_version:
        reasons.append("manifest version does not match installation")
    approved = not reasons
    if approved:
        reasons.append("activation approved")
    return ExtensionActivationDecision(
        installation_id=installation.installation_id,
        approved=approved,
        reasons=tuple(reasons),
        required_permission_approval=permission_approval_required,
    )


def preview_extension_impact(
    *,
    package_id: str,
    action: str,
    retained_reference_ids: tuple[UUID, ...] = (),
    dependent_extension_ids: tuple[str, ...] = (),
) -> ExtensionImpactPreview:
    if action not in {"disable", "uninstall"}:
        raise ValueError("extension impact action must be disable or uninstall")
    references = tuple(
        ExtensionImpactReference(
            reference_type="retained_artifact",
            reference_id=reference_id,
            summary=f"retained artifact depends on {package_id}",
        )
        for reference_id in retained_reference_ids
    )
    return ExtensionImpactPreview(
        package_id=package_id,
        action=action,  # type: ignore[arg-type]
        impacted_references=references,
        dependent_extension_ids=dependent_extension_ids,
        safe_to_apply=not references and not dependent_extension_ids,
    )
