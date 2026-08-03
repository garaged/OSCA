# Contributor and Extension Readiness Delta Specification

## ADDED Requirements

### Requirement: Reproducible contributor bootstrap

OSCA SHALL document and validate one canonical contributor bootstrap for supported development platforms.

#### Scenario: Fresh contributor checkout

- **WHEN** a contributor follows the canonical bootstrap from a fresh checkout
- **THEN** the locked environment SHALL install successfully
- **AND** the complete repository validation suite SHALL be discoverable and executable
- **AND** no paid provider credential SHALL be required.

### Requirement: Stable trusted-local extension contract

OSCA SHALL define a versioned extension manifest covering identity, API compatibility, capabilities, entry points, provenance, licensing, and trust classification.

#### Scenario: Valid trusted-local extension

- **WHEN** an extension manifest satisfies the supported contract
- **THEN** validation SHALL produce a machine-readable passing result
- **AND** SHALL identify the exact API and capability compatibility decision
- **AND** SHALL NOT imply execution approval beyond trusted-local use.

#### Scenario: Unsafe or incompatible extension

- **WHEN** an extension requests prohibited capabilities, lacks required provenance, or targets an unsupported API version
- **THEN** validation SHALL fail closed
- **AND** SHALL provide actionable remediation
- **AND** SHALL NOT import or execute the extension.

### Requirement: Example extension and conformance fixture

OSCA SHALL include an independently buildable example extension and deterministic conformance tests.

#### Scenario: Example extension validation

- **WHEN** the example extension is built and validated
- **THEN** its manifest, package contents, entry point, capability declarations, and expected output SHALL pass conformance
- **AND** the test SHALL not require network access or credentials.

### Requirement: Compatibility and deprecation policy

OSCA SHALL document supported extension API versions, compatibility guarantees, migration expectations, and deprecation notice periods.

#### Scenario: Deprecated API contract

- **WHEN** an extension targets a deprecated but temporarily supported API
- **THEN** validation SHALL report the deprecation and replacement path
- **AND** SHALL identify the last supported OSCA release family.

### Requirement: Contribution governance

OSCA SHALL document contribution scope, testing, security review, licensing, provenance, changelog, and pull-request expectations.

#### Scenario: Contributor submits a change

- **WHEN** a contributor prepares a pull request
- **THEN** the repository SHALL provide a discoverable checklist and local validation command
- **AND** safety-boundary changes SHALL require explicit architectural authority.

### Requirement: Safety preservation

U14 SHALL NOT enable public untrusted extension distribution, remote installation, automatic updates, authoritative recommendations, live serving, broker connectivity, autonomous execution, real-capital orders, remote writes, or public evidence publication.