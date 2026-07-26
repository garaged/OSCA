# P6 Exit Review

- **Status:** Implementation candidate
- **Scope reviewed:** Governed local CSV/Parquet OHLCV import, strict validation, metadata and payload persistence, operator CLI, documentation, and deferred boundaries
- **Decision:** Pending hosted Quality and PR review

## Implementation evidence

P6 adds:

- `src/osca/local_data_import/contracts.py`
- `src/osca/local_data_import/services.py`
- `osca local-ohlcv-import`
- `tests/test_p6_local_ohlcv_import.py`
- `tests/fixtures/local_ohlcv/aapl_daily.csv`

The importer accepts local CSV or Parquet files using the strict canonical schema:

`timestamp,open,high,low,close,volume`

Successful imports write Parquet payloads and SQLite metadata while retaining source checksum, dataset revision identity, symbol, timeframe, timestamp range, row count, calendar assumption, quality findings, and disabled network-access state.

## Deferred boundaries

P6 does not implement:

- Live provider calls.
- Credential materialization.
- Runtime provider routing.
- Production ingestion.
- SEC/FRED enrichment execution.
- Paid provider promotion.
- Trading execution or real-capital orders.

## Validation

Local validation was not executed in this connector-only implementation environment because no authenticated local checkout was available and `gh` is not installed.

Required hosted/local gates for acceptance:

- `ruff`
- `mypy`
- `pytest`
- architecture validation
- OpenSpec validation
- secret scanning
- hosted Quality

## Outcome

P6 should be marked complete only after PR review, merge, and hosted Quality evidence.
