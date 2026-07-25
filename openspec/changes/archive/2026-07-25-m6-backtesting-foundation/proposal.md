# M6 Backtesting Foundation

## Why

OSCA needs deterministic strategy-validation semantics before implementing the event engine, portfolio accounting, paper accounts, ML promotion, or LLM orchestration.

## What Changes

- Add governed M6 requirements for backtesting request, execution plan, order intent, and result contracts.
- Add fail-closed execution planning for look-ahead/provisional data and fidelity profile mismatches.
- Add tests and evidence for M6.1 behavior.

## Impact

- Adds `osca.backtesting` contracts and application services.
- Does not execute strategies, simulate fills, mutate portfolios, or place live orders.
