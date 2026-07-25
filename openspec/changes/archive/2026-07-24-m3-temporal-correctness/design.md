# Design — M3 temporal correctness

## Compatibility posture

M3 adds `osca.market-data.ohlcv-bar` and supporting temporal contracts beside the accepted M2 `osca.market-data.daily-bar` 1.0.0 contract. M2 imports, daily payloads, and daily publication behavior remain valid.

## Temporal model

All interval windows are UTC start-inclusive/end-exclusive. Completion is evaluated against the current UTC instant minus a declared publication lag, floored to the interval boundary.

Stock windows are generated from accepted exchange sessions. A missing stock observation is repair eligible only when the session evidence is accepted and the window has completed. Missing calendar evidence yields unresolved.

Crypto windows are generated from UTC day boundaries. Completed missing crypto windows are repair eligible.

## Resampling

Resampling groups contiguous lower-interval bars into a higher approved interval. It emits no output for partial coverage. Aggregation uses first open, max high, min low, last close, and summed volume. Each output has source-bar lineage.

## Persistence and publication

Dataset manifests and retrieval requests carry interval identity. Retrieval only selects satisfying ready canonical revisions for the requested interval. Storage inspection groups usage by interval. Accepted canonical manifests remain protected under the M2 retention posture, including intraday OHLCV manifests.

Non-daily OHLCV publication uses a dedicated interval-aware intent and publisher with governed Parquet encoding, staged manifest publication, interval-scoped object keys, idempotent fingerprint reuse, and interval mismatch rejection before ready publication.
