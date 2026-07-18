# m1-documentation-operational-evidence Specification

## Purpose

Index the verified M1 version-matched operational guidance, executable-example disposition, navigation, and retained traceability governed by REQ-0019, REQ-0020, ADR-0005, and the accepted M1 specification.

## Requirements

### Requirement: Version-matched operational entry path

The repository SHALL provide one task-oriented M1 entry path that links installation, developer setup, configuration, security, readiness interfaces, diagnostic jobs, recovery, telemetry, troubleshooting, schemas, and limitations without replacing authoritative specifications or ADRs.

#### Scenario: Clean-checkout reader finds the supported path

- **WHEN** a reader starts from the root README at the M1 source revision
- **THEN** the reader can reach prerequisites, locked setup, migration, startup, readiness verification, focused operations, and limitations through valid repository links

### Requirement: Executable documentation evidence

Representative safe M1 documentation examples SHALL be automatically validated where practical, and every non-executed example SHALL state the operator-supplied or environment-specific boundary that prevents deterministic CI execution.

#### Scenario: Documentation validation runs

- **WHEN** the documentation example gate runs in the locked reference environment
- **THEN** safe setup and readiness examples execute successfully and security-sensitive examples are covered by explicit tests or marked operator-supplied

### Requirement: Traceable M1.7 closure

M1.7 SHALL retain evidence linking REQ-0019 and REQ-0020 to the accepted specification, documentation, validation results, limitations, source revision, and immutable CI identity.

#### Scenario: Completion is reviewed

- **WHEN** an M1.7 completion claim is inspected
- **THEN** no mandatory trace link is missing and the record distinguishes executed evidence from limitations and deferred M1.8 work
