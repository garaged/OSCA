from enum import StrEnum
from typing import Annotated, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from osca.provider_catalog import ProviderCatalogIdentifier

Identifier = Annotated[str, Field(min_length=1, max_length=128)]
Description = Annotated[str, Field(min_length=1, max_length=2048)]


class ProviderAdapterEndpoint(StrEnum):
    SEC_COMPANY_FACTS = "sec_company_facts"
    SEC_SUBMISSIONS = "sec_submissions"
    FRED_SERIES_OBSERVATIONS = "fred_series_observations"


class ProviderAdapterCredentialRequirement(StrEnum):
    PUBLIC_NO_KEY = "public_no_key"
    NAMED_API_KEY_REFERENCE = "named_api_key_reference"


class ProviderAdapterContract(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.provider-adapters.contract"] = (
        "osca.provider-adapters.contract"
    )
    version: Literal["1.0.0"] = "1.0.0"
    contract_id: UUID = Field(default_factory=uuid4)
    provider_id: ProviderCatalogIdentifier
    display_name: Identifier
    endpoints: tuple[ProviderAdapterEndpoint, ...] = Field(min_length=1)
    credential_requirement: ProviderAdapterCredentialRequirement
    source_uri: Identifier
    user_agent_required: bool
    rate_limit_policy: Description
    fixture_required: Literal[True] = True
    network_access_enabled: Literal[False] = False
    production_promotion_required: Literal[True] = True
    notes: Description

    @model_validator(mode="after")
    def validate_contract(self) -> Self:
        if len(set(self.endpoints)) != len(self.endpoints):
            raise ValueError("provider adapter endpoints must be unique")
        for endpoint in self.endpoints:
            _validate_provider_endpoint(self.provider_id, endpoint)
        if self.provider_id is ProviderCatalogIdentifier.SEC_EDGAR:
            if (
                self.credential_requirement
                is not ProviderAdapterCredentialRequirement.PUBLIC_NO_KEY
            ):
                raise ValueError(
                    "SEC EDGAR adapter contract must not require an API key"
                )
            if not self.user_agent_required:
                raise ValueError("SEC EDGAR adapter contract must require a user-agent")
        if self.provider_id is ProviderCatalogIdentifier.FRED:
            if (
                self.credential_requirement
                is not ProviderAdapterCredentialRequirement.NAMED_API_KEY_REFERENCE
            ):
                raise ValueError(
                    "FRED adapter contract must require a named API-key reference"
                )
        return self


class ProviderAdapterRequestParameter(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: Identifier
    value: Identifier


class ProviderAdapterRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.provider-adapters.request"] = "osca.provider-adapters.request"
    version: Literal["1.0.0"] = "1.0.0"
    request_id: UUID = Field(default_factory=uuid4)
    provider_id: ProviderCatalogIdentifier
    endpoint: ProviderAdapterEndpoint
    resource_id: Identifier
    parameters: tuple[ProviderAdapterRequestParameter, ...] = ()
    network_access_enabled: Literal[False] = False

    @model_validator(mode="after")
    def validate_request(self) -> Self:
        _validate_provider_endpoint(self.provider_id, self.endpoint)
        parameter_names = tuple(parameter.name for parameter in self.parameters)
        if len(set(parameter_names)) != len(parameter_names):
            raise ValueError("provider adapter request parameters must be unique")
        return self


class ProviderAdapterFixture(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.provider-adapters.fixture"] = "osca.provider-adapters.fixture"
    version: Literal["1.0.0"] = "1.0.0"
    fixture_id: UUID = Field(default_factory=uuid4)
    provider_id: ProviderCatalogIdentifier
    endpoint: ProviderAdapterEndpoint
    fixture_name: Identifier
    resource_id: Identifier
    payload_sha256: Annotated[str, Field(min_length=64, max_length=64)]
    source_uri: Identifier
    record_count: int = Field(ge=0)
    network_access_enabled: Literal[False] = False

    @model_validator(mode="after")
    def validate_fixture(self) -> Self:
        _validate_provider_endpoint(self.provider_id, self.endpoint)
        if not all(
            character in "0123456789abcdef" for character in self.payload_sha256
        ):
            raise ValueError("fixture payload sha256 must be lowercase hexadecimal")
        return self


class ProviderAdapterValidationDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.provider-adapters.validation-decision"] = (
        "osca.provider-adapters.validation-decision"
    )
    version: Literal["1.0.0"] = "1.0.0"
    decision_id: UUID = Field(default_factory=uuid4)
    provider_id: ProviderCatalogIdentifier
    accepted: bool
    rationale: Description
    finding_ids: tuple[Identifier, ...] = ()


def _validate_provider_endpoint(
    provider_id: ProviderCatalogIdentifier,
    endpoint: ProviderAdapterEndpoint,
) -> None:
    if provider_id is ProviderCatalogIdentifier.SEC_EDGAR and endpoint not in {
        ProviderAdapterEndpoint.SEC_COMPANY_FACTS,
        ProviderAdapterEndpoint.SEC_SUBMISSIONS,
    }:
        raise ValueError("SEC EDGAR adapter endpoints are limited to SEC filing APIs")
    if provider_id is ProviderCatalogIdentifier.FRED and endpoint not in {
        ProviderAdapterEndpoint.FRED_SERIES_OBSERVATIONS,
    }:
        raise ValueError(
            "FRED adapter endpoints are limited to macro series observations"
        )
    if provider_id not in {
        ProviderCatalogIdentifier.SEC_EDGAR,
        ProviderCatalogIdentifier.FRED,
    }:
        raise ValueError(
            "provider adapter contracts are limited to preferred candidates"
        )
