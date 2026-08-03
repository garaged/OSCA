# Release-Candidate Acceptance Delta Specification

## ADDED Requirements

### Requirement: Official acceptance matrix

OSCA SHALL execute and retain one official release-candidate acceptance result covering all sixteen U13 acceptance areas.

#### Scenario: Complete passing matrix

- **WHEN** every acceptance area completes successfully on the supported environments
- **THEN** the result SHALL identify every area as passed
- **AND** SHALL retain command, artifact, evidence, platform, version, and digest references
- **AND** SHALL remain ineligible for tagging until the defect threshold also passes.

#### Scenario: Blocked or failed area

- **WHEN** an acceptance area cannot execute or does not meet its requirement
- **THEN** the result SHALL identify it as blocked or failed
- **AND** SHALL include actionable remediation
- **AND** SHALL deny release-candidate eligibility.

### Requirement: Defect threshold

OSCA SHALL deny release-candidate eligibility while any critical or high-severity defect remains open.

#### Scenario: Medium defect disposition

- **WHEN** a medium-severity defect remains open
- **THEN** it SHALL have an explicit disposition, workaround, owner, and target milestone
- **OR** release-candidate eligibility SHALL be denied.

### Requirement: Release artifact traceability

The acceptance result SHALL link the selected package version to checksums, SBOM, provenance, supported-platform results, release notes, and source commit.

#### Scenario: Candidate artifacts are evaluated

- **WHEN** the official acceptance job evaluates release artifacts
- **THEN** wheel and source artifacts SHALL be identified
- **AND** the source commit and candidate version SHALL be retained
- **AND** missing artifact evidence SHALL deny eligibility.

### Requirement: Safety preservation

Acceptance and tagging SHALL NOT enable recommendations, automatic promotion, live model serving, broker or exchange connectivity, autonomous execution, real-capital orders, remote writes, or public evidence publication.

#### Scenario: Candidate becomes eligible

- **WHEN** all release-candidate gates pass
- **THEN** the acceptance result SHALL retain every prohibited capability as disabled
- **AND** SHALL report that no publication was performed.

### Requirement: Explicit tag authority

A release-candidate tag SHALL be recommended only after all blocking gates pass. Tag creation or publication SHALL remain an explicit action and SHALL NOT occur as a side effect of acceptance execution.

#### Scenario: Eligible candidate is evaluated

- **WHEN** the candidate is eligible
- **THEN** the result SHALL recommend the version-derived tag
- **AND** SHALL report `tag_created` as false
- **AND** SHALL require a separate explicit tag action.
