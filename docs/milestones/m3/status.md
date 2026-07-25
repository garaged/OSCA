# M3 Status

- **Current implementation slice:** M3.4 OHLCV publication and interval canonicalization
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
- Governed OHLCV Parquet schema, serialization, deserialization, and codec support are added for non-daily and resampled bars.
- Non-daily OHLCV publication is integrated through a dedicated interval-aware publication intent and publisher.
- Published OHLCV manifests use interval-scoped object keys and remain protected canonical history.
- Unit and component tests cover temporal correctness, interval metadata, OHLCV payloads, interval-scoped retrieval, retention protection, and OHLCV publication behavior.

## Remaining M3 work

- Final evidence reconciliation, OpenSpec archive, hosted CI cleanup, and merge readiness.
