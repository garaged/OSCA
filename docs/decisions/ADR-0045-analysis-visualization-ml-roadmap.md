# ADR-0045 - Analysis, Visualization, and ML Experiment Roadmap

- **Status:** Proposed
- **Date:** 2026-07-31
- **Deciders:** Product and architecture authorities
- **Related milestones:** U2-U7

## Context

OSCA has governed data, temporal, analysis, visualization, backtesting, paper-evidence, and ML lifecycle contracts, but the current operator experience remains evidence- and command-oriented. The product lacks an integrated runtime for chart-ready analytical series, common quantitative indicators, interactive exploration, and reproducible local training execution.

Implementing visualization first without a shared analytical data runtime would duplicate transformation logic across the workspace, reports, backtests, and ML. Implementing ML training first would create features and predictions that users cannot adequately inspect and would increase leakage and reproducibility risk.

## Decision

OSCA will execute the next product phase in this order:

1. U2 shared point-in-time analytical data and chart-series runtime.
2. U3 interactive visualization in the existing loopback-only analyst workspace.
3. U4 built-in common quantitative analysis.
4. U5 governed local ML experiment execution behind M9 contracts.
5. U6 prediction-lab visualization and diagnostics.
6. U7 explicit model-to-event/backtest/paper validation integration.

The shared analytical runtime is authoritative for derived-series definitions used by charts, reports, backtests, and ML features. Derived data must retain input revision, parameters, warm-up/null semantics, point-in-time safety, and output digest.

ML execution must remain local, reproducible, chronologically split, baseline-compared, leakage-checked, and incapable of automatic promotion or live serving.

## Consequences

- Users receive visible OHLCV value early through U2/U3 rather than waiting for the full ML phase.
- Indicator formulas and ML features share one governed transformation path.
- M4 and M9 contracts are reused instead of replaced.
- Numerical, charting, and ML dependencies require explicit licensing, reproducibility, and packaging review in the owning milestone.
- ADR-0044 remains authoritative; this roadmap cannot introduce broker connectivity, recommendations, autonomous capital control, or real orders.

## Rejected alternatives

- **Start with ML training:** rejected because visualization, feature inspection, baseline analysis, and leakage diagnostics are insufficient.
- **Embed formulas directly in the browser:** rejected because it would create a second analytical authority and weaken reproducibility.
- **Build a new public web service:** rejected because the current trusted single-user loopback workspace is sufficient and safer.
- **One large milestone:** rejected because dependency choices, formula validation, UI behavior, and ML safety require independently reviewable increments.
