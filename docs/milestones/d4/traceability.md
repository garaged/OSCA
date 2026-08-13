# D4 Traceability

Status: implementation candidate; concurrency regression remediation in validation

| Requirement | Implementation | Verification | Status |
|---|---|---|---|
| REQ-0309–0313 | `desktop_api.asset_catalog` canonical IDs, aliases, deterministic search, ambiguity | `test_d4_asset_catalog.py`; frontend source checks | Implemented |
| REQ-0314–0315 | profile-derived availability and recent assets | Python service, Markets UI, manual acceptance | Implemented |
| REQ-0316–0320 | SQLite watchlists, ordered canonical membership, migration, bounded Python mutation locking plus persistent broker-owned per-window profile sessions and a shared broker/CLI session-lease boundary | Python persistence tests; Rust broker ownership tests; CLI-versus-desktop session-lock regressions; supported-platform concurrency acceptance | Remediation validation |
| REQ-0321–0322 | typed D4 desktop methods and narrow React bridge; Rust broker adds only bounded session-ownership enforcement needed across short-lived sidecar calls; broker-owned sidecars receive profile-specific authorization so normal GUI writes do not deadlock | service/API/frontend tests; Rust broker authorization tests; Rust format/unit/clippy gates | Remediation validation |
| REQ-0323 | responsive accessible Markets UI, recents, rename, ordered membership and conflict states | frontend checks and supported-platform manual acceptance | Manual pending |
| REQ-0324 | evidence-based D4 exit including per-window/profile isolation and supported non-UI lock enforcement | validation evidence and exit review | Pending |

Concurrency regression contract:

- successful `profile.open` establishes ownership for the requesting desktop window/session;
- a second window/process cannot open or mutate the same owned profile;
- `profile.select` alone never grants profile mutation authority;
- remembered global profile preference cannot silently replace another live window's active profile context;
- a supported direct Python/CLI desktop-API mutation cannot bypass a desktop-held session lease;
- a broker-launched sidecar may reuse ownership only for the exact profile owned by its requesting window and still uses the bounded Python mutation lock for serialization;
- ownership is released when the owning window closes or explicitly leaves the opened profile, after which a supported non-UI mutation may acquire it;
- rejected concurrent attempts leave watchlists, ordering, recents, profile metadata, and the owning window's active profile unchanged.

D4 does not add streaming quotes, charts, recommendations, alerts, portfolio ownership, broker connectivity, or execution.
