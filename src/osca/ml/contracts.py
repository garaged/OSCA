from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

Identifier = Annotated[str, Field(min_length=1, max_length=128)]
Description = Annotated[str, Field(min_length=1, max_length=2048)]


class FeatureValueType(StrEnum):
    FLOAT = "float"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    CATEGORY = "category"


class LabelObjective(StrEnum):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    RANKING = "ranking"


class DatasetSplit(StrEnum):
    TRAIN = "train"
    VALIDATION = "validation"
    TEST = "test"
    HOLDOUT = "holdout"


class ModelArtifactStatus(StrEnum):
    CANDIDATE = "candidate"
    CHAMPION = "champion"
    CHALLENGER = "challenger"
    RETIRED = "retired"
    REJECTED = "rejected"


class MLFindingSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class MLFinding(BaseModel):
    model_config = ConfigDict(frozen=True)
    code: Identifier
    severity: MLFindingSeverity
    message: Description


class MLFeatureDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.ml.feature-definition"] = "osca.ml.feature-definition"
    version: Literal["1.0.0"] = "1.0.0"
    feature_id: Identifier
    name: Identifier
    value_type: FeatureValueType
    source_dataset_id: UUID
    point_in_time_safe: bool
    transformation: Description
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_feature(self) -> Self:
        if self.created_at.tzinfo is None:
            raise ValueError("feature definition created_at must be timezone-aware")
        if not self.point_in_time_safe:
            raise ValueError("ML features must declare point-in-time-safe construction")
        return self


class MLLabelDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.ml.label-definition"] = "osca.ml.label-definition"
    version: Literal["1.0.0"] = "1.0.0"
    label_id: Identifier
    objective: LabelObjective
    horizon: Identifier
    source_dataset_id: UUID
    leakage_checked: bool
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_label(self) -> Self:
        if self.created_at.tzinfo is None:
            raise ValueError("label definition created_at must be timezone-aware")
        if not self.leakage_checked:
            raise ValueError("ML labels must pass leakage checks before training")
        return self


class MLTrainingWorkflow(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.ml.training-workflow"] = "osca.ml.training-workflow"
    version: Literal["1.0.0"] = "1.0.0"
    workflow_id: Identifier
    trainer_id: Identifier
    feature_ids: tuple[Identifier, ...] = Field(min_length=1)
    label_id: Identifier
    split_policy_id: Identifier
    parameter_set_id: Identifier
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_workflow(self) -> Self:
        if self.created_at.tzinfo is None:
            raise ValueError("training workflow created_at must be timezone-aware")
        if len(set(self.feature_ids)) != len(self.feature_ids):
            raise ValueError("training workflow feature ids must be unique")
        return self


class MLExperimentRun(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.ml.experiment-run"] = "osca.ml.experiment-run"
    version: Literal["1.0.0"] = "1.0.0"
    experiment_run_id: UUID = Field(default_factory=uuid4)
    workflow_id: Identifier
    dataset_revision_id: UUID
    code_revision: Identifier
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_started_at(self) -> Self:
        if self.started_at.tzinfo is None:
            raise ValueError("experiment run started_at must be timezone-aware")
        return self


class MLMetric(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: Identifier
    value: float
    split: DatasetSplit
    methodology: Identifier


class MLModelArtifact(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.ml.model-artifact"] = "osca.ml.model-artifact"
    version: Literal["1.0.0"] = "1.0.0"
    model_artifact_id: UUID = Field(default_factory=uuid4)
    experiment_run_id: UUID
    model_family: Identifier
    artifact_uri: Identifier
    artifact_digest: Identifier
    status: ModelArtifactStatus = ModelArtifactStatus.CANDIDATE
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_artifact(self) -> Self:
        if self.created_at.tzinfo is None:
            raise ValueError("model artifact created_at must be timezone-aware")
        if ":" not in self.artifact_digest:
            raise ValueError("model artifact digest must include algorithm prefix")
        return self


class MLEvaluationReport(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.ml.evaluation-report"] = "osca.ml.evaluation-report"
    version: Literal["1.0.0"] = "1.0.0"
    evaluation_report_id: UUID = Field(default_factory=uuid4)
    model_artifact_id: UUID
    experiment_run_id: UUID
    metrics: tuple[MLMetric, ...] = Field(min_length=1)
    calibration_methodology: Identifier
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_report(self) -> Self:
        if self.evaluated_at.tzinfo is None:
            raise ValueError("evaluation report evaluated_at must be timezone-aware")
        splits = {metric.split for metric in self.metrics}
        if DatasetSplit.HOLDOUT not in splits:
            raise ValueError("ML evaluation requires holdout metrics")
        return self


class MLPromotionDecision(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.ml.promotion-decision"] = "osca.ml.promotion-decision"
    version: Literal["1.0.0"] = "1.0.0"
    promotion_decision_id: UUID = Field(default_factory=uuid4)
    model_artifact_id: UUID
    evaluation_report_id: UUID
    approved_for_event_validation: bool
    approved_for_paper_challenger: bool = False
    rationale: Description
    findings: tuple[MLFinding, ...] = ()
    decided_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_decision(self) -> Self:
        if self.decided_at.tzinfo is None:
            raise ValueError("ML promotion decided_at must be timezone-aware")
        if self.approved_for_paper_challenger and not self.approved_for_event_validation:
            raise ValueError("paper challenger approval requires event-validation approval")
        if self.approved_for_event_validation and any(
            finding.severity is MLFindingSeverity.ERROR for finding in self.findings
        ):
            raise ValueError("ML promotion cannot approve artifacts with error findings")
        return self
