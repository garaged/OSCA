# P6 - No-Cost Local OHLCV Import Provider

- **Status:** Implementation candidate
- **Governing role:** Product authority
- **Phase:** Minimum usable local/demo tool
- **Authoritative outcome:** Add a governed local file import path for OHLCV history so OSCA can analyze real user-supplied data without paid providers.
- **Baseline:** Completed M0-M12 roadmap and P1-P4 provider governance
- **Last reviewed:** 2026-07-26
- **Validation:** Pending hosted Quality

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
- Provide sample fixtures, a shared application API, and a CLI import command.

## Explicit non-scope

- Network provider ingestion.
- SEC/FRED enrichment execution.
- Paid provider promotion.
- Trading execution.

## Acceptance criteria

- REQ-0198-REQ-0204 are allocated before implementation begins.
- The implementation proves the stated scope with automated tests for CSV import, metadata/payload persistence, validation failures, CLI output, and deferred-boundary visibility.
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

## Implementation candidate

P6 adds the `osca.local_data_import` package and `osca local-ohlcv-import` CLI command.

The canonical import schema is strict:

| Column | Meaning |
|---|---|
| `timestamp` | ISO-8601 timestamp with timezone. Values are normalized to UTC. |
| `open` | Positive opening price. |
| `high` | Positive high price, greater than or equal to open, low, and close. |
| `low` | Positive low price, less than or equal to open, high, and close. |
| `close` | Positive closing price. |
| `volume` | Non-negative volume. |

Accepted imports write:

- Parquet payloads under `<storage-root>/payloads/<dataset-revision-id>.parquet`.
- SQLite metadata under `<storage-root>/osca-local-data.sqlite`.
- Source checksum, lineage, symbol, timeframe, timestamp range, row count, calendar assumption, and quality findings.

P6 remains local-only. Live provider calls, credential materialization, runtime provider routing, production ingestion, and real-capital orders remain disabled.
