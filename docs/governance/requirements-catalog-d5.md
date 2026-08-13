# D5 Requirements Catalog — Production Charting and Quantitative Analysis Workbench

Status: Draft for implementation
Baseline: D4 merge `a4e733292ff42775848520afd536d57a18cada1f`

| ID | Requirement | Verification |
|---|---|---|
| REQ-0325 | Every chart, table, comparison, indicator, and export shall originate from governed analytical results or canonical dataset revisions; React shall not author authoritative numerical calculations. | Contract, architecture, and frontend source tests |
| REQ-0326 | Users shall inspect governed OHLCV series across bounded ranges with synchronized price, volume, indicator, and table views. | Service, frontend, and manual interaction tests |
| REQ-0327 | Users shall compare compatible canonical assets or governed series over a common declared time range with explicit identity, units, timeframe, provenance, and missing-data behavior. | Comparison contract and mismatch tests |
| REQ-0328 | Indicator controls shall invoke deterministic authoritative calculations and expose parameter, warm-up, point-in-time-safety, input identity, and output evidence. | Quantitative-analysis and chart-series tests |
| REQ-0329 | Displayed chart points and synchronized table values shall be derived from the same returned analytical result so chart/table parity is deterministic and testable. | Golden-result and frontend parity tests |
| REQ-0330 | Large visual datasets shall use a declared deterministic downsampling method, preserve required boundary points, disclose displayed versus source row counts, and never present downsampled values as full-resolution analytical inputs. | Downsampling property and presentation tests |
| REQ-0331 | Data export shall use the governed full-resolution filtered result rather than the downsampled display series and shall include reproduction metadata sufficient to identify dataset revision, timeframe, range, series definitions, provenance digest, and export semantics. | Export contract and full-resolution regression tests |
| REQ-0332 | Users shall save, list, load, rename, update, and delete profile-scoped workbench view state without mutating underlying datasets or analytical results. | Persistence, migration, restart, and ownership tests |
| REQ-0333 | Saved view state shall contain only declarative presentation/query configuration and canonical identities; it shall not store arbitrary executable code, database queries, credentials, or provider secrets. | Schema, security-negative, and source inspection tests |
| REQ-0334 | The desktop workbench shall provide keyboard operation, visible focus, reduced-motion and forced-colors support, screen-reader descriptions, non-color status cues, and an accessible synchronized data table. | Frontend checks and supported-platform manual accessibility tests |
| REQ-0335 | React shall access D5 data and saved-view operations only through typed desktop application methods on the existing `desktop_request` bridge; Rust shall gain no numerical, database, network, secret, brokerage, or order authority. | Desktop API, frontend boundary, and Rust architecture tests |
| REQ-0336 | The D5 chart renderer shall use an OSCA-owned declarative SVG/DOM adapter with no new third-party chart runtime dependency; any later renderer replacement requires separate license, accessibility, performance, and compatibility evidence. | Dependency/license inspection and frontend source tests |
| REQ-0337 | Typical cached/local workbench loads shall meet the PRD chart responsiveness objective, and large-series display shall remain bounded in memory and rendering work through declared row limits/downsampling. | Repeatable performance tests and manual responsiveness evidence |
| REQ-0338 | D5 charting, deterministic indicators, saved views, and export shall remain usable with local/sample/cached data without paid providers or network access. | Offline/network-negative and clean-profile tests |
| REQ-0339 | D5 shall not introduce frontend-authored financial calculations, strategy execution, model training, recommendation generation, live quotes, brokerage connectivity, or real-capital order execution. | Scope and architecture audit |
| REQ-0340 | D5 exit shall retain automated, performance, accessibility, licensing, export, persistence, supported-platform manual, traceability, and exit-review evidence. | Exit review |
