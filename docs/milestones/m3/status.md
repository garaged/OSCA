# M3 Status

- **Current implementation slice:** M3.1 temporal correctness foundation
- **Branch:** `agent/m3-temporal-correctness`
- **Last updated:** 2026-07-24

## Complete in this slice

- Governed M3 intent/spec package is drafted and linked.
- ADR-0029 is accepted for additive temporal correctness.
- Temporal API contracts are added beside M2 daily contracts.
- Temporal application services cover completed-bar cutoff, stock expected windows, crypto UTC windows, gap classification, and resampling lineage.
- Unit tests cover the first temporal correctness surface.

## Remaining M3 work

- Interval-aware persistence and manifests.
- Interval-aware freshness and repair jobs.
- Interval-aware retention and canonical revision behavior.
- Final evidence reconciliation, OpenSpec archive, hosted CI cleanup, and merge readiness.