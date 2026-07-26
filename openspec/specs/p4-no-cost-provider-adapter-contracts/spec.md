# p4-no-cost-provider-adapter-contracts Specification

## Purpose

Index the verified P4 no-cost provider adapter contract semantics under REQ-0184-REQ-0190 and ADR-0042.

## Requirements

### Requirement: Preferred provider adapter contracts

P4 provider adapters SHALL define deterministic adapter contracts only for preferred no-cost providers selected by P3.

#### Scenario: Adapter contracts are built
- **GIVEN** the default P3 provider profile catalog
- **WHEN** P4 adapter contracts are derived
- **THEN** only SEC EDGAR and FRED receive adapter contracts.

### Requirement: SEC EDGAR contract constraints

P4 provider adapters SHALL preserve SEC EDGAR public no-key access, declared user-agent requirement, fair-access policy, and SEC filing endpoint scope.

#### Scenario: SEC contract is inspected
- **GIVEN** the SEC EDGAR adapter contract
- **WHEN** its constraints are inspected
- **THEN** the contract requires a user-agent, does not require an API key, and exposes only SEC filing endpoints.

### Requirement: FRED contract constraints

P4 provider adapters SHALL preserve FRED named API-key reference requirements without storing credential values.

#### Scenario: FRED contract is inspected
- **GIVEN** the FRED adapter contract
- **WHEN** its credential requirement is inspected
- **THEN** the contract requires a named API-key reference and stores no credential value.

### Requirement: Fixture-backed request and payload validation

P4 provider adapters SHALL validate requests and fixtures against provider, endpoint, checksum, source, record-count, and disabled-network expectations.

#### Scenario: Fixture is validated
- **GIVEN** a fixture for a supported provider endpoint
- **WHEN** the fixture is validated against the adapter contract
- **THEN** OSCA accepts matching non-empty fixtures and rejects mismatched or invalid fixtures.

### Requirement: No live runtime boundary

P4 provider adapters SHALL NOT invoke provider APIs, materialize credentials, alter runtime routing, promote providers, or enable production ingestion.

#### Scenario: Adapter contract exists
- **GIVEN** a P4 adapter contract
- **WHEN** runtime provider behavior is evaluated
- **THEN** network access remains disabled and live provider use remains deferred.
