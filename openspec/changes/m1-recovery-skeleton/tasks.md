## 1. Authority and contracts

- [x] 1.1 Approve ADR-0016 and reconcile DD-012.
- [ ] 1.2 Add versioned backup manifest, metadata, verification, restore-plan, and error contracts.
- [ ] 1.3 Register public contract families and deterministic schemas.

## 2. Specification-first tests

- [ ] 2.1 Add consistent-snapshot, deterministic-manifest, checksum, and exclusion tests.
- [ ] 2.2 Add wrong-identity, tamper, timeout, unavailable-tool, cleanup, and secret-canary tests.
- [ ] 2.3 Add malicious archive, compatibility, conflict-preview, and active-state-invariance tests.
- [ ] 2.4 Add isolated restore and post-restore validation tests.

## 3. Persistence and catalog

- [ ] 3.1 Add Recovery-owned operation state and retained Alembic migration.
- [ ] 3.2 Complete Catalog-owned backup and restore metadata through public ports.
- [ ] 3.3 Prove schema ownership, integrity digests, lineage, availability, and retention.

## 4. Recovery implementation

- [ ] 4.1 Implement consistent snapshot and deterministic allowlisted package construction.
- [ ] 4.2 Implement bounded age v1 X25519 adapter and atomic encrypted publication.
- [ ] 4.3 Implement non-mutating verify and explicit conflict preview.
- [ ] 4.4 Implement new-location-only restore and post-restore validation.

## 5. Interfaces and operations

- [ ] 5.1 Add shared application handlers and authorized CLI commands.
- [ ] 5.2 Add correlated telemetry, safe findings, and distinct audit records.
- [ ] 5.3 Add operator documentation for age setup, identity custody, backup, verify, preview, restore, and limitations.

## 6. Validation and evidence

- [ ] 6.1 Run Python, migration, architecture, schema, security, adapter, and documentation gates.
- [ ] 6.2 Run strict OpenSpec validation and reconcile every finding.
- [ ] 6.3 Update traceability, milestone status, navigation, and retained M1 evidence.
- [ ] 6.4 Review, sync, and archive the OpenSpec change before PR merge.
