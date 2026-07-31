from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from osca.provider_catalog import ProviderCatalogIdentifier

Identifier = Annotated[str, Field(min_length=1, max_length=256)]
Description = Annotated[str, Field(min_length=1, max_length=4096)]
LocalPath = Annotated[str, Field(min_length=1, max_length=4096)]


class RuntimeRoutingCapability(StrEnum):
    OHLCV = "ohlcv"
    COMPANY_FACTS = "company_facts"
    FILINGS = "filings"
    MACRO_SERIES = "macro_series"


class RuntimeRoutingSource(StrEnum):
    LOCAL_OHLCV = "local_ohlcv"
    SEC_EDGAR_FIXTURE = "sec_edgar_fixture"
    SEC_EDGAR_LIVE_PREVIEW = "sec_edgar_live_preview"


class RuntimeRoutingStatus(StrEnum):
    SELECTED = "selected"
    POLICY_BLOCKED = "policy_blocked"
    PROVIDER_UNAVAILABLE = "provider_unavailable"


class RuntimeRoutingBatchOutcome(StrEnum):
    SUCCEEDED = "succeeded"
    PARTIAL = "partial"
    BLOCKED = "blocked"
    UNAVAILABLE = "unavailable"


class RuntimeRoutingRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.runtime-routing.request"] = "osca.runtime-routing.request"
    version: Literal["1.0.0"] = "1.0.0"
    request_id: UUID = Field(default_factory=uuid4)
    capability: RuntimeRoutingCapability
    resource_id: Identifier
    preferred_provider: Identifier | None = None
    local_payload_uri: LocalPath | None = None
    timeframe: Identifier | None = None
    fixture_path: Path | None = None
    network_access_enabled: bool = False
    user_agent: Identifier | None = None
    force_refresh: bool = False
    secret_reference: Identifier | None = None
    max_age_seconds: int | None = Field(default=None, ge=1)
    allow_stale: bool = False
    requested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("requested_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("runtime routing request time must be timezone-aware")
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def validate_capability_options(self) -> Self:
        if self.capability is RuntimeRoutingCapability.OHLCV:
            if any(
                value is not None
                for value in (self.fixture_path, self.user_agent, self.secret_reference)
            ) or self.network_access_enabled or self.force_refresh:
                raise ValueError("OHLCV routing only accepts local payload options")
        elif self.capability in {
            RuntimeRoutingCapability.COMPANY_FACTS,
            RuntimeRoutingCapability.FILINGS,
        }:
            if self.local_payload_uri is not None or self.timeframe is not None:
                raise ValueError("SEC routing does not accept local OHLCV options")
            if self.secret_reference is not None:
                raise ValueError("SEC routing does not accept credential references")
            if self.fixture_path is not None and self.network_access_enabled:
                raise ValueError("SEC routing cannot combine fixture and live preview")
            if self.user_agent is not None and not self.network_access_enabled:
                raise ValueError("SEC fixture routing does not accept a live user-agent")
        else:
            if any(
                value is not None
                for value in (
                    self.local_payload_uri,
                    self.timeframe,
                    self.fixture_path,
                    self.user_agent,
                )
            ) or self.force_refresh:
                raise ValueError("macro routing only accepts provider and policy options")
        return self


class RuntimeRoutingDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.runtime-routing.decision"] = "osca.runtime-routing.decision"
    version: Literal["1.0.0"] = "1.0.0"
    decision_id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    capability: RuntimeRoutingCapability
    resource_id: Identifier
    status: RuntimeRoutingStatus
    selected_source: RuntimeRoutingSource | None = None
    provider_id: ProviderCatalogIdentifier | None = None
    source_uri: Identifier | None = None
    payload_uri: LocalPath | None = None
    metadata_uri: LocalPath | None = None
    stale: bool = False
    cache_hit: bool = False
    network_access_used: bool = False
    network_access_enabled: bool = False
    credential_materialized: Literal[False] = False
    production_ingestion_enabled: Literal[False] = False
    recommendations_enabled: Literal[False] = False
    real_capital_orders_enabled: Literal[False] = False
    evidence_only: Literal[True] = True
    rationale: Description
    finding_ids: tuple[Identifier, ...] = ()
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_decision(self) -> Self:
        if self.generated_at.tzinfo is None or self.generated_at.utcoffset() is None:
            raise ValueError("runtime routing decision time must be timezone-aware")
        if self.status is RuntimeRoutingStatus.SELECTED:
            if self.selected_source is None or self.payload_uri is None:
                raise ValueError("selected routing decisions require source and payload")
        else:
            if self.selected_source is not None or self.payload_uri is not None:
                raise ValueError("non-selected routing decisions cannot expose a payload")
            if self.network_access_used:
                raise ValueError("non-selected routing decisions cannot use network access")
        if self.network_access_used and not self.network_access_enabled:
            raise ValueError("routing cannot use network access without enablement")
        return self


class RuntimeRoutingBatchResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.runtime-routing.batch-result"] = (
        "osca.runtime-routing.batch-result"
    )
    version: Literal["1.0.0"] = "1.0.0"
    outcome: RuntimeRoutingBatchOutcome
    decisions: tuple[RuntimeRoutingDecision, ...] = Field(min_length=1)
    selected_count: int = Field(ge=0)
    policy_blocked_count: int = Field(ge=0)
    provider_unavailable_count: int = Field(ge=0)
    non_macro_continued: bool

    @model_validator(mode="after")
    def validate_counts(self) -> Self:
        expected_selected = sum(
            decision.status is RuntimeRoutingStatus.SELECTED
            for decision in self.decisions
        )
        expected_blocked = sum(
            decision.status is RuntimeRoutingStatus.POLICY_BLOCKED
            for decision in self.decisions
        )
        expected_unavailable = sum(
            decision.status is RuntimeRoutingStatus.PROVIDER_UNAVAILABLE
            for decision in self.decisions
        )
        if (
            self.selected_count,
            self.policy_blocked_count,
            self.provider_unavailable_count,
        ) != (expected_selected, expected_blocked, expected_unavailable):
            raise ValueError("runtime routing batch counts do not match decisions")
        return self
