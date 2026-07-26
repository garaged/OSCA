from osca.provider_catalog.contracts import (
    ProviderCatalogAccessMode,
    ProviderCatalogCapability,
    ProviderCatalogConstraint,
    ProviderCatalogDisposition,
    ProviderCatalogIdentifier,
    ProviderCatalogProfile,
    ProviderImplementationReadiness,
    ProviderImplementationReadinessDecision,
)
from osca.provider_promotion import ProviderCostModel


def build_default_no_cost_provider_profiles() -> tuple[ProviderCatalogProfile, ...]:
    return (
        ProviderCatalogProfile(
            provider_id=ProviderCatalogIdentifier.SEC_EDGAR,
            display_name="SEC EDGAR / data.sec.gov",
            cost_model=ProviderCostModel.NO_COST,
            payment_required=False,
            access_mode=ProviderCatalogAccessMode.PUBLIC_NO_KEY,
            capabilities=(
                ProviderCatalogCapability.FUNDAMENTALS,
                ProviderCatalogCapability.FILINGS,
                ProviderCatalogCapability.DISCLOSURE_EVENTS,
            ),
            disposition=ProviderCatalogDisposition.PREFERRED_CANDIDATE,
            source_uris=(
                "https://www.sec.gov/search-filings/edgar-application-programming-interfaces",
                "https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data",
            ),
            constraints=(
                ProviderCatalogConstraint(
                    constraint_id="declared-user-agent-required",
                    description="Automated access must use a declared user-agent.",
                ),
                ProviderCatalogConstraint(
                    constraint_id="fair-access-rate-limit",
                    description="Automated access must respect SEC fair-access limits.",
                ),
            ),
            notes="Official public filing, company-facts, and disclosure-event enrichment source.",
        ),
        ProviderCatalogProfile(
            provider_id=ProviderCatalogIdentifier.FRED,
            display_name="FRED",
            cost_model=ProviderCostModel.NO_COST,
            payment_required=False,
            access_mode=ProviderCatalogAccessMode.API_KEY_REQUIRED,
            capabilities=(ProviderCatalogCapability.MACRO,),
            disposition=ProviderCatalogDisposition.PREFERRED_CANDIDATE,
            source_uris=("https://fred.stlouisfed.org/docs/api/terms_of_use.html",),
            constraints=(
                ProviderCatalogConstraint(
                    constraint_id="registered-api-key-required",
                    description="FRED API use requires a registered API key.",
                ),
            ),
            notes="Official macroeconomic enrichment source; not an OHLCV substitute.",
        ),
        ProviderCatalogProfile(
            provider_id=ProviderCatalogIdentifier.ALPHA_VANTAGE,
            display_name="Alpha Vantage",
            cost_model=ProviderCostModel.FREE_TIER,
            payment_required=False,
            access_mode=ProviderCatalogAccessMode.API_KEY_REQUIRED,
            capabilities=(
                ProviderCatalogCapability.OHLCV,
                ProviderCatalogCapability.INDICATORS,
            ),
            disposition=ProviderCatalogDisposition.CONDITIONAL_CANDIDATE,
            source_uris=("https://www.alphavantage.co/support/",),
            constraints=(
                ProviderCatalogConstraint(
                    constraint_id="free-tier-quota-limited",
                    description="Free-tier requests are low-volume and unsuitable for broad refresh.",
                    blocks_default_automation=True,
                ),
            ),
            notes=(
                "Potential low-volume equity fallback after exact endpoint, quota, "
                "and terms evidence."
            ),
        ),
        ProviderCatalogProfile(
            provider_id=ProviderCatalogIdentifier.NASDAQ_DATA_LINK,
            display_name="Nasdaq Data Link",
            cost_model=ProviderCostModel.FREE_TIER,
            payment_required=False,
            access_mode=ProviderCatalogAccessMode.ACCOUNT_KEY_LIKELY,
            capabilities=(
                ProviderCatalogCapability.MACRO,
                ProviderCatalogCapability.FUNDAMENTALS,
                ProviderCatalogCapability.RESEARCH_DATA,
            ),
            disposition=ProviderCatalogDisposition.CONDITIONAL_CANDIDATE,
            source_uris=("https://docs.data.nasdaq.com/docs/getting-started",),
            constraints=(
                ProviderCatalogConstraint(
                    constraint_id="dataset-specific-terms-required",
                    description=(
                        "Each dataset must be gated by its own license and "
                        "redistribution evidence."
                    ),
                    blocks_default_automation=True,
                ),
            ),
            notes=(
                "Dataset-specific source; useful only after named dataset terms "
                "are accepted."
            ),
        ),
        ProviderCatalogProfile(
            provider_id=ProviderCatalogIdentifier.STOOQ,
            display_name="Stooq",
            cost_model=ProviderCostModel.NO_COST,
            payment_required=False,
            access_mode=ProviderCatalogAccessMode.UNCLEAR,
            capabilities=(ProviderCatalogCapability.RESEARCH_DATA,),
            disposition=ProviderCatalogDisposition.RESEARCH_ONLY,
            source_uris=("https://stooq.com/",),
            constraints=(
                ProviderCatalogConstraint(
                    constraint_id="automation-terms-unclear",
                    description=(
                        "Automation, stability, and redistribution terms are not "
                        "clear enough."
                    ),
                    blocks_default_automation=True,
                ),
            ),
            notes="Research-only until official automation and redistribution evidence is accepted.",
        ),
        ProviderCatalogProfile(
            provider_id=ProviderCatalogIdentifier.YAHOO_FINANCE_UNOFFICIAL,
            display_name="Yahoo Finance unofficial paths",
            cost_model=ProviderCostModel.NO_COST,
            payment_required=False,
            access_mode=ProviderCatalogAccessMode.UNOFFICIAL,
            capabilities=(ProviderCatalogCapability.OHLCV,),
            disposition=ProviderCatalogDisposition.EXCLUDED,
            source_uris=(
                "https://legal.yahoo.com/us/en/yahoo/terms/product-atos/apiforydn/index.html",
            ),
            constraints=(
                ProviderCatalogConstraint(
                    constraint_id="official-finance-api-not-evidenced",
                    description=(
                        "No compliant official public Yahoo Finance market-data "
                        "API path is evidenced."
                    ),
                    blocks_default_automation=True,
                ),
            ),
            notes="Excluded until a compliant official API or license path is evidenced.",
        ),
    )


def classify_provider_implementation_readiness(
    profile: ProviderCatalogProfile,
) -> ProviderImplementationReadinessDecision:
    blocking_constraint_ids = tuple(
        constraint.constraint_id
        for constraint in profile.constraints
        if constraint.blocks_default_automation
    )

    if profile.disposition is ProviderCatalogDisposition.PREFERRED_CANDIDATE:
        readiness = ProviderImplementationReadiness.READY_FOR_CONTRACTS
        rationale = "Preferred no-cost provider can proceed to adapter-contract planning."
    elif profile.disposition is ProviderCatalogDisposition.CONDITIONAL_CANDIDATE:
        readiness = ProviderImplementationReadiness.NEEDS_EVIDENCE
        rationale = "Provider needs exact terms, quota, dataset, or account-plan evidence."
    else:
        readiness = ProviderImplementationReadiness.BLOCKED
        rationale = "Provider disposition blocks default automated implementation."

    if blocking_constraint_ids and readiness is ProviderImplementationReadiness.READY_FOR_CONTRACTS:
        readiness = ProviderImplementationReadiness.NEEDS_EVIDENCE
        rationale = "Blocking provider constraints must be resolved before implementation planning."

    return ProviderImplementationReadinessDecision(
        provider_id=profile.provider_id,
        readiness=readiness,
        rationale=rationale,
        blocking_constraint_ids=blocking_constraint_ids,
    )


def preferred_no_cost_profiles(
    profiles: tuple[ProviderCatalogProfile, ...],
) -> tuple[ProviderCatalogProfile, ...]:
    return tuple(
        profile
        for profile in profiles
        if profile.disposition is ProviderCatalogDisposition.PREFERRED_CANDIDATE
        and not profile.payment_required
    )
