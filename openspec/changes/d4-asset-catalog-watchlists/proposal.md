# D4 Asset Catalog, Market Browser, and Watchlists

## Why

D3 enables governed data import and acquisition, but users still lack a coherent way to discover canonical assets, inspect local evidence coverage, and organize a persistent working set.

## What changes

- Add a canonical asset identity model separate from provider symbols.
- Add deterministic local search, filtering, pagination, aliases, and ambiguity handling.
- Add local-data availability summaries derived from retained metadata.
- Add profile-scoped persistent watchlists with ordered memberships.
- Add typed Python desktop methods and a responsive Markets UI.
- Add migrations, recovery behavior, performance budgets, and supported-platform acceptance.

## Boundaries

Python remains authoritative. SQLite stores D4 metadata. React uses the existing desktop request bridge. D4 remains offline-first and does not introduce streaming prices, charting, recommendations, brokerage connectivity, or order execution.

## Requirements

This change implements REQ-0309 through REQ-0324 in `docs/governance/requirements-catalog-d4.md`.
