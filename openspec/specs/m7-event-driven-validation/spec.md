# m7-event-driven-validation Specification

## Purpose

Index the verified M7 F2 event-driven validation behavior under REQ-0093-REQ-0101 and ADR-0033.

## Requirements

### Requirement: Event stream identity

F2 validation SHALL represent market, clock, order, fill, risk, valuation, and accounting events with stable typed identity and timezone-aware effective time.

#### Scenario: Event has timezone-aware time
- **WHEN** an F2 event is created
- **THEN** it preserves stable identity, type, and effective time

### Requirement: Order lifecycle authority

Order lifecycle events SHALL retain simulated order-intent links and SHALL reject invalid lifecycle regressions.

#### Scenario: Filled order is cancelled later
- **WHEN** a lifecycle sequence attempts to cancel a filled order
- **THEN** validation fails closed

### Requirement: Simulated fill model metadata

Simulated fills SHALL identify fill model, market observation, price, quantity, fees, spread, slippage, latency, liquidity, and partial-fill status where applicable.

#### Scenario: Fill is represented
- **WHEN** a simulated fill is recorded
- **THEN** it retains model and market-observation lineage

### Requirement: Deterministic risk outcomes

F2 validation SHALL represent deterministic risk decisions that approve, modify, reject, or pause simulated order processing with policy version and rationale.

#### Scenario: Risk decision is represented
- **WHEN** a risk policy evaluates an order intent
- **THEN** the resulting decision retains action, policy version, and rationale

### Requirement: Balanced journal transactions

Journal transactions SHALL balance by currency.

#### Scenario: Transaction is imbalanced
- **WHEN** journal lines do not sum to zero for each currency
- **THEN** validation rejects the transaction

### Requirement: Multi-currency valuation evidence

F2 valuation snapshots SHALL retain base currency, priced holdings, price source, FX source when applicable, effective time, and valuation version.

#### Scenario: Valuation is represented
- **WHEN** a valuation snapshot includes holdings
- **THEN** it retains source identity and effective time

### Requirement: Rebuildable projections

F2 portfolio projections SHALL identify the journal and valuation evidence required for rebuild.

#### Scenario: Projection is represented
- **WHEN** a portfolio projection is created
- **THEN** it references journal transaction identities and valuation identity

### Requirement: Promotion gate evidence

Promotion gates SHALL disclose blocking findings and SHALL NOT activate F3 paper trading.

#### Scenario: Gate has blockers
- **WHEN** blocking findings exist
- **THEN** the promotion gate is not approved

### Requirement: F2 validation persistence

F2 validation records SHALL be persisted as metadata records scoped by request identity and record type.

#### Scenario: Validation records are persisted
- **WHEN** lifecycle, fill, journal, valuation, projection, and promotion-gate records are saved
- **THEN** they can be queried by request identity without executing paper trading
