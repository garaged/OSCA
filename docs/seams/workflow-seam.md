# Workflow Seam

- **Status:** Draft
- **Owner:** Durable workflows capability
- **Purpose:** Execute long-running, scheduled, resumable, and multi-step application processes without moving domain rules into workers or schedulers.

## Contract groups

- immutable workflow definition;
- schedule and trigger policy;
- durable run identity and correlation;
- step invocation and result references;
- checkpoint, retry, timeout, cancellation, and compensation policy;
- progress and health events;
- missed-run, concurrency, and duplicate behavior;
- recovery and replay manifest.

## Mandatory behavior

- Steps invoke published application capabilities.
- Workflow state records process progress and references module-owned state; it does not become domain authority.
- Definitions identify exact capability and contract versions required for replay.
- Retryability derives from structured errors and idempotency rules.
- At-least-once execution is assumed unless stronger guarantees are proven.
- Concurrency policy is explicit per workflow and target identity.
- Cancellation and timeout leave a declared safe state.
- Missed schedules, partial completion, manual intervention, and degraded dependencies are visible.
- Recovery can resume, compensate, restart, or terminate according to recorded policy.

## Conformance evidence

Fixtures cover duplicate delivery, crash after side effect, checkpoint loss, timeout, cancellation, retry exhaustion, unavailable dependency, incompatible contract, missed schedule, concurrent runs, compensation failure, and recovery replay.