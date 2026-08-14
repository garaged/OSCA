# D7 Validation Evidence — Visual Strategy Builder and Backtest Lab

- **Status:** Implementation retained; hosted validation and manual acceptance pending
- **Pull request:** [#87](https://github.com/garaged/OSCA/pull/87)
- **Branch:** `agent/d7-strategy-builder-backtest-lab`
- **Baseline:** D6 merge `9d7210011f0bc86b8e811ae92796d84ebc3c10ab`

## Automated Validation

Local validation passed for the D7 implementation:

- `uv run pytest tests/test_d7_desktop_strategies.py`: 7 passed;
- `uv run pytest tests/test_d3_desktop_import.py tests/test_d5_desktop_workbench.py tests/test_d5_workbench_quantitative.py tests/test_d6_desktop_projects.py tests/test_d7_desktop_strategies.py`: 32 passed;
- `uv run ruff check src/osca/desktop_api/service.py src/osca/desktop_api/strategies.py src/osca/desktop_api/d7_service.py src/osca/desktop_api/stdio.py src/osca/desktop_api/projects.py tests/test_d3_desktop_import.py tests/test_d7_desktop_strategies.py`;
- `uv run mypy src/osca/desktop_api/service.py src/osca/desktop_api/strategies.py src/osca/desktop_api/d7_service.py tests/test_d3_desktop_import.py tests/test_d7_desktop_strategies.py`;
- desktop TypeScript check;
- D7-focused desktop frontend tests: 32 passed;
- full desktop frontend source tests: 32 passed;
- desktop Vite production build;
- `npm run openspec:validate`: 51 passed, 0 failed;
- source-boundary scan found only expected forbidden-key, negative-test, and disclosure references;
- local Rust validation not run because `cargo` is unavailable in the Codex container.

Covered in this slice:

- profile-scoped strategy definitions and immutable strategy versions;
- typed declarative SMA DSL validation and guided frontend controls;
- blocking for executable fields, look-ahead rules, invalid combinations, missing data, and unsafe provider/execution authority;
- Python-authoritative deterministic vectorized backtest with explicit fees, slippage, sizing, fidelity disclosure, metrics, trades, equity/drawdown series, digest, and retained JSON evidence;
- retained backtest JSON evidence, thin result manifest export, and full-resolution result CSV export;
- D6 project pin types for `strategy`, `strategy_version`, and `backtest_result` references;
- bounded sensitivity and walk-forward evaluations with budget, cancellation, train/test, and overfitting disclosures;
- D7 sidecar method registration and Rust profile-mutation classification;
- local CSV import path whitespace trimming with regression coverage;
- accessible responsive Strategy Lab source coverage with keyboard and pointer chart/table result inspection.

Still pending for full D7 acceptance:

- final hosted exact-head validation;
- supported-platform clean-profile manual acceptance.

## Manual Acceptance

The complete procedure in `manual-acceptance.md` must pass from a clean profile on:

- macOS ARM64;
- Linux x86-64.

Private host paths, credentials, provider account information, and machine-local profile identifiers must not be committed.

## Current Disposition

- Implementation slices: D7 implementation complete.
- Automated validation: local focused validation passed for implementation.
- macOS ARM64 manual acceptance: pending.
- Linux x86-64 manual acceptance: pending.
- D7 exit decision: pending full implementation and supported-platform manual acceptance.
