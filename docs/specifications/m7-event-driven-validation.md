# Specification - M7 F2 Event-Driven Validation Foundation

- **Status:** Accepted
- **Governing role:** Architecture authority
- **Requirements:** REQ-0093-REQ-0101
- **Related decisions:** D-001, D-002, D-004, D-009, D-027-D-028, D-037-D-038, D-041, D-046; ADR-0033
- **Risk class:** Financial correctness, order lifecycle, accounting, and simulation semantics
- **Last reviewed:** 2026-07-25

## Public contract families

- `osca.backtest.event` 1.0.0 - proposed;
- `osca.backtest.order-lifecycle` 1.0.0 - proposed;
- `osca.backtest.fill` 1.0.0 - proposed;
- `osca.backtest.risk-decision` 1.0.0 - proposed;
- `osca.backtest.journal-transaction` 1.0.0 - proposed;
- `osca.backtest.valuation` 1.0.0 - proposed;
- `osca.backtest.portfolio-projection` 1.0.0 - proposed;
- `osca.backtest.promotion-gate` 1.0.0 - proposed.

## Behavioral specification

F2 event-driven validation represents simulation evidence as typed events with stable identity and timezone-aware effective time.

Order lifecycle events retain links to M6 simulated order intents and support accepted, rejected, cancelled, expired, partially filled, and filled states. Invalid lifecycle regressions fail closed before evidence is accepted.

Simulated fills identify the fill model, linked market observation, price, quantity, fees, spread, slippage, latency, liquidity, and partial-fill state. F2 remains bar-based and does not claim tick, quote, or order-book fidelity.

Risk decisions represent deterministic approve, modify, reject, and pause outcomes with policy version and rationale.

Journal transactions contain double-entry lines and must balance by currency. Valuation snapshots retain base currency, price sources, FX sources where applicable, effective time, and valuation version. Portfolio projections identify journal and valuation evidence required for rebuild.

Promotion gates disclose blocking findings and may approve F2 evidence for later paper evaluation, but cannot activate F3 behavior.
