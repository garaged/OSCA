# M3 Evidence Plan

- **Status:** Active
- **Scope:** M3 temporal correctness implementation and documentation
- **Last reviewed:** 2026-07-24

## Required evidence

- unit tests for approved interval validation and completed-bar cutoff behavior;
- unit tests for stock exchange-session windows, missing gaps, and unresolved sessions;
- unit tests for crypto UTC interval generation;
- unit tests for deterministic resampling and lineage;
- compatibility check that M2 daily contracts remain importable and unchanged;
- OpenSpec validation;
- Python quality gate: pytest, ruff, and mypy;
- secret scanning and hosted Quality run before merge readiness.
