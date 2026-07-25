# M3 Execution Plan

- **Status:** Active
- **Branch:** `agent/m3-temporal-correctness`
- **Last reviewed:** 2026-07-24

## Sequence

1. Establish governed M3 intent, scope, ADR, OpenSpec delta, and traceability.
2. Add additive temporal API and application primitives.
3. Add interval-aware tests for completion, sessions, crypto boundaries, gaps, and resampling.
4. Extend persistence, freshness, repair, retention, and canonical revision semantics for interval-aware datasets.
5. Reconcile documentation, evidence, architecture status, and OpenSpec.
6. Run local validation where available, open PR, monitor hosted Quality, and clean up review findings.
