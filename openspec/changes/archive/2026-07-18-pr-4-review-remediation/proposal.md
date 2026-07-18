## Why

PR #4 review found four blockers against the accepted M1 specification, REQ-0013, REQ-0014, and the M1 evidence plan: caller-controlled actor identity, incomplete workflow telemetry, incomplete retained metadata, and absent PR CI gates.

## What Changes

- Derive a trusted local authorization context at interface boundaries and enforce capabilities in shared handlers.
- Emit correlated logs, metrics, traces, job events, and applicable audit evidence through Operations-facing ports.
- Complete retained run/result metadata with build, lineage, integrity, availability, and retention semantics.
- Add locked GitHub quality and secret-scanning workflows.
- Add negative, contract, component, and workflow evidence; update retained M1.4 evidence.

## Capabilities

### Modified Capabilities

- `durable-diagnostic-jobs`: strengthen authorization, observability, and metadata obligations without changing lifecycle semantics.

## Impact

- **Requirements:** REQ-0002, REQ-0006, REQ-0010, REQ-0013, REQ-0014, REQ-0020.
- **Decisions:** ADR-0003, ADR-0004, ADR-0005, ADR-0009, ADR-0010, ADR-0013–ADR-0015.
- **Risk:** Governed high-risk remediation; no requirement or ADR redefinition.
