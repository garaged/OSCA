# D8 Intent — Virtual-Portfolio Accounting Foundation

## Outcome
Users can create multiple simulated portfolios and inspect auditable cash, positions, cost basis, realized and unrealized P&L, income, corporate actions, exposures, and performance.

## Scope
Append-only event model, double-entry journal, portfolio lifecycle, starting cash, base currency, positions, cost basis, dividends, splits, forks, FX, benchmarks, allocation, drawdown, attribution, scenarios, clone, reset, export, and restore.

## Non-goals
Real brokerage synchronization, tax filing, margin by default, or live execution.

## Dependencies
D7 strategy evidence and accepted paper-account contracts.

## Risks
Accounting drift, rounding and FX errors, non-idempotent corporate actions, destructive reset behavior, and migration corruption.

## Exit intent
Accounting identities hold under property tests; deterministic replay reproduces state; corrections are compensating entries; migrations are backed up and recoverable; every displayed balance traces to journal evidence.
