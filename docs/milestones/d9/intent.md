# D9 Intent — Forward Paper Evaluation and Simulated Orders

## Outcome
Users can evaluate strategies and decisions forward in time using explicitly simulated market, limit, stop, and scheduled orders without any live-order path.

## Scope
Simulated-order drafts and confirmations, lifecycle states, deterministic fill engine, spread/slippage/fees/latency/liquidity assumptions, market calendars, checkpoints, recovery, cancellation, risk controls, and portfolio posting.

## Non-goals
Broker or exchange credentials, destinations, adapters, real-capital orders, or unattended real execution.

## Dependencies
D8 accounting foundation and accepted paper-evaluation contracts.

## Risks
Simulation appearing live, stale prices, duplicate fills after restart, unrealistic liquidity, and recommendation-to-order boundary confusion.

## Exit intent
All actions are visibly simulated; replay and restart are deterministic; fills post balanced journal entries; drafts require user confirmation; tests prove no network or application path can submit a live order.
