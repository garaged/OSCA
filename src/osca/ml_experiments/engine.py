from __future__ import annotations

from datetime import datetime
from statistics import fmean
from uuid import uuid4

from osca.analytical_data import ChartSeriesRequest, build_chart_series
from osca.ml_experiments.contracts import (
    ExperimentStatus,
    ExperimentTask,
    MLExperimentRequest,
    MLExperimentResult,
)
from osca.ml_experiments.services import (
    _Sample,
    _baseline,
    _chronological_split,
    _digest,
    _findings,
    _fit_model,
    _fit_scaler,
    _metrics,
    _predict,
    _records,
    _split_record,
    _transform,
)


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
    findings = _findings(test_metrics, baseline_metrics, request.task)
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
        "purge": request.horizon,
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
    return MLExperimentResult(
        experiment_id=uuid4(),
        status=ExperimentStatus.REVIEW_REQUIRED if findings else ExperimentStatus.COMPLETED,
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
            else f"positive close-to-close return {request.horizon} bars ahead"
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
        findings=findings,
        input_digest=input_digest,
        output_digest=output_digest,
    )


def _materialize_samples(rows: tuple[object, ...], request: MLExperimentRequest) -> tuple[_Sample, ...]:
    closes = [float(getattr(row, "close")) for row in rows]
    timestamps = [getattr(row, "timestamp") for row in rows]
    returns: list[float | None] = [None]
    for index in range(1, len(closes)):
        previous = closes[index - 1]
        returns.append(None if previous == 0 else closes[index] / previous - 1.0)
    samples: list[_Sample] = []
    for index in range(request.feature_window, len(rows) - request.horizon):
        window = returns[index - request.feature_window + 1 : index + 1]
        if any(value is None for value in window):
            continue
        numeric = [float(value) for value in window if value is not None]
        mean = fmean(numeric)
        variance = fmean((value - mean) ** 2 for value in numeric)
        future_return = closes[index + request.horizon] / closes[index] - 1.0
        target = future_return if request.task is ExperimentTask.REGRESSION else float(future_return > 0)
        timestamp = timestamps[index + request.horizon]
        if not isinstance(timestamp, datetime):
            raise ValueError("timestamp column must contain datetimes")
        samples.append(
            _Sample(
                timestamp=timestamp,
                features=(numeric[-1], mean, variance**0.5),
                target=target,
                previous_return=numeric[-1],
            )
        )
    return tuple(samples)
