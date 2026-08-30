# D9 Architecture — Forward Paper Evaluation and Simulated Orders

## Context

D9 extends the accepted M8 paper-evaluation contracts and D8 virtual-portfolio accounting authority. It does not create a broker abstraction or a second balance store.

The authoritative chain is:

`approved/manual decision -> simulated-order draft -> user confirmation -> deterministic order lifecycle -> simulated fill -> D8 accounting event/journal -> forward analytics/comparison`

## Capability ownership

### Existing paper contracts

`src/osca/paper/contracts.py` remains the owner of paper-account, approved-candidate, health/control gate, schedule, checkpoint, recovery, and notification concepts.

### D9 order authority

D9 adds semantic capability modules under `src/osca/paper/`:

- `order_contracts.py` — immutable draft/confirmation/order/lifecycle/fill/assumption/risk evidence;
- `order_persistence.py` — profile-scoped append-only order/fill/checkpoint authority;
- `fill_engine.py` — deterministic bar-based eligibility, trigger, price, liquidity, fee, and latency rules;
- `forward_service.py` — orchestration across health/control gates, order lifecycle, checkpoints, D8 accounting, and comparison evidence.

Long-lived desktop methods use semantic modules such as `desktop_api/paper_evaluation.py`; D9 does not resume milestone-numbered service naming.

## Paper account to D8 portfolio binding

A paper account remains the control/schedule/evaluation identity established before D8. A D9 run explicitly binds that account to one D8 `VirtualPortfolio`.

The binding stores identity/lineage only. Cash, positions, lots, P&L, fees, and valuation remain authoritative in D8 accounting. D9 never mirrors those balances in a paper-order table.

## Order evidence model

### Draft

A draft is immutable/versioned proposal evidence. It contains:

- stable draft/version identity;
- paper run/account/portfolio identity;
- manual or approved-strategy source lineage;
- canonical instrument identity;
- buy/sell side;
- order type: market, limit, stop, or scheduled market;
- exact Decimal quantity and applicable trigger/limit price;
- activation/schedule/expiry information;
- optional D8 lot allocations for disposals;
- execution-assumption identity;
- creation provenance.

Editing a draft creates a new version rather than mutating confirmed evidence.

### Confirmation

A user confirmation freezes one draft version into active simulated-order authority. Confirmation is an OSCA-local event only; there is no route, destination, venue API, credential, or transport associated with it.

### Lifecycle

Lifecycle states are monotonic and append-only:

`confirmed -> pending -> active -> partially_filled -> filled`

with terminal alternatives:

`cancelled`, `expired`, `rejected`.

A partially filled order may later fill, expire, or be cancelled. Retained fills are never undone by cancellation of the remaining quantity.

## Point-in-time market evidence

D9 uses governed completed bars because tick/quote/order-book data is outside the initial product boundary.

Each fill evaluation receives explicit bar evidence with:

- dataset/revision/source identity;
- instrument and timeframe;
- bar start/end/availability time;
- OHLCV and completeness state;
- market-calendar identity where applicable.

An order has an `eligible_at` timestamp after confirmation, schedule, and configured latency are applied.

A bar is fill-eligible only when the order was already eligible at or before the bar start. If an order becomes eligible after a bar starts, D9 skips that bar because OHLCV cannot prove the post-activation intrabar path. Provisional/incomplete bars are never fill authority.

## Deterministic fill rules

### Market

A market order uses the next eligible completed bar's opening price as the unadjusted execution reference. Directional spread/slippage assumptions then move price adversely for the simulated order.

### Limit

A buy limit is trigger-eligible when the bar low is at or below the limit. A sell limit is trigger-eligible when the bar high is at or above the limit.

If the bar opens through the limit at a better price, the open is the reference. Otherwise the limit is the reference. Directional execution adjustments cannot violate the limit price; if configured assumptions would require a worse-than-limit price, the executable quantity for that bar is zero rather than fabricating an invalid fill.

### Stop

A buy stop is triggered when the bar high reaches/exceeds the stop. A sell stop is triggered when the bar low reaches/falls below the stop.

If the bar opens through the stop, the open is the reference to model a gap. Otherwise the stop is the reference. Directional spread/slippage is applied adversely and is not capped by the stop.

### Scheduled market

A scheduled market order is a market order whose eligibility starts at its explicit scheduled activation, adjusted by calendar/session and latency rules. It does not represent unattended real execution.

## Liquidity and partial fills

Each execution-assumption set declares a maximum participation fraction of bar volume and whether volume evidence is mandatory.

When volume is available, fill quantity is bounded by remaining order quantity and configured participation. Partial fills are append-only and may continue across later eligible bars.

If volume is required but missing/invalid, the fill is blocked/degraded. D9 never substitutes unlimited liquidity silently.

## Costs and precision

All authoritative quantities, prices, fees, spread/slippage inputs, and accounting values use Decimal-safe representations.

Execution assumptions retain:

- spread model/amount;
- slippage model/amount;
- fee model/amount;
- latency;
- volume-participation limit;
- freshness/calendar requirements.

The fill records the exact assumption revision used.

## Risk gates

Deterministic risk checks run before activation and again before each fill. The initial built-in gates are bounded and portfolio-derived, such as:

- positive/finite quantity and price constraints;
- sufficient available cash for simulated buys;
- sufficient held quantity and explicit lot allocation for ambiguous simulated sells;
- maximum simulated order notional;
- maximum position/exposure limit when configured;
- paper account pause/kill-switch state;
- healthy/non-stale market evidence.

A failure produces retained rejection/block evidence. No LLM/strategy output can bypass these gates.

## D8 accounting integration

Every accepted fill has a stable source identity and posts exactly once into the bound D8 portfolio.

- simulated buys post D8 acquisition evidence;
- simulated sells post D8 disposal evidence;
- fees are included in the accounting event;
- ambiguous multi-lot disposal requires the order to carry explicit lot allocation;
- duplicate fill posting is rejected/idempotently resolved by source identity.

D9 fills never update D8 projections directly.

## Checkpoint and recovery

Paper-run checkpoints retain the last processed market-evidence identity, lifecycle sequence, fill identities, and accounting-posting state.

Recovery reconstructs state from immutable evidence and resumes only after verifying:

- retained checkpoint consistency;
- no missing/conflicting lifecycle event;
- no fill that was accepted but not reconciled to D8 accounting;
- no duplicate source identity;
- current control/health gate permits processing.

Recovery blocks rather than guessing when reconciliation is ambiguous.

## Desktop boundary

Paper Lab calls typed Python methods through the existing sidecar/broker boundary. Rust owns profile mutation leasing; Python adds mutation locking and business validation.

Write methods include draft/version creation, confirmation, cancellation, step/evaluation, checkpoint/recovery, and accounting-posting actions. Read-only order/run/comparison inspection does not acquire write ownership.

## Safety boundary

D9 contains no:

- brokerage/exchange destination or adapter;
- brokerage/exchange credential type;
- live-order request/response model;
- socket/HTTP transport for order submission;
- recommendation-to-order shortcut;
- real-capital state;
- arbitrary user-code execution path.

The word `order` in D9 always means simulated research evidence.
