# U6 - Prediction Lab and Visual Diagnostics

- **Status:** Planned
- **Depends on:** U3-U5

## Objective

Make ML experiments inspectable and comparable through the local analyst workspace.

## Scope

- Dataset, feature-set, label, split, and model selectors.
- Baseline-relative experiment comparison.
- Prediction-versus-actual overlays and directional correctness markers.
- Residual/error distributions, calibration plots, confusion matrices, ROC/PR where applicable.
- Coefficient and feature-importance evidence with non-causal warnings.
- Walk-forward fold, period, and regime breakdowns.
- Explicit exploratory, invalid, review-required, and eligible-for-F2-validation statuses.

## Non-scope

Automatic model selection, causal claims, authoritative forecasts, production serving, recommendations, brokers, or real orders.

## Acceptance

An operator can understand why one experiment differs from another, inspect where it failed, and export all displayed metrics and predictions with provenance.
