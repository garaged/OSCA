# D6 Research Projects, Saved Workspaces, and Integrated Evidence

- **Status:** Specification draft for implementation
- **Baseline:** D5 merge `1936f1e5b47055f1e8d88d293abaf9dc99c00970`
- **Branch:** `agent/d6-research-projects-workspaces`
- **Intent:** `intent.md`
- **Specification:** `specification.md`
- **Requirements:** `../../governance/requirements-catalog-d6.md`
- **Traceability:** `traceability.md`
- **Manual acceptance:** `manual-acceptance.md`
- **Validation evidence:** `validation-evidence.md`
- **Exit review:** `exit-review.md`
- **OpenSpec:** `../../../openspec/changes/d6-research-projects-workspaces/`

## Outcome

D6 makes research organization a first-class desktop capability. Users can create reproducible projects, pin governed assets and evidence, keep notes separate from calculated outputs, restore saved workspace context, inspect an append-only timeline, clone/archive projects, and export a governed manifest.

## Architecture direction

- Python remains authoritative for project identity, lifecycle, pins, timeline, notes, workspace metadata, manifest export, migration, and validation.
- React renders typed project state and captures declarative user intent only.
- Rust remains the existing transport/session broker and only classifies D6 project mutations under the established ownership lease.
- Projects reference governed resources through immutable typed pins; they do not copy or mutate underlying datasets, Workbench views, exports, or reports.
- Notes are user-authored context and are never promoted silently into authoritative analytical evidence.
- D6 remains offline/local-first and does not add recommendations, executable notebooks, provider routing, strategy execution, brokerage connectivity, or order entry.

## Planned slices

1. D6 requirements, specification, OpenSpec, traceability, and manual-acceptance baseline.
2. Profile-scoped project persistence with migration, lifecycle, archive/restore, clone, and timeline records.
3. Typed project pins for assets, watchlists, dataset revisions, Workbench views, exports, and reports with broken-reference disclosure.
4. User notes and saved project workspace definitions with restart-safe restore.
5. Governed thin manifest export with schema/version, provenance, degraded-link disclosure, and no self-contained data packaging.
6. Desktop Projects UI with accessible lifecycle, pins, timeline, notes, workspace restore, and export flows.
7. Automated migration/recovery, ownership, boundary, accessibility-source, offline, and supported desktop CI evidence.

## Exit work

D6 exits only after implementation, hosted validation, and complete clean-profile manual acceptance pass on:

- macOS ARM64;
- Linux x86-64.

D6 does not add recommendations, model training, strategy execution, executable notebooks, brokerage connectivity, or real-capital execution.
