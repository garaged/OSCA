# Packaging Lifecycle Specification

## ADDED Requirements

### Requirement: Supported isolated installation

OSCA SHALL provide one documented isolated installation path that installs the primary `osca` executable on macOS Apple Silicon and Linux x86-64 without requiring a repository checkout at runtime.

#### Scenario: Fresh supported-platform install

- **WHEN** a clean supported machine installs the declared OSCA package using the documented isolated path
- **THEN** `osca --help`, `osca init`, `osca doctor`, and `osca workspace --snapshot` are available
- **AND** the installed package reports its version and build provenance
- **AND** all U11 safety defaults remain disabled

### Requirement: Package integrity and provenance

Release rehearsal artifacts SHALL include cryptographic checksums, an SBOM, supported-platform metadata, and build provenance sufficient to identify the source revision and package version.

#### Scenario: Verify packaged artifact

- **WHEN** an operator validates a packaged artifact before installation
- **THEN** its checksum matches the published manifest
- **AND** the SBOM and provenance refer to the same package version and source revision
- **AND** verification failure blocks installation guidance

### Requirement: Compatibility inspection before mutation

OSCA SHALL inspect operator configuration and retained storage compatibility before any lifecycle operation mutates state.

#### Scenario: Incompatible profile detected

- **WHEN** an upgrade encounters an unsupported configuration or storage contract
- **THEN** the operation fails before mutation
- **AND** reports the incompatible contract and remediation
- **AND** preserves the original profile and evidence unchanged

### Requirement: Backup before migration

Any upgrade that may migrate configuration or retained storage SHALL create and verify a backup before the first mutation.

#### Scenario: Backup verification fails

- **WHEN** a required pre-migration backup cannot be created or verified
- **THEN** migration does not begin
- **AND** the upgrade returns a structured failed outcome
- **AND** the original profile remains usable

### Requirement: Failed-upgrade recovery

OSCA SHALL provide a deterministic recovery path after a failed upgrade.

#### Scenario: Upgrade fails after backup

- **WHEN** an upgrade fails after a verified backup exists
- **THEN** OSCA retains failure evidence
- **AND** provides an explicit restore or rollback action
- **AND** the recovered profile passes compatibility and evidence-consistency checks

### Requirement: Rollback preserves accepted evidence

Rollback SHALL restore a previously accepted application/profile state without losing accepted retained evidence.

#### Scenario: Roll back upgraded profile

- **WHEN** an operator rolls back to the prior supported package/profile state
- **THEN** accepted dataset and research evidence identifiers remain discoverable
- **AND** workspace item counts and evidence digests agree with the pre-upgrade baseline
- **AND** recommendations, brokers, autonomous execution, and real-capital orders remain disabled

### Requirement: Supported-platform lifecycle validation

The complete fresh-install, workflow, upgrade, recovery, and rollback lifecycle SHALL be validated on macOS Apple Silicon and Linux x86-64.

#### Scenario: Platform lifecycle acceptance

- **WHEN** the U12 acceptance suite runs on either supported platform
- **THEN** installation, initialization, representative workflow execution, backup, upgrade, restore, failed-upgrade recovery, rollback, and packaged workspace startup pass
- **AND** no accepted evidence is lost or silently rewritten
