from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

Identifier = Annotated[str, Field(min_length=1, max_length=160)]
ResourceLocation = Annotated[str, Field(min_length=1, max_length=4096)]
Description = Annotated[str, Field(min_length=1, max_length=2048)]


class ProductionProvider(StrEnum):
    SEC_EDGAR = "sec_edgar"
    KRAKEN = "kraken"
    TWELVE_DATA = "twelve_data"
    ALPHA_VANTAGE = "alpha_vantage"
    NASDAQ_DATA_LINK = "nasdaq_data_link"
    FRED = "fred"


class AdmissionStatus(StrEnum):
    APPROVED = "approved"
    NEEDS_EVIDENCE = "needs_evidence"
    POLICY_BLOCKED = "policy_blocked"


class IngestionStatus(StrEnum):
    SUCCEEDED = "succeeded"
    POLICY_BLOCKED = "policy_blocked"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    FAILED = "failed"


class ProviderAdmissionDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.production-ingestion.admission"] = (
        "osca.production-ingestion.admission"
    )
    version: Literal["1.0.0"] = "1.0.0"
    provider_id: ProductionProvider
    status: AdmissionStatus
    approved_resources: tuple[Identifier, ...] = ()
    internal_use_only: bool = True
    credential_mode: Identifier
    terms_reference_uri: ResourceLocation
    evidence_reviewed_at: datetime
    rationale: Description
    findings: tuple[Identifier, ...] = ()

    @model_validator(mode="after")
    def validate_admission(self) -> Self:
        if self.evidence_reviewed_at.tzinfo is None:
            raise ValueError("provider admission evidence time must be timezone-aware")
        if self.status is AdmissionStatus.APPROVED and not self.approved_resources:
            raise ValueError("approved provider admission requires resources")
        if self.status is not AdmissionStatus.APPROVED and self.approved_resources:
            raise ValueError("non-approved provider admission cannot expose resources")
        return self


class ProductionIngestionRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    request_id: UUID = Field(default_factory=uuid4)
    provider_id: ProductionProvider
    resource_id: Identifier
    endpoint_url: ResourceLocation
    storage_root: ResourceLocation
    network_access_enabled: bool = False
    user_agent: Identifier | None = None
    timeout_seconds: float = Field(default=15.0, gt=0, le=60)
    max_response_bytes: int = Field(default=5_000_000, gt=0, le=25_000_000)
    max_attempts: int = Field(default=3, ge=1, le=5)
    requested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_request(self) -> Self:
        if self.requested_at.tzinfo is None:
            raise ValueError("ingestion request time must be timezone-aware")
        if not self.endpoint_url.startswith("https://"):
            raise ValueError("production ingestion requires HTTPS")
        if self.provider_id is ProductionProvider.SEC_EDGAR and not self.user_agent:
            raise ValueError("SEC ingestion requires a declared user agent")
        return self


class ProductionIngestionEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.production-ingestion.evidence"] = (
        "osca.production-ingestion.evidence"
    )
    version: Literal["1.0.0"] = "1.0.0"
    ingestion_id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    provider_id: ProductionProvider
    resource_id: Identifier
    status: IngestionStatus
    admission_status: AdmissionStatus
    endpoint_url: ResourceLocation
    payload_uri: ResourceLocation | None = None
    metadata_uri: ResourceLocation | None = None
    payload_sha256: Identifier | None = None
    response_bytes: int = Field(default=0, ge=0)
    attempt_count: int = Field(default=0, ge=0)
    network_used: bool = False
    cache_state: Literal["not_applicable", "retained"] = "not_applicable"
    rationale: Description
    findings: tuple[Identifier, ...] = ()
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_evidence(self) -> Self:
        if self.completed_at.tzinfo is None:
            raise ValueError("ingestion evidence time must be timezone-aware")
        if self.status is IngestionStatus.SUCCEEDED:
            if not all((self.payload_uri, self.metadata_uri, self.payload_sha256)):
                raise ValueError("successful ingestion requires retained payload evidence")
            if not self.network_used or self.cache_state != "retained":
                raise ValueError("successful ingestion must record network and retention")
        return self
