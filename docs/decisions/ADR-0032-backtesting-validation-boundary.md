# ADR-0032 - Backtesting Validation Boundary

- **Status:** Proposed
- **Date:** 2026-07-25
- **Tier:** Implementation
- **Deciders:** Architecture authority, product authority
- **Related decisions:** D-004, D-009, D-027, D-028, D-037, D-041, D-046
- **Supersedes:** None

## Context

M6 introduces strategy-validation contracts after M4 research outputs and M5 extension packaging. The PRD requires dual-stage backtesting with point-in-time data handling, visible fidelity profiles, promotion gates, and eventual shared semantics with paper trading.

Building order matching, fills, journals, and paper accounts before the validation boundary is stable would make later corrections expensive and could blur research estimates with authoritative event simulations.

## Decision

OSCA will introduce M6 as a contract-first backtesting foundation. Backtest requests, execution plans, strategy decisions, order intents, assumptions, and results become typed deterministic contracts before the event engine or paper-account authority is implemented.

Execution planning fails closed for look-ahead data, incompatible fidelity profile/execution mode pairs, provisional event-driven inputs, and forward-paper requests before paper-account authority exists.

## Consequences

- F0, F1, F2, and F3 are explicit fidelity profiles with distinct semantics.
- Strategy-generated order intents are simulation inputs, not live orders.
- Completed backtest results require metric methodology metadata.
- Event matching, fills, journals, and portfolio projections remain later governed work.
- M6 can add persistence and operator access after the contract behavior is green.
