# p6-local-ohlcv-import-provider Specification

## Purpose

Index the planned P6 semantics for No-Cost Local OHLCV Import Provider.

## Requirements

### Requirement: P6 milestone scope

P6 SHALL implement the governed scope in docs/specifications/p6-local-ohlcv-import-provider.md before it is marked complete.

#### Scenario: P6 scope is reviewed
- **GIVEN** the P6 milestone specification
- **WHEN** implementation readiness is reviewed
- **THEN** objective, user-visible value, implementation scope, non-scope, acceptance criteria, validation gates, dependencies, and risks are documented.

### Requirement: P6 deferred-boundary enforcement

P6 SHALL preserve explicit deferred boundaries for behavior outside its approved scope.

#### Scenario: Out-of-scope behavior is attempted
- **GIVEN** a P6 implementation
- **WHEN** a caller attempts deferred behavior
- **THEN** OSCA fails closed or reports a policy-blocked state rather than silently enabling the behavior.

### Requirement: P6 evidence retention

P6 SHALL retain requirements, traceability, OpenSpec, manual-testing review, automated validation, and hosted Quality evidence.

#### Scenario: P6 completion is requested
- **GIVEN** P6 implementation work
- **WHEN** completion is evaluated
- **THEN** exit review evidence must identify implemented, specified-only, fixture-backed, and deferred behavior.

### Requirement: Local OHLCV canonical import

P6 SHALL import user-supplied CSV and Parquet OHLCV files using the canonical timestamp, open, high, low, close, and volume schema.

#### Scenario: Valid local CSV is imported
- **GIVEN** a local CSV file with timezone-aware strictly increasing OHLCV rows
- **WHEN** the operator runs the local OHLCV import command
- **THEN** OSCA writes a Parquet payload, SQLite metadata, source checksum, row count, timestamp range, and dataset revision identity without using network access.

#### Scenario: Invalid local file is rejected
- **GIVEN** a local OHLCV file with missing columns or non-increasing timestamps
- **WHEN** import validation runs
- **THEN** OSCA fails closed and does not treat the file as an accepted dataset revision.

### Requirement: P6 local-only boundary

P6 SHALL keep live provider calls, credential materialization, runtime provider routing, production ingestion, and real-capital orders disabled.

#### Scenario: Import result reports deferred boundaries
- **GIVEN** a successful local OHLCV import
- **WHEN** the import result is inspected
- **THEN** the result reports network access disabled and preserves the deferred-boundary flags.
