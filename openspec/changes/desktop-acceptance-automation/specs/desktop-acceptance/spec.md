# Desktop Acceptance Automation Specification

## ADDED Requirements

### Requirement: Deterministic desktop acceptance fixture

OSCA SHALL provide a reset-safe command that prepares a disposable local profile using only bundled synthetic data and the typed desktop application-service boundary.

#### Scenario: Critical-path profile is prepared

- **WHEN** a contributor runs the desktop acceptance seed command
- **THEN** it creates the D5 comparison, D6 project reference, and D7 strategy/backtest/evaluation evidence
- **AND** it retains a machine-readable manifest
- **AND** network access, recommendations, and real-capital execution remain disabled.

### Requirement: Bounded human acceptance

OSCA SHALL classify repeated desktop checks as automated, human judgment, or exploratory and provide a changed-surface human smoke test with a ten-minute time budget for normal milestones.

#### Scenario: A normal desktop change is reviewed

- **WHEN** automated desktop acceptance has passed
- **THEN** the reviewer performs only the documented visual, usability, and changed-surface checks
- **AND** does not repeat historical D5--D7 setup unless the change affects it.
