# D6 Validation Evidence — Research Projects, Saved Workspaces, and Integrated Evidence

- **Status:** Planned
- **Pull request:** pending
- **Branch:** `agent/d6-research-projects-workspaces`
- **Baseline:** D5 merge `1936f1e5b47055f1e8d88d293abaf9dc99c00970`

## Automated validation

Pending implementation.

Expected evidence includes:

- strict OpenSpec validation;
- secret scanning;
- Ruff and strict mypy;
- Python project-service, migration, recovery, ownership, export, and profile-isolation tests;
- desktop API and launcher validation;
- frontend TypeScript build and Node tests;
- Rust format, tests, and Clippy;
- source-boundary checks proving no generic frontend filesystem/database/shell/provider/notebook/order authority;
- accessibility and responsive-source checks;
- manifest export and broken-link/degraded-state regressions.

## Manual acceptance

The complete procedure in `manual-acceptance.md` must pass from a clean profile on:

- macOS ARM64;
- Linux x86-64.

Private host paths, credentials, provider account information, and machine-local profile identifiers must not be committed.

## Current disposition

- Implementation slices: pending.
- Automated validation: pending.
- macOS ARM64 manual acceptance: pending.
- Linux x86-64 manual acceptance: pending.
- D6 exit decision: pending.
