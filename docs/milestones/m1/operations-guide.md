# Run and operate the M1 secure walking skeleton

- **Status:** M1.7 operational guidance
- **Requirements:** REQ-0001–REQ-0020; documentation closure under REQ-0019 and REQ-0020
- **Governing specification:** [M1 secure walking skeleton](../../specifications/m1-secure-walking-skeleton.md)
- **Evidence plan:** [M1 evidence plan](evidence-plan.md)
- **Last reviewed:** 2026-07-18

This page is non-normative, version-matched guidance for the current source tree. The accepted specification, ADRs, and public contracts govern behavior.

## Supported M1 boundary

M1 is a Python 3.13 local-first modular monolith. The default profile uses the operating-system user boundary and loopback listener. The personal-server profile is a validation skeleton: non-loopback serving is rejected unless TLS certificate/key references, trust configuration, and an authenticated session provider are present. M1 is not certified for public-internet exposure, multi-user identity, distributed work, or restored-state activation.

## Clean setup

Prerequisites:

- Python 3.13;
- [uv](https://docs.astral.sh/uv/) compatible with the committed lockfile;
- Node.js 20.19 or later only for governed OpenSpec validation;
- a compatible `age` executable only for production-format backup and restore operations.

From a clean checkout:

```bash
uv sync --locked
uv run alembic upgrade head
uv run osca readiness
```

Use `OSCA_DATABASE_PATH` to select a non-default SQLite metadata database. The default is `osca.db`.

For development validation:

```bash
uv run ruff check .
uv run mypy
uv run pytest
```

The engineering rules and additional architecture, migration, schema, security, documentation, and OpenSpec gates are defined in [AGENTS.md](../../../AGENTS.md) and the [M1 evidence plan](evidence-plan.md).

## Start and verify readiness

Start the web/API adapter on loopback:

```bash
uv run uvicorn osca.bootstrap.web:app --host 127.0.0.1 --port 8080
```

In another terminal, exercise the three presentations of the shared readiness query:

```bash
uv run osca readiness
curl --fail http://127.0.0.1:8080/api/v1/readiness
curl --fail http://127.0.0.1:8080/health
```

The representations differ, but the CLI, versioned API, and web route derive from the same application behavior. Readiness reports availability and safe acceptance of supported work; it does not certify analytical correctness.

## Configuration and security

The local defaults are profile `local`, deployment mode `local`, listener `127.0.0.1:8080`, and no remote-security references. Do not change the process listener to a wildcard or non-loopback address and assume the application has accepted a personal-server profile.

Personal-server validation requires all of the following before affected work can serve:

- explicit `personal_server` deployment mode;
- TLS certificate and private-key references;
- trust-store reference;
- authenticated session-provider configuration;
- a non-secret, named-reference path to credentials.

Secrets belong in the operating-system credential store or replaceable vault adapter. Secret values must not appear in configuration, commands, URLs, logs, errors, audit details, backups, examples, or evidence. The current source exposes the validated configuration contracts but does not yet provide a production deployment wrapper for remote TLS/session termination.

## Durable diagnostic jobs

Initialize the database first, then follow [durable diagnostic jobs](diagnostic-jobs.md). A representative submission is:

```bash
uv run osca diagnostic-submit storage adapter-fixture
uv run osca diagnostic-list
```

The second argument is an idempotency key, not a secret. Save the returned typed run identifier for `diagnostic-get` or `diagnostic-cancel`. Execution is embedded, durable, lease-based, checkpointed, and at-least-once; it is not a distributed scheduler.

## Protected backup and isolated restore

Follow [M1 protected backup and isolated restore](recovery.md). Those commands require a real operator-generated X25519 recipient and a separately custodied identity stored through the Security capability. Example recipients in documentation are deliberately non-executable and are never production credentials.

Verification and preview do not mutate active state. M1 restore writes only to a new isolated destination and never activates it.

## Telemetry, audit, and troubleshooting

Use correlation identity to connect interface, application, workflow, persistence, and recovery observations. Ordinary telemetry uses structured safe fields; audit records are separate and cover security-sensitive actions. Never paste secret values into diagnostics.

| Symptom | Check | Safe response |
|---|---|---|
| Startup or readiness rejects configuration | Stable code, field path, and deployment profile | Correct the named field; do not bypass validation |
| Readiness is degraded or blocked | Required component state and remediation | Restore the dependency, then query readiness again |
| Diagnostic submission conflicts | Actor, idempotency key, and versioned input | Reuse the original input or choose a new non-secret key |
| A run remains interrupted | Lease expiry and configured local recovery policy | Resume only through the declared policy; do not edit SQLite |
| Backup/restore fails | Recovery stable code and correlation identity | Follow the [recovery troubleshooting table](recovery.md#troubleshooting) |
| Telemetry export fails | Built-in health and local structured logs | Diagnose the exporter; built-in health remains authoritative for availability |

## Contracts and schemas

The accepted public families and compatibility rules are listed in the [M1 specification](../../specifications/m1-secure-walking-skeleton.md#public-contract-families). Deterministic contract schemas live under `contracts/schemas/`; SQLite migrations live under `migrations/versions/`. Treat generated schemas as contract projections, not replacements for requirements or ADRs.

## Example-validation matrix

| Example | Automated evidence |
|---|---|
| Locked environment and migration | CI locked-environment and migration gates |
| CLI readiness | CLI/contract tests and M1.7 operational example run |
| API and web readiness | end-to-end/semantic contract tests and M1.7 operational example run |
| Diagnostic submit/list/get/cancel | workflow CLI, component, lifecycle, and documentation tests |
| Backup/verify/preview/isolated restore | recovery CLI, adapter interoperability, malicious-input, and invariance tests |
| Real credential-store and recovery identity custody | adapter conformance plus operator procedure; platform- and identity-specific, so no example secret is executed in CI |
| Personal-server TLS/session deployment | configuration security-negative tests; production deployment certification is outside M1 |

## Known M1 limitations

- Python 3.13 and the committed locked environment define the reference runtime.
- Credential-store conformance and loopback-family behavior can vary by operating system.
- Personal-server configuration proves fail-closed validation, not public-internet hardening certification.
- Diagnostic work is embedded and at-least-once; distributed execution is deferred.
- Recovery depends on an external compatible `age` executable and separately custodied identity.
- Restore activation, in-place overwrite, remote backup transport, scheduling, automated retention, full disaster recovery, and market payloads are deferred.
- M1.7 closes documentation and operational evidence only. M1 acceptance remains subject to the M1.8 exit review.
