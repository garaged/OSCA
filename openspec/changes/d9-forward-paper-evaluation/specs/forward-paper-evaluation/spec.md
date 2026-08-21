# Forward Paper Evaluation Specification

## ADDED Requirements

### Requirement: Explicit simulated-order confirmation
The system SHALL retain immutable simulated-order drafts and SHALL require explicit user confirmation before a draft can become active simulated-order authority.

#### Scenario: Confirm draft
- **WHEN** a user confirms one immutable draft version
- **THEN** OSCA retains a simulated-only confirmation and creates no external venue request

### Requirement: Point-in-time safe bar evaluation
The fill engine SHALL consume only governed complete bar evidence that was temporally eligible after the order became active.

#### Scenario: Mid-bar activation
- **WHEN** an order becomes eligible after a bar has started
- **THEN** that bar is skipped rather than using OHLCV to infer an unknown post-activation path

### Requirement: Deterministic simulated fill semantics
Market, limit, stop, and scheduled market orders SHALL use documented deterministic rules with retained assumptions and no tick/order-book invention.

#### Scenario: Stop gaps through trigger
- **WHEN** an eligible bar opens beyond a stop trigger
- **THEN** the open is the execution reference before adverse spread/slippage assumptions are applied

#### Scenario: Limit price protection
- **WHEN** adverse execution assumptions would require a limit-order fill beyond its limit
- **THEN** the order does not fill at the invalid price

### Requirement: Bounded liquidity and partial fills
The system SHALL apply explicit bar-volume participation limits and SHALL retain deterministic partial fills.

#### Scenario: Missing required volume
- **WHEN** a liquidity model requires volume and the eligible bar lacks valid volume evidence
- **THEN** filling is blocked/degraded rather than assuming unlimited liquidity

### Requirement: Append-only order lifecycle
Order lifecycle, fills, cancellation, expiry, rejection, checkpoints, and recovery SHALL be append-only and idempotent.

#### Scenario: Recovery after accepted fill
- **WHEN** a run restarts after a fill was retained and posted to accounting
- **THEN** recovery resumes without creating a duplicate fill or accounting event

### Requirement: Deterministic risk controls
Paper account controls and portfolio-derived risk gates SHALL run before activation and before each fill and SHALL fail closed on violations.

#### Scenario: Insufficient cash
- **WHEN** a simulated buy would violate cash/risk requirements
- **THEN** the fill is rejected/blocked with retained reason evidence and D8 accounting is unchanged

### Requirement: D8 accounting integration
Every accepted simulated fill SHALL post exactly once into the bound D8 virtual portfolio and SHALL preserve fill/data/assumption lineage.

#### Scenario: Ambiguous disposal lots
- **WHEN** a simulated sell can consume more than one D8 lot and no explicit allocation is supplied
- **THEN** the fill is blocked until explicit lot allocation is provided

### Requirement: Research-only desktop Paper Lab
The desktop SHALL expose paper drafts, confirmation, lifecycle, fills, assumptions, checkpoints, accounting effects, and descriptive comparisons through Python authority while exposing no broker/live-order/real-capital path.

#### Scenario: Offline paper evaluation
- **WHEN** D9 is exercised with local/synthetic governed bars and no external accounts
- **THEN** the forward paper workflow remains usable without network or paid-provider dependency
