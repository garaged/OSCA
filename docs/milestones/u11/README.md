# U11 — First-Run and Unified Operator Experience

- **Status:** In progress
- **Baseline:** U10 merged through PR #73 at `4711c6f2f4ba17a0904515c6ca935e653cbee6ed`
- **Branch:** `agent/u11-first-run-operator-experience`

## Intent

Let a technically capable new user complete OSCA's primary local research workflow through the primary `osca` CLI without invoking internal Python modules or hand-authoring JSON.

## Scope

1. Add canonical primary commands for initialization, diagnostics, workspace startup, acquisition/import, analysis, backtesting, experiments, diagnostics, and validation.
2. Preserve compatibility aliases for existing entry points during a documented deprecation window.
3. Provide safe local defaults that keep network access explicit and recommendations, brokers, autonomous execution, and real-capital orders disabled.
4. Add structured corrective diagnostics with optional machine-readable output.
5. Add shell-safe quickstarts for zsh, Bash, and PowerShell.
6. Diagnose runtime compatibility, writable storage, SQLite and Parquet readiness, ports, provider capability, credentials, and retained-evidence consistency.

## Implementation sequence

1. Inventory the current primary CLI and internal-module-only operator paths.
2. Define U11 OpenSpec contracts and compatibility policy.
3. Implement `osca init` and `osca doctor` with deterministic local configuration and JSON output.
4. Promote workspace startup and remaining workflow stages into the primary CLI.
5. Add compatibility aliases and deprecation evidence.
6. Add clean-profile quickstarts, end-to-end tests, manual acceptance, traceability, and exit review.

## Exit gate

A new user follows one canonical quickstart from installation to a populated read-only workspace without manual JSON composition or `python -m osca.*` commands.

## Safety

U11 does not enable recommendations, automatic model promotion, live model serving, broker or exchange connectivity, autonomous execution, real-capital orders, remote writes, or public evidence sharing.
