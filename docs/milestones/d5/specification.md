# D5 Specification — Production Charting and Quantitative Analysis Workbench

## 1. Authority and numerical ownership

D5 is a desktop presentation and orchestration milestone. Python analytical capabilities remain authoritative for OHLCV normalization, indicators, comparisons, downsampling, provenance, and export data. React renders returned values and captures declarative user intent; it does not calculate authoritative financial series.

The existing `osca.analytical_data` and `osca.quantitative_analysis` capabilities are reused rather than duplicated. D5 may add application-layer composition around those public seams but must not import private infrastructure from another capability.

## 2. Governed workbench series

A workbench request identifies a canonical asset, governed dataset revision, timeframe, bounded optional range, display row budget, and requested deterministic series definitions. Python resolves the retained payload and returns a typed workbench result containing:

- canonical asset and dataset revision identity;
- timeframe and requested/effective range;
- OHLCV rows for display;
- deterministic derived/indicator values and evidence;
- source, filtered, and displayed row counts;
- declared downsampling method and boundary-preservation status;
- payload/provenance digests and local-data semantics;
- explicit safety flags showing that network, recommendation, brokerage, and real-capital execution are disabled.

The frontend shall not accept an arbitrary database query or provider URL as a chart source.

## 3. Visualization adapter

D5 uses an OSCA-owned declarative SVG/DOM chart adapter. No new third-party chart runtime is required for D5. This avoids a new runtime licensing/attribution surface while preserving an explicit renderer boundary that can be replaced later through governed evidence.

The chart adapter supports, in D5 scope:

- candlestick/OHLC price rendering;
- volume pane;
- deterministic line overlays and indicator panes where semantically appropriate;
- visible range selection, zoom, and pan as presentation operations;
- synchronized cursor/table inspection;
- comparison series;
- accessible summaries and non-color status cues.

Zooming or panning never recomputes authoritative indicators in React. A change that requires different analytical inputs produces a new typed Python request; a purely visual viewport change selects from already returned display values.

## 4. Indicators and quantitative controls

Indicator controls bind to authoritative Python definitions. The initial D5 set reuses existing deterministic capabilities, including moving averages, returns, rolling volatility/volume, RSI, ATR, Bollinger calculations, and MACD-family outputs where supported by the existing quantitative-analysis contract.

Every requested indicator exposes its definition and parameters. Returned evidence preserves warm-up behavior, input identity, point-in-time-safety metadata where available, and deterministic output identity. Unsupported parameter combinations fail visibly instead of being approximated in the frontend.

## 5. Comparisons

Users may compare compatible governed series over a common declared range. A comparison response keeps each canonical asset, dataset revision, timeframe, currency/unit semantics, provenance, and missing-data behavior explicit.

D5 shall not silently join incompatible timeframes, currencies, adjustment views, or temporal semantics. When direct comparison is invalid, the service returns a typed incompatibility result with remediation guidance. Any normalized-performance comparison uses an authoritative Python transformation and labels its basis explicitly.

## 6. Chart/table parity

The visible chart and synchronized table consume the same returned display result. A value displayed in a tooltip or chart marker must correspond to the same timestamp/value available in the accessible table.

Frontend tests shall verify that the renderer does not independently calculate OHLCV, returns, moving averages, volatility, RSI, ATR, Bollinger, MACD, or comparison normalization.

## 7. Downsampling and bounded rendering

Display requests use an explicit row budget. If the filtered result exceeds that budget, Python applies the declared deterministic downsampling method and returns source, filtered, and displayed row counts. First and last required boundary observations are preserved.

The UI visibly identifies a downsampled display and must not describe it as the full analytical input. Downsampling affects only presentation. It must not alter retained datasets, authoritative quantitative results, or full-resolution exports.

D5 initially reuses the existing deterministic evenly-spaced display method. A future aggregation or shape-preserving algorithm requires an explicit versioned method and regression evidence before replacing it.

## 8. Full-resolution export

Export operates on the authoritative filtered/enriched result before display downsampling. D5 export must therefore use a dedicated full-resolution analytical path rather than serializing the current displayed rows.

Supported D5 evidence export is tabular CSV plus JSON reproduction metadata. The metadata identifies at least canonical asset, dataset revision, timeframe, effective range, requested series definitions and parameters, payload/input digest, row count, export schema/version, and whether any display downsampling was active.

The export path is subject to existing provider licensing and data-retention policy. D5 local/sample/cached acceptance data is exportable without a paid provider. The renderer may additionally export an SVG image of the visible chart; that image is presentation evidence and is not a substitute for full-resolution data export.

## 9. Saved view state

Saved workbench views are profile-scoped declarative records with stable identifiers, unique normalized names, optional descriptions, timestamps, and versioned configuration. A view may retain:

- canonical primary and comparison asset identifiers;
- selected governed dataset/timeframe references or resolution preferences;
- requested range and display row budget;
- enabled indicators and parameters;
- pane/layout visibility;
- presentation range preferences that are safe to restore.

A saved view never copies or mutates analytical data. It cannot contain executable code, arbitrary SQL, provider credentials, secret values, arbitrary provider URLs, or brokerage/order instructions.

SQLite is authoritative for saved-view metadata. Mutations use the established profile ownership/session lease and bounded Python mutation lock. Schema changes use the repository migration conventions and restart/recovery tests.

## 10. Desktop application API

Python exposes narrow typed methods for the D5 surface. The implemented method family is:

- `workbench.series.get`;
- `workbench.analysis.get`;
- `workbench.comparison.get`;
- `workbench.export.prepare`;
- `workbench.view.list`;
- `workbench.view.get`;
- `workbench.view.create`;
- `workbench.view.update`;
- `workbench.view.rename`;
- `workbench.view.delete`.

React accesses D5 only through `desktop_request`. Rust remains a transport/session broker; it classifies D5 profile mutations for the established window-ownership lease but gains no numerical calculation, generic database/filesystem/network access, provider credentials, brokerage authority, or order execution authority.

## 11. Desktop UX

D5 adds a first-class Workbench area reachable from the established desktop shell. The surface includes:

- asset/dataset and timeframe context;
- bounded range controls;
- chart and volume panes;
- indicator controls with visible parameters;
- optional compatible comparison controls;
- source/display row-count and downsampling disclosure;
- synchronized accessible table;
- provenance/evidence summary;
- saved-view lifecycle controls;
- full-resolution evidence export;
- loading, empty, unavailable, incompatible, invalid-parameter, locked-profile, and error states.

The workbench must preserve the existing research-only/no-execution boundary visibly.

## 12. Accessibility

The workbench provides keyboard-accessible controls, visible focus, semantic labels, screen-reader chart description/summary, an equivalent synchronized data table, reduced-motion support, forced-colors/high-contrast safeguards, and non-color encoding for state and direction where practical.

Chart interaction is never the only way to obtain a displayed numerical value. Pointer hover may enhance inspection but must have keyboard/table alternatives.

## 13. Performance

D5 adopts the PRD responsiveness objective for cached/indexed data: typical dashboards and charts target p95 under three seconds on recommended hardware.

For supported desktop acceptance hardware:

- ordinary local workbench load for retained/sample data should complete within three seconds;
- presentation row budgets keep SVG/DOM rendering bounded;
- changing a purely visual viewport must remain interactive without re-reading the full dataset;
- large-series tests must prove that display payload size is bounded by the requested row budget;
- full-resolution export may take longer than display rendering but exposes progress/error state rather than freezing the UI.

## 14. Licensing and dependency boundary

The D5 renderer adds no new third-party chart runtime dependency. Existing application/runtime dependencies retain their current license governance. Any proposal to replace the OSCA-owned renderer with a third-party chart library must first record exact package/version/license, required attribution or notices, security/dependency implications, accessibility behavior, performance evidence, and compatibility/replacement strategy.

## 15. Offline and safety boundaries

D5 must work with governed local imports, sample data, or already cached/retained datasets without paid services and without network access.

D5 does not add:

- frontend-authored authoritative financial calculations;
- live/streaming quote transport;
- strategy execution or backtest changes;
- model training;
- recommendation generation;
- brokerage/exchange connections;
- submission of paper or real-capital orders.

## 16. Exit criteria

- REQ-0325 through REQ-0340 are traceably implemented or explicitly dispositioned.
- Strict OpenSpec, architecture, secret, Python, frontend, Rust, migration, and packaging gates pass.
- Golden tests prove chart/table parity and authoritative indicator ownership.
- Downsampling tests prove disclosure, deterministic bounded output, and first/last preservation.
- Full-resolution export tests prove display downsampling does not truncate exported analytical rows.
- Saved-view migration, restart, profile isolation, lock, and failure tests pass.
- Dependency/license inspection confirms no new chart runtime dependency.
- Repeatable performance evidence meets the declared D5 budgets.
- Clean-profile manual acceptance passes on macOS ARM64 and Linux x86-64.
- Accessibility and offline/network-negative acceptance pass.
- Traceability, validation evidence, and exit review are reconciled before owner-directed squash merge.
