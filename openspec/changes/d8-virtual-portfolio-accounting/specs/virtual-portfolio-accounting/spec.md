# Virtual-Portfolio Accounting Specification

## ADDED Requirements

### Requirement: Multiple independent virtual portfolios
The system SHALL support multiple profile-scoped virtual portfolios with stable identity, base currency, lifecycle, starting-cash evidence, and optional source lineage.

#### Scenario: Independent creation
- **WHEN** two portfolios are created in one profile
- **THEN** each has independent identity, journal sequence, cash, and projections

### Requirement: Append-only balanced accounting authority
Every accepted economic event SHALL produce immutable balanced journal evidence using decimal-safe arithmetic.

#### Scenario: Balanced transaction
- **WHEN** an economic event is accepted
- **THEN** every generated journal transaction balances by currency and can be replayed from its source event

#### Scenario: Conflicting identity reuse
- **WHEN** an existing event/journal identity is submitted with different canonical content
- **THEN** the operation fails closed without modifying retained evidence

### Requirement: Rebuildable portfolio projections
Cash, positions, lots, book cost, realized/unrealized P&L, fees, income, exposure, allocation, equity, and drawdown SHALL be derived from retained evidence.

#### Scenario: Replay
- **WHEN** the same retained journal and valuation evidence is replayed
- **THEN** the resulting projection is deterministic

### Requirement: Explicit lot disposal semantics
The system SHALL NOT silently choose a tax-oriented disposal policy when multiple lots are eligible.

#### Scenario: Ambiguous disposal
- **WHEN** a disposal can consume more than one open lot and no allocation is supplied
- **THEN** the request is rejected with remediation to provide explicit lot allocations

### Requirement: Idempotent corporate actions
Splits, dividends/distributions, and crypto forks SHALL retain source identity and be safe to retry.

#### Scenario: Duplicate split source
- **WHEN** the same split source identity is submitted twice
- **THEN** holdings change once and retained evidence is not duplicated

### Requirement: Provenanced multi-currency valuation
Valuations SHALL retain price and FX source/effective-time/revision evidence and surface missing evidence explicitly.

#### Scenario: Missing FX
- **WHEN** a non-base holding lacks required FX evidence
- **THEN** the projection is degraded instead of inventing a conversion

### Requirement: Non-destructive lifecycle tools
Clone/reset/export/restore SHALL preserve source history and validate evidence before mutation.

#### Scenario: Reset
- **WHEN** a user resets a portfolio
- **THEN** a successor portfolio with reset lineage is created and the source journal remains unchanged

### Requirement: Desktop research-only surface
The desktop SHALL expose accounting evidence through Python authority without enabling recommendation, broker, live-order, real-capital, or arbitrary-code paths.

#### Scenario: Offline acceptance
- **WHEN** D8 is exercised with local/synthetic evidence and no provider account
- **THEN** portfolio accounting remains usable without network access
