# m7-event-driven-validation Specification

## Purpose

Define the initial M7 F2 event-driven validation behavior under REQ-0093-REQ-0101 and ADR-0033.

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

### Requirement: Balanced journal transactions

Journal transactions SHALL balance by currency.

#### Scenario: Transaction is imbalanced
- **WHEN** journal lines do not sum to zero for each currency
- **THEN** validation rejects the transaction

### Requirement: Promotion gate evidence

Promotion gates SHALL disclose blocking findings and SHALL NOT activate F3 paper trading.

#### Scenario: Gate has blockers
- **WHEN** blocking findings exist
- **THEN** the promotion gate is not approved
