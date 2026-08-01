from __future__ import annotations

import hashlib
import json
import math
from statistics import fmean

from osca.ml_experiments import ExperimentStatus, ExperimentTask, MLExperimentResult
from osca.prediction_lab.contracts import (
    CalibrationBin,
    CurvePoint,
    DiagnosticStatus,
    ExperimentComparison,
    ExperimentDiagnostic,
    RegimeBreakdown,
)


def diagnose_experiment(result: MLExperimentResult, *, calibration_bins: int = 10) -> ExperimentDiagnostic:
    if calibration_bins < 2 or calibration_bins > 100:
        raise ValueError("calibration_bins must be between 2 and 100")
    predictions = tuple(item for item in result.predictions if item.split == "test")
    if not predictions:
        raise ValueError("experiment has no test predictions")
    residuals = tuple(item.prediction - item.actual for item in predictions)
    errors = tuple(abs(value) for value in residuals)
    confusion = _confusion(predictions) if result.task is ExperimentTask.CLASSIFICATION else {}
    calibration = _calibration(predictions, calibration_bins)
    roc, precision_recall = _curves(predictions)
    coefficients = dict(zip(result.feature_names, result.coefficients, strict=True))
    regimes = _regime_breakdowns(result.task, predictions)
    findings = list(result.findings)
    status = _status(result, findings)
    warnings = (
        "Coefficients and feature importance are associative evidence, not causal effects.",
        "Diagnostics describe retained validation/test evidence and are not authoritative forecasts.",
        "No displayed result is an investment recommendation or execution instruction.",
    )
    payload = {
        "experiment_id": str(result.experiment_id),
        "status": status,
        "residuals": residuals,
        "confusion": confusion,
        "calibration": [item.model_dump(mode="json") for item in calibration],
        "roc": [item.model_dump(mode="json") for item in roc],
        "precision_recall": [item.model_dump(mode="json") for item in precision_recall],
        "coefficients": coefficients,
    }
    return ExperimentDiagnostic(
        experiment_id=result.experiment_id,
        task=result.task,
        status=status,
        predictions=predictions,
        residuals=residuals,
        absolute_error_quantiles={
            "p50": _quantile(errors, 0.50),
            "p90": _quantile(errors, 0.90),
            "p95": _quantile(errors, 0.95),
            "maximum": max(errors),
        },
        confusion_matrix=confusion,
        calibration=calibration,
        roc_curve=roc,
        precision_recall_curve=precision_recall,
        coefficient_evidence=coefficients,
        regime_breakdowns=regimes,
        findings=tuple(findings),
        warnings=warnings,
        diagnostic_digest=_digest(payload),
    )


def compare_experiments(results: tuple[MLExperimentResult, ...]) -> ExperimentComparison:
    if len(results) < 2:
        raise ValueError("at least two experiments are required")
    tasks = {item.task for item in results}
    if len(tasks) != 1:
        raise ValueError("experiments must use the same task")
    task = results[0].task
    if task is ExperimentTask.REGRESSION:
        metric_name = "test_mae_improvement_over_baseline"
        scores = {
            str(item.experiment_id): _regression_score(item)
            for item in results
        }
    else:
        metric_name = "test_accuracy_improvement_over_baseline"
        scores = {
            str(item.experiment_id): _classification_score(item)
            for item in results
        }
    ordered = tuple(
        item.experiment_id
        for item in sorted(results, key=lambda item: scores[str(item.experiment_id)], reverse=True)
    )
    findings = tuple(
        f"{experiment_id} did not outperform its baseline."
        for experiment_id, score in scores.items()
        if score <= 0.0
    )
    return ExperimentComparison(
        experiment_ids=tuple(item.experiment_id for item in results),
        ranking_metric=metric_name,
        ordered_experiment_ids=ordered,
        baseline_relative_scores=scores,
        findings=findings,
    )


def _status(result: MLExperimentResult, findings: list[str]) -> DiagnosticStatus:
    if result.status is ExperimentStatus.INVALID:
        return DiagnosticStatus.INVALID
    if result.status is ExperimentStatus.REVIEW_REQUIRED or findings:
        return DiagnosticStatus.REVIEW_REQUIRED
    if len(tuple(item for item in result.predictions if item.split == "test")) < 30:
        findings.append("Fewer than 30 test observations; keep the experiment exploratory.")
        return DiagnosticStatus.EXPLORATORY
    return DiagnosticStatus.ELIGIBLE_FOR_F2_VALIDATION


def _confusion(predictions: tuple[object, ...]) -> dict[str, int]:
    values = {"true_positive": 0, "true_negative": 0, "false_positive": 0, "false_negative": 0}
    for item in predictions:
        actual = float(item.actual) >= 0.5
        predicted = float(item.prediction) >= 0.5
        key = (
            "true_positive" if actual and predicted else
            "true_negative" if not actual and not predicted else
            "false_positive" if not actual and predicted else
            "false_negative"
        )
        values[key] += 1
    return values


def _calibration(predictions: tuple[object, ...], bins: int) -> tuple[CalibrationBin, ...]:
    probabilistic = tuple(item for item in predictions if item.probability is not None)
    output: list[CalibrationBin] = []
    for index in range(bins):
        lower = index / bins
        upper = (index + 1) / bins
        bucket = tuple(
            item for item in probabilistic
            if lower <= float(item.probability) <= upper if index == bins - 1
            else lower <= float(item.probability) < upper
        )
        if bucket:
            output.append(CalibrationBin(
                lower=lower,
                upper=upper,
                count=len(bucket),
                mean_probability=fmean(float(item.probability) for item in bucket),
                positive_rate=fmean(float(item.actual >= 0.5) for item in bucket),
            ))
    return tuple(output)


def _curves(predictions: tuple[object, ...]) -> tuple[tuple[CurvePoint, ...], tuple[CurvePoint, ...]]:
    probabilistic = tuple(item for item in predictions if item.probability is not None)
    if not probabilistic:
        return (), ()
    thresholds = tuple(sorted({0.0, 1.0, *(float(item.probability) for item in probabilistic)}))
    roc: list[CurvePoint] = []
    pr: list[CurvePoint] = []
    for threshold in thresholds:
        tp = fp = tn = fn = 0
        for item in probabilistic:
            actual = item.actual >= 0.5
            predicted = float(item.probability) >= threshold
            tp += int(actual and predicted)
            fp += int(not actual and predicted)
            tn += int(not actual and not predicted)
            fn += int(actual and not predicted)
        tpr = 0.0 if tp + fn == 0 else tp / (tp + fn)
        fpr = 0.0 if fp + tn == 0 else fp / (fp + tn)
        precision = 1.0 if tp + fp == 0 else tp / (tp + fp)
        recall = tpr
        roc.append(CurvePoint(threshold=threshold, x=fpr, y=tpr))
        pr.append(CurvePoint(threshold=threshold, x=recall, y=precision))
    return tuple(roc), tuple(pr)


def _regime_breakdowns(task: ExperimentTask, predictions: tuple[object, ...]) -> tuple[RegimeBreakdown, ...]:
    midpoint = len(predictions) // 2
    groups = (("early_test", predictions[:midpoint]), ("late_test", predictions[midpoint:]))
    output: list[RegimeBreakdown] = []
    for name, group in groups:
        if not group:
            continue
        if task is ExperimentTask.REGRESSION:
            mae = fmean(abs(item.prediction - item.actual) for item in group)
            rmse = math.sqrt(fmean((item.prediction - item.actual) ** 2 for item in group))
            metrics = {"mean_absolute_error": mae, "root_mean_squared_error": rmse}
        else:
            accuracy = fmean(float((item.prediction >= 0.5) == (item.actual >= 0.5)) for item in group)
            metrics = {"accuracy": accuracy}
        from osca.ml_experiments import ExperimentMetrics
        output.append(RegimeBreakdown(regime=name, observations=len(group), metrics=ExperimentMetrics(**metrics)))
    return tuple(output)


def _regression_score(result: MLExperimentResult) -> float:
    model = result.test_metrics.mean_absolute_error
    baseline = result.baseline_test_metrics.mean_absolute_error
    if model is None or baseline is None:
        return float("-inf")
    return baseline - model


def _classification_score(result: MLExperimentResult) -> float:
    model = result.test_metrics.accuracy
    baseline = result.baseline_test_metrics.accuracy
    if model is None or baseline is None:
        return float("-inf")
    return model - baseline


def _quantile(values: tuple[float, ...], probability: float) -> float:
    ordered = sorted(values)
    index = (len(ordered) - 1) * probability
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return ordered[lower]
    weight = index - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(encoded).hexdigest()
