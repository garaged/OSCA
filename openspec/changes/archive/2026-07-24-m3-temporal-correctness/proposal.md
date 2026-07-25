# Proposal — M3 temporal correctness

## Why

M2 intentionally stopped at governed daily market data and used conservative date logic. M3 adds intraday intervals, explicit stock session evidence, crypto UTC boundaries, completed-bar semantics, deterministic resampling, and interval-aware dataset behavior without weakening accepted M2 contracts.

## What changed

- Added interval-aware temporal contracts for the approved intervals.
- Added exchange-session and crypto UTC boundary models.
- Added completed-bar cutoff behavior with publication lag.
- Added calendar/session-aware gap classification and repair-window selection.
- Added deterministic lower-to-higher interval resampling with lineage.
- Added interval identity to retrieval requests, manifests, storage inspection, and revision selection.
- Added governed OHLCV Parquet payload support.
- Added interval-aware OHLCV publication with protected canonical manifests.
- Preserved M2 daily-bar compatibility and kept provider production promotion deferred.

## Impact

Market Data now has the temporal correctness foundation needed for multi-timeframe analysis. Daily and intraday canonical datasets are separated by interval identity, current bars are not published as complete, and resampled bars retain reproducible source lineage.
