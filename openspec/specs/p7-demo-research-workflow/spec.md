# p7-demo-research-workflow Specification

## Purpose

Index the planned P7 semantics for First Demo Research Workflow.

## Requirements

### Requirement: P7 milestone scope

P7 SHALL implement the governed scope in docs/specifications/p7-demo-research-workflow.md before it is marked complete.

#### Scenario: P7 scope is reviewed
- **GIVEN** the P7 milestone specification
- **WHEN** implementation readiness is reviewed
- **THEN** objective, user-visible value, implementation scope, non-scope, acceptance criteria, validation gates, dependencies, and risks are documented.

### Requirement: P7 deferred-boundary enforcement

P7 SHALL preserve explicit deferred boundaries for behavior outside its approved scope.

#### Scenario: Out-of-scope behavior is attempted
- **GIVEN** a P7 implementation
- **WHEN** a caller attempts deferred behavior
- **THEN** OSCA fails closed or reports a policy-blocked state rather than silently enabling the behavior.

### Requirement: P7 evidence retention

P7 SHALL retain requirements, traceability, OpenSpec, manual-testing review, automated validation, and hosted Quality evidence.

#### Scenario: P7 completion is requested
- **GIVEN** P7 implementation work
- **WHEN** completion is evaluated
- **THEN** exit review evidence must identify implemented, specified-only, fixture-backed, and deferred behavior.


### Requirement: P6 payload demo research report

P7 SHALL produce a deterministic demo research report from canonical local OHLCV payloads created by P6.

#### Scenario: Local payload is analyzed
- **GIVEN** a canonical P6 OHLCV Parquet payload
- **WHEN** the operator runs the demo research report command
- **THEN** OSCA returns CLI JSON with watchlist identity, metric summary, quality summary, evidence-only observations, and disabled deferred-boundary flags.

#### Scenario: Static report is requested
- **GIVEN** a canonical P6 OHLCV Parquet payload and output file path
- **WHEN** the report workflow runs
- **THEN** OSCA writes a Markdown or JSON report file without invoking provider APIs.

#### Scenario: Invalid payload is rejected
- **GIVEN** a payload missing required OHLCV columns
- **WHEN** the report workflow validates the payload
- **THEN** OSCA fails closed instead of producing an accepted research report.

### Requirement: P7 no-advice boundary

P7 SHALL report deterministic observations without recommendations, financial advice, ML execution, or LLM execution.

#### Scenario: Report boundaries are inspected
- **GIVEN** a successful demo research report
- **WHEN** the report is inspected
- **THEN** it states evidence-only and not-financial-advice semantics and reports recommendations, ML execution, and LLM execution as disabled.
