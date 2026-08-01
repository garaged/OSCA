# u6-prediction-lab Specification

## Purpose

Make retained U5 experiment evidence inspectable and comparable without retraining, automatic promotion, recommendations, or execution.

## Requirements

### Requirement: Retained-evidence diagnostics

U6 SHALL derive diagnostics only from an explicit retained U5 experiment result.

#### Scenario: An experiment is diagnosed
- **GIVEN** a valid retained U5 experiment result
- **WHEN** the U6 diagnostic runtime is called
- **THEN** it calculates diagnostics from the retained predictions, metrics, coefficients, and provenance without rerunning training.

### Requirement: Regression and classification diagnostics

U6 SHALL provide residual/error evidence for regression and confusion, calibration, ROC, and precision-recall evidence for probabilistic classification.

#### Scenario: Classification evidence is inspected
- **GIVEN** retained test predictions with probabilities
- **WHEN** diagnostics are produced
- **THEN** confusion counts, calibration bins, ROC points, and precision-recall points are exportable.

### Requirement: Baseline-relative comparison

U6 SHALL compare experiments of the same task using explicit improvement relative to each experiment's retained naive baseline.

#### Scenario: Two experiments are compared
- **GIVEN** two retained experiments for the same task
- **WHEN** comparison is requested
- **THEN** they are ordered by baseline-relative test performance and underperforming experiments are identified.

### Requirement: Interpretability warnings and review status

U6 SHALL expose coefficient evidence with non-causal warnings and assign exploratory, invalid, review-required, or eligible-for-F2-validation status.

#### Scenario: A diagnostic is reviewed
- **GIVEN** completed diagnostic evidence
- **WHEN** an operator inspects its status and coefficients
- **THEN** small-sample, baseline, and existing experiment findings affect status and coefficients are not presented as causal effects.

### Requirement: Safety boundaries

U6 SHALL keep automatic promotion, recommendations, brokers, autonomous execution, and real-capital execution disabled.

#### Scenario: Diagnostics are exported
- **GIVEN** a diagnostic result
- **WHEN** it is retained or returned through the workspace API
- **THEN** disabled promotion and execution boundaries remain explicit.
