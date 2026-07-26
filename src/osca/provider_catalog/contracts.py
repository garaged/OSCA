from enum import StrEnum
from typing import Annotated, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from osca.provider_promotion import ProviderCostModel

Identifier = Annotated[str, Field(min_length=1, max_length=128)]
Description = Annotated[str, Field(min_length=1, max_length=2048)]


class ProviderCatalogIdentifier(StrEnum):
    SEC_EDGAR = "sec_edgar"
    FRED = "fred"
    ALPHA_VANTAGE = "alpha_vantage"
    NASDAQ_DATA_LINK = "nasdaq_data_link"
    STOOQ = "stooq"
    YAHOO_FINANCE_UNOFFICIAL = "yahoo_finance_unofficial"


class ProviderCatalogDisposition(StrEnum):
    PREFERRED_CANDIDATE = "preferred_candidate"
    CONDITIONAL_CANDIDATE = "conditional_candidate"
    RESEARCH_ONLY = "research_only"
    EXCLUDED = "excluded"


class ProviderCatalogCapability(StrEnum):
    OHLCV = "ohlcv"
    MACRO = "macro"
    FUNDAMENTALS = "fundamentals"
    FILINGS = "filings"
    DISCLOSURE_EVENTS = "disclosure_events"
    INDICATORS = "indicators"
    RESEARCH_DATA = "research_data"


class ProviderCatalogAccessMode(StrEnum):
    PUBLIC_NO_KEY = "public_no_key"
    API_KEY_REQUIRED = "api_key_required"
    ACCOUNT_KEY_LIKELY = "account_key_likely"
    UNCLEAR = "unclear"
    UNOFFICIAL = "unofficial"


class ProviderImplementationReadiness(StrEnum):
    READY_FOR_CONTRACTS = "ready_for_contracts"
    NEEDS_EVIDENCE = "needs_evidence"
    BLOCKED = "blocked"


class ProviderCatalogConstraint(BaseModel):
    model_config = ConfigDict(frozen=True)

    constraint_id: Identifier
    description: Description
    blocks_default_automation: bool = False


class ProviderCatalogProfile(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.provider-catalog.profile"] = "osca.provider-catalog.profile"
    version: Literal["1.0.0"] = "1.0.0"
    profile_id: UUID = Field(default_factory=uuid4)
    provider_id: ProviderCatalogIdentifier
    display_name: Identifier
    cost_model: ProviderCostModel
    payment_required: bool
    access_mode: ProviderCatalogAccessMode
    capabilities: tuple[ProviderCatalogCapability, ...] = Field(min_length=1)
    disposition: ProviderCatalogDisposition
    source_uris: tuple[Identifier, ...] = Field(min_length=1)
    constraints: tuple[ProviderCatalogConstraint, ...] = ()
    production_promotion_required: bool = True
    notes: Description

    @model_validator(mode="after")
    def validate_profile(self) -> Self:
        if self.cost_model is ProviderCostModel.PAID and not self.payment_required:
            raise ValueError("paid provider profiles must require payment")
        if self.cost_model is not ProviderCostModel.PAID and self.payment_required:
            raise ValueError("no-cost provider profiles must not require payment")
        if len(set(self.capabilities)) != len(self.capabilities):
            raise ValueError("provider catalog capabilities must be unique")
        if len(set(self.source_uris)) != len(self.source_uris):
            raise ValueError("provider catalog source URIs must be unique")
        constraint_ids = tuple(constraint.constraint_id for constraint in self.constraints)
        if len(set(constraint_ids)) != len(constraint_ids):
            raise ValueError("provider catalog constraint ids must be unique")
        if self.disposition is ProviderCatalogDisposition.PREFERRED_CANDIDATE:
            if self.payment_required:
                raise ValueError("preferred no-cost candidates must not require payment")
            if self.access_mode is ProviderCatalogAccessMode.UNOFFICIAL:
                raise ValueError("preferred candidates must not use unofficial access")
        if self.disposition is ProviderCatalogDisposition.EXCLUDED:
            has_blocking_constraint = any(
                constraint.blocks_default_automation for constraint in self.constraints
            )
            if not has_blocking_constraint:
                raise ValueError("excluded providers must retain a blocking constraint")
        return self


class ProviderImplementationReadinessDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.provider-catalog.readiness-decision"] = (
        "osca.provider-catalog.readiness-decision"
    )
    version: Literal["1.0.0"] = "1.0.0"
    decision_id: UUID = Field(default_factory=uuid4)
    provider_id: ProviderCatalogIdentifier
    readiness: ProviderImplementationReadiness
    rationale: Description
    blocking_constraint_ids: tuple[Identifier, ...] = ()
