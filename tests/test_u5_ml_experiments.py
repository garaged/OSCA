from __future__ import annotations

import math
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from osca.ml_experiments import (
    ExperimentModel,
    ExperimentStatus,
    ExperimentTask,
    MLExperimentRequest,
    run_experiment,
)


def _payload(path: Path, rows: int = 180) -> Path:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    close = 100.0
    values = []
    for index in range(rows):
        close *= 1.0 + 0.002 * math.sin(index / 5) + 0.0005
        values.append(
            {
                "timestamp": start + timedelta(days=index),
                "open": close - 0.25,
                "high": close + 0.75,
                "low": close - 0.75,
                "close": close,
                "volume": 1_000.0 + index,
            }
        )
    pq.write_table(pa.Table.from_pylist(values), path)
    return path


def test_regression_experiment_is_chronological_and_reproducible(tmp_path: Path) -> None:
    path = _payload(tmp_path / "regression.parquet")
    request = MLExperimentRequest(
        dataset_revision_id=uuid4(),
        payload_path=path,
        symbol="TEST",
        timeframe="1d",
        task=ExperimentTask.REGRESSION,
        model=ExperimentModel.RIDGE,
        feature_window=5,
        horizon=2,
        embargo=1,
        iterations=200,
    )
    first = run_experiment(request)
    second = run_experiment(request)

    assert first.status in {ExperimentStatus.COMPLETED, ExperimentStatus.REVIEW_REQUIRED}
    assert first.splits[0].end < first.splits[1].start < first.splits[2].start
    assert first.parameters["purge"] == 2
    assert first.parameters["scaler"] == "training_only_standardization"
    assert first.test_metrics.mean_absolute_error is not None
    assert first.baseline_test_metrics.mean_absolute_error is not None
    assert first.coefficients == second.coefficients
    assert first.output_digest == second.output_digest
    assert first.point_in_time_safe is True
    assert first.network_access_enabled is False
    assert first.automatic_promotion_enabled is False
    assert first.real_capital_execution_enabled is False


def test_classification_experiment_retains_probabilities(tmp_path: Path) -> None:
    path = _payload(tmp_path / "classification.parquet")
    result = run_experiment(
        MLExperimentRequest(
            dataset_revision_id=uuid4(),
            payload_path=path,
            symbol="TEST",
            timeframe="1d",
            task=ExperimentTask.CLASSIFICATION,
            model=ExperimentModel.LOGISTIC,
            feature_window=5,
            iterations=250,
        )
    )

    assert result.test_metrics.accuracy is not None
    assert result.test_metrics.log_loss is not None
    assert all(record.probability is not None for record in result.predictions)
    assert all(0.0 <= float(record.probability) <= 1.0 for record in result.predictions)


def test_insufficient_samples_fail_closed(tmp_path: Path) -> None:
    path = _payload(tmp_path / "small.parquet", rows=20)
    with pytest.raises(ValueError, match="insufficient samples"):
        run_experiment(
            MLExperimentRequest(
                dataset_revision_id=uuid4(),
                payload_path=path,
                symbol="TEST",
                timeframe="1d",
                task=ExperimentTask.REGRESSION,
                model=ExperimentModel.LINEAR,
            )
        )


def test_model_task_mismatch_fails_validation(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="classification currently requires"):
        MLExperimentRequest(
            dataset_revision_id=uuid4(),
            payload_path=tmp_path / "unused.parquet",
            symbol="TEST",
            timeframe="1d",
            task=ExperimentTask.CLASSIFICATION,
            model=ExperimentModel.RIDGE,
        )
