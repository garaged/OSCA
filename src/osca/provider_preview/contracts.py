from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from osca.provider_adapters import ProviderAdapterEndpoint
from osca.provider_catalog import ProviderCatalogIdentifier

Identifier = Annotated[str, Field(min_length=1, max_length=256)]
Description = Annotated[str, Field(min_length=1, max_length=4096)]


class ProviderPreviewMode(StrEnum):
    FIXTURE_REPLAY = "fixture_replay"
    LIVE_PREVIEW = "live_preview"
    POLICY_BLOCKED = "policy_blocked"


class ProviderPreviewOutcome(StrEnum):
    SUCCEEDED = "succeeded"
    CACHE_HIT = "cache_hit"
    BLOCKED = "blocked"


class SecPreviewRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.provider-preview.sec-request"] = (
        "osca.provider-preview.sec-request"
    )
    version: Literal["1.0.0"] = "1.0.0"
    request_id: UUID = Field(default_factory=uuid4)
    provider_id: Literal[ProviderCatalogIdentifier.SEC_EDGAR] = (
        ProviderCatalogIdentifier.SEC_EDGAR
    )
    endpoint: Literal[
        ProviderAdapterEndpoint.SEC_COMPANY_FACTS,
        ProviderAdapterEndpoint.SEC_SUBMISSIONS,
    ]
    cik: Annotated[str, Field(pattern=r"^(?:CIK)?\d{1,10}$")]
    network_access_enabled: bool = False
    fixture_path: Path | None = None
    user_agent: Identifier | None = None
    force_refresh: bool = False
    timeout_seconds: float = Field(default=15.0, ge=1.0, le=60.0)
    max_response_bytes: int = Field(default=5_000_000, ge=1024, le=10_000_000)

    @property
    def normalized_cik(self) -> str:
        raw = self.cik.removeprefix("CIK")
        return raw.zfill(10)

    @model_validator(mode="after")
    def validate_execution_mode(self) -> Self:
        if self.network_access_enabled and self.fixture_path is not None:
            raise ValueError("SEC live preview cannot also use a fixture path")
        if not self.network_access_enabled and self.fixture_path is None:
            raise ValueError(
                "SEC preview requires either fixture_path or explicit network access"
            )
        if self.network_access_enabled:
            _validate_declared_sec_user_agent(self.user_agent)
        elif self.user_agent is not None:
            raise ValueError("SEC fixture replay does not accept a live user-agent")
        return self


class FredPreviewRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.provider-preview.fred-request"] = (
        "osca.provider-preview.fred-request"
    )
    version: Literal["1.0.0"] = "1.0.0"
    request_id: UUID = Field(default_factory=uuid4)
    provider_id: Literal[ProviderCatalogIdentifier.FRED] = (
        ProviderCatalogIdentifier.FRED
    )
    endpoint: Literal[ProviderAdapterEndpoint.FRED_SERIES_OBSERVATIONS] = (
        ProviderAdapterEndpoint.FRED_SERIES_OBSERVATIONS
    )
    series_id: Annotated[str, Field(pattern=r"^[A-Za-z0-9._-]{1,128}$")]
    network_access_enabled: bool = False
    secret_reference: Identifier | None = None

    @model_validator(mode="after")
    def validate_secret_reference(self) -> Self:
        if self.secret_reference is None:
            return self
        if not self.secret_reference.startswith("secret:"):
            raise ValueError("FRED credentials must use named secret references")
        lowered = self.secret_reference.lower()
        if "key=" in lowered or "token=" in lowered or "password=" in lowered:
            raise ValueError("FRED secret references must not contain secret values")
        return self


class ProviderPreviewEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.provider-preview.evidence"] = (
        "osca.provider-preview.evidence"
    )
    version: Literal["1.0.0"] = "1.0.0"
    evidence_id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    provider_id: ProviderCatalogIdentifier
    endpoint: ProviderAdapterEndpoint
    mode: ProviderPreviewMode
    outcome: ProviderPreviewOutcome
    resource_id: Identifier
    source_uri: Identifier | None = None
    payload_uri: Identifier | None = None
    metadata_uri: Identifier | None = None
    payload_sha256: Annotated[str, Field(min_length=64, max_length=64)] | None = None
    record_count: int = Field(ge=0)
    cache_hit: bool
    network_access_used: bool
    network_access_enabled: bool
    credential_materialized: Literal[False] = False
    production_ingestion_enabled: Literal[False] = False
    runtime_provider_routing_enabled: Literal[False] = False
    recommendations_enabled: Literal[False] = False
    real_capital_orders_enabled: Literal[False] = False
    evidence_only: Literal[True] = True
    rationale: Description
    finding_ids: tuple[Identifier, ...] = ()
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_evidence(self) -> Self:
        if self.generated_at.tzinfo is None:
            raise ValueError("preview evidence time must be timezone-aware")
        if self.outcome is ProviderPreviewOutcome.BLOCKED:
            if self.payload_uri is not None or self.payload_sha256 is not None:
                raise ValueError("blocked preview evidence cannot expose a payload")
            if self.network_access_used:
                raise ValueError("blocked preview evidence cannot use network access")
        else:
            if self.payload_uri is None or self.payload_sha256 is None:
                raise ValueError("successful preview evidence requires payload provenance")
        if self.cache_hit and self.outcome is not ProviderPreviewOutcome.CACHE_HIT:
            raise ValueError("cache-hit evidence must use the cache_hit outcome")
        if self.network_access_used and not self.network_access_enabled:
            raise ValueError("network access cannot be used without explicit enablement")
        return self


def _validate_declared_sec_user_agent(user_agent: str | None) -> None:
    if user_agent is None:
        raise ValueError("SEC live preview requires a declared user-agent")
    lowered = user_agent.lower()
    if "@" not in user_agent or len(user_agent.split()) < 2:
        raise ValueError(
            "SEC user-agent must identify an organization and contact email"
        )
    if "example.com" in lowered or "sample company" in lowered:
        raise ValueError("SEC user-agent must not use placeholder identity")
