# m6-backtesting-foundation Specification

## Purpose

Index the verified M6 backtesting request, fidelity profile, point-in-time validation, execution-planning, lifecycle persistence, operator administration, simulated order-intent, and result-metric semantics under REQ-0085-REQ-0092 and ADR-0032.

## Requirements

### Requirement: Backtest request identity

Backtest requests SHALL declare project identity, strategy identity, fidelity profile, execution mode, bounded timezone-aware window, pinned dataset revisions, data availability, assumptions, and optional deterministic seed.

#### Scenario: Event-driven request is represented
- **WHEN** a request declares F2 event-driven bar simulation with point-in-time dataset revisions and pinned assumptions
- **THEN** the request preserves those identities and can be validated before execution

### Requirement: Fidelity profile compatibility

Backtest execution planning SHALL require each fidelity profile to use its compatible execution mode.

#### Scenario: Event-driven profile uses vectorized mode
- **WHEN** an F2 event-driven bar request declares vectorized execution
- **THEN** planning fails closed with an execution-mode mismatch finding

### Requirement: Point-in-time enforcement

Backtest execution planning SHALL reject revised-after-fact data availability.

#### Scenario: Revised data is provided
- **WHEN** a backtest request uses data marked revised after the fact
- **THEN** planning fails closed before execution

### Requirement: Provisional data protection

Event-driven and forward-paper profiles SHALL reject provisional data.

#### Scenario: Provisional event-driven data is provided
- **WHEN** an F2 request uses provisional data
- **THEN** planning fails closed before execution

### Requirement: Simulated order intent boundary

Strategy decisions and order intents SHALL retain evidence and decision linkage without implying live brokerage or exchange execution.

#### Scenario: Strategy decision produces order intent
- **WHEN** a strategy decision creates a simulated order intent
- **THEN** the order intent links to the decision and remains a backtesting contract

### Requirement: Execution plan checks

Execution plans SHALL disclose required checks and SHALL NOT be executable when error findings exist.

#### Scenario: Planning has error findings
- **WHEN** validation reports an error
- **THEN** the execution plan is not executable

### Requirement: Backtest result metrics

Completed backtest results SHALL include at least one typed metric with methodology metadata.

#### Scenario: Completed result has no metrics
- **WHEN** a completed result is constructed without metrics
- **THEN** validation rejects it

### Requirement: Backtest lifecycle persistence

Backtest requests, execution plans, and results SHALL be persisted in governed SQLite metadata storage with stable identifiers and queryable lifecycle history.

#### Scenario: Result saved for request
- **WHEN** a backtest result is saved for a stored request
- **THEN** the result can be queried by result identity and request identity

### Requirement: Operator backtest administration

The CLI SHALL expose metadata-only backtest request planning and request-listing operations backed by the lifecycle store.

#### Scenario: Local owner plans request metadata
- **WHEN** a local owner plans a backtest request through the CLI
- **THEN** the request and execution plan are persisted without executing a strategy

### Requirement: M6 scope boundary

M6 SHALL NOT implement event matching, fills, portfolio accounting, paper journals, runtime strategy execution, ML, LLM, paper trading, or live execution.

#### Scenario: Forward-paper execution is requested
- **WHEN** an F3 forward-paper request is planned before paper-account authority exists
- **THEN** planning fails closed
