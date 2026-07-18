## Context

M1.1–M1.3 established shared contracts, SQLite WAL persistence, migrations, configuration/security controls, telemetry, and separate audit storage. M1.4 is governed by REQ-0011–REQ-0015, the accepted M1 specification, and ADR-0013. OpenSpec tracks this bounded change but does not replace those authorities.

## Goals and non-goals

### Goals

- Prove durable single-node execution and recovery using OSCA-owned semantics.
- Keep Workflow state and repositories private to the Workflow capability.
- Expose versioned application contracts through shared CLI/API handlers.
- Produce deterministic, failure-oriented evidence.
- Evaluate OpenSpec as an agent-readable change execution layer.

### Non-goals

- Distributed execution, brokers, Temporal/Celery integration, schedule triggers, market workflows, or exactly-once guarantees.
- Changes to Frozen Tier-1 ADRs or accepted M1 requirements.
- Recovery-package encryption or M1 milestone exit.

## Decisions

### Capability and dependency model

Create `osca.workflow` with public immutable contracts under `workflow.api`, application commands/queries and owned ports under `workflow.application`, domain transition policy under `workflow.domain`, and SQLite/executor adapters under `workflow.infrastructure`. Bootstrap adapters depend on Workflow public application entry points. Workflow may publish result references through the Catalog public seam but cannot access Catalog tables.

### Persistence ownership

Add Alembic revision `m1_0003` for Workflow-prefixed run, idempotency, lease, checkpoint, and attempt state. Repository methods perform atomic compare-and-transition operations with expected revision/state predicates. Transactions remain short and capability-local.

### Execution and recovery

A single-node executor atomically claims pending/interrupted eligible work. Lease owner, expiry, and heartbeat are persisted. Expiry recovery changes running work to interrupted before resume. The diagnostic handler is a versioned phase machine whose phases are duplicate-aware. No exactly-once claim is made.

Only pending work is claimable. Policy-controlled recovery explicitly moves interrupted work to pending before a new atomic claim, preserving the governed transition graph and an observable interrupted state.

### Interaction classification

- Submit and cancel are commands.
- Get/list status are queries.
- Completed/failed/interrupted facts are integration events after commit.
- Executor coordination is a durable workflow and owns process state only.

### Contracts and compatibility

Implement `osca.workflow.diagnostic-run` 1.0.0 using Pydantic models. Checkpoints and inputs declare family/version. Unsupported major versions fail before execution. Public errors use `osca.error.envelope` semantics. Structural schemas and semantic fixtures are deterministic.

### Security and observability

Application commands accept an explicit actor/capability context. Correlation flows through persistence and telemetry. Run inputs and errors are schema-limited and secret-free. Operations receives health findings through a public port; audit remains Operations-owned.

## Risks and tradeoffs

- SQLite contention is controlled through short atomic operations, WAL, busy timeout, and bounded retry classification.
- Process crashes can replay work; handler phases must be idempotent or duplicate-aware.
- An embedded executor adds custom lifecycle logic; property tests and restart fixtures are mandatory.
- OpenSpec could duplicate normative specifications; this change links rather than modifies OSCA authority.

## Rollout and recovery

Land contracts and migration first, then repository/transition properties, executor, adapters, and evidence. Migration downgrade removes only Workflow-owned state and is for development evidence; released-state recovery favors forward repair. A failed executor can be disabled while retained runs remain queryable.

## Validation

- strict OpenSpec validation;
- migration upgrade/downgrade and retained fixture tests;
- state-machine property tests;
- idempotency conflict tests;
- concurrent claim and lease-expiry tests;
- process-restart/checkpoint recovery tests;
- cancellation and retry tests;
- API/CLI semantic fixtures;
- telemetry, redaction, audit, and health assertions;
- Ruff, strict mypy, architecture checks, and full pytest suite.
