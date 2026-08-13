# D6 Specification — Research Projects, Saved Workspaces, and Integrated Evidence

## 1. Authority and ownership

D6 is a desktop organization and reproducibility milestone. Python application services remain authoritative for project identity, lifecycle transitions, timeline records, notes, pins, saved project workspaces, manifest export, validation, migration, and profile-scoped persistence.

React renders typed returned state and captures declarative project intent. React must not inspect databases, read arbitrary files, resolve provider resources, calculate analytical facts, execute notebooks, or mutate evidence directly. Rust remains the existing transport/session broker and may only classify D6 project mutations under the established profile ownership lease.

D6 reuses the accepted M4 research-project semantics and the D5 Workbench evidence surfaces. It does not create a second project model.

## 2. Project model

A project record contains:

- stable project identity;
- normalized unique name within a profile;
- user-visible objective;
- optional horizon or research window description;
- lifecycle status: active, archived, or deleted only when deletion is safe under retained-evidence policy;
- immutable creation timestamp and producer metadata;
- update timestamp and version metadata;
- optional tags or short description when accepted by the implementation schema.

Project records are profile-scoped. A project in one profile must not appear in another profile and must not reference another profile's private storage as a valid local resource.

## 3. Lifecycle behavior

D6 supports:

- create project;
- list projects with lifecycle filters;
- inspect project detail;
- rename/update objective or metadata;
- archive and restore;
- clone;
- delete only if implemented as an evidence-safe tombstone or otherwise proven not to break retained evidence;
- export manifest.

Every lifecycle mutation records a project timeline event. Clone creates a new project identity, copies declarative metadata, notes, pins, and saved workspaces, preserves source references, and records original project identity as clone provenance.

## 4. Typed pins and immutable references

Projects organize evidence by typed pins. Pins reference governed resources rather than copying or mutating them. Initial D6 pin types include:

- canonical asset;
- watchlist;
- dataset revision or retained local-data import;
- D5 Workbench view;
- D5 full-resolution export artifact;
- report or evidence file produced by existing governed OSCA flows;
- external reference placeholder only when it contains no credential, secret, executable code, or provider query authority.

Each pin records source type, source identity, display label, creation metadata, optional digest or revision metadata, and degraded/broken-link status when the referenced resource is unavailable. Broken pins remain visible in the project instead of being silently removed or replaced.

## 5. Timeline

The project timeline is append-only for accepted events. It records at least:

- project created, updated, archived, restored, cloned, or deleted;
- pin added, relabeled, degraded, restored, or removed;
- note added or updated;
- saved workspace created or updated;
- manifest exported;
- migration or recovery-relevant event.

Timeline ordering is deterministic and restart-safe. A failed mutation must not produce a misleading successful timeline event.

## 6. Notes

User notes are first-class project content but are not authoritative analytical evidence. The UI and export must label them as user notes. Notes may reference project pins by identity, but a note cannot silently promote itself into a finding, recommendation, strategy, model output, report, or calculated result.

Notes are stored as bounded plain text or bounded structured text accepted by the implementation schema. D6 does not introduce executable notebooks, arbitrary script blocks, or embedded remote content.

## 7. Saved project workspaces

Project workspaces restore declarative desktop context. A saved workspace may retain:

- selected project;
- selected tab or pane;
- selected pins and timeline filters;
- referenced D5 Workbench view identities;
- presentation layout preferences;
- local UI state safe to restore.

Saved workspaces do not recalculate evidence, mutate underlying Workbench views, rewrite dataset references, or bypass project validation.

## 8. Manifest export

D6 exports a governed thin project manifest. The manifest includes:

- export schema and producer version;
- project identity and metadata;
- lifecycle state;
- pins and degraded/broken-link disclosures;
- timeline events;
- notes clearly labeled as user-authored;
- saved project workspaces;
- export timestamp;
- source profile identity metadata that is safe to retain;
- manifest digest.

Self-contained project packages that embed underlying datasets or third-party provider data remain deferred until provider licensing, storage pressure, redaction, restore, and recovery evidence is accepted.

## 9. Desktop application API

Python exposes narrow typed methods for the D6 surface. The planned method family is:

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

The implementation may split or rename methods only if the final traceability preserves the same capabilities and narrow-authority boundary.

## 10. Storage, migration, and recovery

SQLite is authoritative for project metadata, pins, timeline events, notes, and saved project workspace definitions. The store is profile-scoped and versioned. Schema changes require preflight, forward migration, restart tests, newer-schema rejection, and interruption/idempotence tests.

Bulk evidence artifacts remain in their existing governed locations. D6 project storage references them through typed identities and optional digests.

Mutations use the established profile ownership/session lease and bounded Python mutation lock. Non-owner windows or supported external mutation attempts must fail closed while an owner holds the profile.

## 11. Desktop UX

D6 adds a first-class Projects area reachable from the established desktop shell. The surface includes:

- project list and lifecycle filters;
- create, edit, archive, restore, clone, and export actions;
- project detail with objective, status, pins, notes, timeline, and saved workspace sections;
- pin add/remove flows for supported governed resources;
- broken-link/degraded disclosures;
- empty, loading, locked, unavailable, validation-error, and export-result states;
- research-only/no-execution safety copy consistent with prior desktop milestones.

D6 should make the project itself the primary working screen, not a marketing or explanatory landing page.

## 12. Accessibility and responsive layout

The Projects UI must provide keyboard operation, visible focus, logical focus order, screen-reader labels, status roles for long-running export or mutation results, reduced-motion handling, forced-colors/high-contrast safeguards, and responsive layouts at 320 and 680 CSS pixels.

Notes, pins, and timeline entries must remain inspectable without relying on color alone.

## 13. Offline and safety boundaries

D6 must operate with local/sample/cached data and existing retained evidence without paid providers, network access, or external accounts.

D6 does not add:

- recommendation generation;
- model training or inference;
- strategy execution or backtest changes;
- executable notebooks or arbitrary scripts;
- live quotes;
- provider credential collection;
- brokerage/exchange connections;
- paper-order or real-capital order submission.

## 14. Exit criteria

- REQ-0341 through REQ-0356 are traceably implemented or explicitly dispositioned.
- Strict OpenSpec, architecture, secret, Python, frontend, Rust, migration, and packaging gates pass.
- Project lifecycle, pins, notes, timeline, saved workspace, clone/archive/restore, and manifest export tests pass.
- Migration, restart, interruption/idempotence, profile isolation, lock, and newer-schema tests pass.
- Frontend accessibility, responsive, no-generic-authority, and safety-boundary checks pass.
- Clean-profile manual acceptance passes on macOS ARM64 and Linux x86-64.
- Traceability, validation evidence, and exit review are reconciled before owner-directed squash merge.
