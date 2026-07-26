from osca.provider_promotion.contracts import (
    PromotionFinding,
    PromotionFindingSeverity,
    PromotionOutcome,
    ProviderCostModel,
    ProviderPermission,
    ProviderProductionEvidenceBundle,
    ProviderPromotionDecision,
)

_REQUIRED_PERMISSIONS = {
    ProviderPermission.RETRIEVAL,
    ProviderPermission.RETENTION,
    ProviderPermission.TRANSFORMATION,
    ProviderPermission.EXPORT,
    ProviderPermission.BACKUP,
}


def evaluate_provider_promotion(
    evidence: ProviderProductionEvidenceBundle,
) -> ProviderPromotionDecision:
    findings = list(evidence.findings)
    findings.extend(evidence.license_evidence.findings)
    findings.extend(evidence.credential_evidence.findings)
    findings.extend(evidence.quota_evidence.findings)

    missing_permissions = _REQUIRED_PERMISSIONS.difference(
        evidence.license_evidence.allowed_permissions
    )
    for permission in sorted(missing_permissions, key=lambda item: item.value):
        findings.append(
            PromotionFinding(
                code=f"missing-{permission.value}-permission",
                severity=PromotionFindingSeverity.ERROR,
                message=f"Provider license evidence lacks {permission.value} permission.",
            )
        )

    if not evidence.credential_evidence.credential_configured:
        findings.append(
            PromotionFinding(
                code="credential-not-configured",
                severity=PromotionFindingSeverity.ERROR,
                message="Provider credentials are not configured through a named secret reference.",
            )
        )
    if not evidence.credential_evidence.credential_verified:
        findings.append(
            PromotionFinding(
                code="credential-not-verified",
                severity=PromotionFindingSeverity.ERROR,
                message="Provider credentials have not passed verification.",
            )
        )

    required_remaining = int(
        evidence.quota_evidence.request_limit
        * evidence.quota_evidence.required_headroom_ratio
    )
    if evidence.quota_evidence.remaining_requests < required_remaining:
        findings.append(
            PromotionFinding(
                code="quota-headroom-too-low",
                severity=PromotionFindingSeverity.ERROR,
                message="Provider quota headroom is below the required promotion threshold.",
            )
        )

    if any(finding.severity is PromotionFindingSeverity.ERROR for finding in findings):
        outcome = PromotionOutcome.BLOCK
        enabled = False
        rationale = "Provider production promotion is blocked by required evidence failures."
    elif any(finding.severity is PromotionFindingSeverity.WARNING for finding in findings):
        outcome = PromotionOutcome.DEGRADE
        enabled = False
        rationale = "Provider production promotion is deferred by warning findings."
    else:
        outcome = PromotionOutcome.APPROVE
        enabled = True
        rationale = "Provider production promotion evidence satisfies deterministic gates."

    return ProviderPromotionDecision(
        provider_id=evidence.provider_id,
        evidence_bundle_id=evidence.evidence_bundle_id,
        outcome=outcome,
        provider_enabled=enabled,
        rationale=rationale,
        findings=tuple(findings),
    )


def promotion_is_enabled(decision: ProviderPromotionDecision) -> bool:
    return decision.outcome is PromotionOutcome.APPROVE and decision.provider_enabled


def provider_supports_no_cost_baseline(
    evidence: ProviderProductionEvidenceBundle,
) -> bool:
    decision = evaluate_provider_promotion(evidence)
    no_cost_models = {
        ProviderCostModel.NO_COST,
        ProviderCostModel.FREE_TIER,
    }
    return (
        evidence.license_evidence.cost_model in no_cost_models
        and not evidence.license_evidence.payment_required
        and promotion_is_enabled(decision)
    )
