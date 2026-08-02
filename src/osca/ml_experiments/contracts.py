from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ExperimentTask(StrEnum):
    REGRESSION = "regression"
    CLASSIFICATION = "classification"


class ExperimentModel(StrEnum):
    PERSISTENCE = "persistence"
    MOVING_AVERAGE = "moving_average"
    LINEAR = "linear_regression"
    RIDGE = "ridge_regression"
    LOGISTIC = "logistic_classification"


class ExperimentStatus(StrEnum):
    COMPLETED = "completed"
    INVALID = "invalid"
    REVIEW_REQUIRED = "review_required"


class MLExperimentRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    dataset_revision_id: UUID
    payload_path: Path
    symbol: str
    timeframe: str
    task: ExperimentTask
    model: ExperimentModel
    horizon: int = Field(default=1, ge=1, le=252)
    feature_window: int = Field(default=5, ge=2, le=252)
    train_fraction: float = Field(default=0.6, gt=0.4, lt=0.9)
    validation_fraction: float = Field(default=0.2, gt=0.05, lt=0.4)
    embargo: int = Field(default=0, ge=0, le=252)
    ridge_alpha: float = Field(default=1.0, ge=0.0)
    learning_rate: float = Field(default=0.05, gt=0.0, le=1.0)
    iterations: int = Field(default=500, ge=10, le=100_000)
    random_seed: int = 17

    @model_validator(mode="after")
    def validate_model_task(self) -> MLExperimentRequest:
        if self.train_fraction + self.validation_fraction >= 0.95:
            raise ValueError("train and validation fractions leave too little test data")
        if self.task is ExperimentTask.CLASSIFICATION and self.model is not ExperimentModel.LOGISTIC:
            raise ValueError("classification currently requires logistic_classification")
        if self.task is ExperimentTask.REGRESSION and self.model is ExperimentModel.LOGISTIC:
            raise ValueError("regression cannot use logistic_classification")
        return self


class ExperimentSplit(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    start: datetime
    end: datetime
    rows: int


class PredictionRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    timestamp: datetime
    split: str
    actual: float
    prediction: float
    probability: float | None = None


class ExperimentMetrics(BaseModel):
    model_config = ConfigDict(frozen=True)

    mean_absolute_error: float | None = None
    root_mean_squared_error: float | None = None
    directional_accuracy: float | None = None
    accuracy: float | None = None
    precision: float | None = None
    recall: float | None = None
    log_loss: float | None = None


class MLExperimentResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.ml-experiment.result"] = "osca.ml-experiment.result"
    version: Literal["1.0.0"] = "1.0.0"
    experiment_id: UUID
    status: ExperimentStatus
    dataset_revision_id: UUID
    payload_sha256: str
    symbol: str
    timeframe: str
    task: ExperimentTask
    model: ExperimentModel
    feature_names: tuple[str, ...]
    label_definition: str
    splits: tuple[ExperimentSplit, ...]
    predictions: tuple[PredictionRecord, ...]
    validation_metrics: ExperimentMetrics
    test_metrics: ExperimentMetrics
    baseline_test_metrics: ExperimentMetrics
    parameters: dict[str, int | float | str]
    coefficients: tuple[float, ...]
    intercept: float
    findings: tuple[str, ...]
    input_digest: str
    output_digest: str
    point_in_time_safe: bool = True
    network_access_enabled: bool = False
    credential_access_enabled: bool = False
    automatic_promotion_enabled: bool = False
    recommendations_enabled: bool = False
    broker_execution_enabled: bool = False
    real_capital_execution_enabled: bool = False
