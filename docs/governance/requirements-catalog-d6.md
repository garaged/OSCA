# D6 Requirements Catalog — Research Projects, Saved Workspaces, and Integrated Evidence

Status: Draft for implementation
Baseline: D5 merge `1936f1e5b47055f1e8d88d293abaf9dc99c00970`

| ID | Requirement | Verification |
|---|---|---|
| REQ-0341 | D6 shall provide profile-scoped research projects with stable identity, normalized unique name, objective, optional horizon, lifecycle status, immutable creation metadata, and update metadata. | Project service, persistence, migration, and desktop API tests |
| REQ-0342 | Project lifecycle operations shall support create, list, inspect, rename/update metadata, archive, restore, clone, and delete only where deletion preserves audit/evidence constraints. | Lifecycle, restart, archive/restore, clone, and negative tests |
| REQ-0343 | Projects shall reference canonical assets, watchlists, dataset revisions, Workbench views, analytical exports, reports, and other evidence through typed immutable pins rather than copying or mutating underlying resources. | Pin validation and storage tests |
| REQ-0344 | Project pins shall preserve source identity, source type, display label, profile scope, optional digest/revision metadata, creation metadata, and broken-link/degraded status. | Pin schema and broken-reference tests |
| REQ-0345 | D6 shall provide a project timeline that records typed events for lifecycle changes, notes, pins, workspace saves, evidence exports, clone/archive/restore actions, and migration-relevant changes. | Timeline append-only and ordering tests |
| REQ-0346 | User-authored notes shall be stored separately from generated or calculated evidence, shall be clearly labeled as user notes in the UI/export, and shall not be treated as authoritative analytical output. | Notes schema, rendering, and export tests |
| REQ-0347 | Saved project workspaces shall restore declarative layout and context, including selected project, pinned assets/evidence, Workbench view references, visible panes, and presentation preferences without recalculating or mutating evidence. | Workspace persistence/restart and frontend tests |
| REQ-0348 | Project exports shall produce a governed manifest that includes project metadata, lifecycle state, pins, timeline, notes, workspace definitions, schema version, export timestamp, producer version, and broken-link/degraded disclosures. | Manifest export contract and regression tests |
| REQ-0349 | Thin project exports shall reference existing governed artifacts; self-contained package export remains deferred unless provider licensing, storage pressure, redaction, and recovery evidence are explicitly accepted. | Scope/audit tests and manual acceptance |
| REQ-0350 | Project clone shall create a new project identity and copy declarative project metadata, pins, notes, and workspace definitions while preserving original source references and recording clone provenance. | Clone identity/provenance tests |
| REQ-0351 | Project storage shall be profile-scoped, versioned, migratable, restart-safe, idempotent under interrupted operations, and protected by the established desktop profile ownership/locking boundary for mutations. | SQLite migration, restart, interruption, Rust mutation classification, and lock tests |
| REQ-0352 | D6 desktop methods shall use narrow typed `desktop_request` application APIs; React shall not gain arbitrary filesystem, database, shell, provider, notebook, extension, brokerage, or order authority. | Desktop API, frontend source, Rust boundary, and architecture tests |
| REQ-0353 | The Projects UI shall provide keyboard operation, visible focus, screen-reader labels, reduced-motion and forced-colors support, empty/loading/error/degraded states, and responsive 320/680 CSS-pixel layouts. | Frontend accessibility/responsive tests and supported-platform manual acceptance |
| REQ-0354 | Project screens shall visibly preserve OSCA's research-only/no-recommendation/no-execution boundary and shall distinguish project organization from financial advice, recommendation generation, strategy execution, or order entry. | Source, UI, and manual safety-boundary checks |
| REQ-0355 | D6 shall remain usable with local/sample/cached data and existing retained evidence without paid providers, network access, or external accounts. | Offline/source-boundary tests and clean-profile manual acceptance |
| REQ-0356 | D6 exit shall retain requirements, OpenSpec, traceability, migration/recovery evidence, automated validation, supported-platform manual acceptance, limitations, and accepted exit review evidence. | Exit review |
