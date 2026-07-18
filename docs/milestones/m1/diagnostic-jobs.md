# Durable diagnostic jobs

- **Status:** Implemented M1.4 slice
- **Governing requirements:** REQ-0011–REQ-0015
- **Governing decision:** ADR-0013
- **Public contract:** `osca.workflow.diagnostic-run` 1.0.0
- **Schema revision:** `m1_0004`

## Prepare the database

Apply retained migrations before starting the API or using diagnostic commands:

```bash
uv run alembic upgrade head
```

Set `OSCA_DATABASE_PATH` to select a non-default metadata database. The default is `osca.db`.

## CLI

```bash
uv run osca diagnostic-submit storage adapter-fixture
uv run osca diagnostic-list
uv run osca diagnostic-get <run-uuid>
uv run osca diagnostic-cancel <run-uuid>
```

Submission requires a probe and idempotency key. Actor identity and capabilities are derived from the trusted local operating-system boundary; HTTP bodies and CLI options cannot assert them. Repeating an equivalent submission for the same actor returns the existing run. Reusing the key with different input is rejected.

## HTTP API

The versioned endpoints are:

- `POST /api/v1/diagnostic-runs`
- `GET /api/v1/diagnostic-runs`
- `GET /api/v1/diagnostic-runs/{run_id}`
- `POST /api/v1/diagnostic-runs/{run_id}/cancel`

HTTP and CLI adapters use the same application handlers and return the same run semantics.

## Execution and recovery

The embedded executor claims only pending work using an atomic revision guard and bounded lease. Heartbeats extend the active lease. An expired running lease first becomes interrupted; an explicit local recovery policy moves it to pending before another claim.

Execution is at-least-once. The diagnostic handler persists versioned named-phase checkpoints and is duplicate-aware. Success is rejected until a typed durable result reference exists. Retry is bounded and only applies to structured retryable errors.

## Operations and safety

Workflow telemetry includes stable run and correlation identities but excludes input values and idempotency keys. Security-relevant cancellation produces a separate Operations-owned audit record. Failed or blocked work produces a safe health finding log with a stable code.

This slice does not provide distributed workers, external brokers, scheduling, market workflows, or exactly-once execution.
