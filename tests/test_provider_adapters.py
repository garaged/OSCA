import pytest
from pydantic import ValidationError

from osca.provider_adapters import (
    ProviderAdapterEndpoint,
    ProviderAdapterFixture,
    ProviderAdapterRequest,
    build_default_preferred_no_cost_adapter_contracts,
    provider_adapter_contract_by_id,
    validate_adapter_fixture_for_contract,
    validate_adapter_request_for_contract,
)
from osca.provider_catalog import (
    ProviderCatalogIdentifier,
    build_default_no_cost_provider_profiles,
)


def test_default_adapter_contracts_are_limited_to_sec_and_fred() -> None:
    contracts = build_default_preferred_no_cost_adapter_contracts(
        build_default_no_cost_provider_profiles()
    )

    assert tuple(contract.provider_id for contract in contracts) == (
        ProviderCatalogIdentifier.SEC_EDGAR,
        ProviderCatalogIdentifier.FRED,
    )
    assert all(contract.fixture_required for contract in contracts)
    assert all(not contract.network_access_enabled for contract in contracts)


def test_sec_adapter_contract_requires_user_agent_and_public_no_key() -> None:
    contracts = build_default_preferred_no_cost_adapter_contracts(
        build_default_no_cost_provider_profiles()
    )
    sec_contract = provider_adapter_contract_by_id(
        contracts,
        ProviderCatalogIdentifier.SEC_EDGAR,
    )

    assert sec_contract is not None
    assert sec_contract.user_agent_required
    assert sec_contract.endpoints == (
        ProviderAdapterEndpoint.SEC_COMPANY_FACTS,
        ProviderAdapterEndpoint.SEC_SUBMISSIONS,
    )


def test_fred_adapter_contract_requires_named_api_key_reference() -> None:
    contracts = build_default_preferred_no_cost_adapter_contracts(
        build_default_no_cost_provider_profiles()
    )
    fred_contract = provider_adapter_contract_by_id(
        contracts,
        ProviderCatalogIdentifier.FRED,
    )

    assert fred_contract is not None
    assert fred_contract.endpoints == (
        ProviderAdapterEndpoint.FRED_SERIES_OBSERVATIONS,
    )
    assert "API-key" in fred_contract.rate_limit_policy


def test_adapter_request_validation_accepts_matching_fixture_backed_request() -> None:
    contracts = build_default_preferred_no_cost_adapter_contracts(
        build_default_no_cost_provider_profiles()
    )
    sec_contract = provider_adapter_contract_by_id(
        contracts,
        ProviderCatalogIdentifier.SEC_EDGAR,
    )
    assert sec_contract is not None

    request = ProviderAdapterRequest(
        provider_id=ProviderCatalogIdentifier.SEC_EDGAR,
        endpoint=ProviderAdapterEndpoint.SEC_COMPANY_FACTS,
        resource_id="CIK0000320193",
    )

    decision = validate_adapter_request_for_contract(sec_contract, request)

    assert decision.accepted
    assert decision.finding_ids == ()


def test_adapter_request_validation_rejects_wrong_endpoint() -> None:
    contracts = build_default_preferred_no_cost_adapter_contracts(
        build_default_no_cost_provider_profiles()
    )
    sec_contract = provider_adapter_contract_by_id(
        contracts,
        ProviderCatalogIdentifier.SEC_EDGAR,
    )
    assert sec_contract is not None

    request = ProviderAdapterRequest(
        provider_id=ProviderCatalogIdentifier.SEC_EDGAR,
        endpoint=ProviderAdapterEndpoint.SEC_SUBMISSIONS,
        resource_id="CIK0000320193",
    )
    fred_contract = provider_adapter_contract_by_id(
        contracts,
        ProviderCatalogIdentifier.FRED,
    )
    assert fred_contract is not None

    decision = validate_adapter_request_for_contract(fred_contract, request)

    assert not decision.accepted
    assert decision.finding_ids == ("provider-mismatch", "endpoint-not-supported")


def test_adapter_fixture_validation_requires_records_and_matching_contract() -> None:
    contracts = build_default_preferred_no_cost_adapter_contracts(
        build_default_no_cost_provider_profiles()
    )
    fred_contract = provider_adapter_contract_by_id(
        contracts,
        ProviderCatalogIdentifier.FRED,
    )
    assert fred_contract is not None

    fixture = ProviderAdapterFixture(
        provider_id=ProviderCatalogIdentifier.FRED,
        endpoint=ProviderAdapterEndpoint.FRED_SERIES_OBSERVATIONS,
        fixture_name="fred-cpi-observations.json",
        resource_id="CPIAUCSL",
        payload_sha256="a" * 64,
        source_uri="fixtures/provider_adapters/fred-cpi-observations.json",
        record_count=3,
    )

    decision = validate_adapter_fixture_for_contract(fred_contract, fixture)

    assert decision.accepted
    assert decision.finding_ids == ()


def test_adapter_fixture_rejects_non_hex_sha() -> None:
    with pytest.raises(ValidationError, match="lowercase hexadecimal"):
        ProviderAdapterFixture(
            provider_id=ProviderCatalogIdentifier.FRED,
            endpoint=ProviderAdapterEndpoint.FRED_SERIES_OBSERVATIONS,
            fixture_name="bad-fixture.json",
            resource_id="CPIAUCSL",
            payload_sha256="z" * 64,
            source_uri="fixtures/provider_adapters/bad-fixture.json",
            record_count=1,
        )


def test_adapter_contracts_reject_non_preferred_provider_requests() -> None:
    with pytest.raises(ValidationError, match="preferred candidates"):
        ProviderAdapterRequest(
            provider_id=ProviderCatalogIdentifier.ALPHA_VANTAGE,
            endpoint=ProviderAdapterEndpoint.FRED_SERIES_OBSERVATIONS,
            resource_id="IBM",
        )
