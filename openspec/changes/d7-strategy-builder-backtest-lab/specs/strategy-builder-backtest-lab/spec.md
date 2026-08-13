# strategy-builder-backtest-lab Specification

## ADDED Requirements

### Requirement: Profile-scoped strategy definitions

D7 SHALL provide profile-scoped strategy definitions with immutable version records.

#### Scenario: Strategy edit creates a version
- **GIVEN** a saved strategy
- **WHEN** the user changes a rule and saves
- **THEN** the previous version remains inspectable
- **AND** the updated strategy points at a new immutable version.

### Requirement: Typed declarative strategy DSL

D7 SHALL express strategies through a typed declarative DSL and guided templates, not arbitrary executable code.

#### Scenario: Executable snippets are rejected
- **WHEN** a strategy definition includes arbitrary code, SQL, shell commands, notebooks, provider calls, broker instructions, or filesystem access
- **THEN** validation rejects the strategy before execution.

### Requirement: Rule and data-integrity validation

D7 SHALL validate rule compatibility, unsupported combinations, look-ahead hazards, and dataset integrity before running a backtest.

#### Scenario: Look-ahead rule is blocked
- **GIVEN** a strategy that references future observations
- **WHEN** validation runs
- **THEN** the backtest cannot start
- **AND** the user sees a clear explanation.

### Requirement: Python-authoritative backtest execution

D7 SHALL run backtests through Python services against governed dataset revisions and retain complete provenance.

#### Scenario: Run records provenance
- **WHEN** a backtest completes
- **THEN** the result records the strategy version, dataset revision, engine, fidelity level, assumptions, parameters, producer version, warnings, and digest.

### Requirement: Explicit fidelity and assumptions

D7 SHALL disclose fidelity level, costs, slippage, fills, cash, sizing, risk controls, and benchmark assumptions before and after execution.

#### Scenario: Assumptions are visible
- **WHEN** a user reviews a backtest result
- **THEN** the assumptions are visible with the result evidence
- **AND** are included in export.

### Requirement: Deterministic result evidence

D7 SHALL produce deterministic metrics, equity curves, drawdowns, trade lists, exposure summaries, and benchmark comparisons without mutating source datasets or strategy versions.

#### Scenario: Repeated run is reproducible
- **GIVEN** the same strategy version, dataset revision, parameters, and assumptions
- **WHEN** the backtest is rerun
- **THEN** deterministic result values and digests match.

### Requirement: Sensitivity and walk-forward evidence

D7 SHALL provide bounded sensitivity and walk-forward evaluations with explicit budgets, train/test ranges, cancellation behavior, and overfitting warnings.

#### Scenario: Future observations remain isolated
- **WHEN** a walk-forward evaluation runs
- **THEN** earlier windows cannot use future test observations
- **AND** the train/test ranges are visible.

### Requirement: Accessible Strategy Lab UI

D7 SHALL provide keyboard, pointer, screen-reader, reduced-motion, forced-colors, and responsive operation for strategy definition, result inspection, chart/table parity, and export controls.

#### Scenario: Synchronized values are inspectable
- **WHEN** the user inspects a chart observation with keyboard or pointer
- **THEN** the corresponding table/result values are synchronized
- **AND** x-axis and y-axis labels remain readable.

### Requirement: D6 project integration

D7 SHALL allow strategy definitions and backtest results to be pinned into D6 projects as typed governed references without duplicating large provider datasets.

#### Scenario: Project pin preserves reference
- **WHEN** a user pins a D7 result into a D6 project
- **THEN** the project stores a typed reference and degraded-state metadata
- **AND** does not copy provider dataset payloads.

### Requirement: Research-only boundary

D7 SHALL preserve OSCA's research-only/no-recommendation/no-execution boundary.

#### Scenario: Execution paths are absent
- **WHEN** D7 is used from the desktop app
- **THEN** there is no brokerage, paper-order, live-order, real-capital, automatic-promotion, credential-collection, or recommendation path.

### Requirement: Offline supported operation

D7 SHALL remain usable with local, sample, or cached governed data without paid providers, network access, external accounts, or credentials.

#### Scenario: Offline backtest uses local evidence
- **GIVEN** network access is unavailable
- **WHEN** the user runs or reopens a D7 workflow using retained local data
- **THEN** the workflow remains usable without external accounts.

### Requirement: Retained validation and exit evidence

D7 SHALL retain requirements, OpenSpec, traceability, migration/recovery evidence, automated validation, supported-platform manual acceptance, limitations, and accepted exit review evidence.

#### Scenario: Exit is evidence-backed
- **WHEN** D7 is marked accepted
- **THEN** validation evidence identifies exact automated runs, manual platforms, residual limitations, and exit decision.
