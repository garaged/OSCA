# D5 Production Charting and Quantitative Analysis Workbench

## Why

D4 provides canonical assets, local-data visibility, and persistent working sets, while earlier analytical milestones already provide governed deterministic series and quantitative calculations. Users still lack a first-class desktop surface that composes those capabilities into accessible chart/table inspection, comparison, saved views, and evidence export.

## What changes

- Add typed workbench-series and comparison application methods over governed analytical results.
- Add an OSCA-owned declarative SVG/DOM desktop chart adapter with synchronized accessible tables.
- Add deterministic indicator controls that invoke Python-authoritative calculations.
- Disclose bounded display downsampling and source/filter/display row counts.
- Add full-resolution analytical export with reproduction metadata.
- Add profile-scoped declarative saved workbench views using the established ownership/locking boundary.
- Add performance, accessibility, licensing, offline, and supported-platform acceptance evidence.

## Boundaries

Python remains authoritative for numerical results, indicator semantics, comparisons, downsampling, export data, and saved-view persistence. React renders typed results and captures declarative intent only. Rust remains the existing transport/session broker. D5 adds no third-party chart runtime dependency and no recommendations, strategy execution, model training, brokerage connectivity, or order execution.

## Requirements

This change implements REQ-0325 through REQ-0340 in `docs/governance/requirements-catalog-d5.md`.
