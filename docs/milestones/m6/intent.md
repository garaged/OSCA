# M6 Intent - Backtesting and Strategy Validation Foundation

- **Status:** Active
- **Baseline:** M5 complete
- **Last reviewed:** 2026-07-25

## Intent

Enable OSCA to represent fair, reproducible strategy validation work through governed backtest requests, fidelity profiles, point-in-time data requirements, pinned assumptions, order intents, execution plans, and structured results.

M6 turns the PRD dual-stage backtesting model into deterministic contracts and application behavior before building the full event engine or paper-account authority.

## Outcome

A local owner or automation client can define a strategy validation request, identify whether it is a signal study, vectorized estimate, event-driven bar simulation, or forward-paper evaluation, and receive a fail-closed execution plan that exposes required checks and invalid prerequisites.

## Non-goals

- Matching engine, fills, journal accounting, or portfolio projections.
- Paper-account authority.
- ML training lifecycle.
- LLM tool orchestration.
- Live brokerage or exchange execution.
- Tick-level, quote-level, or order-book simulation.
