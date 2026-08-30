# D9 Proposal — Forward Paper Evaluation and Simulated Orders

## Why

D8 provides auditable virtual-portfolio accounting but does not yet evaluate decisions forward through realistic order lifecycle and fill behavior. D9 is the bridge from historical backtest evidence to deterministic paper trading while preserving the no-live-execution boundary.

## What changes

- bind paper runs to D8 virtual portfolios without duplicating balances;
- add immutable/versioned simulated-order drafts and explicit user confirmations;
- support simulated market, limit, stop, and scheduled market orders;
- add deterministic completed-bar fill semantics with conservative point-in-time rules;
- retain spread, slippage, fees, latency, liquidity, calendar, and data provenance;
- support partial fills, cancellation, expiry, rejection, risk gates, checkpoints, and recovery;
- post accepted fills exactly once into D8 accounting;
- add descriptive backtest-to-forward comparison evidence;
- add a semantic desktop Paper Lab and profile ownership enforcement;
- preserve local/synthetic/no-cost workflows and prove no broker/live-order/real-capital path exists.

## Non-goals

Broker/exchange credentials, destinations or adapters, real-capital orders, unattended live execution, tick/order-book simulation, arbitrary executable order models, implicit tax-lot policy, or recommendation-to-order shortcuts.
