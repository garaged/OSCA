# p16-live-order-readiness-study Specification

## Purpose

Govern the study-only decision on whether OSCA may proceed toward real-money order execution.

## Requirements

### Requirement: Threat model

P16 SHALL identify assets, trust boundaries, threats, abuse cases, and residual risk for capital execution.

#### Scenario: Readiness is assessed
- **GIVEN** OSCA's current research, operations, and extension capabilities
- **WHEN** live-order readiness is reviewed
- **THEN** technical, financial, credential, venue, operational, and legal threats are documented.

### Requirement: Mandatory controls

P16 SHALL define mandatory controls for authorization, separation, credentials, limits, idempotency, venue state, reconciliation, kill switches, monitoring, audit, testing, release, and incident response.

#### Scenario: A future implementation is proposed
- **GIVEN** the P16 control matrix
- **WHEN** any blocker remains unresolved
- **THEN** the proposal remains NO-GO.

### Requirement: Legal and accountability boundaries

P16 SHALL identify questions requiring qualified external review and named accountable owners without asserting unsupported legal conclusions.

#### Scenario: Legal applicability is unknown
- **GIVEN** an unspecified jurisdiction, venue, account, or user model
- **WHEN** readiness is evaluated
- **THEN** OSCA records the uncertainty as a blocker rather than assuming permission.

### Requirement: Explicit decision

P16 SHALL record a go/no-go ADR.

#### Scenario: P16 decision is recorded
- **GIVEN** unresolved independent authorization, limits, reconciliation, credential, kill-switch, and legal controls
- **WHEN** ADR-0044 is accepted
- **THEN** real-money execution remains NO-GO.

### Requirement: Deferred-boundary enforcement

P16 SHALL add no broker adapter, trading credential, order submission, sandbox/production order, autonomous execution, or capital pilot behavior.

#### Scenario: P17 or an order path is requested
- **GIVEN** ADR-0044 has not been superseded
- **WHEN** live execution is proposed
- **THEN** the behavior remains unauthorized and absent or policy-blocked.

### Requirement: Reconsideration and evidence

P16 SHALL require closure of all control blockers, qualified review, and a superseding ADR before reconsideration, while retaining traceability and hosted validation evidence.

#### Scenario: Completion is requested
- **GIVEN** the P16 study artifacts
- **WHEN** completion is evaluated
- **THEN** requirements, ADR indexing, traceability, OpenSpec, exit review, links, secret scanning, and hosted Quality are current.
