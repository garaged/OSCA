# Proposal — M3 temporal correctness

## Why

M2 intentionally stopped at governed daily market data and used conservative date logic. M3 must add intraday intervals, explicit stock session evidence, crypto UTC boundaries, completed-bar semantics, and deterministic resampling without weakening accepted M2 contracts.

## What changes

- Add interval-aware temporal contracts for the approved intervals.
- Add exchange-session and crypto UTC boundary models.
- Add completed-bar cutoff behavior with publication lag.
- Add calendar/session-aware gap classification.
- Add deterministic lower-to-higher interval resampling with lineage.
- Preserve M2 daily-bar compatibility and keep provider production promotion deferred.

## Impact

Market Data gains temporal correctness primitives used by retrieval, repair, freshness, retention, and canonical revision policy in later M3 slices. The first slice is additive and does not change M2 persisted daily semantics.
