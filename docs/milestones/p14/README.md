# P14 - Personal-Server Production Operations

- **Status:** Implementation candidate
- **Governing role:** Product authority
- **Phase:** Production-capable version
- **Authoritative outcome:** Make single-user personal-server operation credible through explicit scheduler execution, alerts, backup/restore, hardened deployment templates, and fail-closed security controls.
- **Baseline:** P1-P13 complete
- **Last reviewed:** 2026-07-31
- **Validation:** Hosted Quality pending

## Objective

Turn the retained OSCA workflow into an operable single-user service without creating a multi-tenant SaaS or enabling autonomous trading.

## User-visible value

An operator can run governed commands on a schedule, deliver configured alerts, create off-source backups, restore through validated staging, and deploy hardened systemd units.

## Implemented scope

- Immutable scheduler, alert, backup, restore, security, and evidence contracts.
- Explicit scheduled-command execution with timeout and stdout/stderr retention.
- File and HTTPS-webhook alerts, disabled by default.
- Off-source-tree tar.gz backups with manifest and SHA-256 evidence.
- Active restore through path-safe temporary staging and explicit overwrite permission.
- Non-loopback security gate requiring TLS and authentication.
- Hardened systemd service and timer templates.
- CLI through `python -m osca.personal_server`.

## Explicit behavior

- Operational actions require explicit `--enable` flags or enabled contracts.
- Loopback operation is allowed without TLS/auth; non-loopback binding is rejected unless both are enabled.
- Webhook destinations require HTTPS and are redacted in evidence.
- Backup destinations inside the source tree are rejected.
- Restore to a non-empty destination requires explicit overwrite permission.

## Explicit non-scope

- Multi-tenant SaaS or public anonymous access.
- Embedded secret values or credential materialization.
- Arbitrary shell scheduling controlled by remote callers.
- Managed cloud orchestration, Kubernetes operators, or automatic infrastructure provisioning.
- Recommendations, broker/exchange connections, autonomous execution, or real-capital orders.

## Acceptance criteria

- REQ-0254-REQ-0260 map to implementation and tests.
- Operator actions remain disabled by default and retain structured evidence.
- Backup and restore prove path safety and explicit overwrite behavior.
- Non-loopback exposure fails closed without TLS and authentication.
- Automated tests, manual usage, OpenSpec, traceability, and hosted Quality are current before completion.

## Dependencies

P10-P13 routing, workspace, and ingestion capabilities plus M12 operations/recovery contracts.

## Risks and decisions

- P14 targets a trusted single-user host, not a public service.
- systemd templates are deployment examples; the operator still owns OS hardening, TLS termination, identities, firewalling, and off-device storage permissions.
- Restore success requires an operator post-restore functional check.
