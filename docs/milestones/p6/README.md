# P6 - No-Cost Local OHLCV Import Provider

- **Status:** Planned
- **Governing role:** Product authority
- **Phase:** Minimum usable local/demo tool
- **Authoritative outcome:** Add a governed local file import path for OHLCV history so OSCA can analyze real user-supplied data without paid providers.
- **Baseline:** Completed M0-M12 roadmap and P1-P4 provider governance
- **Last reviewed:** 2026-07-26
- **Validation:** Planned

## Current artifacts

- [Milestone plan](README.md)
- [Specification](../../specifications/p6-local-ohlcv-import-provider.md)
- [Accepted OpenSpec specification](../../../openspec/specs/p6-local-ohlcv-import-provider/spec.md)

## Objective

Add a governed local file import path for OHLCV history so OSCA can analyze real user-supplied data without paid providers.

## User-visible value

Users can run OSCA locally with their own CSV or Parquet market data and no provider spend.

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

- REQ-0198-REQ-0204 are allocated before implementation begins.
- The implementation proves the stated scope with automated tests where code changes are made.
- Manual testing and usage is updated when operator-visible behavior changes.
- Deferred provider, credential, production-ingestion, and real-capital boundaries remain visible and fail closed unless this milestone explicitly owns them.
- Hosted Quality passes before completion is marked.

## Validation gates

- Ruff, mypy, pytest, architecture validation, OpenSpec validation, and secret scanning.
- Documentation, traceability, and manual-testing review.
- Exit review recording final evidence.

## Dependencies

P5 reconciliation, M2 storage model, M3 temporal correctness.

## Risks and decisions

CSV schemas vary; P6 must choose one canonical format and reject ambiguous files.
