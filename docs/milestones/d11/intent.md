# D11 Intent — Model Registry, Validation, Explainability, and Drift

## Outcome
Users can review immutable model versions, compare them with simple baselines, approve or reject bounded uses, understand explanations and uncertainty, and suspend models when drift or quality gates fail.

## Scope
Model cards, validation suites, calibration, explainability, out-of-distribution checks, drift monitoring, approval states, audit history, rollback, suspension, retirement, and outcome tracking.

## Non-goals
Automatic promotion, opaque eligibility, cloud deployment infrastructure, or models acting directly on simulated or real orders.

## Dependencies
D10 governed datasets, features, experiments, and lineage.

## Risks
Overfitting, misleading explanations, approval scope creep, drift thresholds without context, and inability to reproduce serialized models.

## Exit intent
Human approval is mandatory and scoped; model artifacts and environments are reproducible; failed validation or drift suspends eligible uses; baseline comparisons and uncertainty are visible; rollback and audit paths are tested.
