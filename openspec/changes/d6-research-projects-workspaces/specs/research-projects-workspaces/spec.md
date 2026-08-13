# Research Projects, Saved Workspaces, and Integrated Evidence

## ADDED Requirements

### Requirement: Profile-scoped project lifecycle
The desktop SHALL provide profile-scoped research projects with stable identity, unique normalized name, objective, lifecycle status, immutable creation metadata, update metadata, and restart-safe lifecycle operations.

#### Scenario: Project is created and reopened
- **WHEN** a user creates a project with a valid name and objective
- **THEN** the project receives a stable identity and active lifecycle state
- **AND** reopening the same profile lists the project with unchanged creation metadata

### Requirement: Typed immutable project pins
Projects SHALL reference governed resources through typed pins rather than copying or mutating underlying assets, datasets, Workbench views, exports, or reports.

#### Scenario: Workbench evidence is pinned
- **WHEN** a user pins a Workbench view or export to a project
- **THEN** the project stores the typed source identity, label, revision or digest metadata when available, and creation metadata
- **AND** the original Workbench evidence is not mutated by the pin

### Requirement: Broken reference disclosure
Project pins SHALL preserve unavailable or broken references as degraded project state rather than silently deleting or replacing them.

#### Scenario: Pinned evidence is unavailable
- **WHEN** a project is opened and a pinned governed resource cannot be resolved
- **THEN** the project marks the pin degraded or broken
- **AND** the UI and manifest disclose the unresolved reference

### Requirement: Append-only project timeline
Project lifecycle changes, pin changes, notes, workspace saves, exports, clone/archive/restore actions, and migration-relevant changes SHALL create deterministic timeline events.

#### Scenario: Failed mutation does not create success event
- **WHEN** a project mutation fails validation
- **THEN** no successful timeline event is appended for that mutation

### Requirement: User notes are distinct from evidence
User-authored notes SHALL be stored and presented separately from generated or calculated evidence and SHALL NOT be treated as authoritative analytical output.

#### Scenario: Project note is exported
- **WHEN** a project manifest includes a note
- **THEN** the note is labeled as user-authored content
- **AND** it is not represented as a finding, recommendation, signal, or calculated result

### Requirement: Declarative saved project workspaces
Saved project workspaces SHALL restore project context, layout, filters, selected pins, and referenced Workbench view identities without recalculating or mutating underlying evidence.

#### Scenario: Workspace restore
- **WHEN** a saved project workspace is restored after restart
- **THEN** the selected project context and presentation preferences return
- **AND** underlying datasets, Workbench views, and evidence records are unchanged

### Requirement: Governed thin manifest export
Project export SHALL produce a thin manifest with schema/version, producer, export timestamp, project metadata, lifecycle state, pins, timeline, notes, workspaces, and degraded-link disclosures.

#### Scenario: Project manifest is prepared
- **WHEN** the user exports a project
- **THEN** the manifest identifies its schema version, producer, project identity, pins, timeline, notes, workspaces, and digest
- **AND** it does not unexpectedly bundle provider datasets or private profile paths

### Requirement: Clone preserves provenance
Project clone SHALL create a new project identity while copying declarative metadata, pins, notes, and workspaces with original source references and clone provenance preserved.

#### Scenario: Project is cloned
- **WHEN** a user clones a project
- **THEN** the clone has a distinct project identity
- **AND** the clone records the original project identity and preserves source pin references

### Requirement: Versioned storage and ownership
D6 project storage SHALL be profile-scoped, versioned, migratable, restart-safe, idempotent under interrupted operations, and protected by the established desktop profile ownership boundary for mutations.

#### Scenario: Non-owner mutates project
- **WHEN** a non-owner desktop window or supported external request attempts a project mutation while another owner holds the profile
- **THEN** the mutation fails visibly without changing project state

### Requirement: Narrow desktop authority
React SHALL access D6 project operations only through typed `desktop_request` methods, Python SHALL remain authoritative for project behavior, and Rust SHALL gain no generic filesystem, database, shell, provider, notebook, brokerage, or order authority.

#### Scenario: Project operation crosses desktop boundary
- **WHEN** React requests a project lifecycle, pin, note, workspace, or export operation
- **THEN** it invokes a typed Python desktop method through `desktop_request`
- **AND** no generic host authority is exposed to React

### Requirement: Accessible responsive project UI
The Projects UI SHALL provide keyboard operation, visible focus, screen-reader labels, reduced-motion and forced-colors support, non-color-only state, and responsive 320/680 CSS-pixel layouts.

#### Scenario: Project is operated without pointer input
- **WHEN** a user navigates projects, pins, notes, timeline, workspaces, and export controls using only the keyboard
- **THEN** every actionable control is reachable, labeled, and visibly focused

### Requirement: Offline research organization
D6 project lifecycle, pins, notes, workspace restore, and thin manifest export SHALL remain usable with local/sample/cached data and retained evidence without paid providers, network access, or external accounts.

#### Scenario: Clean profile uses local evidence
- **GIVEN** local/sample/cached evidence exists in a profile
- **WHEN** the user creates a project and pins that evidence
- **THEN** no provider request, credential, or network access is required

### Requirement: Permanent D6 safety boundaries
D6 SHALL NOT introduce recommendation generation, executable notebooks, model training or inference, strategy execution, live quotes, provider credential collection, brokerage connectivity, paper-order submission, or real-capital execution.

#### Scenario: User organizes project evidence
- **WHEN** the user creates projects, pins evidence, writes notes, restores workspaces, or exports a manifest
- **THEN** no broker, order, recommendation, notebook execution, or provider credential method is invoked
