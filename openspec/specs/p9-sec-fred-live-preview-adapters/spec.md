# p9-sec-fred-live-preview-adapters Specification

## Purpose

Define the corrected P9 semantics for an opt-in SEC EDGAR enrichment preview and a fail-closed FRED terms gate.

## Requirements

### Requirement: P9 SEC preview scope

P9 SHALL implement deterministic SEC fixture replay and explicit opt-in SEC company-facts or submissions preview with bounded network, cache, and provenance controls.

#### Scenario: SEC fixture replay is requested
- **GIVEN** a supported SEC endpoint, CIK, and deterministic fixture
- **WHEN** preview runs without network access
- **THEN** OSCA returns evidence from the fixture and does not use the network.

#### Scenario: SEC live preview is requested
- **GIVEN** a supported SEC endpoint and normalized CIK
- **WHEN** the caller explicitly enables network access and supplies a declared organization/contact user-agent
- **THEN** OSCA requests only an approved HTTPS `data.sec.gov` path under bounded fair-access, timeout, and response-size controls.

#### Scenario: SEC live preview is not explicitly enabled
- **GIVEN** no fixture path and disabled network access
- **WHEN** preview is requested
- **THEN** OSCA fails closed before transport use.

### Requirement: P9 SEC cache and provenance

P9 SHALL retain bounded local SEC preview payloads and evidence metadata without presenting them as production ingestion.

#### Scenario: A cached SEC preview exists
- **GIVEN** a valid cached payload for the same endpoint and CIK
- **WHEN** preview runs without force refresh
- **THEN** OSCA returns cache-hit evidence and does not issue another network request.

#### Scenario: A SEC response is invalid or oversized
- **GIVEN** malformed JSON, missing provider structures, or content above the configured limit
- **WHEN** preview validates the response
- **THEN** OSCA fails closed and does not accept the payload as evidence.

### Requirement: P9 FRED terms gate

P9 SHALL preserve the FRED fixture contract while blocking live FRED API use, credential resolution, and content retention until accepted terms evidence permits them.

#### Scenario: FRED live preview is attempted
- **GIVEN** a FRED series request with or without a named secret reference
- **WHEN** preview is evaluated
- **THEN** OSCA returns policy-blocked evidence, performs no network request, resolves no credential, and exposes no payload.

#### Scenario: A FRED secret value is embedded
- **GIVEN** a credential field containing a value rather than a named `secret:` reference
- **WHEN** the request is validated
- **THEN** OSCA rejects it before policy evaluation.

### Requirement: P9 deferred-boundary enforcement

P9 SHALL preserve explicit deferred boundaries for behavior outside its approved scope.

#### Scenario: Production or trading behavior is inferred
- **GIVEN** P9 preview evidence
- **WHEN** a caller inspects its capability flags
- **THEN** production ingestion, runtime routing, recommendations, broker execution, autonomous execution, and real-capital orders remain disabled.

### Requirement: P9 evidence retention

P9 SHALL retain requirements, traceability, OpenSpec, manual-testing review, automated validation, and hosted Quality evidence.

#### Scenario: P9 completion is requested
- **GIVEN** P9 implementation work
- **WHEN** completion is evaluated
- **THEN** exit-review evidence identifies implemented SEC behavior, fixture-backed contracts, FRED policy-blocked behavior, and deferred production/trading behavior.
