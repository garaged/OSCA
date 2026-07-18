# durable-diagnostic-jobs Specification

## Purpose
Define the verified M1 semantics for durable single-node diagnostic-run submission,
execution, observation, interruption, and recovery under REQ-0011–REQ-0015 and ADR-0013.
## Requirements
### Requirement: Idempotent diagnostic-run submission
The Workflow capability SHALL accept mutation identity only from a trusted adapter-derived actor/capability context, SHALL enforce the required capability in shared application handlers, SHALL persist a stable typed run before execution, and SHALL preserve the declared idempotency behavior.

#### Scenario: First submission
- **WHEN** an authorized caller submits a valid versioned diagnostic input with a new idempotency key
- **THEN** the system persists a pending run and returns its stable identity

#### Scenario: Equivalent duplicate submission
- **WHEN** the same caller submits the semantically equivalent input with the same idempotency key
- **THEN** the system returns the existing run identity without creating another run

#### Scenario: Conflicting duplicate submission
- **WHEN** the same idempotency key is reused with semantically different input
- **THEN** the system rejects the request with a structured non-retryable conflict

#### Scenario: Caller attempts identity spoofing
- **WHEN** an API caller includes actor or capability-like fields in a submission payload
- **THEN** those fields cannot determine execution identity and the trusted boundary context is used

#### Scenario: Missing capability
- **WHEN** a trusted context lacks the required submit or cancel capability
- **THEN** the mutation is rejected before persistence with a structured non-retryable denial

### Requirement: Governed lifecycle transitions
The Workflow capability SHALL permit only the pending, running, blocked, succeeded, failed, cancelling, cancelled, and interrupted transitions defined by ADR-0013.

The permitted graph is:

- pending to running or cancelled;
- running to blocked, succeeded, failed, cancelling, or interrupted;
- blocked to pending or cancelled;
- cancelling to cancelled or interrupted;
- interrupted to pending, failed, or cancelled;
- succeeded, failed, and cancelled are terminal.

#### Scenario: Invalid transition
- **WHEN** a caller or executor attempts a transition not present in the accepted transition graph
- **THEN** the system rejects it without changing durable state and records correlated diagnostics

### Requirement: Lease and heartbeat recovery
The executor SHALL use an atomic claim with bounded lease and heartbeat metadata and SHALL recover expired work with at-least-once semantics.

#### Scenario: Active lease
- **WHEN** another executor attempts to claim a run with an unexpired lease
- **THEN** the claim is rejected and the current owner remains unchanged

#### Scenario: Expired lease after process loss
- **WHEN** a running lease expires without a heartbeat
- **THEN** the run becomes interrupted and eligible for policy-controlled resume from its last valid checkpoint

### Requirement: Versioned checkpoints and duplicate-aware execution
The diagnostic handler SHALL persist versioned checkpoints and SHALL tolerate replay of a completed phase without duplicating its externally visible effect.

#### Scenario: Resume from valid checkpoint
- **WHEN** an interrupted run is resumed with a compatible checkpoint
- **THEN** execution continues from the next incomplete phase and preserves prior completed phase results

#### Scenario: Incompatible checkpoint
- **WHEN** a checkpoint family or major version is unsupported
- **THEN** the run enters blocked state with a compatibility finding and is not executed

### Requirement: Cooperative cancellation
The executor SHALL persist cancellation intent and SHALL acknowledge it before safe handler termination according to the M1 performance target.

#### Scenario: Cancel running work
- **WHEN** an authorized caller cancels a running diagnostic run
- **THEN** the run enters cancelling and then cancelled after the handler reaches a safe boundary

#### Scenario: Cancel terminal work
- **WHEN** cancellation is requested for a terminal run
- **THEN** the system returns the existing terminal state without rewriting history

### Requirement: Structured retry policy
The executor SHALL retry only failures classified as retryable and SHALL apply bounded deterministic backoff under test.

#### Scenario: Retryable failure below limit
- **WHEN** a handler reports a retryable failure and attempts remain
- **THEN** the run is rescheduled with the declared next-attempt time and retained failure evidence

#### Scenario: Non-retryable or exhausted failure
- **WHEN** a failure is non-retryable or the attempt limit is exhausted
- **THEN** the run enters failed state and produces a visible Operations finding

### Requirement: Durable result metadata before success
Catalog-owned result metadata SHALL include stable identity, version, producer build, producing-run lineage, correlation, integrity, availability, retention, and registration time before Workflow commits success.

#### Scenario: Missing result reference
- **WHEN** a handler attempts to complete successfully without registered result metadata
- **THEN** the transition is rejected and the run remains non-terminal or failed according to the structured error category

#### Scenario: Metadata round trip
- **WHEN** result metadata is registered and reloaded
- **THEN** its deterministic integrity digest verifies and all governed metadata semantics are preserved

### Requirement: Consistent interface observation
The API and CLI SHALL expose the same run identity, lifecycle state, progress, checkpoint phase, attempt, and safe error semantics through shared application queries.

#### Scenario: Observe run through API and CLI
- **WHEN** an existing run is queried through both supported adapters
- **THEN** both results are semantically equivalent apart from presentation and request correlation identity

### Requirement: Correlated operational evidence
Submission, claim, transition, checkpoint, retry, cancellation, recovery, and completion SHALL emit safe correlated logs, OpenTelemetry metrics and spans, and typed job events; security-sensitive actions SHALL also emit distinct Operations-owned audit records.

#### Scenario: Failed run evidence
- **WHEN** a diagnostic run fails
- **THEN** structured telemetry, a distinct audit record where security-sensitive, and a health finding reference the run and correlation identity without exposing protected values

#### Scenario: Operation evidence fan-out
- **WHEN** a workflow operation is recorded
- **THEN** its log, metric, span, and job event carry the same run and correlation identities without input, idempotency key, or secret values

### Requirement: Retained verification
The change SHALL retain evidence for lifecycle properties, migration, idempotency, lease expiry, restart recovery, cancellation, adapter equivalence, telemetry, architecture boundaries, and required pull-request automation for locked environments, static analysis, tests, strict OpenSpec validation, and secret scanning.

#### Scenario: OpenSpec and OSCA verification
- **WHEN** all implementation tasks are complete
- **THEN** strict OpenSpec validation passes and the OSCA evidence record links the source revision and executed gate results

#### Scenario: Pull request head changes
- **WHEN** a commit is pushed to the PR branch
- **THEN** required quality and secret-scanning workflows evaluate that exact head revision

