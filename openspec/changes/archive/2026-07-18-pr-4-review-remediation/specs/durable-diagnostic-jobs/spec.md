## MODIFIED Requirements

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

### Requirement: Correlated operational evidence
Submission, claim, transition, checkpoint, retry, cancellation, recovery, and completion SHALL emit safe correlated logs, OpenTelemetry metrics and spans, and typed job events; security-sensitive actions SHALL also emit distinct Operations-owned audit records.

#### Scenario: Failed run evidence
- **WHEN** a diagnostic run fails
- **THEN** structured telemetry, a distinct audit record where security-sensitive, and a health finding reference the run and correlation identity without exposing protected values

#### Scenario: Operation evidence fan-out
- **WHEN** a workflow operation is recorded
- **THEN** its log, metric, span, and job event carry the same run and correlation identities without input, idempotency key, or secret values

### Requirement: Durable result metadata before success
Catalog-owned result metadata SHALL include stable identity, version, producer build, producing-run lineage, correlation, integrity, availability, retention, and registration time before Workflow commits success.

#### Scenario: Missing result reference
- **WHEN** a handler attempts to complete successfully without registered result metadata
- **THEN** the transition is rejected and the run remains non-terminal or failed according to the structured error category

#### Scenario: Metadata round trip
- **WHEN** result metadata is registered and reloaded
- **THEN** its deterministic integrity digest verifies and all governed metadata semantics are preserved

### Requirement: Retained verification
The change SHALL retain evidence for lifecycle properties, migration, idempotency, lease expiry, restart recovery, cancellation, adapter equivalence, telemetry, architecture boundaries, and required pull-request automation for locked environments, static analysis, tests, strict OpenSpec validation, and secret scanning.

#### Scenario: OpenSpec and OSCA verification
- **WHEN** all implementation tasks are complete
- **THEN** strict OpenSpec validation passes and the OSCA evidence record links the source revision and executed gate results

#### Scenario: Pull request head changes
- **WHEN** a commit is pushed to the PR branch
- **THEN** required quality and secret-scanning workflows evaluate that exact head revision
