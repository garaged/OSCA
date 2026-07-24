## 1. Specification and contracts

- [x] 1.1 Accept persistence, retention, numeric, expected-date, publication, incomplete-observation, revision, selection, and canonical-history decisions.
- [x] 1.2 Register remaining Market Data contract families and compatibility semantics.
- [x] 1.3 Add contract, normalization, manifest, date-policy, retrieval, and cleanup specification tests.

## 2. Governed ingestion and persistence

- [x] 2.1 Add exact canonical daily-bar normalization and immutable dataset manifests.
- [x] 2.2 Add deterministic bounded Parquet serialization and staged atomic publication.
- [x] 2.3 Add owned SQLite migration, integrity, lineage, and canonical-history protection.

## 3. Retrieval, repair, and quality

- [x] 3.1 Add explicit freshness, completeness, unavailable, corrupt, and exact-pin resolution.
- [x] 3.2 Add conservative expected-date classification and targeted repair ranges.
- [x] 3.3 Integrate durable retrieval/repair work, deterministic findings, telemetry, and audit.

## 4. Inspection and cleanup

- [x] 4.1 Add preview-only cleanup selection with explicit policy eligibility.
- [x] 4.2 Add usage/provenance inspection and protected/pinned/reproducibility accounting.
- [x] 4.3 Add authorized cleanup execution with race-safe revalidation and evidence.

## 5. Reference providers

- [x] 5.1 Add deterministic Twelve Data and Kraken candidate parsers behind injected I/O.
- [x] 5.2 Add bounded endpoint, timeout, size, quota, retry, redaction, and failure controls.
- [x] 5.3 Record production-promotion deferral for paid, authenticated, or license-sensitive provider use. No M2 production promotion is approved.

## 6. Validation and evidence

- [x] 6.1 Add integrated fixture paths, migration/recovery tests, performance observations, and executable operator examples.
- [x] 6.2 Run all Python, architecture, OpenSpec, link, migration, and security gates.
- [x] 6.3 Reconcile traceability, risks, navigation, limitations, and retained M2 evidence.
- [ ] 6.4 Complete M2 exit review, sync/archive this change, and make the PR ready only with no M2 blockers.
