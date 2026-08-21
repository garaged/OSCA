# D8 Requirements Catalog — Virtual-Portfolio Accounting Foundation

- **Milestone:** D8
- **Status:** Draft for implementation
- **Baseline:** D7 merge `95d2d6ad6a3a7d530ceae4f2c6cd76527f263559`
- **Authority:** `docs/product-requirements.md` §23, D-028, ADR-0046, and `docs/milestones/d8/intent.md`

| ID | Requirement | Verification |
|---|---|---|
| REQ-0375 | A profile SHALL support multiple independent virtual portfolios with stable identity, name, base currency, lifecycle state, creation time, and optional lineage to a source portfolio. | Contract + persistence tests |
| REQ-0376 | Creating a virtual portfolio SHALL retain starting cash as an immutable economic event rather than mutable balance state. | Unit + replay tests |
| REQ-0377 | Every economic event SHALL produce a balanced append-only double-entry journal transaction with immutable source lineage. | Property + persistence tests |
| REQ-0378 | Journal corrections SHALL be represented by explicit reversal and replacement events; persisted journal rows SHALL NOT be updated or deleted in normal operation. | Mutation/reversal tests |
| REQ-0379 | Accounting quantities and monetary amounts SHALL use decimal-safe representations; authoritative accounting SHALL NOT depend on binary floating-point accumulation. | Contract + precision tests |
| REQ-0380 | Cash, positions, lots, book cost, realized P&L, income, fees, and journal balances SHALL be deterministically rebuildable from retained events and journal entries. | Deterministic replay tests |
| REQ-0381 | A disposal spanning more than one open lot SHALL require explicit lot allocation unless a single unambiguous lot exists; D8 SHALL NOT silently impose a tax-accounting disposal policy. | Lot-allocation tests |
| REQ-0382 | Splits, dividends/distributions, and crypto forks SHALL be idempotent economic events with source identity and replay-safe effects. | Corporate-action tests |
| REQ-0383 | Multi-currency holdings and valuations SHALL retain price source, price effective time, FX rate, FX source, FX effective time, and valuation revision. | Valuation contract tests |
| REQ-0384 | Unrealized P&L, gross/net exposure, allocation, equity, and drawdown SHALL be derived projections and SHALL identify missing/stale valuation evidence rather than inventing prices. | Projection tests |
| REQ-0385 | Portfolio performance and benchmark comparisons SHALL be analytical evidence with explicit time range and provenance; they SHALL NOT be investment recommendations. | Service + UI tests |
| REQ-0386 | Clone SHALL create an independent portfolio with explicit source lineage and copied opening state evidence; reset SHALL preserve the original journal and create a successor/reset lineage rather than destructively erasing history. | Lifecycle tests |
| REQ-0387 | Portfolio export SHALL include account metadata, immutable events, journal transactions, valuation evidence, and a deterministic digest sufficient for audit/replay. | Export/replay tests |
| REQ-0388 | Restore/import SHALL validate schema, digest, identities, balanced journals, and compatibility before mutating a profile; failed validation SHALL leave existing portfolio data unchanged. | Restore failure tests |
| REQ-0389 | The desktop portfolio surface SHALL expose portfolio creation/listing, journal-backed balances, positions/lots, P&L/income/exposure, valuation provenance, and explicit research-only boundaries through the Python authority path. | Desktop API + frontend tests |
| REQ-0390 | D8 SHALL remain usable with local/synthetic data and no paid account, SHALL make no network call by default, and SHALL expose no broker, real-capital, recommendation, or arbitrary-code path. | Boundary + manual acceptance |
| REQ-0391 | D8 persistence SHALL be profile scoped and use existing profile mutation ownership/locking for every accounting write. | Broker/API ownership tests |
| REQ-0392 | D8 migrations or schema initialization SHALL be idempotent and recoverable; existing M8 paper-evaluation records SHALL remain readable and behaviorally compatible. | Migration + regression tests |
| REQ-0393 | Long-lived D8 desktop modules SHALL use capability-semantic names. Existing `d3_*` through `d7_service.py` names SHALL be treated as transitional compatibility names and SHALL NOT be extended with a new `d8_service.py`. | Architecture/source review |

## Interpretation note: book cost and lots

D8 needs deterministic realized/unrealized accounting without inventing a tax policy. Acquisitions therefore retain explicit lots and book cost. A disposal may consume the only open lot automatically; when multiple lots could satisfy it, the authoritative request must provide lot allocations. Later milestones may add governed convenience policies, but they must not rewrite D8 history.
