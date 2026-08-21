# D8 Specification — Virtual-Portfolio Accounting Foundation

## 1. Outcome

Deliver a usable virtual-portfolio accounting foundation after D7 so a user can create independent simulated portfolios, record research-only economic events, and inspect auditable balances, positions, lots, P&L, income, exposure, performance, and valuation provenance.

## 2. Portfolio model

A portfolio has stable UUID identity, name, ISO-style three-character base currency, lifecycle state, creation time, optional source lineage, and an immutable event sequence. Starting cash is posted as the first economic event.

Multiple portfolios coexist inside a profile. Closing a portfolio prevents new economic events but preserves reads, export, and replay.

## 3. Economic events

D8 supports a bounded declarative event vocabulary:

- funding/deposit and withdrawal;
- simulated acquisition and disposal;
- fee/expense;
- dividend/distribution;
- split;
- crypto fork/distribution;
- FX cash conversion;
- manual accounting adjustment with explicit rationale;
- reversal/replacement correction;
- lifecycle/clone/reset lineage events.

These are accounting evidence, not executable orders. D9 remains responsible for simulated order lifecycle and forward paper execution.

Every event carries stable identity, portfolio identity, effective time, recorded time, event type, source kind/source ID, and canonical payload digest.

## 4. Double-entry journal

Accepted economic events map to one or more immutable journal transactions. Each transaction has at least two postings and balances by currency. Postings use explicit account codes such as cash, investment book value, realized P&L, income, fee expense, and equity/funding.

Persistence permits INSERT only for journal authority. Reusing an identity with byte-equivalent canonical content returns the existing record; reusing it with different content raises a conflict. Corrections append a reversing transaction and replacement transaction linked to the original.

## 5. Lots and cost basis

Acquisitions create retained lots with quantity and book cost. Disposals consume explicit lot allocations. If exactly one open lot can satisfy a disposal, the service may infer that allocation; otherwise the request must specify it. This gives deterministic book accounting without silently selecting a tax policy.

Realized P&L is disposal proceeds minus allocated book cost minus directly attributed fees. Unrealized P&L requires valuation evidence and remains unavailable/degraded when required prices or FX are missing.

## 6. Corporate actions

Splits proportionally change lot quantities while preserving aggregate book cost. Cash dividends/distributions post income and cash. Crypto forks/distributions create an explicitly sourced new holding/lot under the supplied book-value allocation. Corporate-action source identity is unique per portfolio so retries cannot duplicate effects.

## 7. Multi-currency and valuation

Each portfolio has one base currency and may hold other currencies/assets. A valuation observation identifies instrument, quantity, price, price currency, price source, price effective time, FX rate to base, FX source/effective time when needed, and valuation revision.

Derived valuation output reports equity, cash by currency, positions, book cost, realized/unrealized P&L, income, fees, gross/net exposure, allocation, and drawdown where sufficient evidence exists. Missing or stale evidence is surfaced explicitly.

## 8. Performance, benchmark, scenario

Performance series are derived from replay plus valuation observations and disclose their evidence window. Benchmark comparison requires governed/local series identity and is descriptive only. Scenario inputs are explicit hypothetical price/FX shocks applied to a projection copy; scenarios never append journal events or mutate portfolio authority.

## 9. Clone, reset, export, restore

Clone creates a new portfolio from a source revision with lineage and opening evidence. Reset creates a fresh successor portfolio linked to the source; it does not erase the source.

Portable export contains metadata, events, journal transactions/postings, valuation observations, schema version, and content digest. Restore validates the whole bundle before a transactional write and rejects incompatible/unbalanced/conflicting evidence.

## 10. Desktop API

The semantic `PortfolioAccountingDesktopService` extends the current D7 service and adds allow-listed methods for portfolio create/list/get, event append, valuation append, projection, journal inspection, clone/reset, and export/restore preparation. All writes require profile ownership through the existing lock/broker policy.

The desktop UI adds a Portfolio Lab with account creation, portfolio selection, starting-cash workflow, journal/evidence inspection, position/lot table, P&L and exposure summaries, valuation provenance, and persistent safety disclosure.

## 11. Compatibility and naming

Existing M8 `PaperAccount` and `SQLitePaperEvaluationStore` contracts remain compatible. D8 does not retrofit append-only journal semantics onto the operational upsert store. Existing D3-D7 milestone-labelled desktop service modules remain transitional compatibility names; D8 does not add another milestone-labelled service module.

## 12. Validation

Required automated coverage includes balance identities, decimal precision, deterministic replay, duplicate/idempotency conflicts, correction reversal, explicit multi-lot disposal, split/dividend/fork idempotency, multi-currency valuation provenance, degraded valuation, clone/reset history preservation, export/restore round trip and fail-closed restore, profile isolation, desktop protocol boundaries, and no-live-execution invariants.

Manual acceptance uses a clean profile and local/synthetic evidence only. Hosted Quality/Desktop/Python/frontend/Rust/Linux packaging remain the final CI gate.
