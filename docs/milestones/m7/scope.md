# M7 Scope

## In scope

- F2 event stream, market event, order lifecycle, fill, risk decision, journal, valuation, reconciliation, projection, and promotion-gate contracts.
- Deterministic contract validation for timezone-aware events, fill quantities, balanced journal transactions, valuation source identity, and promotion blocking findings.
- Initial service helpers for order lifecycle transition validation, journal balance validation, and promotion-gate evaluation.
- Focused tests, OpenSpec change, ADR, requirement allocation, traceability, and retained evidence.

## Out of scope

- F3 paper accounts and forward automation.
- Runtime strategy execution against live provider streams.
- Live order placement or external execution adapters.
- Tick, quote, or order-book simulation.
- ML, LLM, notification delivery, and provider production promotion.
