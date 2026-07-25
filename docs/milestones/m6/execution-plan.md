# M6 Execution Plan

## M6.1 Backtesting contracts and planner

- Add backtesting API contracts.
- Add application validation and execution planning services.
- Add unit coverage for point-in-time, execution-mode, provisional-data, order-intent, and result rules.
- Record hosted Quality evidence.

## M6.2 Backtest lifecycle persistence

- Persist backtest requests, plans, and results after M6.1 is green.
- Preserve immutable request/result identity and queryable history.

## M6.3 Operator administration

- Add metadata-only CLI/API access after persistence exists.
- Keep strategy runtime and event matching deferred until their contracts are accepted.

## M6 closeout

- Archive the OpenSpec change.
- Accept the canonical spec.
- Update traceability, architecture status, validation evidence, and exit review.
