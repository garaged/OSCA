# D8 Architecture — Virtual-Portfolio Accounting Foundation

## Authority

D8 follows PRD §23, D-028, and ADR-0046. Python remains the only authoritative owner of accounting semantics. React presents typed results; Rust supervises the sidecar and profile ownership but does not calculate balances, fills, valuations, or P&L.

## Capability ownership

D8 extends `osca.paper` because the existing paper-account identity and F3 controls already own simulated-account concepts. It adds a dedicated accounting sub-capability instead of changing `SQLitePaperEvaluationStore` into an immutable journal. The existing M8 store intentionally supports upsert-style operational records; journal authority requires stricter append-only semantics.

The accounting capability is split into:

1. immutable accounting contracts and event vocabulary;
2. event-to-journal posting rules;
3. append-only SQLite persistence;
4. deterministic replay/projection services;
5. valuation evidence and analytical projections;
6. a semantic desktop adapter, `portfolio_accounting.py` / `PortfolioAccountingDesktopService`.

## Accounting invariants

- Monetary and quantity arithmetic uses `Decimal` at the Python authority boundary.
- Every journal transaction balances independently by currency.
- Journal transaction identity and source-event identity are unique and immutable.
- Duplicate submission with identical canonical content is idempotent; identity reuse with different content fails closed.
- Corrections append reversal/replacement evidence. No journal UPDATE/DELETE path is exposed.
- Cash, lots, positions, book cost, realized P&L, fees, and income are replay projections, not mutable sources of truth.
- Multi-lot disposal is explicit rather than silently selecting FIFO/LIFO/average-cost tax policy.
- Corporate actions carry stable source identity so replay cannot apply them twice.
- Valuation records preserve price and FX provenance; missing evidence degrades the projection instead of fabricating a value.

## Persistence

D8 uses a profile-scoped SQLite accounting database beneath the configured profile storage. Tables are append-only for accounting events, journal transactions/postings, and valuation evidence. Portfolio metadata may have lifecycle status changes recorded as immutable lifecycle events; projections are regenerable caches only.

Schema initialization is idempotent. Existing `paper_records` from M8 are not rewritten. Restore validates a portable bundle before any mutation and uses a transaction so failure leaves the profile unchanged.

## Clone and reset semantics

Clone and reset must preserve audit history. Clone creates a new account identity with source lineage and an opening-state event derived from a specific source revision. Reset creates a successor account with explicit `reset_of` lineage; it never deletes or truncates the source journal.

## Desktop boundary and naming follow-up

`src/osca/desktop_api` currently contains both capability-semantic modules and milestone-labelled `d3_*` through `d7_service.py` modules. Those names form an inheritance compatibility ladder and a broad rename would touch mature D3-D7 behavior. D8 therefore freezes them as transitional compatibility names and stops the pattern: the D8 adapter uses the semantic `PortfolioAccountingDesktopService` name and no `d8_service.py` is introduced. A later focused refactor can flatten the old inheritance ladder with dedicated regression coverage.

## Safety boundaries

D8 has no brokerage/exchange connection, live-order route, recommendation generation, autonomous execution, real-capital operation, or arbitrary user-code execution. Manual accounting events are simulated research evidence only. Network access is unnecessary for the local/synthetic acceptance path.
