# M3 — Multi-Timeframe Market Data and Temporal Correctness

- **Status:** In progress
- **Governing role:** Product authority
- **Architecture, data, quality, and licensing review:** Required for M3 scope
- **Authoritative outcome:** PRD M3 temporal correctness capability
- **Baseline:** Completed M2 governed daily-data vertical slice
- **Branch:** `agent/m3-temporal-correctness`
- **Last reviewed:** 2026-07-24

## Current artifacts

- [Accepted intent](intent.md)
- [Accepted scope](scope.md)
- [Evidence plan](evidence-plan.md)
- [Execution plan](execution-plan.md)
- [Risk register](risk-register.md)
- [M3 temporal correctness specification](../../specifications/m3-temporal-correctness.md)
- [ADR-0029 temporal correctness model](../../decisions/ADR-0029-m3-temporal-correctness-model.md)
- [OpenSpec change](../../../openspec/changes/m3-temporal-correctness/README.md)

## Required chain

Intent -> Requirements -> Architecture -> Specification -> Validation -> Evidence

M3 may extend the M2 Market Data capability with approved intraday intervals and temporal semantics. It must not promote paid, authenticated, or license-sensitive provider production use without exact provider evidence.
