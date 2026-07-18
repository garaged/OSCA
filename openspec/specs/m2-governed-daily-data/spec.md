# m2-governed-daily-data Specification

## Purpose

Index the accepted M2 initiation controls for governed canonical instruments, provider selection, daily retrieval, evidence, and the M2/M3 boundary under REQ-0021–REQ-0040.

## Requirements

### Requirement: Governed M2 initiation

M2 implementation SHALL begin only after its intent, REQ-0021–REQ-0040 allocation, capability ownership, contracts, risk treatments, triggered decisions, acceptance criteria, and evidence plan are accepted by their named authorities.

#### Scenario: Implementation is requested before entry acceptance

- **WHEN** a provider, persistence, instrument, or market-data implementation is proposed before all M2 entry gates are accepted
- **THEN** the work remains blocked and no prototype establishes an architectural or product default

### Requirement: Evidence-gated provider selection

A production-visible M2 reference provider SHALL be selected only after official-access, licensing, quota, credential, semantic, fixture, and reproducible-failure evidence is reviewed.

#### Scenario: A technically accessible provider lacks rights evidence

- **WHEN** acquisition works but retention, transformation, fixture, export, or backup rights are uncertain
- **THEN** selection and affected operations fail closed

### Requirement: Protected M2/M3 boundary

M2 planning SHALL limit implementation to governed daily observations and SHALL defer intraday calendars, provisional bars, corporate actions, provider reconciliation, derived layers, and representative product-scale benchmarks to M3.

#### Scenario: M3 behavior is convenient during M2

- **WHEN** an M2 design could silently establish later temporal, reconciliation, or analytical semantics
- **THEN** the behavior is excluded or requires a separately governed scope decision

### Requirement: Provider-neutral instrument registration

The system SHALL persist immutable versioned stock and crypto-pair references whose canonical identity is independent of provider symbols.

#### Scenario: Duplicate identity

- **WHEN** registration supplies an existing canonical identity under a different display symbol
- **THEN** registration fails without creating another instrument

### Requirement: Governed provider mapping

The system SHALL activate only verified, time-aware mappings whose provider alias is unambiguous for the applicable interval.

#### Scenario: Ambiguous alias

- **WHEN** a verified alias overlaps a different canonical instrument
- **THEN** mapping activation fails before any canonical market-data write

### Requirement: One provider acquisition contract

Every M2 daily provider adapter SHALL publish the same versioned capability, request, result, observation, and failure semantics.

#### Scenario: Provider-specific limitation

- **WHEN** a provider has different authentication, quota, timestamp, rights, or quality limitations
- **THEN** the adapter expresses them as capability/policy metadata without changing canonical contract meaning

### Requirement: Offline deterministic conformance

Stock and crypto fixture adapters SHALL pass the same deterministic conformance suite without live networking or credentials.

#### Scenario: Rights uncertainty

- **WHEN** retrieval rights are false or uncertain
- **THEN** the adapter returns a policy failure and no observations
