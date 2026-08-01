# u7-model-research-validation Specification

## Purpose

Connect approved retained ML evidence to deterministic local research validation and evidence-only paper-challenger review without enabling live model serving, recommendations, brokers, or orders.

## Requirements

### Requirement: Human-gated F2 validation entry

U7 SHALL accept an experiment only when its matching U6 diagnostic is eligible for F2 validation and a named human promotion decision approves the local validation step.

#### Scenario: An experiment enters validation
- **GIVEN** a retained U5 classification experiment and matching eligible U6 diagnostic
- **WHEN** a named human approves promotion into local F2 validation
- **THEN** U7 may translate its retained test predictions into research signals.

#### Scenario: Promotion evidence is absent or rejected
- **GIVEN** a retained experiment without an approved human promotion decision
- **WHEN** U7 validation is requested
- **THEN** the request fails closed before any signal or result is created.

### Requirement: Versioned point-in-time signal translation

U7 SHALL translate retained out-of-sample classification predictions through a versioned long-only rule with explicit threshold, whole-bar latency, cost, slippage, and missing-prediction assumptions.

#### Scenario: A prediction becomes a research event
- **GIVEN** an aligned retained test prediction
- **WHEN** its probability crosses the configured threshold
- **THEN** the signal executes only after the configured latency at an eligible bar open and records its close, gross return, cost, and net return.

### Requirement: Baseline-relative event-driven evidence

U7 SHALL report aligned prediction counts, skipped predictions, invested periods, position changes, final equity, total return, maximum drawdown, costs, buy-and-hold return, and baseline excess return.

#### Scenario: Validation completes
- **GIVEN** one or more executable research events
- **WHEN** event-driven validation finishes
- **THEN** all event, summary, assumption, provenance, and digest evidence is exportable.

### Requirement: Separate paper-challenger approval

U7 SHALL require a second named human decision before designating a completed validation as a local evidence-only paper challenger.

#### Scenario: Paper challenger designation is requested
- **GIVEN** completed local validation
- **WHEN** a named reviewer supplies explicit rationale
- **THEN** the result may be marked paper-challenger-approved while broker and order capabilities remain disabled.

### Requirement: Safety boundaries

U7 SHALL keep live model serving, automatic promotion, recommendations, broker execution, and real-capital execution disabled.

#### Scenario: A U7 result is inspected
- **GIVEN** any completed validation result
- **WHEN** its capability flags are reviewed
- **THEN** every deferred serving, promotion, recommendation, broker, and real-capital boundary remains explicit and false.
