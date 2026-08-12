# D4 Traceability

Status: implementation candidate; concurrency regression remediation in validation

| Requirement | Implementation | Verification | Status |
|---|---|---|---|
| REQ-0309–0313 | `desktop_api.asset_catalog` canonical IDs, aliases, deterministic search, ambiguity | `test_d4_asset_catalog.py`; frontend source checks | Implemented |
| REQ-0314–0315 | profile-derived availability and recent assets | Python service, Markets UI, manual acceptance | Implemented |
| REQ-0316–0320 | SQLite watchlists, ordered canonical membership, migration, bounded Python mutation locking plus persistent broker-owned per-window profile sessions | Python persistence tests; Rust broker ownership tests; supported-platform concurrency acceptance | Remediation validation |
| REQ-0321–0322 | typed D4 desktop methods and narrow React bridge; Rust broker adds only bounded session-ownership enforcement needed across short-lived sidecar calls | service/API/frontend tests; Rust format/unit/clippy gates | Remediation validation |
| REQ-0323 | responsive accessible Markets UI, recents, rename, ordered membership and conflict states | frontend checks and supported-platform manual acceptance | Manual pending |
| REQ-0324 | evidence-based D4 exit including per-window/profile isolation | validation evidence and exit review | Pending |

Concurrency regression contract:

- successful `profile.open` establishes ownership for the requesting desktop window/session;
- a second window/process cannot open or mutate the same owned profile;
- `profile.select` alone never grants profile mutation authority;
- remembered global profile preference cannot silently replace another live window's active profile context;
- ownership is released when the owning window closes or explicitly leaves the opened profile;
- rejected concurrent attempts leave watchlists, ordering, recents, profile metadata, and the owning window's active profile unchanged.

D4 does not add streaming quotes, charts, recommendations, alerts, portfolio ownership, broker connectivity, or execution.
