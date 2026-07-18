## ADDED Requirements

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
