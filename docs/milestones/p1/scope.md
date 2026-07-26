# P1 Scope

## Included

- Provider production evidence bundle contracts for Twelve Data and Kraken.
- Capability-scope records covering asset classes, intervals, and supported provider capabilities.
- Licensing/account-plan evidence with explicit allowed permissions.
- Named credential-reference and verification evidence without storing secret values.
- Quota policy and headroom evidence.
- Deterministic promotion decisions that approve, degrade, or block production enablement.
- SQLite metadata persistence for evidence bundles and decisions.
- Requirements, traceability, ADR, OpenSpec, manual testing, and exit-review evidence.

## Excluded

- Real Twelve Data or Kraken API calls.
- Credential materialization or secret-value inspection.
- Production ingestion jobs.
- External redistribution/export implementation.
- Runtime provider scheduling.
- Live brokerage or exchange execution.
- Real-capital orders.

## No-cost baseline

P1 must preserve a no-cost market-data path by allowing complete free-tier or no-cost provider evidence to satisfy promotion gates without requiring user payment. No-cost providers remain subject to the same licensing, quota, credential-reference, retention, export, backup, and review evidence as paid providers.
