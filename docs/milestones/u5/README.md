# U5 - Governed Local ML Experiment Runner

- **Status:** Planned
- **Depends on:** U2-U4

## Objective

Add reproducible local trainer execution behind the existing M9 lifecycle contracts.

## Scope

- Feature/label materialization through U2/U4 transformations.
- Chronological train/validation/test splits, walk-forward folds, purge/embargo where needed, and training-only fitting of transforms.
- Naive persistence and moving-average baselines.
- Linear/ridge regression and logistic classification as initial transparent models.
- Explicit dependency review before accepting scikit-learn or additional model families.
- Reproducible seeds, parameters, environment, dataset/code revisions, predictions, metrics, artifact digests, timings, and findings.
- Regression and classification targets for future return, volatility, direction, or threshold events.
- Leakage, insufficient-sample, invalid-split, and baseline-underperformance findings.

## Non-scope

Remote trainers, cloud tuning, GPU requirements, automatic promotion/retraining, production serving, recommendations, brokers, or real orders.

## Acceptance

A local operator can run and compare at least one regression and one classification experiment against naive baselines, with no future leakage and complete M9 evidence retention.
