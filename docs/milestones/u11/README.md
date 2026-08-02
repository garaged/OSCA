# U11 — First-Run and Unified Operator Experience

- **Status:** In progress; foundation implemented and green
- **Baseline:** U10 merged through PR #73 at `4711c6f2f4ba17a0904515c6ca935e653cbee6ed`
- **Branch:** `agent/u11-first-run-operator-experience`
- **Implementation PR:** #74

## Intent

Let a technically capable new user complete OSCA's primary local research workflow through the primary `osca` CLI without invoking internal Python modules or hand-authoring JSON.

## Delivered foundation

1. `osca init` creates a versioned local profile and writable data root with safe defaults.
2. `osca doctor` reports machine-readable runtime, PyArrow, SQLite, storage, port, and retained-evidence checks with remediation.
3. `osca workspace` starts or snapshots the read-only workspace from operator configuration and rejects non-loopback hosts.
4. `osca import-data`, `osca analyze`, and `osca backtest` provide canonical aliases for existing workflows.
5. `osca research-pipeline` remains the canonical combined experiment, diagnostic, and human-gated validation path.
6. zsh, Bash, and PowerShell quickstarts and a compatibility window through U13 are documented.
7. OpenSpec contracts, focused tests, and initial traceability are present.

Quality run #713 passed on the foundation implementation head:

- Ruff;
- strict mypy across 244 source files;
- tests, contracts, migrations, links, and architecture checks;
- OpenSpec doctor and strict validation;
- secret scanning.

Documentation-only progress commits follow that green head and remain subject to the next hosted run.

## Remaining implementation

1. Tighten operator configuration parsing and remove the temporary focused mypy exception.
2. Add provider capability, credential-reference, and deeper evidence-consistency diagnostics.
3. Add canonical/compatibility command-equivalence tests.
4. Reconcile the root README and central manual-testing guide.
5. Add U11 exit review and clean-profile end-to-end acceptance.

## Exit gate

A new user follows one canonical quickstart from installation to a populated read-only workspace without manual JSON composition or `python -m osca.*` commands.

## Safety

U11 does not enable recommendations, automatic model promotion, live model serving, broker or exchange connectivity, autonomous execution, real-capital orders, remote writes, or public evidence sharing.