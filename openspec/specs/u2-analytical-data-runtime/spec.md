# u2-analytical-data-runtime Specification

## Purpose

Provide governed chart-ready OHLCV and point-in-time derived analytical series for visualization, analysis, and later ML experiments.

## Requirements

### Requirement: Governed chart-series query

U2 SHALL return bounded chart rows only from an explicitly identified governed dataset revision.

#### Scenario: Chart data is requested
- **GIVEN** a valid OHLCV dataset revision and bounded range
- **WHEN** the operator requests chart-series data
- **THEN** timestamp, OHLC, volume, interval, completeness, source, revision, and provenance are returned.

#### Scenario: Query is unbounded or invalid
- **WHEN** the requested range, revision, or row budget is invalid
- **THEN** the request fails closed without silently selecting another dataset.

### Requirement: Point-in-time derived series

U2 SHALL compute derived series without using observations later than each output timestamp.

#### Scenario: A derived series is computed
- **WHEN** returns, SMA, EMA, rolling volatility, or rolling volume are requested
- **THEN** definition identity, parameters, warm-up/null values, input digest, output digest, and point-in-time status are retained.

### Requirement: Deterministic large-series handling

U2 SHALL enforce bounded output and deterministic downsampling.

#### Scenario: Source data exceeds the chart budget
- **WHEN** a valid large series is requested
- **THEN** deterministic downsampling is applied and its preservation rules are reported.

### Requirement: Safety boundaries

U2 SHALL perform no provider network calls, credential access, recommendations, broker actions, or real-capital behavior.
