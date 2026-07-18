# ADR-0017 — M2 Metadata and Daily-Payload Persistence

- **Status:** Accepted
- **Date:** 2026-07-18
- **Decision owners:** Architecture authority and data owner
- **Scope:** M2 instrument/provider metadata, retrieval state, source evidence, canonical daily bars, revisions, integrity, cleanup, migration, and recovery
- **Related requirements:** REQ-0021 through REQ-0040
- **Related product decisions:** D-012, D-016, D-018, D-040
- **Supersedes:** DD-003 for M2 persistence; does not supersede ADR-0012
- **Superseded by:** None

## Context

M2 introduces governed daily market-data payloads that ADR-0012 and DD-003 explicitly excluded from the M1 metadata decision. The slice must remain local-first, preserve exact source and canonical meaning, support deterministic migrations and targeted repair, and avoid selecting the M3 analytical engine prematurely.

Metadata and payloads have different durability and access profiles. Instrument identities, provider mappings, policies, request state, lineage, manifests, and quality findings require transactional constraints and owned migrations. Immutable source responses and revisioned canonical daily bars require bounded columnar range access, portable export, integrity evidence, and replaceable bulk storage.

## Decision drivers

- preserve exact numeric, temporal, source, revision, and lineage meaning;
- enforce capability ownership and transactional metadata invariants;
- support bounded range reads, integrity checks, gaps, and targeted repair;
- operate on one workstation without a mandatory service;
- provide deterministic migration, export, recovery, and cleanup;
- keep public dataset identity independent of physical paths and engines;
- avoid deciding M3 intraday or analytical-storage architecture.

## Considered alternatives

### Dedicated SQLite for metadata and payloads

**Benefits**

- one migration and transaction mechanism;
- no additional payload format or coordination protocol;
- strong uniqueness and targeted-update behavior.

**Costs and risks**

- couples bulk series access and growth to the metadata database;
- weakens the explicit payload boundary established after M1;
- makes later bulk-store replacement and portable payload inspection harder.

### DuckDB with Parquet payloads

**Benefits**

- strong columnar scans and direct Parquet integration;
- convenient analytical querying and export.

**Costs and risks**

- introduces an analytical engine before M3 requirements and evidence exist;
- risks allowing implementation code to depend on engine-specific query behavior;
- expands the M2 dependency and operational surface unnecessarily.

### SQLite metadata with Parquet payloads

**Benefits**

- matches transactional metadata and immutable columnar payload workloads;
- preserves local-first operation and portable bulk files;
- keeps payload access behind an owned, replaceable repository;
- does not require an analytical database engine.

**Costs and risks**

- SQLite and the filesystem cannot share one atomic transaction;
- manifests, reconciliation, cleanup, backup, and recovery must handle partial operations explicitly;
- Parquet schema and writer compatibility become governed persistence contracts.

## Decision

M2 will persist capability-owned metadata in SQLite and source/canonical daily payloads in Parquet.

SQLite use continues the ADR-0012 operational profile—WAL mode, SQLAlchemy 2, Alembic migrations, foreign keys, bounded contention, integrity checks, and capability-owned repositories—but M2 tables and migrations remain explicitly owned by the Instrument, Provider, Market Data, Catalog, Workflow, and Operations capabilities. Cross-capability table access remains prohibited.

Parquet payload rules are:

- source evidence and canonical datasets are separate immutable objects;
- canonical corrections create new revisions rather than overwriting accepted payloads;
- every object has a stable logical dataset/revision identity independent of its path;
- a SQLite manifest records owner, dataset, layer, schema version, revision, bounded date range, row count, byte size, content digest, creation state, provenance, and retention/protection state;
- prices use governed fixed-precision decimal fields; volumes use governed integral or fixed-precision fields; dates and timestamps use explicit logical types and UTC semantics where timestamps apply;
- readers resolve only manifest entries in the `ready` state and verify schema identity and digest according to the access policy;
- application capabilities access payloads only through the Market Data public repository port, never by constructing paths or issuing engine-specific queries.

The initial Parquet implementation will use PyArrow behind that repository port. DuckDB is not selected by this ADR and may be evaluated later without changing public contracts or logical dataset identity.

## Coordination protocol

Because SQLite and filesystem changes are not jointly atomic, writers use a recoverable state machine:

1. create a manifest in `staging` with its intended logical identity;
2. write a same-filesystem temporary Parquet object, validate schema/row invariants, compute its digest, and durably close it;
3. atomically rename the object to its content-addressed final path;
4. commit the completed manifest as `ready`;
5. emit lineage, quality, audit, and operational evidence through their owning seams.

Readers ignore `staging`, `deleting`, quarantined, missing, or digest-invalid objects. A deterministic reconciler classifies interrupted writes as resumable, orphaned, missing, or corrupt without silently accepting them. Cleanup first marks eligible objects `deleting`, removes only the exact manifest-addressed object, and then records completion; retries are idempotent.

## Rationale

The split aligns each persistence mechanism with its workload while preserving ADR-0009 ownership and ADR-0012's local durability model. Parquet supplies a standard, inspectable columnar payload without importing an analytical engine. Explicit manifests and reconciliation make the unavoidable cross-resource failure boundary observable and testable instead of pretending it is transactional.

## Consequences

### Positive

- M2.1 metadata work can begin without selecting M3 storage.
- Source and canonical layers, revisions, digests, and retention are first-class.
- Bulk payload replacement remains possible behind stable repository and dataset identities.
- Backup, export, inspection, and cleanup can operate from governed manifests.

### Negative and tradeoffs

- PyArrow becomes an M2 runtime dependency once payload implementation begins.
- Writers, cleanup, and recovery require a state machine and failure-injection tests.
- Small daily datasets may create inefficient tiny files unless compaction remains bounded and governed.
- Cross-resource snapshots require an explicit consistency marker rather than a single database transaction.

### Required follow-up

- M2.1 defines owned SQLite schemas and migrations for registry and provider mappings.
- M2.2 fixes the Parquet conformance schema and license-safe fixtures before live adapters.
- M2.3 implements the manifest, repository port, revision protocol, and staged writer.
- M2.4 implements reconciliation, gap repair, restart, and cancellation behavior.
- M2.6 implements manifest-driven inspection and cleanup preview.
- Recovery guidance defines metadata-plus-payload snapshot consistency and payload inclusion policy before claiming recoverability.

## Fitness and verification

- architecture tests prohibit direct filesystem/Parquet access outside Market Data infrastructure;
- migrations succeed from every retained M2 metadata fixture and preserve ownership;
- schema compatibility tests round-trip exact decimal/date/timestamp values;
- property tests prove stable logical identity, revision monotonicity, and bounded range reads;
- failure injection at every coordination step produces only defined manifest/object states;
- corruption, missing objects, orphan objects, and digest mismatch are detected deterministically;
- cleanup preview and execution address the same manifest identities and respect pins/protection;
- backup/restore or reconstruction evidence declares the exact consistency marker and exclusions;
- no DuckDB dependency or engine-specific public contract is introduced by M2.

## Migration and compatibility

M2 begins with new owned metadata migrations and Parquet schema version 1; no M1 market payload migration exists. Public identities never contain physical paths. A future payload implementation must read or deterministically migrate retained Parquet schema versions, preserve revision and lineage identity, and provide rollback/reconstruction evidence before replacement.

## Risks

This decision treats M2-R04 canonical corruption, M2-R05 partial/stale data, M2-R07 storage pressure, M2-R08 cleanup loss, and M2-R09 migration/recovery ambiguity. Residual risks are cross-resource interruption, library compatibility, tiny-file growth, and filesystem durability differences; each remains covered by the M2 evidence plan.

## Revisit triggers

Revisit when measured M2 workloads exceed the bounded SQLite or Parquet envelope, M3 accepts analytical-storage requirements, PyArrow cannot preserve governed semantics, filesystem atomicity assumptions do not hold on a supported platform, or recovery evidence shows the coordination protocol cannot meet accepted objectives.
