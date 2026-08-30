# D9 Specification — Forward Paper Evaluation and Simulated Orders

## 1. Purpose

D9 turns accepted strategy/manual decisions into forward simulated-order evidence and deterministic fills that post into D8 virtual-portfolio accounting. The milestone is a research simulator, not a broker client.

## 2. Run binding

A forward paper run binds:

- one existing paper account;
- one D8 virtual portfolio;
- zero or one approved paper candidate for strategy-driven runs;
- one execution-assumption revision;
- governed market-data requirements;
- health/control/checkpoint/recovery state.

The paper account owns controls and scheduling. The D8 portfolio owns balances and accounting.

## 3. Simulated-order draft

A draft/version records stable identity, paper run/account/portfolio, source lineage, canonical instrument, side, exact quantity, order type, required prices, activation/schedule/expiry, assumptions, and optional disposal lot allocation.

Draft edits create a new version. A confirmed version cannot be rewritten.

### Order types

- `market`: no limit/stop price;
- `limit`: exactly one limit price;
- `stop`: exactly one stop price;
- `scheduled_market`: explicit scheduled activation and no limit/stop price.

Invalid combinations fail validation.

## 4. Confirmation

A user must explicitly confirm a specific immutable draft version. Confirmation retains who/what was confirmed, timestamp, assumptions, and a clear `simulated_only` safety marker.

Confirmation creates no external request and has no venue/destination field.

## 5. Lifecycle

Accepted transitions are append-only and monotonic. Initial lifecycle:

- confirmed;
- pending;
- active;
- partially filled;
- filled;
- cancelled;
- expired;
- rejected.

Terminal orders cannot reactivate. Duplicate idempotency/source identities return/reconcile retained evidence rather than duplicate state.

## 6. Market evidence eligibility

Only governed complete bars may produce fills.

A bar is eligible when:

1. its instrument/timeframe match the run/order requirement;
2. its governed dataset/revision is allowed by the run;
3. it is complete and not blocked by freshness/quality policy;
4. the order's `eligible_at` is at or before the bar start;
5. calendar/session policy permits activity at the bar.

An order that becomes eligible during a bar skips that bar. D9 does not infer post-activation intrabar path from OHLCV.

## 7. Fill rules

### 7.1 Market

The next eligible bar open is the unadjusted reference. Directional spread/slippage moves the execution price adversely.

### 7.2 Limit

Buy: bar low <= limit. Sell: bar high >= limit.

When the eligible bar opens at a price better than the limit, the open is the reference; otherwise the limit is the reference. Final simulated price may never violate the limit. If configured adverse adjustments cannot fit inside the limit constraint, no fill occurs on that bar.

### 7.3 Stop

Buy: bar high >= stop. Sell: bar low <= stop.

If the eligible bar opens through the stop, open is the reference; otherwise stop is the reference. Directional spread/slippage may produce a worse price than the stop to represent gap/slippage risk.

### 7.4 Scheduled market

Scheduled market behaves as market after its scheduled timestamp becomes eligible under calendar and latency policy.

## 8. Liquidity and partial fills

The assumption revision includes maximum bar-volume participation and a flag indicating whether valid volume is required.

Fill quantity is bounded by remaining order quantity and permitted bar participation. Multiple partial fills may occur across bars. Missing required volume blocks filling; unlimited liquidity is never silently assumed.

## 9. Fees, spread, slippage, latency

All assumptions are explicit, Decimal-safe, versioned, and retained with fills. Initial models remain transparent and bounded; unsupported/custom executable formulas are outside D9.

Latency shifts `eligible_at`. If latency places eligibility after a bar start, that bar is skipped.

## 10. Calendar behavior

Session-based instruments use the governed market calendar/timezone. Crypto instruments may use an explicit 24/7 calendar policy. Closed-session bars cannot activate/fill session-bound orders.

## 11. Risk controls

Before activation and each fill, deterministic controls evaluate current D8 portfolio state and paper-control state. Built-in checks include valid quantity/price, cash/holding sufficiency, explicit lots for ambiguous sells, configured order-notional/exposure limits, pause/kill switch, and data health.

Blocked/rejected decisions retain reason evidence and do not mutate accounting.

## 12. Accounting posting

Each accepted fill posts exactly once using a stable fill source identity:

- buy -> D8 acquisition;
- sell -> D8 disposal with explicit lot allocations when required;
- execution fee -> same D8 economic event.

D8 journal/projection remains the accounting source of truth. D9 never writes mutable balance snapshots.

## 13. Cancellation and expiry

Cancellation affects only unfilled remaining quantity. Completed partial fills remain retained/accounted. Expiry is deterministic from explicit order/run policy and market calendar.

## 14. Checkpoint and recovery

Each forward-processing step can retain a checkpoint containing source market evidence, sequence, accepted lifecycle/fill identities, and accounting reconciliation state.

Recovery must prove that retained fills and D8 postings agree before resuming. Conflicts block with user-visible remediation; recovery never duplicates a fill to "catch up".

## 15. Comparison evidence

Forward results may be compared with linked backtest/event-driven evidence using aligned ranges/assumptions where possible. Differences are descriptive findings with provenance, never recommendations.

## 16. Desktop Paper Lab

Paper Lab SHALL provide:

- paper account/portfolio/run selection;
- order draft/version creation;
- prominent simulated-only confirmation;
- lifecycle and cancellation controls;
- assumptions and data provenance;
- fill/event timeline;
- D8 accounting effect links;
- checkpoint/recovery state;
- forward-vs-backtest descriptive comparison;
- explicit safety/no-live-destination disclosure.

The UI uses typed Python authority. No direct provider/broker transport exists in React or Rust.

## 17. Offline/no-cost path

D9 must be fully exercisable with retained/local/synthetic governed bar evidence and a D8 portfolio. No paid provider, network connection, broker account, or exchange credential is required.

## 18. Safety invariants

The D9 implementation must prove through source/boundary tests that it does not expose a brokerage destination, external order submission path, real-capital state, autonomous live execution, recommendation-to-order shortcut, or arbitrary user-code execution.
