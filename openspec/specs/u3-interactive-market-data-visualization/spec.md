# u3-interactive-market-data-visualization Specification

## Purpose

Provide offline interactive visualization of governed OHLCV and U2-derived analytical series.

## Requirements

### Requirement: U2 remains the analytical authority

U3 SHALL render and export only values returned by the U2 analytical runtime.

#### Scenario: A chart is requested
- **GIVEN** an explicit governed payload and dataset revision
- **WHEN** the chart API is called
- **THEN** the U2 runtime builds the chart-series result before browser rendering.

### Requirement: Interactive OHLCV visualization

U3 SHALL provide candlestick and volume rendering with zoom, pan, reset, crosshair, and tooltip interaction.

#### Scenario: An operator inspects a chart
- **GIVEN** valid chart-series data
- **WHEN** the operator loads and interacts with the chart
- **THEN** the visible range changes without mutating source evidence or recalculating indicators.

### Requirement: Offline accessible evidence

U3 SHALL bundle its rendering surface locally and expose accessible tabular and export representations.

#### Scenario: The machine has no internet access
- **GIVEN** the loopback-only workspace and governed local evidence
- **WHEN** the chart page is opened
- **THEN** charts, the visible-data table, SVG export, JSON export, and CSV export remain available without external assets.

### Requirement: Provenance and safety boundaries

U3 SHALL preserve dataset identity and keep network, credential, recommendation, broker, and real-capital behavior disabled.

#### Scenario: Chart evidence is exported
- **GIVEN** a loaded governed chart series
- **WHEN** JSON, CSV, or SVG evidence is exported
- **THEN** dataset revision, symbol, timeframe, and visible values are retained and no execution capability is enabled.
