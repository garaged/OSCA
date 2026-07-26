# P11 Useful Analyst Workspace Specification

## Purpose

Add a focused analyst workspace for projects, datasets, reports, backtests, and enrichment evidence.

## Phase

Useful analyst workflow

## User-visible value

Users can browse and inspect OSCA output without reading raw metadata tables.

## Requirements

- REQ-0233-REQ-0239: OSCA must implement the P11 scope described by this specification before P11 is marked complete.
- REQ-0233-REQ-0239: P11 must preserve explicit non-scope boundaries and fail closed when a caller attempts deferred behavior.
- REQ-0233-REQ-0239: P11 completion requires updated requirements, traceability, milestone status, manual-testing review, OpenSpec evidence, automated validation, and hosted Quality evidence.

## Implementation scope

- Add a minimal local web/API-backed workspace or equivalent product UI.
- Show projects, watchlists, imported datasets, data quality, reports, backtests, and enrichment evidence.
- Add empty/error/loading states and manual smoke tests.

## Explicit non-scope

- Full BI platform, multi-user SaaS, extension marketplace UI.

## Acceptance criteria

- The milestone objective is demonstrable from supported CLI, API, UI, or documented operator workflow surfaces, as applicable.
- Automated tests cover new code paths and negative/deferred-boundary behavior.
- Documentation and traceability identify implemented, specified-only, fixture-backed, and deferred behavior.
- The milestone exit review records validation evidence and remaining deferrals.

## Dependencies

P7-P10.

## Risks and decisions

UI scope can sprawl; P11 must stay read-mostly and evidence-oriented.
