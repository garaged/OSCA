from osca.provider_adapters.contracts import (
    ProviderAdapterContract,
    ProviderAdapterCredentialRequirement,
    ProviderAdapterEndpoint,
    ProviderAdapterFixture,
    ProviderAdapterRequest,
    ProviderAdapterValidationDecision,
)
from osca.provider_catalog import (
    ProviderCatalogIdentifier,
    ProviderCatalogProfile,
    ProviderImplementationReadiness,
    classify_provider_implementation_readiness,
    preferred_no_cost_profiles,
)


def build_default_preferred_no_cost_adapter_contracts(
    profiles: tuple[ProviderCatalogProfile, ...],
) -> tuple[ProviderAdapterContract, ...]:
    ready_profiles = tuple(
        profile
        for profile in preferred_no_cost_profiles(profiles)
        if classify_provider_implementation_readiness(profile).readiness
        is ProviderImplementationReadiness.READY_FOR_CONTRACTS
    )
    ready_ids = {profile.provider_id for profile in ready_profiles}

    contracts: list[ProviderAdapterContract] = []
    if ProviderCatalogIdentifier.SEC_EDGAR in ready_ids:
        contracts.append(
            ProviderAdapterContract(
                provider_id=ProviderCatalogIdentifier.SEC_EDGAR,
                display_name="SEC EDGAR / data.sec.gov",
                endpoints=(
                    ProviderAdapterEndpoint.SEC_COMPANY_FACTS,
                    ProviderAdapterEndpoint.SEC_SUBMISSIONS,
                ),
                credential_requirement=(
                    ProviderAdapterCredentialRequirement.PUBLIC_NO_KEY
                ),
                source_uri=(
                    "https://www.sec.gov/search-filings/"
                    "edgar-application-programming-interfaces"
                ),
                user_agent_required=True,
                rate_limit_policy=(
                    "Adapter implementations must apply declared user-agent and "
                    "fair-access throttling before network access is enabled."
                ),
                notes=(
                    "Fixture-backed adapter contract for company facts and "
                    "submission metadata enrichment."
                ),
            )
        )
    if ProviderCatalogIdentifier.FRED in ready_ids:
        contracts.append(
            ProviderAdapterContract(
                provider_id=ProviderCatalogIdentifier.FRED,
                display_name="FRED",
                endpoints=(ProviderAdapterEndpoint.FRED_SERIES_OBSERVATIONS,),
                credential_requirement=(
                    ProviderAdapterCredentialRequirement.NAMED_API_KEY_REFERENCE
                ),
                source_uri=(
                    "https://fred.stlouisfed.org/docs/api/fred/"
                    "series_observations.html"
                ),
                user_agent_required=False,
                rate_limit_policy=(
                    "Adapter implementations must enforce API-key, quota, and "
                    "terms evidence before network access is enabled."
                ),
                notes=(
                    "Fixture-backed adapter contract for macroeconomic series "
                    "enrichment."
                ),
            )
        )

    return tuple(contracts)


def provider_adapter_contract_by_id(
    contracts: tuple[ProviderAdapterContract, ...],
    provider_id: ProviderCatalogIdentifier,
) -> ProviderAdapterContract | None:
    for contract in contracts:
        if contract.provider_id is provider_id:
            return contract
    return None


def validate_adapter_request_for_contract(
    contract: ProviderAdapterContract,
    request: ProviderAdapterRequest,
) -> ProviderAdapterValidationDecision:
    findings: list[str] = []
    if request.provider_id is not contract.provider_id:
        findings.append("provider-mismatch")
    if request.endpoint not in contract.endpoints:
        findings.append("endpoint-not-supported")
    if request.network_access_enabled or contract.network_access_enabled:
        findings.append("network-access-not-enabled")

    return ProviderAdapterValidationDecision(
        provider_id=request.provider_id,
        accepted=not findings,
        rationale=(
            "Request matches fixture-backed adapter contract."
            if not findings
            else "Request does not match fixture-backed adapter contract."
        ),
        finding_ids=tuple(findings),
    )


def validate_adapter_fixture_for_contract(
    contract: ProviderAdapterContract,
    fixture: ProviderAdapterFixture,
) -> ProviderAdapterValidationDecision:
    findings: list[str] = []
    if fixture.provider_id is not contract.provider_id:
        findings.append("provider-mismatch")
    if fixture.endpoint not in contract.endpoints:
        findings.append("endpoint-not-supported")
    if fixture.network_access_enabled or contract.network_access_enabled:
        findings.append("network-access-not-enabled")
    if fixture.record_count == 0:
        findings.append("empty-fixture")

    return ProviderAdapterValidationDecision(
        provider_id=fixture.provider_id,
        accepted=not findings,
        rationale=(
            "Fixture matches adapter contract and contains records."
            if not findings
            else "Fixture does not satisfy adapter contract requirements."
        ),
        finding_ids=tuple(findings),
    )
