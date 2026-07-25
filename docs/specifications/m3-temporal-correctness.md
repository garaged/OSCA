# Specification — M3 Temporal Correctness

- **Status:** Accepted
- **Governing role:** Architecture authority
- **Approval roles:** Product, data, quality, and licensing authorities
- **Governing intent:** [M3 intent](../milestones/m3/intent.md)
- **Requirements:** REQ-0041-REQ-0052
- **Related decisions:** D-004, D-012-D-018, D-040; ADR-0001-ADR-0029
- **Risk class:** Governed high-risk data-integrity and temporal-semantics change
- **Last reviewed:** 2026-07-24

## Public contract candidates

- `osca.market-data.interval` 1.0.0;
- `osca.market-data.exchange-session` 1.0.0;
- `osca.market-data.crypto-utc-day` 1.0.0;
- `osca.market-data.ohlcv-bar` 1.0.0;
- `osca.market-data.temporal-gap` 1.0.0;
- `osca.market-data.resample-lineage` 1.0.0.

## Behavioral specification

Approved intervals are exactly `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, and `1d`. Unknown intervals fail validation.

Every bar has an explicit UTC start and end. Windows are start-inclusive and end-exclusive. A completed-bar cutoff is computed from current UTC time minus declared publication lag, floored to the interval boundary.

Stock expected windows come from accepted exchange-session records. Closed and holiday sessions produce no expected windows. Early-close sessions produce only windows fully contained by the shortened session. Missing stock bars are repair eligible only when their expected session window is accepted and complete. Unknown session evidence remains unresolved.

Crypto expected windows are generated from UTC day boundaries. Completed missing crypto windows are repair eligible after the interval close has passed.

Resampling from lower to higher intervals requires contiguous complete source windows with one instrument, provider, currency, volume unit, and calendar revision. It aggregates OHLCV using first open, maximum high, minimum low, last close, and summed volume. Each output bar records source-bar lineage.

M2 daily contracts remain supported. M3 adds interval-aware contracts rather than changing the meaning of `osca.market-data.daily-bar` 1.0.0.
