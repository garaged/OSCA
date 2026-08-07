# D4 Traceability

Status: implementation candidate

| Requirement | Implementation | Verification | Status |
|---|---|---|---|
| REQ-0309–0313 | `desktop_api.asset_catalog` canonical IDs, aliases, deterministic search, ambiguity | `test_d4_asset_catalog.py`; frontend source checks | Implemented |
| REQ-0314–0315 | profile-derived availability and recent assets | Python service and manual acceptance | Implemented |
| REQ-0316–0320 | SQLite watchlists, ordered canonical membership, migration, locking | Python tests and manual recovery/concurrency | Implemented |
| REQ-0321–0322 | typed D4 desktop methods and narrow React bridge | service/API/frontend tests | Implemented |
| REQ-0323 | responsive accessible Markets UI | frontend checks and supported-platform manual acceptance | Manual pending |
| REQ-0324 | evidence-based D4 exit | validation evidence and exit review | Pending |

D4 does not add streaming quotes, charts, recommendations, alerts, portfolio ownership, broker connectivity, or execution.
