# Research-Evidence Workspace Delta Specification

## ADDED Requirements

### Requirement: Dedicated retained-evidence sections

The analyst workspace SHALL expose datasets, acquisitions, backtests, experiments, diagnostics, validations, and pipeline runs as dedicated read-only sections rather than presenting research workflow artifacts only as generic reports.

#### Scenario: U9 and U8 evidence is classified

- **WHEN** a storage root contains a canonical dataset, historical-acquisition evidence, an experiment, a diagnostic, and a pipeline manifest
- **THEN** each artifact appears in its dedicated section
- **AND** those artifacts do not duplicate under generic reports.

### Requirement: Explicit artifact health

The workspace SHALL distinguish available, review-required, not-eligible, incomplete, corrupt, incompatible, orphaned, policy-blocked, and provider-unavailable states.

#### Scenario: Malformed JSON exists

- **WHEN** a dedicated research artifact cannot be decoded as a JSON object
- **THEN** the workspace presents it as corrupt
- **AND** emits a warning
- **AND** does not present it as healthy evidence.

### Requirement: Navigable lineage

The workspace SHALL provide read-only upstream and downstream lineage from dataset acquisition through experiment, diagnostic, optional validation, and pipeline run.

#### Scenario: Diagnostic prevents validation

- **WHEN** a pipeline manifest records a diagnostic-not-eligible result
- **THEN** the workspace shows the dataset, acquisition, experiment, diagnostic, and manifest lineage
- **AND** identifies validation as not expected rather than missing or successful.

### Requirement: Read-only filtering and details

The workspace SHALL support read-only detail views and filtering by date, symbol, timeframe, artifact type, and status without altering retained evidence.

### Requirement: Governed evidence export

The workspace SHALL support bounded raw JSON download and portable evidence-bundle export only when provider policy permits the included artifacts.

#### Scenario: Export is requested

- **WHEN** an operator exports a retained lineage
- **THEN** secrets and credentials are excluded
- **AND** provider redistribution policy is enforced
- **AND** exported identifiers and evidence agree with CLI and API representations.

### Requirement: Safety boundaries remain disabled

The workspace SHALL remain loopback-only and read-only, with network retrieval, credential materialization, recommendations, automatic model promotion, broker connections, autonomous execution, and real-capital orders disabled.
