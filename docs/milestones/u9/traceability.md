# U9 Traceability

| Requirement area | Implementation | Automated evidence | Manual/retained evidence |
|---|---|---|---|
| Canonical bounded request and mapping | `src/osca/historical_acquisition.py`, `src/osca/historical_acquisition_cli.py` | `test_bounded_range_filters_rows_and_retains_mapping`, `test_invalid_range_and_mapping_fail_before_acceptance`, CLI option test | U9 manual guide bounded-range procedure |
| Provider admission and policy gate | P13 admission policy plus U9 orchestration | `test_network_and_equity_policy_fail_closed` | Retained Kraken approval and blocked Twelve Data evidence |
| No-cost principal workflow | Kraken public OHLC plus governed CSV fallback | Kraken success and CSV equivalence tests | Clean-profile Kraken acquisition and blocked-equity outputs |
| Canonical normalization and immutable revision | local OHLCV import service with processing revision salt | canonical revision, CSV equivalence, parser-revision tests | Dataset revision and Parquet/SQLite identifiers retained |
| Durable idempotent retrieval | persisted acquisition job records, reuse, in-process joining, recovery, cancellation | reuse, concurrency, interrupted recovery, cancellation tests | Manual guide reuse and cancellation checks |
| Explicit degraded outcomes | U9 status taxonomy and remediation contract | quota, unavailable, corrupt, invalid, partial, stale tests | Deterministic hosted failure acceptance |
| Acquisition evidence and telemetry | stable request/correlation/job/acquisition IDs, attempts, timing, progress, digests, lineage | full-lineage/job evidence test | Clean-profile acquisition and U8 manifest |
| Provider correction lineage | parser/normalizer revision salt and predecessor/supersession fields | parser or normalizer change test | Manual guide correction procedure |
| Secret and endpoint safety | inherited P13 allowlist, HTTPS, explicit network opt-in, no credential use for Kraken | P13 suite, network policy test, secret scan | Provider review and retained safety flags |
| Primary CLI and U8 handoff | primary `osca historical-data fetch`, timezone-safe ISO parser, U8 pipeline | CLI option test and `test_u9_pipeline_handoff` | Retained U8 run `d2cfcf58-ce0d-4bf9-be04-62ed84abb61d` |
| Workspace discovers complete evidence chain | recursive P11 workspace scan | `test_workspace_discovers_complete_u9_evidence_chain` | Required clean-profile snapshot procedure in manual guide |
| Execution boundary preservation | immutable false safety flags | acquisition, workspace, and pipeline tests | Kraken, blocked-equity, and U8 retained outputs |

## Acceptance rule

U9 is complete only when hosted Quality is green, the clean-profile Kraken and blocked-equity evidence remains retained, the U8 handoff is recorded, and workspace discovery is proven automatically and included explicitly in the manual acceptance checklist. Dedicated workspace sections and detail pages remain U10 scope; basic discovery of the complete existing chain is U9 scope.
