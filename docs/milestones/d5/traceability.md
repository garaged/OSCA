# D5 Traceability

Status: specification baseline; implementation in progress

| Requirement | Planned implementation | Verification | Status |
|---|---|---|---|
| REQ-0325–0326 | typed Python workbench-series application service over `osca.analytical_data`; desktop SVG/DOM chart, volume, table | Python contract/service tests; frontend boundary/parity tests | Planned |
| REQ-0327 | authoritative compatible-series comparison service | comparison alignment/incompatibility tests; manual inspection | Planned |
| REQ-0328–0329 | authoritative indicator requests/evidence; one returned result consumed by chart and table | quantitative/analytical golden tests; frontend source/parity tests | Planned |
| REQ-0330 | existing versioned deterministic display downsampling plus visible source/filter/display counts | property tests; frontend disclosure tests | Planned |
| REQ-0331 | dedicated full-resolution export path and reproduction metadata | export row-count/digest/schema tests | Planned |
| REQ-0332–0333 | profile-scoped SQLite saved-view metadata guarded by established ownership/mutation locks | migration, restart, profile-isolation, schema/security tests | Planned |
| REQ-0334 | keyboard, focus, reduced-motion, forced-colors, screen-reader summary, equivalent table | frontend source tests; macOS VoiceOver/Linux Orca manual acceptance | Planned |
| REQ-0335 | typed D5 methods through `desktop_request`; Rust unchanged except existing generic transport | desktop API and architecture-boundary tests | Planned |
| REQ-0336 | OSCA-owned SVG/DOM renderer; no new chart runtime dependency | package-lock/dependency/license inspection | Planned |
| REQ-0337 | bounded display rows and PRD chart responsiveness objective | repeatable performance tests; packaged manual timing | Planned |
| REQ-0338–0339 | local/sample/cached offline operation; explicit no-recommendation/no-execution boundary | network-negative, source-boundary, manual acceptance | Planned |
| REQ-0340 | retained D5 validation and exit evidence | validation evidence and exit review | Pending |

## Reused authoritative capabilities

D5 intentionally reuses `osca.analytical_data` for governed OHLCV/derived chart series and declared downsampling, and `osca.quantitative_analysis` for deterministic quantitative metrics and indicators. D5 desktop code must not recreate those calculations in TypeScript.

## Permanent D5 boundary

D5 is a research visualization workbench. It does not enable live quotes, recommendations, model training, strategy execution, brokerage connectivity, paper-order submission, or real-capital execution.
