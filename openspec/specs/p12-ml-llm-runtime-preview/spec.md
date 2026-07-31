# p12-ml-llm-runtime-preview Specification

## Purpose

Govern optional local model-assisted previews with budgets, provenance, review, and fail-closed controls.

## Requirements

### Requirement: Deterministic local preview

P12 SHALL provide a deterministic zero-cost local trend preview over explicit numeric evidence.

#### Scenario: Local trend succeeds
- **GIVEN** at least three numeric values within budget
- **WHEN** the local preview runs
- **THEN** it records exact model identity, input digest, metrics, output, zero cost, and disabled network/recommendation/order boundaries.

#### Scenario: Local input exceeds budget
- **GIVEN** more records than the approved budget
- **WHEN** the local preview is requested
- **THEN** it returns `budget_exceeded` without output.

### Requirement: Governed LLM fixture preview

P12 SHALL permit fixture-backed LLM analysis with exact provider, model, prompt, budget, and review evidence.

#### Scenario: Fixture analysis is generated
- **GIVEN** explicit input, exact identities, budgets, and a fixture response
- **WHEN** the preview runs with network disabled
- **THEN** it returns `review_required`, retains the fixture output, and records human-review and not-financial-advice findings.

#### Scenario: No fixture is available
- **GIVEN** network access is disabled and no fixture response exists
- **WHEN** LLM analysis is requested
- **THEN** the preview returns `policy_blocked` without output.

#### Scenario: Live executor is absent
- **GIVEN** a caller explicitly checks live model mode
- **WHEN** no governed executor is configured
- **THEN** the preview returns `provider_unavailable` without network use or credential resolution.

### Requirement: Evidence retention

P12 SHALL retain immutable preview evidence atomically under the configured storage root.

#### Scenario: Evidence is retained
- **GIVEN** any completed preview decision
- **WHEN** retention is requested
- **THEN** the exact request linkage, status, identities, digest, output, metrics, findings, cost, latency, and safety boundaries are persisted.

### Requirement: Deferred-boundary enforcement

P12 SHALL NOT enable production serving, recommendations, brokers, autonomous actions, or real-capital orders.

#### Scenario: Evidence is validated
- **GIVEN** preview evidence
- **WHEN** a forbidden capability is marked enabled
- **THEN** contract validation fails closed.
