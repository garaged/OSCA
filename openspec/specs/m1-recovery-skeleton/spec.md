# m1-recovery-skeleton Specification

## Purpose
Index the verified M1 protected-backup, non-mutating verification, explicit preview, and
new-location-only restore semantics governed by REQ-0010, REQ-0013, REQ-0017, REQ-0018,
ADR-0016, and the accepted M1 specification.
## Requirements
### Requirement: Protected consistent backup

Recovery SHALL create a consistent SQLite snapshot, deterministic allowlisted payload, canonical manifest, checksums, schema/build identity, and explicit exclusion report before encrypting the package as `age/v1+x25519`.

#### Scenario: Successful protected backup
- **WHEN** an authorized operator creates a backup for a validated X25519 recipient
- **THEN** one atomically published encrypted package and typed Catalog record identify the same verified digest and source revision

#### Scenario: Source changes during backup
- **WHEN** active SQLite state changes while the snapshot is created
- **THEN** the package contains one coherent SQLite snapshot rather than a partial cross-transaction view

#### Scenario: Encryption fails
- **WHEN** encryption is unavailable, times out, or rejects the recipient
- **THEN** no valid-looking final package remains and all cleartext staging is removed

### Requirement: Secret and transient exclusion

Recovery SHALL export secret references but SHALL exclude secret values and transient content from configuration, manifests, archives, diagnostics, audit details, and retained evidence.

#### Scenario: Secret canary exists in the vault
- **WHEN** a backup is created while a canary secret is resolvable
- **THEN** the canary does not occur in the encrypted-package inputs, decrypted listing, manifest, exclusion report, logs, errors, or audit payload

### Requirement: Typed recovery metadata

Catalog-owned backup and restore records SHALL carry stable typed identity, contract version, timestamps, source build/schema, configuration revision, lineage, integrity, availability, retention, and correlation metadata as applicable.

#### Scenario: Metadata round trip
- **WHEN** a recovery record is registered and reloaded
- **THEN** its deterministic integrity digest verifies and all governed metadata semantics are preserved

### Requirement: Non-mutating verification

Verification SHALL authenticate/decrypt privately, validate manifest/schema/checksums and compatibility, reject unsafe content, and remove cleartext staging without mutating active state.

#### Scenario: Valid compatible package
- **WHEN** a compatible package is verified with the correct vault-resolved identity
- **THEN** verification returns typed evidence and the active-state digest remains unchanged

#### Scenario: Wrong identity or modified package
- **WHEN** identity authentication fails or ciphertext, manifest, or payload is modified
- **THEN** verification fails closed with a safe stable error and active state remains unchanged

#### Scenario: Malicious archive
- **WHEN** decrypted content contains traversal, absolute, duplicate, linked, undeclared, oversized, or excessive entries
- **THEN** verification rejects it before extraction or restore writes

### Requirement: Explicit restore preview

Preview SHALL require successful verification and produce an immutable plan containing destination, operations, compatibility assessment, conflicts, and required post-restore checks.

#### Scenario: Conflicting destination or identity
- **WHEN** preview detects an existing destination, incompatible schema, duplicate identity, or unresolved reference
- **THEN** it reports the conflict and the plan is not executable

### Requirement: Isolated restore only

M1 restore SHALL execute only a currently non-existent isolated destination from an unmodified verified plan and SHALL never activate or overwrite active state.

#### Scenario: Successful isolated restore
- **WHEN** an authorized operator executes a conflict-free verified plan
- **THEN** Recovery creates the isolated destination, validates database integrity, migrations, catalog references, audit structure, and readiness smoke behavior, and records the outcome

#### Scenario: Destination appears after preview
- **WHEN** the planned destination exists at execution time
- **THEN** restore fails without overwriting it and active state remains unchanged

### Requirement: Correlated recovery evidence

Backup creation and restore execution SHALL emit safe correlated logs, traces, metrics, and distinct Operations-owned audit records without protected values.

#### Scenario: Recovery operation fan-out
- **WHEN** a recovery operation completes or fails
- **THEN** its metadata, telemetry, audit, and finding references use the same operation and correlation identities

### Requirement: Retained verification

The change SHALL retain migration, snapshot, encryption interoperability, compatibility, malicious-input, cleanup, active-state-invariance, adapter, documentation, architecture, and traceability evidence.

#### Scenario: Completion review
- **WHEN** implementation tasks are complete
- **THEN** strict OpenSpec validation and all applicable OSCA gates pass against the retained source revision
