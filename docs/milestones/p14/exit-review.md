# P14 Exit Review

- **Milestone:** P14 personal-server production operations
- **Status:** Implementation candidate; hosted Quality and review pending
- **Branch:** `agent/p14-personal-server-operations`
- **Pull request:** #57
- **Baseline:** merged P13 commit `b22d23970be25f6425c4e5bd4d8a8ea51bb38335`

## Implemented evidence

- Frozen security, scheduled-job, alert, backup, restore, and evidence contracts.
- Non-loopback exposure gate requiring TLS and authentication.
- Explicit scheduled-command execution with timeout and retained logs.
- File and HTTPS-webhook alert transports with explicit enablement.
- Off-source backup archive, manifest, file count, and SHA-256 evidence.
- Path-safe staged restore with explicit overwrite behavior.
- Hardened systemd service and timer templates.
- Operator CLI and manual quickstart.

## Safety behavior

- All operational actions are disabled by default.
- Webhook destinations require HTTPS and are redacted in evidence.
- Backup destinations inside the source tree are blocked.
- Unsafe archives and implicit overwrite are blocked.
- Multi-tenant SaaS, remote arbitrary command control, recommendations, broker/exchange connections, autonomous execution, and real-capital orders remain disabled.

## Automated validation

Tests cover security validation, disabled and successful job execution, alert enablement and HTTPS enforcement, backup source separation, successful backup/restore, restore enablement, and overwrite protection.

## Hosted validation

Pending final review-ready run:

- Ruff
- strict mypy
- pytest, contracts, migrations, links, and architecture checks
- OpenSpec doctor and strict validation
- secret scanning

## Completion decision

P14 remains an implementation candidate until final Quality is green, documentation and traceability are reconciled, the branch diff is reviewed, and PR #57 is merged.
