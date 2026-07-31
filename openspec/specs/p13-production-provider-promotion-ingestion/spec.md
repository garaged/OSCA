# p13-production-provider-promotion-ingestion Specification

## Purpose

Define evidence-gated provider admission and durable internal-use ingestion.

## Requirements

### Requirement: Auditable provider admission

P13 SHALL classify each candidate provider as `approved`, `needs_evidence`, or `policy_blocked`, with exact resource scope, terms reference, evidence-review time, and findings.

#### Scenario: Admission policy is inspected
- **GIVEN** the P13 policy command
- **WHEN** the operator inspects provider admission
- **THEN** SEC and Kraken expose only their admitted resources, account-specific providers remain evidence-gated, and FRED remains blocked.

### Requirement: Fail closed before network use

P13 SHALL reject non-admitted providers, non-admitted resources, disabled network access, and non-allowlisted endpoints before provider transport is invoked.

#### Scenario: Deferred provider is requested
- **GIVEN** a provider in `needs_evidence`
- **WHEN** ingestion is requested
- **THEN** OSCA returns `provider_unavailable` without network use.

#### Scenario: FRED is requested
- **GIVEN** FRED remains `policy_blocked`
- **WHEN** ingestion is requested
- **THEN** OSCA returns `policy_blocked` without credential resolution, network use, or retention.

### Requirement: Bounded durable ingestion

P13 SHALL apply bounded timeout, response-size, and retry controls and SHALL atomically retain successful JSON payloads with metadata and SHA-256 lineage.

#### Scenario: Approved ingestion succeeds
- **GIVEN** an admitted resource and explicit network permission
- **WHEN** a valid provider payload is returned
- **THEN** OSCA retains the payload and metadata with provider, resource, endpoint, attempts, network state, size, and digest.

#### Scenario: Provider response is invalid
- **GIVEN** an admitted request
- **WHEN** the provider returns invalid JSON or exceeds the response limit
- **THEN** OSCA fails after bounded attempts and does not publish a successful evidence record.

### Requirement: Reversible and internal-use-only admission

P13 SHALL evaluate admission before every run so a downgraded decision stops future ingestion without deleting historical evidence. Redistribution and external public display SHALL remain disabled.

#### Scenario: Admission is revoked
- **GIVEN** retained historical evidence and a provider admission changed away from `approved`
- **WHEN** another run is requested
- **THEN** OSCA blocks the new run while preserving prior retained evidence.

### Requirement: P13 completion evidence

P13 SHALL retain requirements, traceability, manual usage, automated validation, OpenSpec, and hosted Quality evidence before completion is marked.
