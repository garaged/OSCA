# M3 Status

- **Current implementation slice:** M3.2 interval metadata, freshness, and repair planning
- **Branch:** `agent/m3-temporal-correctness`
- **Last updated:** 2026-07-24

## Complete in this slice

- Governed M3 intent/spec package is drafted and linked.
- ADR-0029 is accepted for additive temporal correctness.
- Temporal API contracts are added beside M2 daily contracts.
- Temporal application services cover completed-bar cutoff, stock expected windows, crypto UTC windows, gap classification, repair-window planning, and resampling lineage.
- Dataset manifests and retrieval requests carry approved interval identity while remaining daily-compatible by default.
- Retrieval resolution filters by interval, so daily and intraday revisions are not silently substituted.
- Storage inspection groups usage by interval.
- SQLite manifest persistence retains interval metadata through the existing JSON payload repository.
- Unit and component tests cover the first two temporal correctness surfaces.

## Remaining M3 work

- Interval-aware retention and canonical revision behavior beyond manifest identity.
- Interval-aware publication/payload support for non-daily OHLCV Parquet objects.
- Final evidence reconciliation, OpenSpec archive, hosted CI cleanup, and merge readiness.
