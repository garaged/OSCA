# P6 No-Cost Local OHLCV Import Provider Specification

## Purpose

Add a governed local file import path for OHLCV history so OSCA can analyze real user-supplied data without paid providers.

## Phase

Minimum usable local/demo tool

## User-visible value

Users can run OSCA locally with their own CSV or Parquet market data and no provider spend.

## Requirements

- REQ-0198-REQ-0204: OSCA must implement the P6 scope described by this specification before P6 is marked complete.
- REQ-0198-REQ-0204: P6 must preserve explicit non-scope boundaries and fail closed when a caller attempts deferred behavior.
- REQ-0198-REQ-0204: P6 completion requires updated requirements, traceability, milestone status, manual-testing review, OpenSpec evidence, automated validation, and hosted Quality evidence.

## Implementation scope

- Define canonical OHLCV import schema and validation errors.
- Import CSV and Parquet into the existing SQLite metadata plus Parquet payload storage model.
- Record lineage, dataset revision identity, symbol, timeframe, calendar assumptions, and data-quality findings.
- Provide sample fixtures and CLI/API import commands.

## Explicit non-scope

- Network provider ingestion.
- SEC/FRED enrichment execution.
- Paid provider promotion.
- Trading execution.

## Acceptance criteria

- The milestone objective is demonstrable from supported CLI, API, UI, or documented operator workflow surfaces, as applicable.
- Automated tests cover new code paths and negative/deferred-boundary behavior.
- Documentation and traceability identify implemented, specified-only, fixture-backed, and deferred behavior.
- The milestone exit review records validation evidence and remaining deferrals.

## Dependencies

P5 reconciliation, M2 storage model, M3 temporal correctness.

## Risks and decisions

CSV schemas vary; P6 must choose one canonical format and reject ambiguous files.
