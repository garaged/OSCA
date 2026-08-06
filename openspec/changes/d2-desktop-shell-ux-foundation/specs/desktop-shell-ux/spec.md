# Desktop Shell and User Experience Foundation Delta Specification

## ADDED Requirements

### Requirement: Responsive honest shell

The desktop application SHALL provide a responsive accessible shell whose available destinations correspond to implemented D2 capabilities.

#### Scenario: User views primary navigation

- **WHEN** the D2 desktop application loads
- **THEN** Home and System are available destinations
- **AND** Research and Evidence are identified as later/unavailable
- **AND** unavailable destinations are not presented as functional controls
- **AND** the shell remains usable at 320 CSS pixels and normal desktop widths.

### Requirement: First-run safety disclosure

The desktop application SHALL present product, storage, network, provider, credential, recommendation, and live-execution boundaries before profile mutation.

#### Scenario: New user begins onboarding

- **WHEN** no known profile exists
- **THEN** OSCA states that it is research and simulation software rather than financial advice
- **AND** local storage and explicit optional networking are disclosed
- **AND** the bundled sample is provider- and credential-free
- **AND** recommendations and live execution remain unavailable.

### Requirement: Python-authoritative profile lifecycle

The desktop frontend SHALL invoke versioned Python application methods for profile list, inspection, creation, selection, and opening.

#### Scenario: User creates a profile

- **WHEN** a user submits a safe new absolute profile path
- **THEN** Python invokes the canonical profile initialization service
- **AND** a versioned local configuration and storage root are created
- **AND** the profile is presented as open only after authoritative validation
- **AND** React and Rust do not create or inspect profile files directly.

#### Scenario: Unsafe profile target is submitted

- **WHEN** the target is relative, the filesystem root, non-empty, unwritable, incompatible, or locked as applicable
- **THEN** the operation fails closed with a structured error
- **AND** existing content remains unchanged
- **AND** no force-overwrite or force-unlock behavior is offered.

### Requirement: Explicit application states and diagnostics

The D2 shell SHALL represent loading, ready, empty, unavailable, retryable error, blocked error, and unexpected rendering failure as applicable, and SHALL show authoritative system diagnostics.

#### Scenario: Sidecar is unavailable

- **WHEN** the Python sidecar cannot be invoked
- **THEN** the shell and permanent safety disclosures remain visible
- **AND** affected content reports unavailable rather than ready
- **AND** a retry is shown only when the typed error is retryable
- **AND** ordinary users do not receive raw stack traces or secret-bearing diagnostics.

### Requirement: Governed synthetic offline sample

The D2 desktop application SHALL import a bundled deterministic synthetic OHLCV sample through the canonical Python local-data import service.

#### Scenario: User imports the sample twice

- **WHEN** a validated profile imports the bundled sample twice
- **THEN** both results identify the data as synthetic
- **AND** no network, provider account, or credential is used
- **AND** governed Parquet payload and SQLite metadata are retained
- **AND** equivalent imports return the same dataset revision identity
- **AND** the UI never describes the sample as actual provider market history.

### Requirement: Accessibility and semantic design foundation

The D2 desktop application SHALL provide keyboard operation, visible focus, semantic landmarks and headings, focus transfer, bounded status announcements, reusable semantic design tokens, reduced-motion handling, and accessible light/dark/forced-colors foundations.

#### Scenario: Keyboard-only user operates onboarding

- **WHEN** a user navigates without a pointer
- **THEN** the skip link, available navigation, profile field, actions, sample action, and diagnostics are reachable
- **AND** primary navigation moves focus to the destination heading
- **AND** a failed submitted action moves focus to the error summary
- **AND** unavailable destinations do not become fake tab stops.

### Requirement: Narrow desktop authority boundary

The D2 frontend and Rust host SHALL preserve a narrow allowlisted versioned application API and SHALL NOT add generic filesystem, shell, database, provider, credential, extension, recommendation, or execution access.

#### Scenario: Desktop dependencies and source are inspected

- **WHEN** D2 architecture tests inspect the frontend and host
- **THEN** React calls the narrow `desktop_request` command
- **AND** no Tauri filesystem or shell plugin is used
- **AND** no frontend SQLite or Parquet access exists
- **AND** no broker, exchange, autonomous, live-order, or real-capital method exists.

### Requirement: Evidence-based D2 completion

D2 SHALL remain incomplete until requirements, specification, implementation, automated tests, OpenSpec, traceability, manual accessibility evidence, supported-platform hosted validation, known limitations, and exit review are retained.

#### Scenario: D2 exit is evaluated

- **WHEN** the milestone exit review is prepared
- **THEN** the deferred D1 hosted-validation obligation has been rerun
- **AND** macOS ARM64 and Linux x86-64 clean-profile acceptance evidence exists
- **AND** all product defects are resolved or explicitly block exit
- **AND** the pull request remains unmerged until explicit owner direction.
