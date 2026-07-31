# P14 Exit Review

- **Milestone:** P14 personal-server production operations
- **Status:** Implementation candidate; review and merge pending
- **Branch:** `agent/p14-personal-server-operations`
- **Pull request:** #57
- **Baseline:** merged P13 commit `b22d23970be25f6425c4e5bd4d8a8ea51bb38335`
- **Validated head:** `fe941548ca1aa81228d968a4c8c4aa3a6a609d0b`

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

All eight P14 tests passed, covering security validation, disabled and successful job execution, alert enablement and HTTPS enforcement, backup source separation, successful backup/restore, restore enablement, and overwrite protection.

## Hosted validation

Quality run `30650308948` passed on the validated implementation head:

- Ruff passed.
- Strict mypy passed across 203 source files.
- 340 tests passed, including all eight P14 tests.
- Contract, migration, document-link, and architecture checks passed.
- OpenSpec doctor and strict validation passed.
- Secret scanning passed.

Earlier validation found unused CLI imports, result-variable type narrowing, a missing scheduler interval argument, and a missing default scheduler interval. Each issue was corrected without changing the milestone safety boundaries.

## Completion decision

P14 is review ready. It remains an implementation candidate until PR #57 is merged. Operator-owned host, TLS, identity, firewall, storage-mount, and post-restore checks remain documented residual responsibilities.
