# M3 Scope — Temporal Correctness

## Requirements allocation

M3 allocates REQ-0041-REQ-0052 for interval-aware market-data and temporal correctness behavior. M2 requirements remain active where identity, source evidence, canonical revision, authorization, retention, and cleanup behavior still apply.

## Acceptance criteria

| ID | Criterion |
|---|---|
| M3-AC-001 | Approved interval values are explicit and unknown intervals fail closed. |
| M3-AC-002 | Every interval bar uses UTC start-inclusive/end-exclusive windows. |
| M3-AC-003 | Completed-bar evaluation honors interval end and declared publication lag. |
| M3-AC-004 | Stock gaps are derived only from accepted exchange-session evidence. |
| M3-AC-005 | Unknown stock session state is unresolved and not repair eligible. |
| M3-AC-006 | Crypto gaps use UTC day and interval boundaries. |
| M3-AC-007 | Gap detection distinguishes observed, missing, unresolved, non-expected, and incomplete states. |
| M3-AC-008 | Resampling requires contiguous complete lower-interval bars. |
| M3-AC-009 | Resampled bars preserve deterministic OHLCV aggregation semantics. |
| M3-AC-010 | Resampling records lineage for every source bar. |
| M3-AC-011 | M2 daily contracts remain compatible. |
| M3-AC-012 | Documentation, ADRs, OpenSpec, traceability, and evidence are updated before exit. |
