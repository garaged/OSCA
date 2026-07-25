from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

Identifier = Annotated[str, Field(min_length=1, max_length=128)]
Description = Annotated[str, Field(min_length=1, max_length=2048)]


class AnalysisPackFamily(StrEnum):
    FUNDAMENTAL_VALUATION = "fundamental_valuation"
    MACRO_CROSS_MARKET = "macro_cross_market"
    EVENTS_CATALYSTS = "events_catalysts"
    NEWS_SENTIMENT = "news_sentiment"
    CRYPTO_MARKET_STRUCTURE = "crypto_market_structure"
    PORTFOLIO_SCENARIO = "portfolio_scenario"
    SPECIALIZED_ML = "specialized_ml"
    VISUALIZATION = "visualization"
    CROSS_FAMILY_SYNTHESIS = "cross_family_synthesis"


class EvidenceKind(StrEnum):
    OBSERVATION = "observation"
    SIGNAL = "signal"
    FINDING = "finding"
    THESIS = "thesis"
    RECOMMENDATION = "recommendation"
    ALERT = "alert"
    REPORT = "report"


class IntelligenceFindingSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class IntelligenceStatus(StrEnum):
    APPROVED = "approved"
    DEGRADED = "degraded"
    BLOCKED = "blocked"


class CalibrationStatus(StrEnum):
    CALIBRATED = "calibrated"
    DEGRADED = "degraded"
    FAILED = "failed"


class MethodComparisonOutcome(StrEnum):
    PREFERRED = "preferred"
    COMPARABLE = "comparable"
    INSUFFICIENT = "insufficient"
    BLOCKED = "blocked"


class IntelligenceFinding(BaseModel):
    model_config = ConfigDict(frozen=True)
    code: Identifier
    severity: IntelligenceFindingSeverity
    message: Description


class PackDataRequirement(BaseModel):
    model_config = ConfigDict(frozen=True)
    capability: Identifier
    interval: Identifier
    quality_policy_id: Identifier
    allow_optional_missing: bool = False
    allow_provisional_data: bool = False

    @model_validator(mode="after")
    def validate_requirement(self) -> Self:
        if self.allow_provisional_data:
            raise ValueError("M11 analytical packs cannot accept provisional data by default")
        return self


class MethodologyDisclosure(BaseModel):
    model_config = ConfigDict(frozen=True)
    methodology_id: Identifier
    methodology_version: Identifier
    assumptions: tuple[Identifier, ...] = Field(min_length=1)
    limitations: tuple[Identifier, ...] = Field(min_length=1)
    documentation_uri: Identifier


class AnalysisPackManifest(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.intelligence.analysis-pack-manifest"] = (
        "osca.intelligence.analysis-pack-manifest"
    )
    version: Literal["1.0.0"] = "1.0.0"
    pack_id: Identifier
    pack_version: Identifier
    pack_family: AnalysisPackFamily
    supported_asset_classes: tuple[Identifier, ...] = Field(min_length=1)
    output_kinds: tuple[EvidenceKind, ...] = Field(min_length=1)
    data_requirements: tuple[PackDataRequirement, ...] = Field(min_length=1)
    methodology: MethodologyDisclosure
    supports_cross_family_synthesis: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_manifest(self) -> Self:
        if self.created_at.tzinfo is None:
            raise ValueError("analysis pack created_at must be timezone-aware")
        if len(set(self.supported_asset_classes)) != len(self.supported_asset_classes):
            raise ValueError("analysis pack asset classes must be unique")
        if len(set(self.output_kinds)) != len(self.output_kinds):
            raise ValueError("analysis pack output kinds must be unique")
        return self


class PackValidationDecision(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.intelligence.pack-validation"] = (
        "osca.intelligence.pack-validation"
    )
    version: Literal["1.0.0"] = "1.0.0"
    validation_decision_id: UUID = Field(default_factory=uuid4)
    pack_id: Identifier
    pack_version: Identifier
    approved: bool
    status: IntelligenceStatus
    rationale: Description
    findings: tuple[IntelligenceFinding, ...] = ()
    decided_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_decision(self) -> Self:
        if self.decided_at.tzinfo is None:
            raise ValueError("pack validation decided_at must be timezone-aware")
        has_error = any(
            finding.severity is IntelligenceFindingSeverity.ERROR
            for finding in self.findings
        )
        if self.approved and (self.status is IntelligenceStatus.BLOCKED or has_error):
            raise ValueError("approved pack validation cannot be blocked or contain errors")
        return self


class EvidenceReference(BaseModel):
    model_config = ConfigDict(frozen=True)
    evidence_id: UUID
    evidence_kind: EvidenceKind
    source_pack_id: Identifier
    dataset_revision_ids: tuple[UUID, ...] = ()
    methodology_id: Identifier
    confidence: float = Field(ge=0, le=1)


class AnalyticalResultBundle(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.intelligence.result-bundle"] = "osca.intelligence.result-bundle"
    version: Literal["1.0.0"] = "1.0.0"
    result_bundle_id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    pack_id: Identifier
    pack_version: Identifier
    result_kind: EvidenceKind
    evidence: tuple[EvidenceReference, ...] = Field(min_length=1)
    findings: tuple[IntelligenceFinding, ...] = ()
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_bundle(self) -> Self:
        if self.generated_at.tzinfo is None:
            raise ValueError("analytical result generated_at must be timezone-aware")
        if any(finding.severity is IntelligenceFindingSeverity.ERROR for finding in self.findings):
            raise ValueError("retained analytical result bundles cannot contain error findings")
        return self


class MethodComparisonReport(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.intelligence.method-comparison"] = (
        "osca.intelligence.method-comparison"
    )
    version: Literal["1.0.0"] = "1.0.0"
    comparison_report_id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    compared_result_ids: tuple[UUID, ...] = Field(min_length=2)
    preferred_result_id: UUID | None
    outcome: MethodComparisonOutcome
    rationale: Description
    findings: tuple[IntelligenceFinding, ...] = ()
    compared_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_comparison(self) -> Self:
        if self.compared_at.tzinfo is None:
            raise ValueError("method comparison compared_at must be timezone-aware")
        if len(set(self.compared_result_ids)) != len(self.compared_result_ids):
            raise ValueError("method comparison result ids must be unique")
        if self.outcome is MethodComparisonOutcome.PREFERRED and self.preferred_result_id is None:
            raise ValueError("preferred method comparison requires a preferred result id")
        if self.preferred_result_id is not None and self.preferred_result_id not in self.compared_result_ids:
            raise ValueError("preferred result must be one of the compared results")
        return self


class OutcomeCalibrationReport(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.intelligence.outcome-calibration"] = (
        "osca.intelligence.outcome-calibration"
    )
    version: Literal["1.0.0"] = "1.0.0"
    calibration_report_id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    source_result_id: UUID
    expected_outcome: Identifier
    realized_outcome: Identifier
    calibration_status: CalibrationStatus
    error_metric: float = Field(ge=0)
    findings: tuple[IntelligenceFinding, ...] = ()
    calibrated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_calibration(self) -> Self:
        if self.calibrated_at.tzinfo is None:
            raise ValueError("outcome calibration calibrated_at must be timezone-aware")
        if self.calibration_status is CalibrationStatus.CALIBRATED and any(
            finding.severity is IntelligenceFindingSeverity.ERROR
            for finding in self.findings
        ):
            raise ValueError("calibrated outcome report cannot contain error findings")
        return self


class PortfolioScenarioReport(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.intelligence.portfolio-scenario"] = (
        "osca.intelligence.portfolio-scenario"
    )
    version: Literal["1.0.0"] = "1.0.0"
    scenario_report_id: UUID = Field(default_factory=uuid4)
    paper_account_id: UUID
    scenario_id: Identifier
    base_currency: Identifier
    exposure_metric_ids: tuple[Identifier, ...] = Field(min_length=1)
    stress_assumption_ids: tuple[Identifier, ...] = Field(min_length=1)
    findings: tuple[IntelligenceFinding, ...] = ()
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_scenario(self) -> Self:
        if self.evaluated_at.tzinfo is None:
            raise ValueError("portfolio scenario evaluated_at must be timezone-aware")
        if len(set(self.exposure_metric_ids)) != len(self.exposure_metric_ids):
            raise ValueError("portfolio scenario exposure metrics must be unique")
        return self


class CrossFamilySynthesisReport(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.intelligence.cross-family-synthesis"] = (
        "osca.intelligence.cross-family-synthesis"
    )
    version: Literal["1.0.0"] = "1.0.0"
    synthesis_report_id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    included_result_ids: tuple[UUID, ...] = Field(min_length=2)
    supporting_evidence: tuple[EvidenceReference, ...] = Field(min_length=1)
    contradicting_evidence: tuple[EvidenceReference, ...] = ()
    conclusion: Description
    findings: tuple[IntelligenceFinding, ...] = ()
    synthesized_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_synthesis(self) -> Self:
        if self.synthesized_at.tzinfo is None:
            raise ValueError("cross-family synthesis synthesized_at must be timezone-aware")
        if len(set(self.included_result_ids)) != len(self.included_result_ids):
            raise ValueError("synthesis result ids must be unique")
        return self


class VisualizationPackSpec(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.intelligence.visualization-pack-spec"] = (
        "osca.intelligence.visualization-pack-spec"
    )
    version: Literal["1.0.0"] = "1.0.0"
    visualization_spec_id: UUID = Field(default_factory=uuid4)
    pack_id: Identifier
    supported_result_kinds: tuple[EvidenceKind, ...] = Field(min_length=1)
    accessible_summary_required: bool = True
    export_metadata_required: bool = True

    @model_validator(mode="after")
    def validate_visualization(self) -> Self:
        if not self.accessible_summary_required:
            raise ValueError("visualization packs require accessible summaries")
        if not self.export_metadata_required:
            raise ValueError("visualization packs require export metadata")
        return self
