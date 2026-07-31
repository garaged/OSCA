# U3 - Interactive Market-Data Visualization

- **Status:** Planned
- **Depends on:** U2

## Objective

Add interactive OHLCV and analytical-series visualization to the existing loopback-only analyst workspace.

## Scope

- Candlestick/OHLC, line, volume, indicator-panel, drawdown, and distribution charts.
- Zoom, pan, crosshair, tooltip, range/timeframe selection, series visibility, and reset.
- Gap, incomplete-bar, stale-data, warm-up, source, and revision visibility.
- Offline-bundled chart assets with licensing, CSP, integrity, accessibility, and packaging review.
- PNG/SVG chart export where supported and provenance-preserving CSV/JSON data export.
- Responsive empty, loading, warning, and error states.

## Non-scope

- Public hosting, collaborative SaaS, browser-side analytical authority, ML training, recommendations, brokers, or real orders.

## Acceptance

A clean-machine operator can import the committed OHLCV fixture, open the workspace, inspect an interactive candlestick/volume chart with derived overlays, and export the visible evidence without network access.
