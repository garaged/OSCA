# P10 Runtime Provider Routing Specification

## Purpose

Introduce governed runtime routing across local imports, fixtures, and approved enrichment adapters with explicit policy-blocked and stale states.

## Phase

Production-capable version

## User-visible value

Users can request data or enrichment through one product surface and understand which source was used or blocked.

## Requirements

- REQ-0226-REQ-0232: OSCA must implement the P10 scope described by this specification before P10 is marked complete.
- REQ-0226-REQ-0232: P10 must preserve explicit non-scope boundaries and fail closed when a caller attempts deferred behavior.
- REQ-0226-REQ-0232: P10 completion requires updated requirements, traceability, milestone status, manual-testing review, OpenSpec evidence, automated validation, and hosted Quality evidence.

## Implementation scope

- Define routing policy and source precedence.
- Route local OHLCV, fixtures, SEC EDGAR, and FRED preview sources where enabled.
- Record source selection, stale data, partial results, and policy blocks.
- Add API/CLI inspection for routing decisions.

## Explicit non-scope

- Production promotion of paid providers, real-time streaming, trading orders.

## Acceptance criteria

- The milestone objective is demonstrable from supported CLI, API, UI, or documented operator workflow surfaces, as applicable.
- Automated tests cover new code paths and negative/deferred-boundary behavior.
- Documentation and traceability identify implemented, specified-only, fixture-backed, and deferred behavior.
- The milestone exit review records validation evidence and remaining deferrals.

## Dependencies

P6 and P9.

## Risks and decisions

Routing must not silently blend sources or bypass provider/legal gates.
