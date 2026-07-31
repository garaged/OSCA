# p11-analyst-workspace Specification

## Purpose

Define the accepted behavior for the P11 read-only local analyst workspace.

## Requirements

### Requirement: Read-only workspace snapshot

P11 SHALL expose immutable sections for projects, watchlists, datasets, reports, backtests, enrichment evidence, and routing evidence.

#### Scenario: Empty storage is inspected
- **GIVEN** a storage root with no retained artifacts
- **WHEN** the workspace snapshot is requested
- **THEN** every section is present with an empty message and all write, network, credential, recommendation, broker, and order boundaries remain disabled.

### Requirement: Retained artifact discovery

P11 SHALL discover supported local metadata and artifact files without mutating them.

#### Scenario: Local evidence exists
- **GIVEN** P6 dataset metadata and retained P7-P10 artifacts
- **WHEN** the workspace is inspected
- **THEN** items include stable identity, section, status, summary, artifact provenance, and safe metadata.

### Requirement: Routing-status preservation

P11 SHALL preserve P10 routing status semantics.

#### Scenario: FRED routing is blocked
- **GIVEN** a retained FRED routing decision with `policy_blocked`
- **WHEN** routing evidence is displayed
- **THEN** the workspace reports `policy_blocked` and does not present SEC or another source as a macro substitute.

### Requirement: Safe local product surface

P11 SHALL expose a local JSON API and browser page without write endpoints.

#### Scenario: Browser workspace is opened
- **GIVEN** the loopback-bound P11 application
- **WHEN** the root page and API are requested
- **THEN** loading, empty, warning, error, and available states can be rendered from read-only data.

#### Scenario: A write is attempted
- **GIVEN** the P11 API
- **WHEN** a caller submits a mutation request
- **THEN** the request is rejected because no write route exists.

#### Scenario: Public binding is attempted
- **GIVEN** the P11 CLI
- **WHEN** a non-loopback host is supplied
- **THEN** startup fails closed with an actionable error.

### Requirement: Metadata minimization

P11 SHALL omit credential-like fields from surfaced artifact metadata.

#### Scenario: Evidence metadata includes a secret reference
- **GIVEN** a retained metadata object containing a credential-like key
- **WHEN** the workspace item is assembled
- **THEN** that key is not exposed in the item metadata.

### Requirement: P11 evidence retention

P11 SHALL retain requirements, traceability, manual-testing guidance, automated validation, OpenSpec, and hosted Quality evidence.

#### Scenario: P11 completion is evaluated
- **GIVEN** the P11 implementation candidate
- **WHEN** completion is requested
- **THEN** the exit review distinguishes implemented, empty-state, retained-artifact, policy-blocked, and deferred behavior.
