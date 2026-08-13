# D6 Traceability

Status: specification baseline; implementation pending

| Requirement | Planned implementation | Planned verification | Status |
|---|---|---|---|
| REQ-0341–0342 | Python project application service and profile-scoped SQLite store for lifecycle operations | lifecycle, restart, archive/restore, clone, and negative tests | Planned |
| REQ-0343–0344 | typed project pins for governed resources with degraded/broken-link state | pin validation, profile-scope, and broken-reference tests | Planned |
| REQ-0345 | append-only project timeline | event ordering, failed-mutation, restart, and migration tests | Planned |
| REQ-0346 | bounded user notes separated from generated/calculated evidence | notes schema, rendering, export, and safety-label tests | Planned |
| REQ-0347 | saved project workspaces with declarative layout/context restore | workspace persistence/restart and frontend tests | Planned |
| REQ-0348–0349 | governed thin manifest export with schema/version/provenance and no self-contained provider-data package | export contract, digest, degraded-link, and scope-boundary tests | Planned |
| REQ-0350 | project clone with new identity and clone provenance | clone identity/reference/provenance tests | Planned |
| REQ-0351 | versioned project storage, migration/recovery, profile isolation, and ownership locks | migration, interruption/idempotence, newer-schema, Rust mutation classification, and lock tests | Planned |
| REQ-0352 | narrow typed desktop methods through `desktop_request` | desktop API, frontend source, Rust boundary, and architecture tests | Planned |
| REQ-0353 | accessible responsive Projects UI | frontend accessibility/responsive tests and supported-platform manual acceptance | Planned |
| REQ-0354–0355 | research-only/offline/no-provider/no-execution boundaries | source-boundary tests and clean-profile manual acceptance | Planned |
| REQ-0356 | retained D6 validation and exit evidence | validation evidence, traceability, manual acceptance, and exit review | Planned |

## Reused authoritative capabilities

D6 reuses the accepted M4 research-project semantics and the D5 Workbench view/export capabilities. It references existing governed resources through typed pins rather than duplicating analytical data or mutating upstream evidence.

## Planned D6 methods

The planned typed method family is:

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

## Closure

The blocking evidence is implementation, hosted validation, and the complete clean-profile manual procedure on macOS ARM64 and Linux x86-64.
