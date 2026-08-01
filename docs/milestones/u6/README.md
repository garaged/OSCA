# U6 - Prediction Lab and Visual Diagnostics

- **Status:** Implementation candidate
- **Depends on:** U3-U5
- **Baseline:** U5 merge `b656033b9bca74dbd9eac7d0367371dd2c83861c`

## Objective

Make retained ML experiments inspectable and comparable through deterministic local diagnostics.

## Implemented scope

- Diagnostics consume retained U5 results without rerunning training.
- Prediction-versus-actual records and residual evidence.
- Absolute-error quantiles and early/late test-period breakdowns.
- Classification confusion matrices, calibration bins, ROC curves, and precision-recall curves.
- Baseline-relative same-task experiment comparison.
- Coefficient evidence with explicit associative/non-causal warnings.
- Explicit exploratory, invalid, review-required, and eligible-for-F2-validation statuses.
- CLI JSON diagnostics through `python -m osca.prediction_lab`.
- Loopback workspace diagnostics API at `/api/prediction-lab/diagnose`.
- Exportable immutable contracts and diagnostic digests.

## Status policy

- `invalid`: the source experiment is invalid.
- `review_required`: the source experiment or diagnostic findings require review.
- `exploratory`: valid evidence exists but the retained test sample is too small.
- `eligible_for_f2_validation`: adequate test evidence exists and no review finding blocks the next research-validation stage.

Eligibility is not approval, promotion, advice, or authorization to execute.

## Dependency decision

U6 adds no visualization, dataframe, or ML dependency. Diagnostics use retained U5 contracts and standard-library mathematics. U3 remains the visualization foundation for a later richer browser page.

## Non-scope

- Automatic model or feature selection.
- Causal claims or authoritative forecasts.
- Retraining, remote trainers, or production serving.
- Automatic promotion to research signals or strategies.
- Recommendations, brokers, autonomous execution, or real orders.

## Acceptance

- Regression diagnostics expose residual and period breakdown evidence.
- Classification diagnostics expose confusion, calibration, ROC, and precision-recall evidence.
- Comparison fails closed for mixed tasks and ranks same-task experiments relative to retained baselines.
- Coefficient evidence always includes non-causal warnings.
- Hosted Quality and manual clean-machine review pass before merge.
