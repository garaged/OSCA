# Evidence — M3 temporal correctness

## Branch evidence

- Verified `main` head at M3 start: `e7cd118fa275bc4c95a39047eeb791baed232c72`.
- Verified M2 closeout commits on `main`: `dd3cd1c`, `f54313e`, `e7cd118`.
- Created branch: `agent/m3-temporal-correctness`.
- Added additive temporal contracts and tests without changing accepted M2 daily-bar contracts.

## Implementation evidence

- Temporal API contracts cover approved intervals, completed windows, exchange sessions, crypto UTC days, temporal gaps, OHLCV bars, and resampling lineage.
- Application services cover completed-bar cutoff, stock expected windows, crypto expected windows, gap classification, repair-window planning, and deterministic resampling.
- Retrieval requests and dataset manifests carry interval identity with `1d` compatibility defaults.
- Retrieval resolution filters by interval and does not silently substitute daily and intraday revisions.
- Storage inspection groups usage by interval.
- SQLite manifest persistence retains interval metadata.
- OHLCV Parquet serialization/deserialization uses governed schema metadata.
- OHLCV publication uses interval-aware intents, interval-scoped object keys, protected canonical manifests, and interval mismatch rejection.

## Validation evidence

Hosted Quality run `30136903096` passed on branch head `7dc3b99510e4f6d87351694f22e6fec0747fc0dc`:

- OpenSpec doctor;
- strict OpenSpec validation;
- secret scanning;
- Ruff;
- strict mypy;
- pytest;
- contract checks;
- migration checks;
- documentation link checks;
- architecture checks.

Production promotion for paid, authenticated, or license-sensitive provider use remains deferred until exact provider evidence is accepted.
