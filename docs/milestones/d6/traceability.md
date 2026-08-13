# D6 Traceability

Status: accepted

| Requirement | Implementation | Verification | Status |
|---|---|---|---|
| REQ-0341–0342 | Python project application service and profile-scoped SQLite store for lifecycle operations | lifecycle, restart, archive/restore, clone, and negative tests in `tests/test_d6_desktop_projects.py` | Accepted |
| REQ-0343–0344 | typed project pins for governed resources with degraded/broken-link state | pin validation, profile-scope, and broken-reference tests; frontend degraded-state disclosure test | Accepted |
| REQ-0345 | append-only project timeline | event ordering, failed-mutation, restart, and migration tests | Accepted |
| REQ-0346 | bounded user notes separated from generated/calculated evidence | notes schema, rendering, export, and safety-label tests | Accepted |
| REQ-0347 | saved project workspaces with declarative layout/context restore | workspace persistence/restart tests and frontend source tests | Accepted |
| REQ-0348–0349 | governed thin manifest export with schema/version/provenance and no self-contained provider-data package | export contract, digest, degraded-link, and scope-boundary tests | Accepted |
| REQ-0350 | project clone with new identity and clone provenance | clone identity/reference/provenance tests | Accepted |
| REQ-0351 | versioned project storage, migration/recovery, profile isolation, and ownership locks | migration, interruption/idempotence, newer-schema, Rust mutation classification, and lock tests | Accepted |
| REQ-0352 | narrow typed desktop methods through `desktop_request` | desktop API, frontend source, Rust boundary, and architecture tests | Accepted |
| REQ-0353 | accessible responsive Projects UI | frontend accessibility/responsive tests and supported-platform manual acceptance | Accepted |
| REQ-0354–0355 | research-only/offline/no-provider/no-execution boundaries | source-boundary tests and clean-profile manual acceptance | Accepted |
| REQ-0356 | retained D6 validation and exit evidence | validation evidence, traceability, manual acceptance, and exit review | Accepted |

## Reused authoritative capabilities

D6 reuses the accepted M4 research-project semantics and the D5 Workbench view/export capabilities. It references existing governed resources through typed pins rather than duplicating analytical data or mutating upstream evidence.

## D6 methods

The typed method family is:

- `project.create`;
- `project.list`;
- `project.get`;
- `project.update`;
- `project.archive`;
- `project.restore`;
- `project.clone`;
- `project.delete`;
- `project.pin.add`;
- `project.pin.update`;
- `project.pin.remove`;
- `project.note.add`;
- `project.note.update`;
- `project.workspace.save`;
- `project.workspace.list`;
- `project.workspace.get`;
- `project.export.prepare`.

## Permanent D6 boundary

D6 is a research organization and evidence-management milestone. It does not enable recommendations, executable notebooks, model training, strategy execution, brokerage connectivity, paper-order submission, or real-capital execution.

## Naming disposition

D6 follows the current desktop milestone-module convention in `src/osca/desktop_api/d6_service.py`. This is acceptable for the current staged desktop series because the public callable surface remains the stable `project.*` method family. Before the desktop API is treated as public extension surface, milestone-named modules should be folded into capability-named modules such as project/workspace services so implementation names do not leak roadmap sequencing.

## Closure

D6 is accepted. Automated validation, hosted exact-head validation, and supported-platform clean-profile manual acceptance are complete.
