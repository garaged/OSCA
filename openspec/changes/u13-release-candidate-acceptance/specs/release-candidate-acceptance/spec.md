# Release-Candidate Acceptance Specification

## Requirement: Official acceptance matrix

OSCA SHALL execute and retain one official release-candidate acceptance result covering all sixteen U13 acceptance areas.

### Scenario: Complete passing matrix

- **WHEN** every acceptance area completes successfully on the supported environments
- **THEN** the result SHALL identify every area as passed
- **AND** SHALL retain command, artifact, evidence, platform, version, and digest references
- **AND** SHALL remain ineligible for tagging until the defect threshold also passes.

### Scenario: Blocked or failed area

- **WHEN** an acceptance area cannot execute or does not meet its requirement
- **THEN** the result SHALL identify it as blocked or failed
- **AND** SHALL include actionable remediation
- **AND** SHALL deny release-candidate eligibility.

## Requirement: Defect threshold

OSCA SHALL deny release-candidate eligibility while any critical or high-severity defect remains open.

### Scenario: Medium defect disposition

- **WHEN** a medium-severity defect remains open
- **THEN** it SHALL have an explicit disposition, workaround, owner, and target milestone
- **OR** release-candidate eligibility SHALL be denied.

## Requirement: Release artifact traceability

The acceptance result SHALL link the selected package version to checksums, SBOM, provenance, supported-platform results, release notes, and source commit.

## Requirement: Safety preservation

Acceptance and tagging SHALL NOT enable recommendations, automatic promotion, live model serving, broker or exchange connectivity, autonomous execution, real-capital orders, remote writes, or public evidence publication.

## Requirement: Explicit tag authority

A release-candidate tag SHALL be recommended only after all blocking gates pass. Tag creation or publication SHALL remain an explicit action and SHALL NOT occur as a side effect of acceptance execution.
