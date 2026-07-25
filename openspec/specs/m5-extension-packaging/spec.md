# m5-extension-packaging Specification

## Purpose

Index the verified M5 independent extension package manifest, installation, activation, permission, trust, integrity, persistence, administration, and impact-preview semantics under REQ-0069-REQ-0084 and ADR-0031.

## Requirements

### Requirement: Extension manifest metadata

Extension manifests SHALL declare package identity, publisher, version, category, entry points, compatibility, schemas, supported scopes, dependencies, permissions, integrity, license, provenance, and trust tier.

#### Scenario: Manifest accepted
- **WHEN** a manifest declares complete identity, compatibility, entry point, permission, dependency, and integrity metadata
- **THEN** validation returns no findings

### Requirement: Manifest validation fails closed

Manifest validation SHALL reject missing entry points, empty compatibility, duplicate dependencies, duplicate permissions, missing integrity digest, and malformed semantic versions.

#### Scenario: Manifest has duplicate permission
- **WHEN** a manifest declares the same permission scope twice
- **THEN** validation reports the duplicate permission before installation

### Requirement: Installation record persistence

Installation records SHALL preserve exact package identity, version, source, integrity digest, resolved dependencies, granted permissions, activation state, and installation timestamp in governed SQLite metadata storage.

#### Scenario: Package installed
- **WHEN** a manifest is installed from a source URI
- **THEN** the persisted installation record preserves the exact manifest identity, digest, permissions, and timestamp

### Requirement: Explicit activation

Activation SHALL be an explicit decision linked to a stored installation record and SHALL fail closed for untrusted or quarantined packages.

#### Scenario: Quarantined activation
- **WHEN** activation is requested for a quarantined package
- **THEN** activation is rejected with a structured reason

### Requirement: Permission renewal

Permission changes SHALL require renewed approval before activation.

#### Scenario: Permission changes
- **WHEN** requested permissions differ from previously granted permissions
- **THEN** activation is rejected until approval is renewed

### Requirement: Disable and uninstall impact preview

Disable and uninstall previews SHALL identify impacted retained analyses, artifacts, projects, reports, and dependent extensions.

#### Scenario: Retained artifact depends on extension
- **WHEN** uninstall is previewed for an installed extension used by retained artifacts
- **THEN** the preview lists impacted references before state changes

### Requirement: Operator extension administration

The CLI SHALL expose metadata-only extension installation, activation decision, and installation-listing operations backed by the lifecycle store.

#### Scenario: Local owner installs extension metadata
- **WHEN** a local owner installs a valid manifest through the CLI
- **THEN** the installation record is persisted and can be listed without executing extension code

### Requirement: M5 scope boundary

M5 SHALL NOT execute third-party code or implement strategy, backtesting, ML, LLM, paper trading, public registry, HTTP API/UI administration, or live execution behavior.

#### Scenario: Runtime execution requested
- **WHEN** a package requires runtime execution
- **THEN** execution is deferred outside M5
