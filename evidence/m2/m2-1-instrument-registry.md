# M2.1 Instrument Registry Evidence

- **Status:** Complete
- **Source revision:** `0901d3df8bc0dda4f8eaf7dd605d968bab519c67`
- **Quality workflow:** `29655469652`
- **Requirements:** REQ-0021–REQ-0024
- **Acceptance criteria:** M2-AC-001, M2-AC-002, partial M2-AC-017
- **ADRs:** ADR-0003, ADR-0004, ADR-0005, ADR-0009, ADR-0012, ADR-0017
- **Risk:** RISK-M2-001

## Delivered behavior

- immutable 1.0.0 stock and spot-crypto-pair canonical identities independent of provider symbols;
- exact asset-specific validation and stable identity keys;
- time-aware mappings with provider, symbol, scope, venue, validity, provenance, verification, and capabilities;
- application guards for duplicate identities, missing canonical instruments, unverified mappings, and overlapping ambiguous aliases;
- Instrument-owned SQLite repository and reversible `m2_0001` Alembic migration;
- public-contract ownership and OpenSpec traceability.

## Validation

Quality run `29655469652` passed at the source revision:

- locked CPython 3.13 environment installation;
- Ruff;
- strict mypy across 82 source files;
- 70 tests including new registry behavior and migration upgrade/downgrade;
- contract, architecture, link, and recovery tests;
- strict OpenSpec validation;
- secret scanning.

The preceding run `29655426553` identified one stale exact-table-list expectation. The test was corrected to include the two governed M2 tables; no production behavior changed.

## Limitations and deferred work

- No live provider, discovery network, daily bar, Parquet payload, routing, or retrieval behavior is implemented.
- Mapping correction history and discovery orchestration remain later M2 increments.
- Production provider mappings remain blocked by provider-specific licensing/policy approval.
- M2-AC-017 is partial: the owned migration is verified, while payload reconciliation and recovery evidence remain deferred to M2.3–M2.4.

## Residual risk

Concurrent alias activation ultimately relies on database constraints and transaction policy in addition to application validation. More complete interval-conflict persistence enforcement and concurrency evidence are required before provider-fed canonical writes are enabled.
