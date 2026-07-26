from datetime import UTC, datetime

from osca.provider_promotion import (
    PromotionOutcome,
    ProviderAssetClass,
    ProviderCapabilityScope,
    ProviderCredentialEvidence,
    ProviderIdentifier,
    ProviderLicenseEvidence,
    ProviderPermission,
    ProviderProductionEvidenceBundle,
    ProviderQuotaEvidence,
    SQLiteProviderPromotionStore,
    evaluate_provider_promotion,
)


def _evidence(provider_id: ProviderIdentifier) -> ProviderProductionEvidenceBundle:
    return ProviderProductionEvidenceBundle(
        provider_id=provider_id,
        capability_scope=ProviderCapabilityScope(
            provider_id=provider_id,
            asset_classes=(ProviderAssetClass.SPOT_CRYPTO,),
            intervals=("1d", "1h"),
            capabilities=("historical_bars",),
        ),
        license_evidence=ProviderLicenseEvidence(
            provider_id=provider_id,
            account_plan_id="paid-plan",
            terms_reference_uri="https://provider.example/terms",
            allowed_permissions=(
                ProviderPermission.RETRIEVAL,
                ProviderPermission.RETENTION,
                ProviderPermission.TRANSFORMATION,
                ProviderPermission.EXPORT,
                ProviderPermission.BACKUP,
            ),
            accepted_at=datetime(2026, 7, 25, tzinfo=UTC),
        ),
        credential_evidence=ProviderCredentialEvidence(
            provider_id=provider_id,
            secret_reference=f"secret:providers/{provider_id.value}/api-key",
            authentication_mode="api-key",
            credential_configured=True,
            credential_verified=True,
            verified_at=datetime(2026, 7, 25, tzinfo=UTC),
        ),
        quota_evidence=ProviderQuotaEvidence(
            provider_id=provider_id,
            quota_policy_id="daily-api-quota",
            request_limit=1000,
            remaining_requests=800,
            required_headroom_ratio=0.5,
            reset_at=datetime(2026, 7, 26, tzinfo=UTC),
            observed_at=datetime(2026, 7, 25, tzinfo=UTC),
        ),
        retention_policy_id="retain-source-and-canonical",
        export_policy_id="derived-export-allowed",
        backup_policy_id="metadata-and-retained-source-backup",
        reviewed_by="architecture-authority",
        reviewed_at=datetime(2026, 7, 25, tzinfo=UTC),
    )


def test_provider_promotion_store_round_trips_evidence_and_decisions(tmp_path) -> None:
    store = SQLiteProviderPromotionStore(tmp_path / "provider-promotion.sqlite3")
    store.initialize()
    evidence = _evidence(ProviderIdentifier.KRAKEN)
    decision = evaluate_provider_promotion(evidence)

    store.save_evidence_bundle(evidence)
    store.save_promotion_decision(decision)

    evidence_records = store.list_evidence_bundles(ProviderIdentifier.KRAKEN)
    decision_records = store.list_promotion_decisions(ProviderIdentifier.KRAKEN)

    assert evidence_records == (evidence,)
    assert len(decision_records) == 1
    assert decision_records[0].outcome is PromotionOutcome.APPROVE
    assert decision_records[0].evidence_bundle_id == evidence.evidence_bundle_id
    assert store.list_evidence_bundles(ProviderIdentifier.TWELVE_DATA) == ()
