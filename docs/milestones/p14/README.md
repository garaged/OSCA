# P14 - Personal-Server Production Operations

- **Status:** Complete through PR #57
- **Governing role:** Product authority
- **Phase:** Production-capable version
- **Authoritative outcome:** Make single-user personal-server operation credible through explicit scheduler execution, alerts, backup/restore, hardened deployment templates, and fail-closed security controls.
- **Baseline:** P1-P13 complete
- **Last reviewed:** 2026-07-31
- **Validation:** Quality run `30650397785`; merge commit `3aa884b4894e4f956fa93e1d70cf1930329b83b4`

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

## Completion evidence

- REQ-0254-REQ-0260 reconciled in `docs/governance/p13-p14-reconciliation.md`.
- 340 tests passed, including all eight P14 tests.
- Ruff, strict mypy, architecture checks, OpenSpec validation, and secret scanning passed.
- P14 was merged through PR #57.

## Dependencies

P10-P13 routing, workspace, and ingestion capabilities plus M12 operations/recovery contracts.

## Risks and decisions

- P14 targets a trusted single-user host, not a public service.
- systemd templates are deployment examples; the operator still owns OS hardening, TLS termination, identities, firewalling, and off-device storage permissions.
- Restore success requires an operator post-restore functional check.
