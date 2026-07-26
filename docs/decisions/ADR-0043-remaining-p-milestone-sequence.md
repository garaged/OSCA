# ADR-0043: Remaining P Milestone Sequence and P5 Reconciliation Gate

- **Status:** Accepted
- **Date:** 2026-07-26
- **Decision makers:** Product authority, architecture authority
- **Related milestones:** P5-P17

## Context

M0-M12 established OSCA's governed foundation. P1-P4 added provider production evidence gates, no-cost provider discovery, no-cost provider profile selection, and fixture-backed adapter contracts for SEC EDGAR and FRED.

The project now needs a clear post-P4 sequence that reaches a usable local/demo tool without prematurely enabling live provider calls, credentials, production ingestion, or real-capital execution.

## Decision

OSCA will follow the P5-P17 sequence documented in docs/milestones/remaining-p-roadmap.md.

P5 is the required next implementation milestone. P5 must review M0-M12 and P1-P4 for documentation drift, implementation drift, stale status, incomplete traceability, and unclear deferred boundaries. P5 must fix drift that could mislead implementation before P6 starts.

The fastest responsible path to usability is:

1. P5 state reconciliation and operator surface.
2. P6 no-cost local OHLCV import provider.
3. P7 first demo research workflow.

## Consequences

- Later implementation work starts from a reconciled authority chain.
- OSCA can become useful locally without requiring paid data providers.
- Live provider and real-money work remain explicitly governed by later milestones and decision gates.
