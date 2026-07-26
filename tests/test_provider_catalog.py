import pytest
from pydantic import ValidationError

from osca.provider_catalog import (
    ProviderCatalogAccessMode,
    ProviderCatalogCapability,
    ProviderCatalogConstraint,
    ProviderCatalogDisposition,
    ProviderCatalogIdentifier,
    ProviderCatalogProfile,
    ProviderImplementationReadiness,
    build_default_no_cost_provider_profiles,
    classify_provider_implementation_readiness,
    preferred_no_cost_profiles,
)
from osca.provider_promotion import ProviderCostModel


def test_default_catalog_preserves_p2_provider_dispositions() -> None:
    profiles = build_default_no_cost_provider_profiles()

    dispositions = {profile.provider_id: profile.disposition for profile in profiles}

    assert dispositions[ProviderCatalogIdentifier.SEC_EDGAR] is (
        ProviderCatalogDisposition.PREFERRED_CANDIDATE
    )
    assert dispositions[ProviderCatalogIdentifier.FRED] is (
        ProviderCatalogDisposition.PREFERRED_CANDIDATE
    )
    assert dispositions[ProviderCatalogIdentifier.ALPHA_VANTAGE] is (
        ProviderCatalogDisposition.CONDITIONAL_CANDIDATE
    )
    assert dispositions[ProviderCatalogIdentifier.NASDAQ_DATA_LINK] is (
        ProviderCatalogDisposition.CONDITIONAL_CANDIDATE
    )
    assert dispositions[ProviderCatalogIdentifier.STOOQ] is ProviderCatalogDisposition.RESEARCH_ONLY
    assert dispositions[ProviderCatalogIdentifier.YAHOO_FINANCE_UNOFFICIAL] is (
        ProviderCatalogDisposition.EXCLUDED
    )


def test_preferred_no_cost_profiles_selects_sec_and_fred_only() -> None:
    profiles = preferred_no_cost_profiles(build_default_no_cost_provider_profiles())

    assert tuple(profile.provider_id for profile in profiles) == (
        ProviderCatalogIdentifier.SEC_EDGAR,
        ProviderCatalogIdentifier.FRED,
    )


def test_readiness_classification_blocks_unofficial_yahoo_path() -> None:
    yahoo = next(
        profile
        for profile in build_default_no_cost_provider_profiles()
        if profile.provider_id is ProviderCatalogIdentifier.YAHOO_FINANCE_UNOFFICIAL
    )

    decision = classify_provider_implementation_readiness(yahoo)

    assert decision.readiness is ProviderImplementationReadiness.BLOCKED
    assert decision.blocking_constraint_ids == ("official-finance-api-not-evidenced",)


def test_conditional_candidates_need_more_evidence() -> None:
    alpha_vantage = next(
        profile
        for profile in build_default_no_cost_provider_profiles()
        if profile.provider_id is ProviderCatalogIdentifier.ALPHA_VANTAGE
    )

    decision = classify_provider_implementation_readiness(alpha_vantage)

    assert decision.readiness is ProviderImplementationReadiness.NEEDS_EVIDENCE
    assert decision.blocking_constraint_ids == ("free-tier-quota-limited",)


def test_preferred_candidates_are_ready_for_contract_planning() -> None:
    fred = next(
        profile
        for profile in build_default_no_cost_provider_profiles()
        if profile.provider_id is ProviderCatalogIdentifier.FRED
    )

    decision = classify_provider_implementation_readiness(fred)

    assert decision.readiness is ProviderImplementationReadiness.READY_FOR_CONTRACTS
    assert decision.blocking_constraint_ids == ()


def test_catalog_profiles_reject_duplicate_capabilities_and_sources() -> None:
    with pytest.raises(ValidationError, match="capabilities"):
        ProviderCatalogProfile(
            provider_id=ProviderCatalogIdentifier.FRED,
            display_name="FRED",
            cost_model=ProviderCostModel.NO_COST,
            payment_required=False,
            access_mode=ProviderCatalogAccessMode.API_KEY_REQUIRED,
            capabilities=(
                ProviderCatalogCapability.MACRO,
                ProviderCatalogCapability.MACRO,
            ),
            disposition=ProviderCatalogDisposition.PREFERRED_CANDIDATE,
            source_uris=("https://provider.example/docs",),
            notes="Duplicate capability example.",
        )

    with pytest.raises(ValidationError, match="source URIs"):
        ProviderCatalogProfile(
            provider_id=ProviderCatalogIdentifier.FRED,
            display_name="FRED",
            cost_model=ProviderCostModel.NO_COST,
            payment_required=False,
            access_mode=ProviderCatalogAccessMode.API_KEY_REQUIRED,
            capabilities=(ProviderCatalogCapability.MACRO,),
            disposition=ProviderCatalogDisposition.PREFERRED_CANDIDATE,
            source_uris=(
                "https://provider.example/docs",
                "https://provider.example/docs",
            ),
            notes="Duplicate source URI example.",
        )


def test_excluded_profiles_require_blocking_constraint() -> None:
    with pytest.raises(ValidationError, match="blocking constraint"):
        ProviderCatalogProfile(
            provider_id=ProviderCatalogIdentifier.YAHOO_FINANCE_UNOFFICIAL,
            display_name="Yahoo Finance unofficial paths",
            cost_model=ProviderCostModel.NO_COST,
            payment_required=False,
            access_mode=ProviderCatalogAccessMode.UNOFFICIAL,
            capabilities=(ProviderCatalogCapability.OHLCV,),
            disposition=ProviderCatalogDisposition.EXCLUDED,
            source_uris=("https://provider.example/terms",),
            constraints=(
                ProviderCatalogConstraint(
                    constraint_id="not-blocking",
                    description="This is not enough to block automation.",
                ),
            ),
            notes="Excluded without blocking constraint.",
        )


def test_preferred_profiles_reject_unofficial_access() -> None:
    with pytest.raises(ValidationError, match="unofficial access"):
        ProviderCatalogProfile(
            provider_id=ProviderCatalogIdentifier.YAHOO_FINANCE_UNOFFICIAL,
            display_name="Yahoo Finance unofficial paths",
            cost_model=ProviderCostModel.NO_COST,
            payment_required=False,
            access_mode=ProviderCatalogAccessMode.UNOFFICIAL,
            capabilities=(ProviderCatalogCapability.OHLCV,),
            disposition=ProviderCatalogDisposition.PREFERRED_CANDIDATE,
            source_uris=("https://provider.example/terms",),
            notes="Incorrect preferred unofficial profile.",
        )
