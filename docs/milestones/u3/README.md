# U3 - Interactive Market-Data Visualization

- **Status:** Implementation candidate
- **Depends on:** U2 merge `8881708358e1eb762d1f6e7efed63e0eab64ec38`
- **Phase:** Analysis, visualization, and ML experiments

## Objective

Add interactive OHLCV and analytical-series visualization to the existing loopback-only analyst workspace without creating a second analytical authority in browser code.

## Implemented scope

- `/charts` read-only visualization page in the existing analyst workspace.
- `/api/chart-series` JSON endpoint backed exclusively by the U2 analytical runtime.
- `/api/chart-series.csv` provenance-preserving CSV export.
- Native offline SVG candlestick rendering with a volume panel.
- U2-derived SMA, EMA, simple-return, and rolling-volatility values available as overlays or exported evidence.
- Wheel zoom, pointer pan, crosshair, tooltip, reset, visible-range JSON export, SVG export, and CSV export.
- Dataset revision, symbol, timeframe, row count, and downsampling visibility.
- Accessible visible-data table and responsive loading/error states.
- Content Security Policy and no CDN, external script, frontend build, or runtime network dependency.

## Dependency and packaging decision

U3 adds no charting dependency. A native SVG renderer is sufficient for the initial local product and avoids CDN, licensing, integrity, wheel, and frontend toolchain risks. A third-party chart library may be reconsidered only if later usability evidence shows the native renderer cannot meet required interaction or scale needs.

## Deferred to U4 or later

- Full technical-indicator catalog.
- Drawdown and distribution visualizations requiring the U4 analysis runtime.
- PNG export; SVG is the authoritative vector export in U3.
- Automatic dataset selection from workspace cards.
- Public hosting, collaborative SaaS, browser-side analytical calculations, ML training, recommendations, brokers, or real orders.

## Manual acceptance

1. Import a governed OHLCV fixture and retain its payload path and dataset revision UUID.
2. Start the loopback-only analyst workspace.
3. Open `/charts`.
4. Enter the payload path, revision UUID, symbol, and timeframe.
5. Load the candlestick/volume chart, add an SMA or EMA overlay, zoom, pan, and inspect the crosshair tooltip.
6. Export SVG, JSON, and CSV evidence.
7. Confirm the page works without internet access and that the API reports all recommendation, credential, broker, and real-capital boundaries as disabled.

## Acceptance criteria

- A clean-machine operator can load governed OHLCV into an interactive candlestick and volume chart.
- Browser rendering consumes only U2 results and does not calculate market indicators independently.
- Visible provenance and warm-up/null states remain honest.
- SVG, JSON, and CSV exports preserve the visible evidence and dataset identity.
- Automated tests cover page availability, U2-backed API behavior, export provenance, invalid derived-series rejection, and safety boundaries.
- Hosted Quality passes before completion is marked.
