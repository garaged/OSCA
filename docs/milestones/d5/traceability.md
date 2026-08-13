# D5 Traceability

Status: implementation and automated validation complete; supported-platform manual acceptance remains

| Requirement | Implementation | Verification | Status |
|---|---|---|---|
| REQ-0325–0326 | typed Python workbench-series application service over `osca.analytical_data`; desktop SVG/DOM price, volume, viewport, keyboard inspection, and table surfaces | Python contract/service/range tests; frontend boundary/parity/inspection tests | Implemented |
| REQ-0327 | authoritative compatible-series comparison through `workbench.comparison.get`, exact-timestamp aligned returns, correlation, beta, explicit normalization basis, and pre-resolution asset-class/currency compatibility validation | quantitative comparison and incompatibility regressions; frontend aligned-return table; manual comparison inspection | Implemented; manual acceptance pending |
| REQ-0328–0329 | `workbench.analysis.get` reuses `osca.quantitative_analysis`; returned indicator/metric values and evidence are rendered without TypeScript financial formulas; selected chart observation and table row share the same returned row | quantitative-analysis regression; analytical golden tests; frontend source/parity/keyboard-inspection tests | Implemented |
| REQ-0330 | existing deterministic display downsampling plus visible filtered/returned counts; presentation-only viewport selects from already returned rows | analytical property tests; 25k-row bounded performance test; frontend disclosure/viewport tests | Implemented |
| REQ-0331 | dedicated full-resolution CSV export plus JSON reproduction metadata before display downsampling | export row-count/digest/schema regression | Implemented; packaged manual export pending |
| REQ-0332–0333 | profile-scoped SQLite saved-view metadata with versioned schema; bounded declarative configuration; Python mutation lock plus Rust window-lease ownership classification for D5 writes | restart, profile-isolation, schema/security tests; Rust mutation classification test | Implemented; manual concurrent-owner acceptance pending |
| REQ-0334 | keyboard controls, focusable chart inspection with Arrow/Home/End selection, selected-row parity, visible focus, reduced-motion, forced-colors, screen-reader chart/volume summaries, equivalent synchronized table | frontend source tests; macOS VoiceOver/Linux Orca manual acceptance | Implemented; manual accessibility pending |
| REQ-0335 | typed D5 methods through `desktop_request`; Rust remains transport/session broker and only classifies D5 profile mutations for existing ownership enforcement | desktop API, Rust broker, and architecture-boundary tests | Implemented |
| REQ-0336 | OSCA-owned SVG/DOM renderer; no new chart runtime dependency | dependency/license inspection and frontend source tests | Implemented; automated evidence retained |
| REQ-0337 | bounded display rows, presentation viewport, 25k-row cached-series regression, and PRD chart responsiveness objective | hosted performance regression; repeatable/manual packaged timing | Implemented; packaged performance acceptance pending |
| REQ-0338–0339 | local/sample/cached offline operation; explicit no-recommendation/no-execution boundary and safety flags; no browser fetch/WebSocket/provider URL/order path | network-negative/source-boundary tests; manual network observation | Implemented; manual offline acceptance pending |
| REQ-0340 | retained D5 validation and provisional exit evidence | `validation-evidence.md`, `exit-review.md`, final manual evidence | Automated evidence retained; final exit pending |

## Reused authoritative capabilities

D5 intentionally reuses `osca.analytical_data` for governed OHLCV/derived chart series and declared downsampling, and `osca.quantitative_analysis` for deterministic quantitative metrics, indicators, and comparison statistics. D5 desktop code does not recreate those authoritative calculations in TypeScript or Rust.

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

## Validated implementation candidate

Implementation candidate `02b8c58aa706fa857e8b0abbfa440b5e6c65455c` passed Quality `31689929269` (#1091) and Desktop Foundation `31689929139` (#238), including strict OpenSpec, secret scanning, Ruff, strict mypy, the complete Python/contracts/migrations/architecture suite, frontend build/tests, desktop API validation, and Rust format/tests/Clippy.

## Permanent D5 boundary

D5 is a research visualization workbench. It does not enable live quotes, recommendations, model training, strategy execution, brokerage connectivity, paper-order submission, or real-capital execution.

## Remaining closure

The blocking evidence is the complete clean-profile manual procedure on macOS ARM64 and Linux x86-64. After both pass, reconcile the final evidence/exit decision and run hosted validation on that evidence head before owner-directed squash merge.
