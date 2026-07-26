# p1-provider-production-promotion Specification

## Purpose

Index the verified P1 provider production promotion semantics under REQ-0157-REQ-0166 and ADR-0039.

## Requirements

### Requirement: Provider production evidence

P1 provider promotion evidence SHALL preserve provider identity, capability scope, licensing/account-plan evidence, named credential-reference evidence, quota evidence, retention policy, export policy, backup policy, reviewer, review time, and findings.

#### Scenario: Mixed provider evidence
- **GIVEN** a provider production evidence bundle
- **WHEN** any nested evidence targets a different provider
- **THEN** validation fails closed.

### Requirement: Licensing permission gates

Provider promotion SHALL require explicit retrieval, retention, transformation, export, and backup permission evidence before production enablement.

#### Scenario: Missing export permission
- **GIVEN** provider license evidence without export permission
- **WHEN** promotion is evaluated
- **THEN** promotion is blocked.

### Requirement: Credential evidence safety

Provider credential evidence SHALL use named secret references and SHALL NOT store secret values.

#### Scenario: Secret-looking reference
- **GIVEN** credential evidence containing a key, token, or password-shaped value
- **WHEN** the record is validated
- **THEN** validation fails closed.

### Requirement: Quota headroom gates

Provider promotion SHALL preserve quota policy, request limit, remaining requests, reset time, observed time, and required headroom evidence.

#### Scenario: Insufficient headroom
- **GIVEN** quota evidence below required headroom
- **WHEN** promotion is evaluated
- **THEN** promotion is blocked.

### Requirement: Deterministic provider promotion decisions

Provider promotion decisions SHALL approve only complete evidence, defer warning findings, and block error findings.

#### Scenario: Warning finding
- **GIVEN** complete provider evidence with a warning finding
- **WHEN** promotion is evaluated
- **THEN** promotion is degraded and production is not enabled.

### Requirement: Provider promotion metadata persistence

Provider promotion metadata SHALL persist evidence bundles and promotion decisions with provider-scoped queries.

#### Scenario: Provider query
- **GIVEN** evidence records for multiple providers
- **WHEN** one provider is queried
- **THEN** only records scoped to that provider are returned.
