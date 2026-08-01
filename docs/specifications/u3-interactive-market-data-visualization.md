# U3 Interactive Market-Data Visualization Specification

## Purpose

Provide an offline, loopback-only visual inspection surface for governed OHLCV and U2-derived analytical series.

## Requirements

### U3-1 U2 analytical authority

Every chart and export must consume a U2 chart-series result. Browser code must not independently calculate indicators, returns, volatility, or other analytical values.

### U3-2 Interactive OHLCV chart

The workspace must provide candlestick price and volume rendering with zoom, pan, crosshair, tooltip, visible-range reset, and responsive loading and error states.

### U3-3 Provenance and state visibility

The surface must display symbol, timeframe, dataset revision, returned row count, downsampling behavior, warm-up/null values, and disabled safety boundaries where applicable.

### U3-4 Offline and security boundary

Visualization assets must be bundled in the application, operate without internet access, use a restrictive Content Security Policy, and make no provider or credential requests.

### U3-5 Accessible fallback

Visible chart data must also be available as an accessible semantic table.

### U3-6 Evidence export

The operator must be able to export SVG chart evidence and provenance-preserving JSON and CSV data.

### U3-7 Safety boundary

Visualization must not produce recommendations, connect brokers, execute autonomous strategies, or place real-capital orders.

## Verification

- FastAPI route tests for page, JSON, and CSV surfaces.
- U2 runtime integration tests.
- Invalid derived-series negative test.
- Inspection of offline asset and CSP behavior.
- Manual zoom, pan, crosshair, overlay, accessible-table, and export acceptance.
