# Charting and Quantitative Analysis Workbench

## ADDED Requirements

### Requirement: Python-authoritative numerical results
The desktop workbench SHALL render governed analytical results and SHALL NOT implement authoritative financial calculations in React.

#### Scenario: Indicator value reaches the chart
- **WHEN** a user enables a deterministic indicator
- **THEN** Python returns the indicator values and evidence through a typed desktop method
- **AND** React renders those returned values without recalculating the indicator

### Requirement: Synchronized chart and table
The workbench SHALL render chart and accessible table values from the same returned display result.

#### Scenario: Inspected candle matches table row
- **WHEN** a user inspects a displayed timestamp
- **THEN** its OHLCV and returned indicator values match the synchronized table row for that timestamp

### Requirement: Declared bounded downsampling
Large display results SHALL use declared deterministic downsampling and SHALL visibly distinguish displayed points from the full filtered analytical result.

#### Scenario: Large range exceeds display budget
- **GIVEN** a filtered series contains more rows than the display budget
- **WHEN** the workbench loads the range
- **THEN** Python returns no more than the requested display row budget
- **AND** the response declares its downsampling method and source, filtered, and displayed row counts
- **AND** required first and last boundary observations are preserved

### Requirement: Full-resolution evidence export
D5 data export SHALL use the full authoritative filtered result rather than the downsampled display result and SHALL include reproduction metadata.

#### Scenario: Export while chart is downsampled
- **GIVEN** the chart displays a downsampled subset
- **WHEN** the user exports analytical data
- **THEN** the export contains the full filtered row set
- **AND** metadata identifies canonical asset, dataset revision, timeframe/range, requested series definitions, row count, schema/version, and provenance digest

### Requirement: Compatible explicit comparisons
The workbench SHALL compare only governed series with compatible declared semantics and SHALL keep identity, timeframe, units/currency, provenance, and missing-data behavior explicit.

#### Scenario: Comparison semantics are incompatible
- **WHEN** two selected series cannot be validly compared under the requested mode
- **THEN** the service returns a typed incompatibility result
- **AND** the frontend does not silently join or normalize the series

### Requirement: Profile-scoped declarative saved views
The workbench SHALL persist profile-scoped declarative view configuration without copying or mutating analytical data.

#### Scenario: Saved view survives restart
- **WHEN** a user saves a workbench view and reopens the same profile
- **THEN** the canonical assets, range, indicator parameters, panes, comparison, and presentation configuration are restored
- **AND** a different profile does not expose that saved view

#### Scenario: Saved view cannot contain executable authority
- **WHEN** view configuration is validated for persistence
- **THEN** arbitrary code, SQL, credentials, secret values, provider URLs, and order instructions are rejected or absent from the schema

### Requirement: Narrow desktop authority
React SHALL use the existing `desktop_request` bridge for D5 operations, Python SHALL remain authoritative for analytical and persistence behavior, and Rust SHALL gain no numerical, database, network, secret, brokerage, or order authority.

#### Scenario: Workbench request crosses the desktop boundary
- **WHEN** React requests a chart, comparison, export, or saved-view operation
- **THEN** it invokes a typed Python desktop method through `desktop_request`
- **AND** no generic filesystem, database, or provider request is exposed to React

### Requirement: Accessible OSCA-owned chart renderer
D5 SHALL use an OSCA-owned declarative SVG/DOM renderer with keyboard-accessible controls, screen-reader description, non-color state cues, reduced-motion/forced-colors safeguards, and an equivalent table. D5 SHALL add no third-party chart runtime dependency.

#### Scenario: Chart is unusable visually
- **WHEN** a user relies on a screen reader, forced-colors mode, or the equivalent data table
- **THEN** the displayed numerical information and chart context remain inspectable without pointer hover or color alone

### Requirement: Offline responsive research workbench
The D5 core workbench SHALL operate with governed local/sample/cached data without paid services or network access and SHALL target the PRD chart responsiveness objective while bounding large display payloads.

#### Scenario: Local sample chart is loaded offline
- **GIVEN** a governed local or bundled sample dataset
- **WHEN** the user loads the workbench without network access
- **THEN** the chart, table, deterministic indicators, saved views, and eligible local export remain usable
- **AND** no provider request is required

### Requirement: Permanent D5 safety boundaries
D5 SHALL NOT introduce frontend-authored authoritative financial calculations, live quotes, recommendation generation, model training, strategy execution, brokerage connectivity, paper-order submission, or real-capital execution.

#### Scenario: User inspects quantitative evidence
- **WHEN** the user changes a chart range, indicator, comparison, or saved view
- **THEN** no broker or order method is invoked
- **AND** the desktop continues to present the workflow as research/analysis only
