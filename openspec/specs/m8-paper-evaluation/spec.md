# m8-paper-evaluation Specification

## Requirements

### Requirement: Independent paper accounts

Paper accounts SHALL preserve stable identity, base currency, lifecycle status, creation time, and independence from research-project mutable state.

#### Scenario: Paper account is created
- **WHEN** a paper account is represented
- **THEN** it has stable identity, base currency, status, and timezone-aware creation time

### Requirement: Approved candidate linkage

Paper evaluation candidates SHALL reference an approved M7 promotion gate.

#### Scenario: Promotion gate is blocked
- **WHEN** a blocked M7 promotion gate is used
- **THEN** paper candidate approval fails closed

### Requirement: Paper run request identity

Paper evaluation requests SHALL declare paper account, approved candidate, promotion gate, explicit data requirements, optional schedule identity, and timezone-aware request time.

#### Scenario: Paper run is requested
- **WHEN** a paper run request is created
- **THEN** it preserves account, candidate, gate, data requirement, and request-time identity

### Requirement: Health gate authority

Paper processing SHALL be blocked when data or operational health gates are blocked or when error findings exist.

#### Scenario: Health gate has an error
- **WHEN** a health gate contains an error finding
- **THEN** paper processing is not allowed

### Requirement: Pause and kill-switch controls

Paper account pause and system kill-switch state SHALL be explicit deterministic evidence.

#### Scenario: Kill switch is engaged
- **WHEN** the system paper kill switch is engaged
- **THEN** paper processing is not allowed

### Requirement: Backtest-versus-forward comparison

Forward comparison records SHALL preserve F2 request, F2 promotion gate, F3 paper run, metric methodology, findings, and comparison time.

#### Scenario: Comparison is recorded
- **WHEN** forward outcome is compared against F2 evidence
- **THEN** the record preserves both F2 and F3 identities


### Requirement: Durable paper schedule identity

Paper schedules SHALL preserve paper account, paper run, cadence, timezone, optional market calendar, missed-run policy, status, and timezone-aware start time.

#### Scenario: Market-aware schedule lacks calendar
- **WHEN** a market-open or market-close schedule omits market calendar identity
- **THEN** schedule validation fails closed

### Requirement: Non-replay recovery decision

Paper recovery SHALL use checkpoints and missed-run policy to decide whether processing can resume, skip missed work, or remain blocked.

#### Scenario: Recovery finding has error
- **WHEN** recovery findings include an error
- **THEN** recovery remains blocked and cannot resume


### Requirement: Paper metadata persistence

Paper evaluation metadata SHALL be persisted with stable record identity and queryable account or paper-run scope without executing paper automation.

#### Scenario: Paper records are persisted
- **WHEN** paper account, run, gate, control, schedule, recovery, and comparison records are saved
- **THEN** they can be queried by paper account or paper run identity


### Requirement: Notification inbox and digest boundary

Paper notifications SHALL be retained as inbox records and digest inputs before delivery adapter execution.

#### Scenario: Digest is generated
- **WHEN** a digest is generated from notification identities
- **THEN** it preserves paper run and notification identity

### Requirement: Delivery adapter declaration

Delivery adapters SHALL declare configuration and enabled state before delivery attempts are planned.

#### Scenario: Adapter is disabled
- **WHEN** a delivery attempt is planned for a disabled adapter
- **THEN** the attempt is skipped without external delivery
