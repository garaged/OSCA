# D4 Exit Review — Asset Catalog, Market Browser, and Watchlists

- **Status:** Candidate; supported-platform manual acceptance pending
- **Pull request:** #84
- **Baseline:** D3 merge `c170e5b2c93f70092ec955159759424d65c4ad64`

## Delivered outcome

D4 adds an offline-first Markets area with canonical asset identities, deterministic search, explicit venue ambiguity, provider aliases, asset provenance, local-data availability summaries, profile-scoped recent assets, and persistent ordered watchlists.

Python remains authoritative for identity resolution, search, details, persistence, validation, and profile mutation locking. React continues to use the single narrow `desktop_request` bridge. No generic filesystem, database, HTTP, shell, provider, brokerage, or execution authority was added to React or Rust.

## Requirements and architecture disposition

Requirements `REQ-0309` through `REQ-0324` are allocated across the D4 specification, OpenSpec capability, implementation, tests, manual-acceptance procedure, traceability, and this exit review.

Canonical identity remains distinct from provider symbols. Exact collisions fail visibly through an ambiguity result. Watchlists store canonical IDs rather than display symbols, are isolated by profile, and retain deterministic member order. Mutations use the established profile lock and SQLite transactions.

Disposition: implementation pass.

## Automated validation disposition

Quality `31140148497` and Desktop Foundation `31140148520` passed on candidate `2675816dd0d128009c74ccbb009628677c2cb3b4`. OpenSpec, secret scanning, Ruff, strict mypy, full Python tests, architecture checks, frontend build/tests, desktop API tests, Rust formatting/tests/Clippy, and wheel-content verification passed.

Disposition: pass.

## Safety and non-goals

D4 does not add streaming quotes, production charting, recommendations, alerts, portfolio ownership, broker or exchange connectivity, order entry, autonomous execution, live orders, or real-capital behavior. Catalog and watchlist operations are offline and no paid provider is required.

Disposition: pass, subject to supported-platform network observation.

## Remaining exit gate

The repository owner must complete the clean-profile manual-acceptance procedure on macOS ARM64 and Linux x86-64, including accessibility and packaged-app smoke. Any discovered security, identity, persistence, locking, accessibility, or offline-boundary defect must be fixed and revalidated.

## Candidate decision

All implementation and hosted-validation slices are complete. D4 is ready for supported-platform manual acceptance. Final exit and merge readiness remain pending that evidence and explicit repository-owner direction.
