# D10 Intent — ML Data Platform, Feature Catalog, and Experiment UX

## Outcome
Users can construct point-in-time datasets, select governed features, run bounded experiments, and inspect reproducible training and validation evidence.

## Scope
Dataset builder, feature catalog and materialization, chronological splits, purge/embargo, survivorship and corporate-action policy, missing-data handling, lineage, experiment configuration, resource bounds, run status, cancellation, and initial registry records.

## Non-goals
Automatic production deployment, recommendation authority, unbounded distributed training, or sequence models without evidence of need.

## Dependencies
D5 data/analysis surfaces and D6 research projects.

## Risks
Look-ahead leakage, stale or revised labels, feature drift, excessive resource use, and experiment results detached from dataset lineage.

## Exit intent
Every experiment references immutable data and feature revisions; leakage checks fail closed; simple baselines are mandatory; time-aware validation is default; cancellation and restart are safe; outputs remain research evidence pending human review.
