# m3-temporal-correctness Specification

## Purpose

Define the accepted M3 temporal correctness semantics for approved intervals, UTC bar windows, stock exchange sessions, crypto UTC boundaries, completed bars, calendar-aware gaps, and resampling lineage.

## Requirements

### Requirement: Approved interval contract

Market Data SHALL support exactly `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, and `1d` interval identifiers for M3 interval-aware contracts.

#### Scenario: Unknown interval
- **WHEN** a caller supplies an interval outside the approved set
- **THEN** validation fails closed before retrieval, repair, publication, or resampling

### Requirement: Completed-bar semantics

Every interval bar SHALL use UTC start-inclusive/end-exclusive windows and SHALL be complete only when its interval end plus declared publication lag has passed.

#### Scenario: Current interval is still open
- **WHEN** a requested window ends after the completed-bar cutoff
- **THEN** it is classified incomplete and is not repair eligible

### Requirement: Stock session-aware gaps

Stock expected windows SHALL be derived from accepted exchange-session evidence.

#### Scenario: Calendar evidence is unavailable
- **WHEN** a stock session is not accepted for a requested interval
- **THEN** the interval is unresolved rather than missing and repair is not automatic

### Requirement: Crypto UTC boundaries

Crypto expected windows SHALL be derived from UTC day boundaries.

#### Scenario: Completed crypto interval missing
- **WHEN** a crypto interval has closed under the UTC boundary model and no observation exists
- **THEN** it is missing and repair eligible

### Requirement: Resampling lineage

Resampling SHALL derive higher intervals only from contiguous complete lower-interval bars and SHALL record every source bar identity.

#### Scenario: Lower interval coverage is partial
- **WHEN** the source bars do not fully cover the target window
- **THEN** no higher-interval bar is published
