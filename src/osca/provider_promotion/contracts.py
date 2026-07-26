from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

Identifier = Annotated[str, Field(min_length=1, max_length=128)]
Description = Annotated[str, Field(min_length=1, max_length=2048)]


class PromotionFindingSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ProviderIdentifier(StrEnum):
    TWELVE_DATA = "twelve_data"
    KRAKEN = "kraken"


class ProviderAssetClass(StrEnum):
    STOCK = "stock"
    ETF = "etf"
    SPOT_CRYPTO = "spot_crypto"


class ProviderCostModel(StrEnum):
    NO_COST = "no_cost"
    FREE_TIER = "free_tier"
    PAID = "paid"


class ProviderPermission(StrEnum):
    RETRIEVAL = "retrieval"
    RETENTION = "retention"
    TRANSFORMATION = "transformation"
    EXPORT = "export"
    BACKUP = "backup"
    REDISTRIBUTION = "redistribution"


class PromotionOutcome(StrEnum):
    APPROVE = "approve"
    DEGRADE = "degrade"
    BLOCK = "block"


class PromotionFinding(BaseModel):
    model_config = ConfigDict(frozen=True)

    code: Identifier
    severity: PromotionFindingSeverity
    message: Description


class ProviderCapabilityScope(BaseModel):
    model_config = ConfigDict(frozen=True)

    provider_id: ProviderIdentifier
    asset_classes: tuple[ProviderAssetClass, ...] = Field(min_length=1)
    intervals: tuple[Identifier, ...] = Field(min_length=1)
    capabilities: tuple[Identifier, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_scope(self) -> Self:
        if len(set(self.asset_classes)) != len(self.asset_classes):
            raise ValueError("provider asset classes must be unique")
        if len(set(self.intervals)) != len(self.intervals):
            raise ValueError("provider intervals must be unique")
        if len(set(self.capabilities)) != len(self.capabilities):
            raise ValueError("provider capabilities must be unique")
        return self


class ProviderLicenseEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    provider_id: ProviderIdentifier
    account_plan_id: Identifier
    cost_model: ProviderCostModel
    payment_required: bool
    terms_reference_uri: Identifier
    allowed_permissions: tuple[ProviderPermission, ...]
    redistribution_allowed: bool = False
    accepted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    findings: tuple[PromotionFinding, ...] = ()

    @model_validator(mode="after")
    def validate_license(self) -> Self:
        if self.accepted_at.tzinfo is None:
            raise ValueError("license acceptance time must be timezone-aware")
        if self.expires_at is not None and self.expires_at.tzinfo is None:
            raise ValueError("license expiration time must be timezone-aware")
        if len(set(self.allowed_permissions)) != len(self.allowed_permissions):
            raise ValueError("provider permissions must be unique")
        if self.cost_model is ProviderCostModel.PAID and not self.payment_required:
            raise ValueError("paid provider plans must require payment")
        if self.cost_model is not ProviderCostModel.PAID and self.payment_required:
            raise ValueError("no-cost provider plans must not require payment")
        has_redistribution_permission = (
            ProviderPermission.REDISTRIBUTION in self.allowed_permissions
        )
        if has_redistribution_permission and not self.redistribution_allowed:
            raise ValueError("redistribution permission requires explicit redistribution_allowed")
        return self


class ProviderCredentialEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    provider_id: ProviderIdentifier
    secret_reference: Identifier
    authentication_mode: Identifier
    credential_configured: bool
    credential_verified: bool
    verified_at: datetime
    findings: tuple[PromotionFinding, ...] = ()

    @model_validator(mode="after")
    def validate_credential(self) -> Self:
        if self.verified_at.tzinfo is None:
            raise ValueError("credential verification time must be timezone-aware")
        if not self.secret_reference.startswith("secret:"):
            raise ValueError("provider credentials must use named secret references")
        lowered = self.secret_reference.lower()
        if "key=" in lowered or "token=" in lowered or "password=" in lowered:
            raise ValueError("provider secret references must not contain secret values")
        if self.credential_verified and not self.credential_configured:
            raise ValueError("unconfigured provider credentials cannot be verified")
        return self


class ProviderQuotaEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    provider_id: ProviderIdentifier
    quota_policy_id: Identifier
    request_limit: int = Field(gt=0)
    remaining_requests: int = Field(ge=0)
    required_headroom_ratio: float = Field(ge=0.0, le=1.0)
    reset_at: datetime
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    findings: tuple[PromotionFinding, ...] = ()

    @model_validator(mode="after")
    def validate_quota(self) -> Self:
        if self.observed_at.tzinfo is None or self.reset_at.tzinfo is None:
            raise ValueError("quota evidence times must be timezone-aware")
        if self.remaining_requests > self.request_limit:
            raise ValueError("remaining provider quota cannot exceed request limit")
        return self


class ProviderProductionEvidenceBundle(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.provider-promotion.evidence-bundle"] = (
        "osca.provider-promotion.evidence-bundle"
    )
    version: Literal["1.0.0"] = "1.0.0"
    evidence_bundle_id: UUID = Field(default_factory=uuid4)
    provider_id: ProviderIdentifier
    capability_scope: ProviderCapabilityScope
    license_evidence: ProviderLicenseEvidence
    credential_evidence: ProviderCredentialEvidence
    quota_evidence: ProviderQuotaEvidence
    retention_policy_id: Identifier
    export_policy_id: Identifier
    backup_policy_id: Identifier
    reviewed_by: Identifier
    reviewed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    findings: tuple[PromotionFinding, ...] = ()

    @model_validator(mode="after")
    def validate_bundle(self) -> Self:
        if self.reviewed_at.tzinfo is None:
            raise ValueError("provider evidence review time must be timezone-aware")
        provider_ids = {
            self.capability_scope.provider_id,
            self.license_evidence.provider_id,
            self.credential_evidence.provider_id,
            self.quota_evidence.provider_id,
        }
        if provider_ids != {self.provider_id}:
            raise ValueError("all provider promotion evidence must target the same provider")
        return self


class ProviderPromotionDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.provider-promotion.decision"] = (
        "osca.provider-promotion.decision"
    )
    version: Literal["1.0.0"] = "1.0.0"
    promotion_decision_id: UUID = Field(default_factory=uuid4)
    provider_id: ProviderIdentifier
    evidence_bundle_id: UUID
    target_environment: Literal["production"] = "production"
    outcome: PromotionOutcome
    provider_enabled: bool
    rationale: Description
    findings: tuple[PromotionFinding, ...] = ()
    decided_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_decision(self) -> Self:
        if self.decided_at.tzinfo is None:
            raise ValueError("provider promotion decision time must be timezone-aware")
        if self.outcome is not PromotionOutcome.APPROVE and self.provider_enabled:
            raise ValueError("blocked or degraded provider decisions cannot enable production")
        if self.outcome is PromotionOutcome.APPROVE and not self.provider_enabled:
            raise ValueError("approved provider promotion must explicitly enable production")
        if self.outcome is PromotionOutcome.APPROVE and any(
            finding.severity is PromotionFindingSeverity.ERROR
            for finding in self.findings
        ):
            raise ValueError("approved provider promotion cannot include error findings")
        return self
