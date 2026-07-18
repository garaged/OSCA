## Context

The local profile relies on the operating-system user boundary, but public adapters must not accept asserted actor identity. Operations telemetry already configures OpenTelemetry, and Catalog owns result metadata.

## Decisions

### Trusted local authorization

Add an immutable actor/capability context. Local API and CLI adapters derive a fixed OS-user context through an injectable boundary dependency. External request bodies contain no actor or capability fields. Shared handlers enforce submit, read, and cancel capabilities and return structured denial.

### Complete observation

WorkflowObserver uses OpenTelemetry tracer and meter APIs and publishes a typed job event to an injected sink for each operation. Operations owns the SQLite event-evidence adapter and cancellation audit storage. Logs and events contain only safe stable fields.

### Retained metadata

Runs and Catalog results carry producer build, lineage, availability, retention, and integrity fields. Integrity is a deterministic SHA-256 digest over canonical safe metadata. Persistence tests verify round trips and ownership.

### CI

GitHub Actions uses locked Python and npm environments, Ruff, strict mypy, pytest, OpenSpec strict validation, deterministic schema tests, and a separate secret scan. Branch protection remains repository administration.

## Validation

Negative authorization tests; adapter spoofing tests; logs/metrics/traces/event/audit tests; metadata schema/round-trip/integrity tests; migrations; architecture checks; Ruff; mypy; pytest; OpenSpec; GitHub checks.
