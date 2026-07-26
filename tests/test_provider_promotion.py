from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from osca.provider_promotion import (
    PromotionFinding,
    PromotionFindingSeverity,
    PromotionOutcome,
    ProviderAssetClass,
    ProviderCapabilityScope,
    ProviderCredentialEvidence,
    ProviderIdentifier,
    ProviderLicenseEvidence,
    ProviderPermission,
    ProviderProductionEvidenceBundle,
    ProviderQuotaEvidence,
    evaluate_provider_promotion,
    promotion_is_enabled,
)


def _scope(provider_id: ProviderIdentifier) -> ProviderCapabilityScope:
    return ProviderCapabilityScope(
        provider_id=provider_id,
        asset_classes=(ProviderAssetClass.STOCK,),
        intervals=("1d", "1h"),
        capabilities=("historical_bars", "provider_health"),
    )


def _license(
    provider_id: ProviderIdentifier,
    permissions: tuple[ProviderPermission, ...],
) -> ProviderLicenseEvidence:
    return ProviderLicenseEvidence(
        provider_id=provider_id,
        account_plan_id="paid-plan",
        terms_reference_uri="https://provider.example/terms",
        allowed_permissions=permissions,
        accepted_at=datetime(2026, 7, 25, tzinfo=UTC),
    )


def _credential(provider_id: ProviderIdentifier) -> ProviderCredentialEvidence:
    return ProviderCredentialEvidence(
        provider_id=provider_id,
        secret_reference=f"secret:providers/{provider_id.value}/api-key",
        authentication_mode="api-key",
        credential_configured=True,
        credential_verified=True,
        verified_at=datetime(2026, 7, 25, tzinfo=UTC),
    )


def _quota(
    provider_id: ProviderIdentifier,
    *,
    request_limit: int = 1000,
    remaining_requests: int = 700,
) -> ProviderQuotaEvidence:
    return ProviderQuotaEvidence(
        provider_id=provider_id,
        quota_policy_id="daily-api-quota",
        request_limit=request_limit,
        remaining_requests=remaining_requests,
        required_headroom_ratio=0.5,
        reset_at=datetime(2026, 7, 26, tzinfo=UTC),
        observed_at=datetime(2026, 7, 25, tzinfo=UTC),
    )


def _bundle(
    provider_id: ProviderIdentifier,
    *,
    license_evidence: ProviderLicenseEvidence | None = None,
    credential_evidence: ProviderCredentialEvidence | None = None,
    quota_evidence: ProviderQuotaEvidence | None = None,
    findings: tuple[PromotionFinding, ...] = (),
) -> ProviderProductionEvidenceBundle:
    return ProviderProductionEvidenceBundle(
        provider_id=provider_id,
        capability_scope=_scope(provider_id),
        license_evidence=license_evidence
        or _license(
            provider_id,
            (
                ProviderPermission.RETRIEVAL,
                ProviderPermission.RETENTION,
                ProviderPermission.TRANSFORMATION,
                ProviderPermission.EXPORT,
                ProviderPermission.BACKUP,
            ),
        ),
        credential_evidence=credential_evidence or _credential(provider_id),
        quota_evidence=quota_evidence or _quota(provider_id),
        retention_policy_id="retain-source-and-canonical",
        export_policy_id="derived-export-allowed",
        backup_policy_id="metadata-and-retained-source-backup",
        reviewed_by="architecture-authority",
        reviewed_at=datetime(2026, 7, 25, tzinfo=UTC),
        findings=findings,
    )


def test_provider_promotion_approves_twelve_data_when_evidence_is_complete() -> None:
    evidence = _bundle(ProviderIdentifier.TWELVE_DATA)

    decision = evaluate_provider_promotion(evidence)

    assert decision.provider_id is ProviderIdentifier.TWELVE_DATA
    assert decision.outcome is PromotionOutcome.APPROVE
    assert promotion_is_enabled(decision)
    assert decision.provider_enabled


def test_provider_promotion_blocks_missing_retention_or_export_permission() -> None:
    evidence = _bundle(
        ProviderIdentifier.TWELVE_DATA,
        license_evidence=_license(
            ProviderIdentifier.TWELVE_DATA,
            (
                ProviderPermission.RETRIEVAL,
                ProviderPermission.TRANSFORMATION,
                ProviderPermission.BACKUP,
            ),
        ),
    )

    decision = evaluate_provider_promotion(evidence)

    assert decision.outcome is PromotionOutcome.BLOCK
    assert not decision.provider_enabled
    assert {finding.code for finding in decision.findings} >= {
        "missing-retention-permission",
        "missing-export-permission",
    }


def test_provider_promotion_blocks_kraken_when_quota_headroom_is_low() -> None:
    evidence = _bundle(
        ProviderIdentifier.KRAKEN,
        quota_evidence=_quota(
            ProviderIdentifier.KRAKEN,
            request_limit=1000,
            remaining_requests=200,
        ),
    )

    decision = evaluate_provider_promotion(evidence)

    assert decision.outcome is PromotionOutcome.BLOCK
    assert not promotion_is_enabled(decision)
    assert any(finding.code == "quota-headroom-too-low" for finding in decision.findings)


def test_provider_promotion_defers_warning_findings() -> None:
    evidence = _bundle(
        ProviderIdentifier.KRAKEN,
        findings=(
            PromotionFinding(
                code="manual-review-needed",
                severity=PromotionFindingSeverity.WARNING,
                message="Manual provider account-plan evidence requires re-review.",
            ),
        ),
    )

    decision = evaluate_provider_promotion(evidence)

    assert decision.outcome is PromotionOutcome.DEGRADE
    assert not decision.provider_enabled


def test_provider_credentials_must_be_named_secret_references() -> None:
    with pytest.raises(ValidationError, match="named secret references"):
        ProviderCredentialEvidence(
            provider_id=ProviderIdentifier.TWELVE_DATA,
            secret_reference="TWELVE_DATA_API_KEY=value",
            authentication_mode="api-key",
            credential_configured=True,
            credential_verified=True,
            verified_at=datetime(2026, 7, 25, tzinfo=UTC),
        )


def test_provider_evidence_rejects_mixed_provider_bundle() -> None:
    with pytest.raises(ValidationError, match="same provider"):
        _bundle(
            ProviderIdentifier.TWELVE_DATA,
            quota_evidence=_quota(ProviderIdentifier.KRAKEN),
        )


def test_license_and_quota_evidence_require_timezone_aware_times() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        ProviderQuotaEvidence(
            provider_id=ProviderIdentifier.KRAKEN,
            quota_policy_id="daily-api-quota",
            request_limit=1000,
            remaining_requests=900,
            required_headroom_ratio=0.5,
            reset_at=datetime(2026, 7, 26),
            observed_at=datetime(2026, 7, 25, tzinfo=UTC),
        )

    with pytest.raises(ValidationError, match="timezone-aware"):
        ProviderLicenseEvidence(
            provider_id=ProviderIdentifier.KRAKEN,
            account_plan_id="paid-plan",
            terms_reference_uri="https://provider.example/terms",
            allowed_permissions=(ProviderPermission.RETRIEVAL,),
            accepted_at=datetime(2026, 7, 25, tzinfo=UTC),
            expires_at=datetime(2026, 7, 25) + timedelta(days=30),
        )
