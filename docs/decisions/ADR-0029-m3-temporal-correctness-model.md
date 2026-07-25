# ADR-0029 — M3 Temporal Correctness Model

- **Status:** Accepted
- **Date:** 2026-07-24
- **Decision owners:** Product, architecture, data, and quality authorities
- **Scope:** M3 intraday intervals, stock sessions, crypto UTC days, completed-bar semantics, gap detection, and resampling lineage
- **Related requirements:** REQ-0041-REQ-0052
- **Related product decisions:** D-004, D-012-D-018, D-040
- **Supersedes:** None
- **Superseded by:** None

## Decision

M3 introduces an additive interval-aware temporal model for the approved intervals `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, and `1d`.

Stock expected bars are derived from explicit exchange-session evidence in UTC. A stock interval without accepted calendar/session evidence is unresolved, not missing, and is not automatically repair eligible.

Crypto expected bars are derived from UTC day boundaries. Completed crypto intervals are expected whenever their UTC close is at or before the completed-bar cutoff.

All interval contracts use start-inclusive/end-exclusive windows. A bar is complete only after its interval end plus any declared publication lag has passed. Gap detection operates on completed expected windows only.

Resampling from lower to higher approved intervals is deterministic and emits lineage from every source bar to the derived bar. Incomplete source coverage produces no derived bar.

## Consequences and fitness

M3 removes M2's conservative weekday approximation without introducing provider-specific time semantics into canonical contracts. It preserves M2 daily compatibility by adding temporal contracts beside the accepted daily-bar family.

Fitness evidence must prove approved interval validation, UTC-only boundaries, stock-session-aware missing/unresolved classification, crypto UTC completion, completed-bar cutoffs, and resampling lineage.
