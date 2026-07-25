# M7 F2 Event-Driven Validation

## Why

OSCA needs deterministic F2 event-driven validation after M6 established backtest request and order-intent contracts. Strategy candidates cannot move toward paper evaluation until historical bar-based order lifecycle, fill, risk, accounting, valuation, projection, and promotion-gate evidence is governed.

## What Changes

- Add governed M7 requirements for F2 event streams, order lifecycle events, simulated fills, deterministic risk outcomes, balanced journal transactions, valuation evidence, rebuildable projections, and promotion gates.
- Add ADR-0033 and M7 milestone documentation.
- Add initial F2 event-driven contracts, validation services, tests, and retained evidence.

## Impact

- Adds `osca.backtesting.eventing` contracts and services.
- Extends M6 simulated order-intent semantics without adding F3 paper accounts.
- Does not execute live orders, create independent paper accounts, run forward schedules, or implement tick/quote/order-book fidelity.
