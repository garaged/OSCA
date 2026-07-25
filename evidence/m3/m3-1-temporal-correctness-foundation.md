# M3.1 temporal correctness foundation evidence

- **Status:** Initial implementation evidence retained
- **Branch:** `agent/m3-temporal-correctness`
- **Baseline:** `e7cd118fa275bc4c95a39047eeb791baed232c72`
- **Scope:** Additive M3 temporal contracts, stock/crypto interval windows, completed-bar cutoff semantics, calendar-aware gap classification, and deterministic resampling lineage.
- **Validation state:** Hosted Quality pending after PR creation; local validation unavailable in this connector-only checkout environment.

## Evidence retained

- M3 branch was created from verified post-M2 `main`.
- M2 closeout commits `dd3cd1c`, `f54313e`, and `e7cd118` are present on `main`.
- M3 requirements REQ-0041-REQ-0052 are allocated.
- ADR-0029 records the additive temporal correctness model.
- Unit tests cover approved intervals, completed-bar cutoffs, stock session gaps, unresolved stock calendars, crypto UTC boundaries, resampling lineage, and invalid intraday bars.

## Deferred within M3

- interval-aware persistence, freshness, repair, retention, and canonical revision integration;
- final OpenSpec archive and exit review;
- hosted Quality result capture and cleanup findings.