# m9-governed-ml-lifecycle Specification

## ADDED Requirements

### Requirement: ML feature registry

ML feature definitions SHALL preserve stable identity, value type, source dataset, transformation description, creation time, and point-in-time safety.

#### Scenario: Feature is not point-in-time safe
- **WHEN** a feature definition declares that it is not point-in-time safe
- **THEN** validation fails closed

### Requirement: ML label registry

ML label definitions SHALL preserve stable identity, objective, horizon, source dataset, creation time, and leakage-check evidence.

#### Scenario: Label has not passed leakage checks
- **WHEN** a label definition lacks leakage-check evidence
- **THEN** validation fails closed

### Requirement: ML training workflow metadata

ML training workflows SHALL preserve trainer identity, feature set, label identity, split policy, parameter-set identity, and creation time.

#### Scenario: Workflow repeats a feature
- **WHEN** a training workflow repeats a feature identifier
- **THEN** validation fails closed

### Requirement: ML model artifact registry

ML model artifacts SHALL preserve immutable artifact identity, experiment identity, model family, artifact URI, artifact digest, lifecycle status, and creation time.

#### Scenario: Artifact digest lacks algorithm
- **WHEN** a model artifact digest omits its digest algorithm
- **THEN** validation fails closed

### Requirement: ML evaluation and calibration

ML evaluation reports SHALL preserve split-scoped metrics and calibration methodology, and require holdout metrics.

#### Scenario: Evaluation lacks holdout metrics
- **WHEN** an evaluation report omits holdout metrics
- **THEN** validation fails closed

### Requirement: ML promotion gate

ML promotion decisions SHALL fail closed when quality findings contain errors or required holdout thresholds are not met.

#### Scenario: Promotion has error finding
- **WHEN** an ML promotion decision contains an error finding
- **THEN** event-validation approval is rejected

### Requirement: M9 manual testing update

M9 SHALL review and update the manual testing and usage baseline for ML lifecycle operator-visible behavior.

#### Scenario: M9 changes operator-visible ML behavior
- **WHEN** M9 adds ML lifecycle contracts or usage surfaces
- **THEN** the manual testing and usage baseline includes M9-specific smoke checks

### Requirement: ML lifecycle metadata persistence

ML lifecycle metadata SHALL be persisted with stable record identity and queryable workflow, experiment, and model-artifact scopes without executing training.

#### Scenario: ML lifecycle records are persisted
- **WHEN** ML lifecycle records are saved
- **THEN** they can be queried by their governed workflow, experiment, or model artifact identity
