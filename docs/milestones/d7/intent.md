# D7 Intent — Visual Strategy Builder and Backtest Lab

## Outcome
Users can define versioned strategies through guided rules, evaluate them under explicit fidelity and cost assumptions, compare benchmarks, and retain reproducible evidence.

## Scope
Strategy DSL and templates, entry/exit rules, sizing and risk controls, validation, vectorized and event-driven backtests, fidelity levels, benchmarks, sensitivity, walk-forward views, and result comparison.

## Non-goals
Live trading, brokerage adapters, opaque frontend execution, or automatic strategy promotion.

## Dependencies
D5 analysis workbench and shared strategy/backtest services.

## Risks
Look-ahead bias, misleading fills, overfitting, invalid rule combinations, and result divergence between engines.

## Exit intent
Definitions are immutable and portable; assumptions are visible; golden and property tests cover calculations; walk-forward and sensitivity evidence is available; failures cannot create plausible but invalid performance results.
