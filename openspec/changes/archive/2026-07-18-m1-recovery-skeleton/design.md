## Context

M1.1–M1.4 established validated configuration, capability-owned SQLite metadata, durable workflows, Catalog result metadata, Security vault references, and Operations telemetry/audit. The accepted M1 specification defines recovery behavior; ADR-0016 selects `age/v1+x25519`. OpenSpec tracks execution and does not replace those authorities.

## Goals and non-goals

### Goals

- Produce a minimal protected backup with deterministic integrity and exclusion evidence.
- Keep active state unchanged during verification, preview, and isolated restore.
- Treat decrypted packages as hostile structured input.
- Complete typed Catalog metadata for backups and restore attempts.
- Retain failure-oriented evidence sufficient for REQ-0017 and REQ-0018.

### Non-goals

- Activation, overwrite/in-place restore, remote storage, scheduled retention, full DR automation, or market payloads.
- Private-key storage in Recovery or OSCA-specific cryptography.
- Changes to Frozen Tier-1 ADRs or accepted product meaning.

## Decisions

### Ownership and seams

Create `osca.recovery` with public contracts, application handlers/ports, and infrastructure adapters. Recovery coordinates public ports only. It cannot import another capability's private persistence. Catalog owns backup/restore metadata; Security resolves named private identity references; Operations receives audit and telemetry through public seams.

### Package construction

Recovery creates a consistent SQLite snapshot using SQLite's backup API. A deterministic archive contains the snapshot, validated configuration export with secret references only, a canonical JSON manifest, and exclusion report. Entries are allowlisted, relative, unique, size-bounded, and checksummed. The cleartext archive is staged with owner-only permissions and encrypted to an explicit X25519 recipient before atomic publication.

### Encryption boundary

A shell-free age process adapter accepts a validated recipient for encryption and private identity bytes obtained from the vault for decryption. Secret identity material is supplied through a private temporary file or standard input supported by the adapter, never command arguments. The adapter enforces executable identity/version probing, timeout, output limits, cleanup, and stable safe errors.

### Verification and restore

Verification authenticates/decrypts into private staging, validates container/manifest/schema/checksums and compatibility, then removes staging without writes to active storage. Preview additionally inspects the snapshot and emits an explicit immutable restore plan and conflicts. Execute requires a verified plan and a new non-existent destination, performs path-safe extraction, and validates migration compatibility, SQLite integrity, references, audit structure, and readiness smoke behavior.

### Persistence and compatibility

Add a Recovery-owned migration for durable operation state and Catalog public metadata registration for backup/restore records. Contract families begin at 1.0.0. Unknown major versions and incompatible product/schema ranges fail before restore writes.

## Risks and tradeoffs

- Cleartext staging exists briefly; private permissions, minimal lifetime, cleanup assertions, and no-crash residue tests are mandatory.
- External age execution can fail or hang; bounded process control and failure cleanup are mandatory.
- Archive traversal and decompression abuse remain risks after decryption; allowlists, normalized paths, entry/count/size limits, and no links are mandatory.
- Snapshot consistency depends on SQLite behavior; integration tests mutate the source during backup and verify a coherent snapshot.

## Rollout and recovery

Land contracts and failure-first tests, then migration/repositories, package creation, verification/preview, isolated restore, adapters, documentation, and evidence. No command becomes production-visible until encrypted creation and negative verification pass. Failed operations retain safe metadata but no valid-looking package or active-state mutation.

## Validation

- strict OpenSpec validation;
- Ruff, strict mypy, full pytest, and architecture boundaries;
- migration upgrade/downgrade/upgrade;
- deterministic manifest/schema/compatibility fixtures;
- concurrent-write snapshot integrity;
- age interoperability, wrong-identity, tamper, timeout, unavailable-tool, and cleanup tests;
- malicious archive, size-limit, duplicate-entry, and traversal tests;
- active-state digest invariance;
- CLI contract and executable-documentation tests;
- telemetry, audit, redaction, and retained traceability evidence.
