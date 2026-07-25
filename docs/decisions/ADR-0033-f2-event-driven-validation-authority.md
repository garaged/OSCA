# ADR-0033 - F2 Event-Driven Validation Authority

- **Status:** Accepted
- **Date:** 2026-07-25
- **Tier:** Implementation
- **Deciders:** Architecture authority, product authority
- **Related decisions:** D-001, D-002, D-004, D-009, D-027, D-028, D-037, D-038, D-041, D-046
- **Supersedes:** None

## Context

M6 established backtesting request, execution-plan, order-intent, and result contracts without event matching, fills, journals, portfolio accounting, or paper accounts. The PRD requires F2 event-driven bar simulation to become the authoritative historical validation mode before F3 forward paper deployment.

The F2 layer must be deterministic and shared in concept with later paper trading, but it cannot create independent paper accounts or replay forward paper actions before M8.

## Decision

OSCA will model M7 F2 validation as a deterministic event-driven simulation authority. F2 contracts represent market events, order lifecycle events, simulated fills, fee/spread/slippage/latency/liquidity model metadata, deterministic risk decisions, balanced double-entry journal transactions, valuation snapshots, reconciliation findings, rebuildable projections, and promotion-gate decisions.

M7 behavior remains historical simulation only. Live execution adapters, independent paper accounts, forward schedules, and real-capital order placement remain absent and fail closed.

## Consequences

- F2 order lifecycle and fill records retain links to M6 strategy decisions and order intents.
- Journal transactions must balance by currency before they can become authoritative simulation evidence.
- Valuations identify price and FX sources and effective times.
- Rebuildable projections derive from journal and valuation evidence rather than mutable balances.
- Promotion gates can approve F2 evidence for later paper evaluation, but cannot activate F3 behavior.
