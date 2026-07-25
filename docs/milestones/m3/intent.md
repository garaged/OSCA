# M3 Intent — Multi-Timeframe Market Data and Temporal Correctness

- **Status:** Accepted
- **Governing role:** Product authority
- **Architecture, data, quality, and licensing approval:** Accepted for M3 implementation entry
- **Purpose:** Extend governed market data from daily-only semantics to interval-aware, session-aware, and resampling-safe behavior.
- **Authoritative sources:** PRD sections 8, 10-14, 37-39; D-004, D-012-D-018, D-040
- **Baseline:** Completed M2 governed daily market data
- **Review trigger:** interval set, calendar source, completed-bar semantics, canonical contract compatibility, retention, licensing, or provider-production change
- **Last reviewed:** 2026-07-24

## Intent statement

Enable a local owner to request, normalize, inspect, repair, and derive market-data bars across the approved intervals `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, and `1d` with explicit stock exchange-session evidence, crypto UTC boundaries, completed-bar semantics, calendar-aware gap detection, and deterministic resampling lineage.

## User outcome

A user can distinguish missing completed bars from incomplete future bars and unresolved stock sessions, repair only confirmed gaps, understand the freshness of interval-specific datasets, and know exactly which lower-interval observations produced a resampled higher-interval bar.

## In scope

- interval contract primitives for `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, and `1d`;
- start-inclusive/end-exclusive UTC bar windows;
- stock exchange-session model with open, close, closed, holiday, and early-close states;
- crypto UTC-day model;
- completed-bar cutoff semantics with publication lag;
- calendar/session-aware missing, unresolved, non-expected, observed, and incomplete classification;
- resampling from lower to higher approved intervals with exact lineage;
- interval-aware tests, documentation, ADR, OpenSpec, traceability, and evidence.

## Non-goals

- production promotion for paid/authenticated provider access;
- corporate actions, adjusted bars, halt microstructure, market-depth/order-book data, tick data, cross-provider reconciliation, distributed scheduling, UI visualization, or live trading;
- claiming full exchange-calendar coverage beyond accepted session evidence and fixtures.
