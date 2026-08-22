# D9 Requirements Catalog — Forward Paper Evaluation and Simulated Orders

- **Milestone:** D9
- **Status:** Draft for implementation
- **Baseline:** D8 merge `addfe119d895aee05751644929264ba9491926e8`
- **Authority:** `docs/product-requirements.md`, D-027, D-028, ADR-0046, and `docs/milestones/d9/intent.md`

| ID | Requirement | Verification |
|---|---|---|
| REQ-0394 | A forward paper run SHALL bind one existing paper account to one D8 virtual portfolio and retain optional approved-candidate/source-decision lineage without duplicating portfolio balances. | Contract + persistence tests |
| REQ-0395 | Simulated-order drafts SHALL be immutable/versioned evidence with stable identity, source kind, instrument, side, quantity, order type, activation/schedule data, assumptions, and lifecycle metadata. | Contract + persistence tests |
| REQ-0396 | No draft SHALL become active until an explicit user confirmation is retained. Confirmation SHALL create immutable simulated-order authority and SHALL NOT represent transmission to an external venue. | Confirmation/boundary tests + manual acceptance |
| REQ-0397 | D9 SHALL support simulated market, limit, stop, and scheduled market orders using Decimal-safe quantities/prices. Unsupported order semantics SHALL fail closed. | Contract + negative tests |
| REQ-0398 | Order activation and fill evaluation SHALL be point-in-time safe. A fill SHALL NOT consume market evidence from before the order became eligible, and ambiguous mid-bar activation SHALL skip that bar rather than infer intrabar sequence. | Temporal/property tests |
| REQ-0399 | The fill engine SHALL be deterministic and consume governed completed-bar evidence with explicit data revision/provenance. D9 SHALL NOT invent tick, quote, or order-book precision. | Golden/replay + provenance tests |
| REQ-0400 | Market, limit, and stop fills SHALL use documented deterministic bar rules, including gap behavior, directional spread/slippage, and price constraints appropriate to each order type. | Golden fill tests |
| REQ-0401 | Liquidity assumptions SHALL be explicit and bounded. When configured volume participation limits a fill, the engine SHALL produce deterministic partial fills; required but missing volume evidence SHALL degrade/block rather than assume unlimited liquidity. | Partial-fill + missing-volume tests |
| REQ-0402 | Spread, slippage, fees, latency, and liquidity assumptions SHALL be retained with each run/order/fill and SHALL be visible in desktop evidence. | Contract + UI tests |
| REQ-0403 | Session-aware instruments SHALL respect the governed market calendar/timezone; 24/7 crypto instruments SHALL remain continuously eligible subject to data availability. | Calendar/DST/crypto tests |
| REQ-0404 | Order lifecycle transitions and fill events SHALL be append-only, idempotent, monotonic, and replayable. Duplicate source/idempotency identities SHALL NOT create duplicate fills. | State-machine + retry tests |
| REQ-0405 | D9 SHALL support explicit cancellation, expiry, rejection, partial-fill, and terminal filled states. Cancellation after a partial fill SHALL preserve completed fills and cancel only the remaining quantity. | Lifecycle tests |
| REQ-0406 | Deterministic risk controls SHALL run before activation and before each fill. Violations SHALL fail closed with retained reason evidence and SHALL NOT be overridden by strategy/LLM output. | Risk-gate tests |
| REQ-0407 | Checkpoints and recovery SHALL resume from retained sequence/idempotency evidence without replaying already-posted fills or skipping accepted terminal events. | Crash/restart/recovery tests |
| REQ-0408 | Every accepted fill SHALL post exactly once into the bound D8 accounting portfolio with fill lineage. A disposal that is ambiguous across D8 lots SHALL require explicit lot allocation and SHALL block rather than invent FIFO/LIFO/tax policy. | Accounting integration + lot tests |
| REQ-0409 | Forward-evaluation valuation/mark evidence SHALL retain source/effective time/revision and SHALL surface stale/missing evidence explicitly. | Valuation/degraded-state tests |
| REQ-0410 | A paper run SHALL support deterministic step/replay from local/governed evidence without requiring paid providers, broker credentials, or network access. | Offline fixture + manual acceptance |
| REQ-0411 | Backtest-to-forward comparisons SHALL retain common evidence windows, assumptions, and provenance and SHALL remain descriptive rather than recommendations. | Comparison tests + UI boundary tests |
| REQ-0412 | The desktop SHALL expose a first-class Paper Lab for draft, confirmation, lifecycle, fills, assumptions, checkpoints, accounting effects, and comparisons through Python authority. | Desktop API + frontend tests |
| REQ-0413 | All paper mutations SHALL be profile scoped and protected by existing Rust ownership plus Python mutation locking; read-only inspection SHALL not acquire write authority. | Broker/API ownership tests |
| REQ-0414 | D9 SHALL contain no broker/exchange destination, credential, live-order API, real-capital action, autonomous live execution, recommendation-to-order shortcut, or arbitrary user-code execution path. | Source/boundary + manual safety tests |

## Fill-model interpretation

D9 operates on governed bar evidence because D-013 explicitly keeps tick/quote/order-book data outside the initial boundary. An order that becomes eligible after a bar has started cannot safely infer what happened after activation from only OHLCV, so that bar is not eligible for filling. This favors temporal correctness over optimistic fill frequency.

A scheduled order is a market order whose activation is deferred to an explicit timestamp/calendar condition; it does not create a background live-order destination.
