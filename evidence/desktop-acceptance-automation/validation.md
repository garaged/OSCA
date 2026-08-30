# Desktop Acceptance Automation Validation Evidence

- **Source revision:** `agent/d9-acceptance-automation-foundation` working tree (based on `addfe119d895aee05751644929264ba9491926e8`)
- **Scope:** deterministic D5--D7 acceptance-profile preparation, expanded D1--D8 focused desktop regression, and shortened human-review procedure
- **Date:** 2026-08-30

## Executed gates

| Gate | Result |
|---|---|
| `uv sync --locked` | PASS |
| `uv run ruff check .` | PASS |
| `uv run mypy` | PASS — 280 source files |
| `uv run pytest` | PASS — 549 passed, 1 skipped (`AGE_TEST_EXECUTABLE` unavailable), 1 pre-existing zipfile duplicate-name warning |
| `make test-desktop` | PASS — 91 Python tests and 38 frontend tests |
| `apps/desktop: npm run check` | PASS |
| `apps/desktop: npm run build` | PASS |
| `DO_NOT_TRACK=1 npm run openspec:doctor` | PASS |
| `DO_NOT_TRACK=1 npm run openspec:validate` | PASS — 53 items |
| `make acceptance-seed` | PASS — retained local manifest with AAPL/MSFT samples, D5 comparison, D7 backtest/evaluations, and D6 project pin |

## Boundaries confirmed

The profile builder invokes only typed local desktop-service methods. Its retained manifest asserts `network_access_enabled`, `recommendations_enabled`, and `real_capital_execution_enabled` are all false. It creates no provider credentials, broker connection, order, or external request.

## Remaining human work

The retained automated manifest does not replace visual/usability judgment. The updated manual guide limits normal milestone review to the changed surface and a 5--10 minute smoke check; release candidates, migrations, shell/package changes, and material interaction redesigns retain broader exploratory/platform acceptance.
