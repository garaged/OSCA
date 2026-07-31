# U2 Analytical Data Runtime Specification

## Purpose

Create one governed point-in-time runtime for chart-ready OHLCV and reusable derived analytical series.

## Requirements

- Dataset selection must identify a governed dataset and revision.
- Queries must be bounded by time range and maximum rows.
- Chart rows must preserve timestamp, OHLC, volume, interval, completeness, source, and revision.
- Derived series must preserve definition identity, parameters, warm-up/null semantics, input/output digests, and point-in-time safety.
- Initial derived series are simple return, log return, SMA, EMA, rolling volatility, and rolling volume.
- Large-series downsampling must be deterministic and document which extrema/order properties it preserves.
- Invalid revisions, ranges, budgets, non-monotonic timestamps, and future-data transformations must fail closed.
- APIs must support the loopback workspace, export, later U4 analysis, and U5 ML features without making browser code an analytical authority.

## Dependency gate

U2 implementation must record the chosen numerical/dataframe dependencies, licenses, supported wheels, reproducibility behavior, and packaging impact before merging runtime code.

## Safety

U2 performs no network/provider calls, credential access, recommendations, broker actions, or real-capital behavior.

## Verification

- Independent known-answer fixtures for each transformation.
- Boundary and invalid-input tests.
- Point-in-time/no-future-data tests.
- Downsampling invariants.
- Clean-machine manual import-to-chart-data workflow.
- Ruff, strict mypy, pytest, architecture, OpenSpec, link, and secret-scan gates.
