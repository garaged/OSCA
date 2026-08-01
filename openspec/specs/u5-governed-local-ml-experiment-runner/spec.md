# u5-governed-local-ml-experiment-runner Specification

## Purpose

Provide reproducible local regression and classification experiments over governed OHLCV evidence without enabling automatic promotion, advice, or execution.

## Requirements

### Requirement: Governed point-in-time materialization

U5 SHALL materialize features and labels only from an explicit dataset revision and payload selected through the U2 analytical runtime.

#### Scenario: An experiment is requested
- **GIVEN** an explicit governed OHLCV payload and dataset revision
- **WHEN** the experiment runner is called
- **THEN** lagged features, future labels, payload digest, and feature/label definitions are retained.

### Requirement: Chronological leakage controls

U5 SHALL use chronological train, validation, and test partitions with horizon purge, optional embargo, and training-only transform fitting.

#### Scenario: A dataset is partitioned
- **GIVEN** enough chronological samples
- **WHEN** experiment splits are created
- **THEN** train ends before validation, validation ends before test, label overlap is purged, and scaling uses training observations only.

### Requirement: Transparent baseline and model execution

U5 SHALL provide naive regression/directional baselines and transparent linear, ridge, and logistic model execution.

#### Scenario: A model completes
- **GIVEN** a valid model/task combination
- **WHEN** local training completes
- **THEN** coefficients, intercept, validation/test predictions, metrics, baseline metrics, parameters, and digests are returned.

### Requirement: Fail-closed experiment validation

U5 SHALL reject insufficient samples, invalid splits, and incompatible task/model combinations.

#### Scenario: Experiment evidence is invalid
- **GIVEN** insufficient observations or incompatible parameters
- **WHEN** the request is validated or executed
- **THEN** no misleading experiment result is emitted.

### Requirement: Safety and promotion boundaries

U5 SHALL keep network access, credentials, remote trainers, automatic promotion, recommendations, broker execution, and real-capital execution disabled.

#### Scenario: An experiment result is inspected
- **GIVEN** a completed or review-required experiment
- **WHEN** its evidence is exported
- **THEN** point-in-time status and every disabled safety boundary remain explicit.
