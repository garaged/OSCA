## 1. Authority and contracts

- [x] 1.1 Confirm REQ-0011–REQ-0015 and ADR-0013 trace links in all Workflow public contracts.
- [x] 1.2 Add versioned diagnostic input, run identity, lifecycle, checkpoint, result, command, query, and error contracts.
- [x] 1.3 Add deterministic JSON Schema and semantic compatibility fixtures.

## 2. Specification-first tests

- [x] 2.1 Add lifecycle transition property tests, including every prohibited transition.
- [x] 2.2 Add idempotent-equivalent and conflicting-key submission tests.
- [x] 2.3 Add lease, heartbeat, concurrent claim, expiry, and restart-recovery tests.
- [x] 2.4 Add checkpoint compatibility, retry, cancellation, and result-before-success tests.

## 3. Persistence and migration

- [x] 3.1 Add Workflow-owned SQLAlchemy metadata and repository ports/adapters.
- [x] 3.2 Add retained Alembic revision `m1_0003` and upgrade/downgrade evidence.
- [x] 3.3 Prove short atomic compare-and-transition operations and schema ownership.

## 4. Executor and handler

- [x] 4.1 Implement the embedded single-node claim/lease/heartbeat executor.
- [x] 4.2 Implement the versioned, duplicate-aware diagnostic phase handler.
- [x] 4.3 Implement bounded retry, cooperative cancellation, safe shutdown, and expired-lease recovery.

## 5. Interfaces and operations

- [x] 5.1 Add shared submit, cancel, get, and list application handlers.
- [x] 5.2 Add versioned API and CLI adapters with semantic contract tests.
- [x] 5.3 Add correlated telemetry, safe failure findings, and applicable audit records.

## 6. Validation and evidence

- [x] 6.1 Run pytest, Ruff, strict mypy, migrations, architecture checks, and adapter smoke tests.
- [x] 6.2 Run strict OpenSpec validation and reconcile every finding.
- [x] 6.3 Update usage documentation, traceability, milestone status, and retained OSCA evidence.
- [ ] 6.4 Archive/sync the OpenSpec change only after implementation review and before the M1 PR is merged.
