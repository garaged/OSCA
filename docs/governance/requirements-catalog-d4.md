# D4 Requirements Catalog — Asset Catalog, Market Browser, and Watchlists

Status: Draft for implementation
Baseline: D3 merge `c170e5b2c93f70092ec955159759424d65c4ad64`

| ID | Requirement | Verification |
|---|---|---|
| REQ-0309 | The system shall represent each asset with a stable canonical identifier independent from provider-specific symbols. | Domain and persistence tests |
| REQ-0310 | The system shall preserve provider aliases with provenance and shall fail visibly when an alias maps ambiguously. | Alias and ambiguity tests |
| REQ-0311 | The catalog shall combine bundled seeds, governed local imports, admitted acquisitions, and explicit user registration without requiring network access. | Composition and offline tests |
| REQ-0312 | Search shall be deterministic, case-insensitive, filtered, paginated, and ordered by declared exact/prefix/name precedence. | Search contract and property tests |
| REQ-0313 | Asset detail shall expose canonical metadata, provenance, lifecycle state, and retained local-data availability without implying live freshness. | Detail contract and presentation tests |
| REQ-0314 | Users shall create, list, rename, describe, delete, and reorder profile-scoped watchlists. | Watchlist service and persistence tests |
| REQ-0315 | Users shall add, remove, and reorder canonical asset memberships without deleting catalog or market data. | Membership and deletion-isolation tests |
| REQ-0316 | Asset, alias, watchlist, membership, recent-asset, and ordering writes shall be transactional and protected by profile compatibility, bounded mutation locking, and a shared desktop/non-UI session-ownership boundary that prevents supported Python/CLI mutation of a desktop-owned profile. | Transaction, rollback, migration, mutation contention, desktop-vs-CLI session-lock, and release/reacquire tests |
| REQ-0317 | SQLite and Alembic shall remain authoritative for D4 metadata persistence and recovery. | Migration and restart tests |
| REQ-0318 | Python shall expose typed asset and watchlist application methods through the existing desktop request boundary. | Desktop API contract tests |
| REQ-0319 | React and Rust shall gain no generic database, filesystem, network, secret, brokerage, or order authority; the persistent Rust broker may hold only bounded per-window session ownership and pass profile-specific ownership proof to its short-lived Python sidecar. | Architecture, source-boundary, broker-authorization, and non-owner rejection tests |
| REQ-0320 | The Markets UX shall provide accessible search, filters, result browsing, detail, watchlists, ambiguity handling, empty/error states, and responsive layouts. | Frontend and manual accessibility tests |
| REQ-0321 | Local catalog search and watchlist mutation shall meet the declared 50,000-asset performance budgets. | Repeatable performance tests |
| REQ-0322 | Optional provider enrichment shall reuse D3 admission and explicit per-request network consent and shall fail closed. | Policy and network-negative tests |
| REQ-0323 | D4 shall not introduce streaming quotes, charting, recommendations, alerts, portfolio ownership, brokerage connections, or order execution. | Scope and architecture audit |
| REQ-0324 | D4 exit shall retain automated, migration, performance, accessibility, supported-platform manual, traceability, profile-ownership, desktop-vs-CLI lock, and exit-review evidence. | Exit review |
