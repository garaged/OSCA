# D7 Validation Evidence — Visual Strategy Builder and Backtest Lab

- **Status:** Planned
- **Pull request:** pending
- **Branch:** `agent/d7-strategy-builder-backtest-lab`
- **Baseline:** D6 merge `9d7210011f0bc86b8e811ae92796d84ebc3c10ab`

## Automated Validation

Pending implementation.

Expected evidence includes:

- strict OpenSpec validation;
- secret scanning;
- Ruff and strict mypy;
- Python strategy, DSL, backtest, migration, recovery, ownership, export, and profile-isolation tests;
- desktop API and launcher validation;
- frontend TypeScript build and Node tests;
- Rust format, tests, and Clippy;
- source-boundary checks proving no generic frontend filesystem/database/shell/provider/notebook/order authority;
- accessibility and responsive-source checks;
- chart/table parity and full-resolution export checks;
- backtest golden metrics, property tests, look-ahead blocking, and no-mutation regressions.

## Manual Acceptance

The complete procedure in `manual-acceptance.md` must pass from a clean profile on:

- macOS ARM64;
- Linux x86-64.

Private host paths, credentials, provider account information, and machine-local profile identifiers must not be committed.

## Current Disposition

- Implementation slices: pending.
- Automated validation: pending.
- macOS ARM64 manual acceptance: pending.
- Linux x86-64 manual acceptance: pending.
- D7 exit decision: pending.
