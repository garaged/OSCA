# D5 Traceability

Status: implementation substantially complete; hosted validation and manual acceptance remain

| Requirement | Implementation | Verification | Status |
|---|---|---|---|
| REQ-0325–0326 | typed Python workbench-series application service over `osca.analytical_data`; desktop SVG/DOM price, volume, viewport, and table surfaces | Python contract/service/range tests; frontend boundary/parity tests | Implemented |
| REQ-0327 | authoritative compatible-series comparison through `workbench.comparison.get`, exact-timestamp aligned returns, correlation, beta, explicit normalization basis | quantitative comparison regression; frontend aligned-return table; manual incompatibility inspection | Implemented; manual acceptance pending |
| REQ-0328–0329 | `workbench.analysis.get` reuses `osca.quantitative_analysis`; returned indicator/metric values and evidence are rendered without TypeScript financial formulas | quantitative-analysis regression; analytical golden tests; frontend source-boundary tests | Implemented |
| REQ-0330 | existing deterministic display downsampling plus visible filtered/returned counts; presentation-only viewport selects from already returned rows | analytical property tests; frontend disclosure/viewport tests | Implemented |
| REQ-0331 | dedicated full-resolution CSV export plus JSON reproduction metadata before display downsampling | export row-count/digest/schema regression | Implemented |
| REQ-0332–0333 | profile-scoped SQLite saved-view metadata with versioned schema; Python mutation lock plus Rust window-lease ownership classification for D5 writes | restart, profile-isolation, schema/security tests; Rust mutation classification test | Implemented; manual concurrent-owner acceptance pending |
| REQ-0334 | keyboard controls, visible focus, reduced-motion, forced-colors, screen-reader chart/volume summaries, equivalent synchronized table | frontend source tests; macOS VoiceOver/Linux Orca manual acceptance | Implemented; manual accessibility pending |
| REQ-0335 | typed D5 methods through `desktop_request`; Rust remains transport/session broker and only classifies D5 profile mutations for existing ownership enforcement | desktop API, Rust broker, and architecture-boundary tests | Implemented |
| REQ-0336 | OSCA-owned SVG/DOM renderer; no new chart runtime dependency | package-lock/dependency/license inspection | Implemented; final dependency evidence pending |
| REQ-0337 | bounded display rows, presentation viewport, and PRD chart responsiveness objective | bounded-series tests; hosted package smoke; repeatable/manual packaged timing | Implemented; performance evidence pending |
| REQ-0338–0339 | local/sample/cached offline operation; explicit no-recommendation/no-execution boundary and safety flags | network-negative/source-boundary tests; manual acceptance | Implemented; manual offline acceptance pending |
| REQ-0340 | retained D5 validation and exit evidence | validation evidence and exit review | Pending final CI/manual acceptance |

## Reused authoritative capabilities

D5 intentionally reuses `osca.analytical_data` for governed OHLCV/derived chart series and declared downsampling, and `osca.quantitative_analysis` for deterministic quantitative metrics, indicators, and comparison statistics. D5 desktop code does not recreate those authoritative calculations in TypeScript.

## Runtime D5 methods

The implemented typed method family is:

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

## Permanent D5 boundary

D5 is a research visualization workbench. It does not enable live quotes, recommendations, model training, strategy execution, brokerage connectivity, paper-order submission, or real-capital execution.
