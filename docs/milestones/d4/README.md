# D4 Asset Catalog, Market Browser, and Watchlists

- **Status:** Implementation and hosted validation complete; supported-platform manual acceptance pending
- **Baseline:** D3 merge `c170e5b2c93f70092ec955159759424d65c4ad64`
- **Branch:** `agent/d4-asset-catalog-watchlists`
- **Pull request:** #84
- **Intent:** `intent.md`
- **Specification:** `specification.md`
- **Requirements:** `../../governance/requirements-catalog-d4.md`
- **Traceability:** `traceability.md`
- **Manual acceptance:** `manual-acceptance.md`
- **Validation evidence:** `validation-evidence.md`
- **Exit review:** `exit-review.md`
- **OpenSpec:** `../../../openspec/changes/d4-asset-catalog-watchlists/`

## Outcome

D4 adds an offline-first Markets area with stable canonical asset identities, deterministic search, explicit ambiguity handling, provider aliases, provenance and local-data availability, profile-scoped recent assets, and persistent ordered watchlists.

## Accepted architecture

- Python remains authoritative for identity resolution, search, details, persistence, validation, and locking.
- React uses only the existing narrow `desktop_request` bridge.
- Canonical asset IDs remain separate from provider symbols and aliases.
- Watchlists persist canonical IDs in profile-scoped SQLite storage.
- Mutations use the established profile lock and transactional writes.
- Asset and watchlist operations remain offline and require no paid provider.
- Streaming quotes, charting, recommendations, portfolios, brokerage, and execution remain unavailable.

## Validation disposition

Quality and Desktop Foundation passed on implementation candidate `2675816dd0d128009c74ccbb009628677c2cb3b4`. The final documentation head must pass refreshed hosted validation before supported-platform manual acceptance begins.

The remaining exit gate is the full clean-profile manual procedure on macOS ARM64 and Linux x86-64, followed by final evidence reconciliation and explicit repository-owner merge direction.
