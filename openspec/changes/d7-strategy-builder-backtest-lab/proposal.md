# D7 Visual Strategy Builder and Backtest Lab

## Why

D5 provides governed charting and quantitative analysis, and D6 organizes retained evidence into projects. Users now need a desktop research lab for defining strategy rules, evaluating them against governed historical data, and retaining reproducible backtest evidence without crossing into recommendation or execution behavior.

## What Changes

- Add profile-scoped strategy definitions with immutable versions.
- Add a typed declarative strategy DSL and guided templates.
- Add validation for rule compatibility, look-ahead/future-data hazards, and dataset integrity.
- Add Python-authoritative backtest execution with explicit fidelity, cost, fill, cash, sizing, and risk assumptions.
- Add deterministic metrics, equity curves, drawdowns, trade lists, exposure summaries, benchmarks, sensitivity, and walk-forward evidence.
- Add accessible responsive Strategy Builder and Backtest Lab UI with chart/table parity and full-resolution export.
- Add D6 project pinning for strategy and result evidence.

## Boundaries

D7 remains research-only. It adds no recommendation generation, automatic promotion, brokerage connectivity, paper-order submission, live-order routing, real-capital execution, arbitrary user code execution, notebooks, or provider credential collection.

## Requirements

This change implements REQ-0357 through REQ-0374 in `docs/governance/requirements-catalog-d7.md`.
