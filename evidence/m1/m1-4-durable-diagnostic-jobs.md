# M1.4 durable diagnostic jobs evidence

- **Status:** Complete
- **Source checkpoint:** `db73be9436c8aeaeb4e4595b5892df743baf3693`
- **Branch:** `agent/m1-secure-walking-skeleton`
- **Requirements:** REQ-0011–REQ-0015
- **Decision:** ADR-0013
- **Contract:** `osca.workflow.diagnostic-run` 1.0.0
- **Schema revision:** `m1_0003`
- **OpenSpec change:** `m1-4-durable-diagnostic-jobs`
- **Validated:** 2026-07-18

## Delivered behavior

- Stable, typed, versioned diagnostic runs persisted before execution.
- Actor-scoped idempotent submission with conflicting-input rejection.
- Explicit governed lifecycle graph and terminal-state protection.
- Atomic revision-guarded claim and transitions with lease and heartbeat metadata.
- Observable interruption followed by explicit policy-controlled resume.
- Versioned, duplicate-aware named-phase checkpoints.
- Cooperative cancellation, bounded deterministic retry, and safe shutdown.
- Typed durable result reference required before success.
- Shared versioned HTTP and CLI application handlers.
- Correlated safe telemetry, Operations-owned cancellation audit, and failure findings.
- Workflow-owned schema and repositories with no private cross-capability imports.

## Gate results

| Gate | Result |
|---|---|
| Full pytest suite | Pass — 35 tests |
| Lifecycle property and prohibited-transition tests | Pass |
| Idempotency and conflict fixtures | Pass |
| Lease, heartbeat, expiry, recovery, and CAS tests | Pass |
| Checkpoint, retry, cancellation, shutdown, and result invariant tests | Pass |
| HTTP/CLI semantic equivalence | Pass |
| Telemetry redaction and audit tests | Pass |
| Architecture boundary tests | Pass |
| Ruff | Pass |
| Strict mypy | Pass — 51 source files |
| Alembic upgrade/downgrade/upgrade through `m1_0003` | Pass |
| CLI smoke test | Pass — all four diagnostic commands registered |
| Strict OpenSpec validation | Pass — 1 change, 0 failures |

## Defect discovered and corrected

Implementation review found that the accepted M1 specification required “only specified lifecycle transitions” while ADR-0013 listed states without enumerating the transition edges. Architecture authority approved the explicit graph. The authoritative M1 specification, OpenSpec delta, property tests, repository claim behavior, and recovery policy were reconciled.

## Limitations and risks

- Execution remains single-node and at-least-once as required by ADR-0013.
- Checkpoint side effects must remain idempotent or duplicate-aware.
- SQLite contention behavior is bounded by short transactions, revision predicates, WAL, and busy timeout; sustained parallelism is a revisit trigger.
- The executor loop is an embeddable component; long-running process supervision is deferred beyond this slice.
- CI run identity will be added by the pull-request checks; this record retains local gate results and source checkpoint.

## Conclusion

M1.4 implementation and retained validation are complete. No blocker remains within the durable diagnostic-job slice. The OpenSpec pilot should be reviewed for Adopt, Revise, or Remove disposition after archival.
