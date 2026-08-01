from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from statistics import fmean
from uuid import UUID, uuid4

from osca.analytical_data import ChartSeriesRequest, build_chart_series
from osca.ml_experiments.contracts import (
    ExperimentMetrics,
    ExperimentModel,
    ExperimentSplit,
    ExperimentStatus,
    ExperimentTask,
    MLExperimentRequest,
    MLExperimentResult,
    PredictionRecord,
)


@dataclass(frozen=True)
class _Sample:
    timestamp: object
    features: tuple[float, ...]
    target: float
    previous_return: float


def run_experiment(request: MLExperimentRequest) -> MLExperimentResult:
    chart = build_chart_series(
        ChartSeriesRequest(
            dataset_revision_id=request.dataset_revision_id,
            payload_path=request.payload_path,
            symbol=request.symbol,
            timeframe=request.timeframe,
            max_rows=50_000,
        )
    )
    samples = _materialize_samples(chart.rows, request)
    minimum = max(30, request.feature_window * 3 + request.horizon)
    if len(samples) < minimum:
        raise ValueError(f"insufficient samples: {len(samples)} available; {minimum} required")
    train, validation, test = _chronological_split(samples, request)
    means, scales = _fit_scaler(train)
    train_x = _transform(train, means, scales)
    validation_x = _transform(validation, means, scales)
    test_x = _transform(test, means, scales)
    coefficients, intercept = _fit_model(train_x, request)
    validation_predictions = _predict(validation_x, coefficients, intercept, request)
    test_predictions = _predict(test_x, coefficients, intercept, request)
    baseline_predictions = _baseline(test, request)
    validation_metrics = _metrics(validation, validation_predictions, request.task)
    test_metrics = _metrics(test, test_predictions, request.task)
    baseline_metrics = _metrics(test, baseline_predictions, request.task)
    findings = list(_findings(test_metrics, baseline_metrics, request.task))
    records = _records(validation, validation_predictions, "validation", request.task)
    records += _records(test, test_predictions, "test", request.task)
    parameters: dict[str, int | float | str] = {
        "horizon": request.horizon,
        "feature_window": request.feature_window,
        "train_fraction": request.train_fraction,
        "validation_fraction": request.validation_fraction,
        "embargo": request.embargo,
        "ridge_alpha": request.ridge_alpha,
        "learning_rate": request.learning_rate,
        "iterations": request.iterations,
        "random_seed": request.random_seed,
        "scaler": "training_only_standardization",
        "split": "chronological_train_validation_test",
    }
    input_digest = _digest(
        {
            "request": request.model_dump(mode="json"),
            "payload_sha256": chart.payload_sha256,
            "sample_count": len(samples),
        }
    )
    output_digest = _digest(
        {
            "coefficients": coefficients,
            "intercept": intercept,
            "validation_metrics": validation_metrics.model_dump(mode="json"),
            "test_metrics": test_metrics.model_dump(mode="json"),
            "baseline_metrics": baseline_metrics.model_dump(mode="json"),
        }
    )
    status = ExperimentStatus.REVIEW_REQUIRED if findings else ExperimentStatus.COMPLETED
    return MLExperimentResult(
        experiment_id=uuid4(),
        status=status,
        dataset_revision_id=request.dataset_revision_id,
        payload_sha256=chart.payload_sha256,
        symbol=request.symbol,
        timeframe=request.timeframe,
        task=request.task,
        model=request.model,
        feature_names=("last_return", "rolling_mean_return", "rolling_volatility"),
        label_definition=(
            f"close-to-close return {request.horizon} bars ahead"
            if request.task is ExperimentTask.REGRESSION
            else f"1 when close-to-close return {request.horizon} bars ahead is positive, else 0"
        ),
        splits=(
            _split_record("train", train),
            _split_record("validation", validation),
            _split_record("test", test),
        ),
        predictions=tuple(records),
        validation_metrics=validation_metrics,
        test_metrics=test_metrics,
        baseline_test_metrics=baseline_metrics,
        parameters=parameters,
        coefficients=tuple(coefficients),
        intercept=intercept,
        findings=tuple(findings),
        input_digest=input_digest,
        output_digest=output_digest,
    )


def _materialize_samples(rows: tuple[object, ...], request: MLExperimentRequest) -> tuple[_Sample, ...]:
    closes = [float(getattr(row, "close")) for row in rows]
    timestamps = [getattr(row, "timestamp") for row in rows]
    returns: list[float | None] = [None]
    for previous, current in zip(closes, closes[1:], strict=True):
        returns.append(None if previous == 0 else current / previous - 1.0)
    samples: list[_Sample] = []
    last_index = len(rows) - request.horizon
    for index in range(request.feature_window, last_index):
        window = returns[index - request.feature_window + 1 : index + 1]
        if any(value is None for value in window):
            continue
        numeric = [float(value) for value in window if value is not None]
        mean = fmean(numeric)
        variance = fmean((value - mean) ** 2 for value in numeric)
        future_return = closes[index + request.horizon] / closes[index] - 1.0
        target = future_return if request.task is ExperimentTask.REGRESSION else float(future_return > 0)
        samples.append(
            _Sample(
                timestamp=timestamps[index + request.horizon],
                features=(numeric[-1], mean, math.sqrt(variance)),
                target=target,
                previous_return=numeric[-1],
            )
        )
    return tuple(samples)


def _chronological_split(
    samples: tuple[_Sample, ...], request: MLExperimentRequest
) -> tuple[tuple[_Sample, ...], tuple[_Sample, ...], tuple[_Sample, ...]]:
    train_end = int(len(samples) * request.train_fraction)
    validation_end = train_end + int(len(samples) * request.validation_fraction)
    purge = request.horizon
    train = samples[: max(0, train_end - purge)]
    validation_start = min(len(samples), train_end + request.embargo)
    validation = samples[validation_start : max(validation_start, validation_end - purge)]
    test_start = min(len(samples), validation_end + request.embargo)
    test = samples[test_start:]
    if min(len(train), len(validation), len(test)) < 5:
        raise ValueError("invalid chronological split after purge and embargo")
    return train, validation, test


def _fit_scaler(samples: tuple[_Sample, ...]) -> tuple[tuple[float, ...], tuple[float, ...]]:
    columns = tuple(zip(*(sample.features for sample in samples), strict=True))
    means = tuple(fmean(column) for column in columns)
    scales = tuple(
        math.sqrt(fmean((value - means[index]) ** 2 for value in column)) or 1.0
        for index, column in enumerate(columns)
    )
    return means, scales


def _transform(
    samples: tuple[_Sample, ...], means: tuple[float, ...], scales: tuple[float, ...]
) -> tuple[tuple[tuple[float, ...], float], ...]:
    return tuple(
        (
            tuple((value - means[index]) / scales[index] for index, value in enumerate(sample.features)),
            sample.target,
        )
        for sample in samples
    )


def _fit_model(
    samples: tuple[tuple[tuple[float, ...], float], ...], request: MLExperimentRequest
) -> tuple[list[float], float]:
    if request.model in {ExperimentModel.PERSISTENCE, ExperimentModel.MOVING_AVERAGE}:
        return [0.0, 0.0, 0.0], 0.0
    coefficients = [0.0] * len(samples[0][0])
    intercept = 0.0
    alpha = request.ridge_alpha if request.model is ExperimentModel.RIDGE else 0.0
    for _ in range(request.iterations):
        gradients = [0.0] * len(coefficients)
        intercept_gradient = 0.0
        for features, target in samples:
            raw = intercept + sum(weight * value for weight, value in zip(coefficients, features, strict=True))
            prediction = _sigmoid(raw) if request.task is ExperimentTask.CLASSIFICATION else raw
            error = prediction - target
            intercept_gradient += error
            for index, value in enumerate(features):
                gradients[index] += error * value
        count = len(samples)
        intercept -= request.learning_rate * intercept_gradient / count
        for index in range(len(coefficients)):
            penalty = alpha * coefficients[index]
            coefficients[index] -= request.learning_rate * (gradients[index] / count + penalty)
    return coefficients, intercept


def _predict(
    samples: tuple[tuple[tuple[float, ...], float], ...],
    coefficients: list[float],
    intercept: float,
    request: MLExperimentRequest,
) -> tuple[float, ...]:
    if request.model is ExperimentModel.PERSISTENCE:
        return tuple(features[0] for features, _ in samples)
    if request.model is ExperimentModel.MOVING_AVERAGE:
        return tuple(features[1] for features, _ in samples)
    values = tuple(
        intercept + sum(weight * value for weight, value in zip(coefficients, features, strict=True))
        for features, _ in samples
    )
    return tuple(_sigmoid(value) for value in values) if request.task is ExperimentTask.CLASSIFICATION else values


def _baseline(samples: tuple[_Sample, ...], request: MLExperimentRequest) -> tuple[float, ...]:
    if request.task is ExperimentTask.CLASSIFICATION:
        return tuple(1.0 if sample.previous_return > 0 else 0.0 for sample in samples)
    return tuple(sample.previous_return for sample in samples)


def _metrics(
    samples: tuple[_Sample, ...], predictions: tuple[float, ...], task: ExperimentTask
) -> ExperimentMetrics:
    actual = tuple(sample.target for sample in samples)
    if task is ExperimentTask.REGRESSION:
        errors = tuple(prediction - target for prediction, target in zip(predictions, actual, strict=True))
        return ExperimentMetrics(
            mean_absolute_error=fmean(abs(error) for error in errors),
            root_mean_squared_error=math.sqrt(fmean(error**2 for error in errors)),
            directional_accuracy=fmean(
                float((prediction > 0) == (target > 0))
                for prediction, target in zip(predictions, actual, strict=True)
            ),
        )
    labels = tuple(float(prediction >= 0.5) for prediction in predictions)
    true_positive = sum(label == 1.0 and target == 1.0 for label, target in zip(labels, actual, strict=True))
    predicted_positive = sum(label == 1.0 for label in labels)
    actual_positive = sum(target == 1.0 for target in actual)
    clipped = tuple(min(max(value, 1e-12), 1.0 - 1e-12) for value in predictions)
    return ExperimentMetrics(
        accuracy=fmean(float(label == target) for label, target in zip(labels, actual, strict=True)),
        precision=None if predicted_positive == 0 else true_positive / predicted_positive,
        recall=None if actual_positive == 0 else true_positive / actual_positive,
        log_loss=-fmean(
            target * math.log(probability) + (1.0 - target) * math.log(1.0 - probability)
            for target, probability in zip(actual, clipped, strict=True)
        ),
    )


def _records(
    samples: tuple[_Sample, ...], predictions: tuple[float, ...], split: str, task: ExperimentTask
) -> list[PredictionRecord]:
    return [
        PredictionRecord(
            timestamp=sample.timestamp,
            split=split,
            actual=sample.target,
            prediction=float(prediction >= 0.5) if task is ExperimentTask.CLASSIFICATION else prediction,
            probability=prediction if task is ExperimentTask.CLASSIFICATION else None,
        )
        for sample, prediction in zip(samples, predictions, strict=True)
    ]


def _findings(
    metrics: ExperimentMetrics, baseline: ExperimentMetrics, task: ExperimentTask
) -> tuple[str, ...]:
    findings: list[str] = []
    if task is ExperimentTask.REGRESSION:
        if metrics.mean_absolute_error is not None and baseline.mean_absolute_error is not None:
            if metrics.mean_absolute_error >= baseline.mean_absolute_error:
                findings.append("Model did not outperform the persistence baseline on test MAE.")
    elif metrics.accuracy is not None and baseline.accuracy is not None:
        if metrics.accuracy <= baseline.accuracy:
            findings.append("Model did not outperform the directional baseline on test accuracy.")
    return tuple(findings)


def _split_record(name: str, samples: tuple[_Sample, ...]) -> ExperimentSplit:
    return ExperimentSplit(name=name, start=samples[0].timestamp, end=samples[-1].timestamp, rows=len(samples))


def _sigmoid(value: float) -> float:
    if value >= 0:
        return 1.0 / (1.0 + math.exp(-value))
    exponential = math.exp(value)
    return exponential / (1.0 + exponential)


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(encoded).hexdigest()
