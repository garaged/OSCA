# Tasks: U11 First-Run and Unified Operator Experience

## Specification and contracts

- [x] Record U11 intent, non-goals, exit gate, and safety boundaries.
- [x] Define initialization, doctor, workspace, compatibility, and quickstart requirements.
- [x] Define versioned operator configuration and structured diagnostic evidence.

## Primary CLI

- [x] Add `osca init` with safe local defaults.
- [x] Add `osca doctor` with corrective machine-readable checks.
- [x] Add `osca workspace` as the primary read-only workspace entry point.
- [x] Promote or alias local import, deterministic analysis, and backtesting commands.
- [x] Keep experiment, diagnostic, and validation execution under the canonical `osca research-pipeline` command.
- [x] Document compatibility aliases and the U13 deprecation window.

## Diagnostics

- [x] Check Python runtime compatibility.
- [x] Check writable storage.
- [x] Check SQLite readiness.
- [x] Check Parquet/PyArrow readiness.
- [x] Check workspace port availability.
- [x] Report retained-evidence presence.
- [x] Add provider capability and credential-reference diagnostics.
- [x] Add workspace-backed retained-evidence consistency diagnostics.
- [x] Strictly reject unsafe or unknown configuration fields.

## Validation and evidence

- [x] Add focused initialization, doctor, CLI discovery, and loopback tests.
- [x] Add canonical/compatibility delegation tests.
- [x] Add zsh, Bash, and PowerShell quickstarts.
- [x] Reconcile the root README to the canonical U11 path.
- [x] Reconcile central manual testing through U11.
- [x] Add U11 traceability, manual acceptance, and exit review.
- [x] Run final hosted Quality on the implementation-closeout head.
- [x] Remove the temporary operator configuration mypy exception.
- [ ] Retain clean-profile end-to-end acceptance evidence.
