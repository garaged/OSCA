# M3 temporal correctness implementation evidence

- **Status:** Implementation evidence retained through M3.4
- **Branch:** `agent/m3-temporal-correctness`
- **Baseline:** `e7cd118fa275bc4c95a39047eeb791baed232c72`
- **Latest validated head:** `37611ac4b574c1b1906432ee2eb3fe76c5f82294`
- **Hosted Quality run:** `30136859685`
- **Scope:** Additive M3 temporal contracts, stock/crypto interval windows, completed-bar cutoff semantics, calendar-aware gap classification, deterministic resampling lineage, interval-aware retrieval/storage metadata, OHLCV Parquet payloads, and non-daily OHLCV publication.

## Evidence retained

- M3 branch was created from verified post-M2 `main`.
- M2 closeout commits `dd3cd1c`, `f54313e`, and `e7cd118` are present on `main`.
- M3 requirements REQ-0041-REQ-0052 are allocated.
- ADR-0029 records the additive temporal correctness model.
- Unit tests cover approved intervals, completed-bar cutoffs, stock session gaps, unresolved stock calendars, crypto UTC boundaries, resampling lineage, temporal repair-window eligibility, and invalid intraday bars.
- Unit and component tests cover interval-aware retrieval, storage inspection, SQLite manifest persistence, and protected canonical retention behavior.
- Component tests cover governed OHLCV Parquet schema round-trips and interval-aware OHLCV publication idempotency, object-key scoping, manifest protection, and interval mismatch rejection.
- Hosted Quality run `30136859685` passed OpenSpec doctor, strict OpenSpec validation, secret scanning, Ruff, strict mypy, pytest, contract checks, migration checks, documentation link checks, and architecture checks.

## Deferred within M3

- final OpenSpec archive and exit review;
- final merge-readiness cleanup after the last documentation-only Quality run.
