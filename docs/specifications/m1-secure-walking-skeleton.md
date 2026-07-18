# Specification — M1 Secure Walking Skeleton

- **Status:** Accepted
- **Governing role:** Architecture authority
- **Approval roles:** Product, security, and quality authorities
- **Purpose:** Define implementation-ready behavior for the M1 system-readiness vertical slice.
- **Governing intent:** [M1 intent](../milestones/m1/intent.md)
- **Requirements:** REQ-0001 through REQ-0020
- **Related decisions:** D-006, D-007, D-021, D-022, D-031, D-032, D-033, D-035, D-036, D-044, D-046; ADR-0001 through ADR-0016
- **Related risks:** Unsafe exposure, secret disclosure, state loss, workflow corruption, interface divergence, documentation drift
- **Downstream consumers:** Implementation, tests, documentation, operations, and M1 evidence
- **Last reviewed:** 2026-07-18

## Problem and context

OSCA needs a minimal product that proves its architecture under executable conditions before market-data capabilities are added. The slice must be useful to an operator while exercising capability ownership, shared application contracts, persistence, security, workflows, observability, recovery, and documentation.

## Scope

### In scope

- validated local and personal-server configuration profiles;
- readiness query exposed through web, HTTP API, and CLI;
- vault capability probe using named references;
- embedded durable diagnostic job;
- typed M1 metadata catalog records;
- structured telemetry, distinct audit records, and health aggregation;
- minimal backup, integrity verification, restore preview, and isolated restore;
- versioned documentation and executable examples.

### Out of scope

All M2+ product behavior, multi-user identity, distributed execution, full DR automation, public-internet hardening certification, market payload persistence, and a permanent rich-client framework.

## Terminology

The repository glossary governs readiness, health, workflow, artifact, lineage, audit, recovery, and owner terminology. A **readiness snapshot** is an immutable observation of whether the configured M1 capabilities can safely accept supported work. It is not a guarantee of analytical correctness.

## Capability ownership

| Capability | Commands | Queries | Events | Owned state |
|---|---|---|---|---|
| Configuration | Validate configuration | Get active validated snapshot | ConfigurationValidated, ConfigurationRejected | Validated snapshot/revision |
| Security | Store/delete test secret reference | Probe vault capability | SecurityProfileRejected, VaultProbeCompleted | Security profile and references, never secret values |
| Workflow | Submit/cancel diagnostic run | Get/list run | DiagnosticRunCompleted/Failed | Run lifecycle, lease, checkpoint, result reference |
| Catalog | Register/update availability | Resolve metadata reference | MetadataRegistered | Typed metadata and lineage |
| Operations | Record finding/audit signal | Get readiness snapshot | ReadinessChanged | Health observations/findings |
| Recovery | Create backup; preview/execute isolated restore | Get backup/restore record | BackupCreated/Rejected, RestoreVerified/Rejected | Manifest, integrity, restore record |

Events are durable integration facts only after owned state commits. M1 may keep events internal to the modular-monolith transport while preserving contract semantics.

## Public contract families

- `osca.readiness.snapshot` major version 1;
- `osca.error.envelope` major version 1;
- `osca.workflow.diagnostic-run` major version 1;
- `osca.catalog.metadata-reference` major version 1;
- `osca.recovery.backup-manifest` major version 1;
- `osca.recovery.restore-plan` major version 1.

Exact revision begins at `1.0.0`. Unknown fields are ignored only where the family schema explicitly allows them. Unknown major versions are rejected with a structured compatibility error.

## Behavioral requirements

### Startup and configuration

1. The application loads a named profile, validates schema and semantic invariants, creates an immutable configuration revision, and only then constructs serving or worker adapters.
2. Local profile defaults to both loopback families where supported. A requested wildcard or non-loopback address is rejected unless personal-server mode is explicit.
3. Personal-server mode is blocked unless TLS certificate/key references, trust configuration, and an authenticated session-provider configuration pass validation.
4. Diagnostics contain field paths, stable error codes, safe remediation, and correlation identity; values classified as secret are redacted.

### Readiness

1. The application query returns product/build identity, configuration revision, overall state, component observations, active blockers, timestamp, and correlation identity.
2. Overall state is derived deterministically from component states and cannot report healthy when a required component is blocked or unavailable.
3. Web, API, and CLI use the same query handler and semantic contract.
4. API route is `GET /api/v1/readiness`; CLI command is `osca readiness`; web route is `/health`.
5. Presentation may differ, but semantic values and error categories must be equivalent.

### Secret-vault probe

1. Configuration and public contracts contain `SecretReference`, never secret values.
2. A diagnostic setup command may store a test secret through the vault port after explicit user action.
3. Readiness probes adapter availability and reference resolvability without retrieving or returning a secret value unless the internal adapter operation requires it.
4. Denied, unavailable, missing, or invalid references produce distinct safe findings.

### Diagnostic job

1. `SubmitDiagnosticRun` accepts a versioned input, idempotency key, and correlation context and returns a stable run identity within one second on the reference environment.
2. A run persists before execution and follows only specified lifecycle transitions:
   - pending to running or cancelled;
   - running to blocked, succeeded, failed, cancelling, or interrupted;
   - blocked to pending or cancelled;
   - cancelling to cancelled or interrupted;
   - interrupted to pending, failed, or cancelled;
   - succeeded, failed, and cancelled are terminal.
3. Claim uses a lease and heartbeat. Expired running leases become interrupted and eligible for policy-controlled resume.
4. The handler checkpoints named phases and is duplicate-aware.
5. Cancellation is cooperative, persisted, and acknowledged within the PRD target before safe termination.
6. Retry occurs only for declared retryable categories with bounded attempts and deterministic backoff under test.
7. Result metadata is registered in the catalog before success is published.
8. Failure creates a visible health finding with safe remediation and retained correlation.

### Metadata

Every retained record declares family, version, stable typed ID, revision, created/effective times as applicable, producing build/workflow, upstream references, configuration revision, integrity digest, availability, and retention classification. A bare path or table key is not a public identity.

### Telemetry and audit

1. Every interface invocation, application operation, job run, repository operation, and recovery action propagates correlation identity.
2. Logs use structured fields and safe error codes. Traces and metrics use OpenTelemetry APIs.
3. Audit records are created for unsafe configuration rejection, secret-reference changes, authentication-sensitive failure, backup creation, and restore execution.
4. Audit storage and queries are separate from ordinary logs.
5. Secret canary tests scan all emitted diagnostics and artifacts.

### Backup and restore

1. M1 backup includes validated configuration excluding secrets, metadata, workflow state, catalog records, audit metadata, schema versions, checksums, and an exclusion report.
2. Backup creation uses a consistent SQLite snapshot and records source build/schema identity.
3. The selected encryption container must be interoperable and separately specified before backup implementation is merged; plaintext backups are test-fixture-only and cannot be exposed as a production command.
4. Verification authenticates/decrypts, validates manifest/schema/checksums, and reports compatibility without mutating active state.
5. Restore preview produces an explicit plan and conflict report.
6. Restore executes only into a new isolated location in M1.
7. Post-restore validation runs migration assessment, database integrity, catalog/reference checks, audit checks, and readiness smoke tests.
8. Activation of restored state is out of scope for M1.

## Invariants

- No secret value crosses a public contract or enters ordinary persistence, backup, logs, traces, metrics, audit payload details, URLs, or error text.
- An interface cannot bypass configuration, authorization, or owned application behavior.
- A workflow success cannot exist without durable result metadata.
- A backup or restore cannot be reported verified without manifest, compatibility, and integrity evidence.
- Active state is never mutated by M1 restore.
- Correlation and stable typed identity are never inferred from a mutable `latest` pointer.
- Health availability never implies analytical correctness.

## Failure and degradation behavior

Failures use the public error envelope with category, stable code, message, retryability, correlation, affected identity, safe details, and remediation link. Configuration/security failures fail closed. Vault unavailability degrades secret-dependent readiness. Telemetry exporter failure does not block built-in health but is visible. Job-store integrity or migration failure blocks worker execution. Backup failure leaves no valid-looking package. Restore failure preserves active state.

## Security and privacy

Threat cases include unsafe bind, certificate/trust bypass, session-provider omission, secret leakage, path traversal, malicious backup archive, schema confusion, lease manipulation, audit suppression, log injection, CSRF for web mutations, and diagnostic denial of service. M1 web mutations require CSRF protection when introduced. All structured inputs have size and schema limits.

## Compatibility and migration

Each public family is cataloged at `1.0.0`. SQLite schema begins at Alembic revision `m1_0001`. Migration tests retain the initial empty state and every released M1 revision. Public contract changes follow ADR-0004. Backup manifests declare readable product and schema ranges; incompatible material fails before restore writes.

## Performance and resource budgets

On recommended hardware:

- readiness query processing p95 under one second;
- job submission acknowledgement under one second;
- visible job state within five seconds;
- cancellation acknowledgement within two seconds before safe completion;
- diagnostic job exposes progress within two seconds;
- local startup target under five seconds, recorded as an M1 benchmark rather than a product-wide guarantee.

## Acceptance criteria

| ID | Criterion | Verification | Requirements |
|---|---|---|---|
| M1-AC-001 | Clean checkout reproduces locked environment and starts local profile. | Build/test demonstration | REQ-0001, REQ-0019 |
| M1-AC-002 | Forbidden dependency and cross-schema examples fail architecture checks. | Structural negative test | REQ-0002, REQ-0020 |
| M1-AC-003 | API, CLI, and web readiness fixtures are semantically equivalent. | Contract/end-to-end | REQ-0002–REQ-0005 |
| M1-AC-004 | Default listeners are loopback-only. | Integration/security test | REQ-0006 |
| M1-AC-005 | Unsafe non-loopback combinations fail before serving. | Security-negative test | REQ-0007, REQ-0008, REQ-0016 |
| M1-AC-006 | Secret canary is absent from all captured outputs and artifacts. | Security scan | REQ-0009, REQ-0010 |
| M1-AC-007 | Vault adapter passes conformance behavior. | Contract/component | REQ-0009 |
| M1-AC-008 | Duplicate job submission returns declared idempotent outcome. | Component/property | REQ-0011, REQ-0012 |
| M1-AC-009 | Terminated job resumes from a valid checkpoint after lease expiry. | Failure/recovery test | REQ-0012 |
| M1-AC-010 | Invalid transition, checkpoint, or result reference is rejected. | Property/component | REQ-0012, REQ-0013 |
| M1-AC-011 | Required health component failure prevents healthy overall status. | Property/contract | REQ-0015 |
| M1-AC-012 | Correlation spans interface, application, job, persistence, and audit. | Observability assertion | REQ-0014 |
| M1-AC-013 | Backup excludes secrets/transients and verifies manifest/checksums. | Recovery/security test | REQ-0010, REQ-0017 |
| M1-AC-014 | Corrupt, malicious, or incompatible backup is rejected safely. | Security-negative/recovery | REQ-0018 |
| M1-AC-015 | Restore occurs in isolated storage and active-state digest is unchanged. | Recovery test | REQ-0018 |
| M1-AC-016 | Schema migration and interrupted-migration behavior match policy. | Migration test | REQ-0013, REQ-0017, REQ-0018 |
| M1-AC-017 | API schemas and compatibility fixtures are deterministic. | Contract test | REQ-0004, REQ-0013 |
| M1-AC-018 | Documented commands execute successfully in CI. | Documentation test | REQ-0019 |
| M1-AC-019 | Performance observations meet or disposition stated M1 budgets. | Benchmark | REQ-0011, REQ-0015 |
| M1-AC-020 | Evidence record contains no missing mandatory trace link. | Traceability validation | REQ-0020 |

## Documentation requirements

Installation, developer setup, local/personal-server configuration, security model, vault behavior, readiness API/CLI/web, diagnostic jobs, backup/restore, telemetry, troubleshooting, limitations, schemas, and executable examples must ship with the behavior.

## Exit dispositions

- The validated IPv4 loopback path is the M1 reference realization. Additional IPv6 listener realization remains platform-dependent and must be revisited before a supported platform requires dual-stack binding.
- M1 makes no named supported-operating-system claim for credential-store conformance. Target-platform keyring runs are required before publishing a supported-platform matrix.

These dispositions narrow M1 support claims without changing the accepted behavior.
