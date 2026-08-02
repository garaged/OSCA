from __future__ import annotations

from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from osca.ml_experiments import ExperimentMetrics, ExperimentTask, PredictionRecord


class DiagnosticStatus(StrEnum):
    EXPLORATORY = "exploratory"
    INVALID = "invalid"
    REVIEW_REQUIRED = "review_required"
    ELIGIBLE_FOR_F2_VALIDATION = "eligible_for_f2_validation"


class CalibrationBin(BaseModel):
    model_config = ConfigDict(frozen=True)

    lower: float
    upper: float
    count: int
    mean_probability: float
    positive_rate: float


class CurvePoint(BaseModel):
    model_config = ConfigDict(frozen=True)

    threshold: float
    x: float
    y: float


class RegimeBreakdown(BaseModel):
    model_config = ConfigDict(frozen=True)

    regime: str
    observations: int
    metrics: ExperimentMetrics


class ExperimentDiagnostic(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.prediction-diagnostic.result"] = "osca.prediction-diagnostic.result"
    version: Literal["1.0.0"] = "1.0.0"
    experiment_id: UUID
    task: ExperimentTask
    status: DiagnosticStatus
    predictions: tuple[PredictionRecord, ...]
    residuals: tuple[float, ...]
    absolute_error_quantiles: dict[str, float]
    confusion_matrix: dict[str, int]
    calibration: tuple[CalibrationBin, ...]
    roc_curve: tuple[CurvePoint, ...]
    precision_recall_curve: tuple[CurvePoint, ...]
    coefficient_evidence: dict[str, float]
    regime_breakdowns: tuple[RegimeBreakdown, ...]
    findings: tuple[str, ...]
    warnings: tuple[str, ...]
    diagnostic_digest: str
    automatic_promotion_enabled: bool = False
    recommendations_enabled: bool = False
    broker_execution_enabled: bool = False
    real_capital_execution_enabled: bool = False


class ExperimentComparison(BaseModel):
    model_config = ConfigDict(frozen=True)

    experiment_ids: tuple[UUID, ...] = Field(min_length=2)
    ranking_metric: str
    ordered_experiment_ids: tuple[UUID, ...]
    baseline_relative_scores: dict[str, float]
    findings: tuple[str, ...]
