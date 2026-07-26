# p17-real-money-controlled-pilot Specification

## Purpose

Index the planned P17 semantics for Real-Money Controlled Pilot.

## Requirements

### Requirement: P17 milestone scope

P17 SHALL implement the governed scope in docs/specifications/p17-real-money-controlled-pilot.md before it is marked complete.

#### Scenario: P17 scope is reviewed
- **GIVEN** the P17 milestone specification
- **WHEN** implementation readiness is reviewed
- **THEN** objective, user-visible value, implementation scope, non-scope, acceptance criteria, validation gates, dependencies, and risks are documented.

### Requirement: P17 deferred-boundary enforcement

P17 SHALL preserve explicit deferred boundaries for behavior outside its approved scope.

#### Scenario: Out-of-scope behavior is attempted
- **GIVEN** a P17 implementation
- **WHEN** a caller attempts deferred behavior
- **THEN** OSCA fails closed or reports a policy-blocked state rather than silently enabling the behavior.

### Requirement: P17 evidence retention

P17 SHALL retain requirements, traceability, OpenSpec, manual-testing review, automated validation, and hosted Quality evidence.

#### Scenario: P17 completion is requested
- **GIVEN** P17 implementation work
- **WHEN** completion is evaluated
- **THEN** exit review evidence must identify implemented, specified-only, fixture-backed, and deferred behavior.
