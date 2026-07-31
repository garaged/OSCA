from __future__ import annotations

from datetime import UTC, datetime

from osca.production_ingestion.contracts import (
    AdmissionStatus,
    ProductionProvider,
    ProviderAdmissionDecision,
)

_REVIEWED_AT = datetime(2026, 7, 31, tzinfo=UTC)


def provider_admission_policy() -> tuple[ProviderAdmissionDecision, ...]:
    return (
        ProviderAdmissionDecision(
            provider_id=ProductionProvider.SEC_EDGAR,
            status=AdmissionStatus.APPROVED,
            approved_resources=("company_facts", "submissions"),
            internal_use_only=True,
            credential_mode="public-no-key",
            terms_reference_uri="https://www.sec.gov/about/developer-resources",
            evidence_reviewed_at=_REVIEWED_AT,
            rationale=(
                "Approved for bounded internal ingestion from official data.sec.gov "
                "endpoints with declared user agent and fair-access controls."
            ),
            findings=("fair-access-required", "redistribution-not-enabled"),
        ),
        ProviderAdmissionDecision(
            provider_id=ProductionProvider.KRAKEN,
            status=AdmissionStatus.APPROVED,
            approved_resources=("spot_ohlc",),
            internal_use_only=True,
            credential_mode="public-no-key",
            terms_reference_uri="https://www.kraken.com/legal/global-terms",
            evidence_reviewed_at=_REVIEWED_AT,
            rationale=(
                "Approved only for personal/internal retrieval and retention of public "
                "spot OHLC evidence; external redistribution is not enabled."
            ),
            findings=("internal-use-only", "redistribution-not-enabled"),
        ),
        ProviderAdmissionDecision(
            provider_id=ProductionProvider.TWELVE_DATA,
            status=AdmissionStatus.NEEDS_EVIDENCE,
            credential_mode="named-secret-reference",
            terms_reference_uri="https://twelvedata.com/terms",
            evidence_reviewed_at=_REVIEWED_AT,
            rationale=(
                "Exact account plan, market coverage, retention window, and intended "
                "display/non-display rights must be accepted before promotion."
            ),
            findings=("account-plan-evidence-required", "dataset-rights-required"),
        ),
        ProviderAdmissionDecision(
            provider_id=ProductionProvider.ALPHA_VANTAGE,
            status=AdmissionStatus.NEEDS_EVIDENCE,
            credential_mode="named-secret-reference",
            terms_reference_uri="https://www.alphavantage.co/realtime_data_policy/",
            evidence_reviewed_at=_REVIEWED_AT,
            rationale=(
                "Commercial and real-time market-data use requires provider onboarding; "
                "no exact accepted OSCA account-plan evidence is retained."
            ),
            findings=("commercial-onboarding-required",),
        ),
        ProviderAdmissionDecision(
            provider_id=ProductionProvider.NASDAQ_DATA_LINK,
            status=AdmissionStatus.NEEDS_EVIDENCE,
            credential_mode="named-secret-reference",
            terms_reference_uri="https://data.nasdaq.com/terms",
            evidence_reviewed_at=_REVIEWED_AT,
            rationale=(
                "Rights are dataset and order-form specific; no exact OSCA dataset "
                "license, retention, export, and redistribution evidence is accepted."
            ),
            findings=("dataset-license-required", "order-form-evidence-required"),
        ),
        ProviderAdmissionDecision(
            provider_id=ProductionProvider.FRED,
            status=AdmissionStatus.POLICY_BLOCKED,
            credential_mode="named-secret-reference",
            terms_reference_uri="https://fred.stlouisfed.org/legal/terms-of-use/",
            evidence_reviewed_at=_REVIEWED_AT,
            rationale=(
                "Live FRED ingestion remains blocked by unresolved retention and "
                "software/AI-use constraints."
            ),
            findings=("retention-not-permitted", "legal-evidence-required"),
        ),
    )


def admission_for(provider_id: ProductionProvider) -> ProviderAdmissionDecision:
    return next(
        decision
        for decision in provider_admission_policy()
        if decision.provider_id is provider_id
    )
