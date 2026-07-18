## Why

M1 requires durable work that remains identifiable, observable, and recoverable across process interruption before OSCA adds market-data workflows. This change pilots OpenSpec while implementing the diagnostic-job slice governed by the M1 intent, REQ-0011, REQ-0012, REQ-0013, REQ-0014, REQ-0015, and REQ-0020.

## What Changes

- Add the Workflow-owned diagnostic-run lifecycle and public application contracts.
- Add idempotent submission, persisted transitions, leases, heartbeats, checkpoints, retry classification, cancellation, and restart recovery.
- Add Workflow-owned SQLite tables through a retained Alembic migration.
- Expose submission and status through the versioned API and CLI using shared application handlers.
- Emit correlated telemetry, Operations-owned audit records, and readiness findings for blocked or failed runs.
- Add component, property, migration, contract, restart, and adapter-equivalence evidence.
- Record OpenSpec validation and OSCA evidence without treating OpenSpec as normative authority.

## Capabilities

### New Capabilities

- `durable-diagnostic-jobs`: Bounded M1.4 behavior for durable diagnostic-run submission, execution, observation, interruption, and recovery.

### Modified Capabilities

None. The authoritative M1 specification remains unchanged; this delta narrows the implementation slice.

## Impact

- **Owning capability:** Workflow owns run state, leases, checkpoints, and result references.
- **Affected contracts:** `osca.workflow.diagnostic-run` 1.0.0 and `osca.error.envelope` 1.0.0.
- **Supporting capabilities:** Catalog owns result metadata; Operations owns health, telemetry, and audit evidence.
- **Governing architecture:** ADR-0003, ADR-0004, ADR-0005, ADR-0006, ADR-0007, ADR-0009, ADR-0010, ADR-0012, ADR-0013, ADR-0014.
- **Risk class:** Governed high-risk foundation change.
- **Non-goals:** distributed workers, external brokers, scheduling breadth, market-data work, exactly-once execution, and M1 recovery-package implementation.

