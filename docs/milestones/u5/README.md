# U5 - Governed Local ML Experiment Runner

- **Status:** Implementation candidate
- **Depends on:** U2-U4
- **Baseline:** U4 merge `2f8e931f70d25aecd024a9e53575a09ddeb96ea5`

## Objective

Add reproducible local trainer execution behind the existing M9 lifecycle contracts without enabling remote training, automatic promotion, advice, or execution.

## Implemented scope

### Governed feature and label materialization

- Reads an explicit governed OHLCV payload through the U2 analytical runtime.
- Uses lagged return, rolling mean return, and rolling volatility features.
- Supports future-return regression and future-direction classification labels.
- Retains explicit feature names, label definition, dataset revision, and payload digest.

### Chronological validation

- Chronological train, validation, and test partitions.
- Horizon-sized purge between partitions.
- Configurable embargo after split boundaries.
- Scaling parameters fit on training data only.
- Minimum-sample and invalid-split checks fail closed.

### Initial transparent models

- Persistence regression baseline.
- Moving-average regression baseline.
- Linear regression.
- Ridge regression.
- Logistic classification.

The implementation uses deterministic standard-library gradient descent and adds no numerical or ML dependency. scikit-learn and additional model families remain subject to a later dependency, packaging, licensing, and reproducibility review.

### Metrics and evidence

Regression evidence includes MAE, RMSE, and directional accuracy. Classification evidence includes accuracy, precision, recall, log loss, class predictions, and probabilities. Every experiment also records:

- validation and test predictions
- naive baseline test metrics
- model coefficients and intercept
- split timestamps and row counts
- model and split parameters
- input/output digests
- baseline-underperformance findings
- point-in-time and safety boundaries

## Operator surfaces

```bash
uv run python -m osca.ml_experiments \
  <payload.parquet> \
  <dataset-revision-uuid> \
  AAPL \
  1d \
  --task regression \
  --model ridge_regression
```

The loopback analyst workspace also exposes the governed experiment request contract through `/api/ml-experiment`; production serving and automatic retention are not enabled.

## Safety boundary

Network access, credential resolution, remote trainers, automatic promotion, recommendations, broker connectivity, autonomous execution, and real-capital orders remain disabled.

## Deferred

- Walk-forward multi-fold orchestration and visual comparison, assigned to U6.
- Volatility and threshold-event targets.
- Tree-based, ensemble, neural, GPU, and externally hosted models.
- Automatic tuning, retraining, promotion, or production model serving.

## Acceptance

A local operator can run deterministic regression and classification experiments against naive baselines. Tests verify chronological ordering, purge/embargo evidence, training-only scaling, reproducibility, probability retention, insufficient-sample failure, task/model validation, and disabled execution boundaries.
