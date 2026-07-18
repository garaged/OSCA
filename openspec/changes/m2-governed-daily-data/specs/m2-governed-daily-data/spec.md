# m2-governed-daily-data Specification

## Purpose

Define the remaining bounded M2 behavior for governed daily ingestion, resolution, repair, quality, inspection, cleanup, and conditional reference adapters under REQ-0030–REQ-0040 and ADR-0017–ADR-0026.

## ADDED Requirements

### Requirement: Immutable governed daily revisions

Market Data SHALL normalize complete daily observations with exact decimal semantics and publish immutable bounded revisions through staged manifests. Accepted canonical history SHALL remain protected throughout M2.

#### Scenario: Equivalent governed content
- **WHEN** normalized content and every governed fingerprint input are equivalent to an accepted revision
- **THEN** ingestion resolves the existing revision rather than publishing duplicate canonical history

#### Scenario: Corrected governed content
- **WHEN** content or another governed fingerprint input changes
- **THEN** ingestion creates a new immutable revision linked to prior history

### Requirement: Explicit retrieval resolution

Market Data SHALL resolve unpinned requests to the latest accepted satisfying revision and exact pins only to the requested revision while exposing freshness, completeness, integrity, and safe remediation.

#### Scenario: Requested pin is unavailable
- **WHEN** an exact pinned revision cannot satisfy the bounded request
- **THEN** resolution is unavailable and no other revision is silently substituted

#### Scenario: Accepted data exceeds maximum age
- **WHEN** a satisfying revision is older than the declared maximum age
- **THEN** resolution is stale and identifies refresh as remediation

### Requirement: Conservative gap repair

Market Data SHALL treat completed UTC dates as expected for crypto and SHALL treat stock weekdays as unresolved until session evidence confirms them. Only confirmed missing dates SHALL become automatic repair ranges.

#### Scenario: Stock session is uncertain
- **WHEN** a weekday has neither an observation nor confirmed session evidence
- **THEN** it is unresolved and excluded from automatic repair

### Requirement: Protected cleanup preview

Cleanup SHALL be preview-first and policy-scoped and SHALL never select accepted canonical, pinned, catalog-required, or reproducibility-required material.

#### Scenario: Canonical revision is declared eligible
- **WHEN** an input incorrectly includes an accepted canonical revision among policy-eligible objects
- **THEN** the plan protects it and reports its bytes as protected

### Requirement: Conditional provider candidates

Twelve Data and Kraken candidate adapters SHALL implement the accepted provider-neutral daily contract with deterministic fixtures. Production visibility SHALL remain policy-blocked until provider-specific licensing, credential, quota, endpoint, and conformance evidence is accepted.

#### Scenario: Candidate payload is malformed
- **WHEN** a provider response violates the governed schema
- **THEN** the adapter returns a typed safe schema failure without observations or protected response content

### Requirement: Retained M2 evidence

The change SHALL retain contract, migration, normalization, revision, resolution, gap, repair, quality, provider, security, cleanup, recovery, documentation, performance, architecture, and traceability evidence.

#### Scenario: M2 completion review
- **WHEN** M2 exit is proposed
- **THEN** strict OpenSpec validation and every applicable OSCA gate pass against the retained source revision with provider promotion blockers explicit
