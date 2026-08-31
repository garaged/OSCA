# ML Data Platform Specification

## ADDED Requirements

### Requirement: Immutable governed dataset plans
The system SHALL construct experiment plans only from server-resolved retained dataset revisions and SHALL pin identity, digest, source attribution, policies, and effective range.

#### Scenario: Client path attempt
- **WHEN** a renderer supplies a payload or filesystem path
- **THEN** the desktop API rejects the request before experiment retention

### Requirement: Versioned point-in-time catalog
The system SHALL expose and retain versioned feature and label definitions with point-in-time, lookback, missing-data, horizon, and leakage evidence.

#### Scenario: Unsafe feature selection
- **WHEN** an unknown, duplicate, or unsupported partial feature set is requested
- **THEN** planning fails closed with no experiment record

### Requirement: Time-aware validation
Every experiment SHALL use chronological train/validation/test partitions, purge its label horizon, apply explicit embargo, and fit transforms on training data only.

#### Scenario: Invalid partition budget
- **WHEN** purge and embargo leave an invalid partition
- **THEN** execution retains a failed result with actionable evidence

### Requirement: Mandatory baseline evidence
Every completed experiment SHALL retain validation/test metrics and a simple baseline evaluated over the same test observations.

#### Scenario: Model underperforms baseline
- **WHEN** the bounded model does not improve on its simple baseline
- **THEN** the result is retained for review and is not promoted

### Requirement: Bounded restart-safe lifecycle
Experiment status, cancellation, failure, interruption recovery, result digests, and timeline events SHALL survive restart under profile ownership controls.

#### Scenario: Interrupted running experiment
- **WHEN** the process restarts with a retained running record
- **THEN** the record becomes failed with an explicit interruption diagnostic and may be deliberately rerun

### Requirement: Research-only ML Lab
The desktop SHALL expose catalog, planning, lifecycle, split, baseline, policy, findings, and digest evidence without network, credentials, arbitrary code, promotion, recommendations, broker, or real-capital authority.

#### Scenario: Offline local experiment
- **WHEN** a profile has sufficient local governed data and no external account
- **THEN** the complete D10 planning and experiment workflow remains available
