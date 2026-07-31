# U7 - Model-to-Research Validation

- **Status:** Planned
- **Depends on:** U5-U6 and existing M6-M9 foundations

## Objective

Connect approved ML experiment evidence to event-driven validation, backtesting, and paper-challenger evaluation without creating a live execution path.

## Scope

- Require an approved M9 promotion decision before F2 validation linkage.
- Convert retained predictions into explicit research signals under versioned rules.
- Compare model signals with deterministic and naive baselines.
- Include transaction-cost, latency, slippage, and missing-prediction assumptions.
- Link predictions, signals, backtest events, paper evidence, drift, and outcomes.
- Require explicit human approval for any paper challenger designation.

## Non-scope

Live model serving, automated strategy scheduling into capital, broker connectivity, order APIs, recommendations, or real orders.

## Acceptance

A promoted experiment can complete a fully traceable local validation path from dataset and features through predictions, signals, backtest results, and paper evidence, while ADR-0044 remains enforced.
