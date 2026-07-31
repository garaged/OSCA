# U1 - First-Run Onboarding and Clean-Machine Acceptance

- **Status:** Implementation candidate
- **Baseline:** P17 blocked disposition merge `cfd0239b74e77ddb2c9450e08d5ee05dc769afad`
- **Phase:** Usability and release hardening

## Objective

Give a new local operator one deterministic command that explains whether the current machine and workspace are ready for OSCA's no-cost research path.

## Implemented scope

- `python -m osca.onboarding check` produces structured JSON checks.
- `--prepare` creates the selected storage root and proves that it is writable.
- Checks Python 3.13, supported platform family, committed AAPL demo fixture availability, and the ADR-0044 capital-execution boundary.
- Returns exit code `0` when ready, `1` when operator action is required, and `2` for a failed check.
- Provides next commands for readiness, local OHLCV import, and read-only workspace inspection.
- Adds automated clean-workspace coverage using temporary directories.

## Explicit non-scope

- Network access or provider calls.
- Credential discovery or materialization.
- Automatic dependency installation.
- Running analysis without an operator command.
- Recommendations, brokers, autonomous execution, or real-capital behavior.

## Acceptance

```bash
uv sync --locked
uv run python -m osca.onboarding check --storage-root .osca/u1 --prepare
```

Expected: status `ready`, all checks `ready`, storage created, and every external/capital boundary reported as disabled.
