# D7 Validation Evidence — Strategy Builder and Backtest Lab

## Accepted baseline

- PR: #87
- PR head accepted: `fce711fbe4b7f5727736743163a7399c02937bd6`
- Squash merge: `95d2d6ad6a3a7d530ceae4f2c6cd76527f263559`
- Manual acceptance: completed by the user
- Supported-platform coverage: macOS ARM64 and Linux x86-64

## Hosted validation

The final ready-for-review run for PR #87 passed:

- Quality — success
- Desktop Foundation — success
- python-desktop-api — success
- frontend — success
- rust-broker — success
- linux-x86_64 desktop package smoke — success

## Manual acceptance outcome

The D7 procedure passed in full, including:

- profile-scoped strategy definition/version persistence;
- declarative SMA strategy validation;
- governed-data backtest execution and retained provenance;
- metrics, trades, equity/drawdown inspection, and full-resolution CSV export;
- keyboard/pointer synchronized chart/table inspection;
- sensitivity and walk-forward evaluation with ranges, budgets, warnings, and ordering;
- D6 project pins for strategy, strategy version, and backtest result;
- restart/reopen persistence, degraded pin behavior, and no duplicated provider data;
- profile isolation and ownership checks;
- local CSV path whitespace trimming;
- continued research-only/no-live-execution boundaries.

This file repairs the placeholder that remained in the D7 merge. The evidence above is reconstructed from the accepted PR #87 state and the completed user acceptance, not from a new post-merge test run.
