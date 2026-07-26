# p3-no-cost-provider-profile-catalog Specification

## Purpose

Index the verified P3 no-cost provider profile catalog semantics under REQ-0177-REQ-0183 and ADR-0041.

## Requirements

### Requirement: Provider profile contracts

P3 provider catalog SHALL represent no-cost provider candidates through deterministic contracts carrying provider identity, cost model, payment requirement, access mode, capabilities, disposition, source URIs, constraints, and production-promotion boundary.

#### Scenario: Profile is created
- **GIVEN** a no-cost provider candidate from the P2 catalog
- **WHEN** it is represented as a provider catalog profile
- **THEN** OSCA records identity, cost model, access mode, capabilities, disposition, source URIs, and constraints.

### Requirement: Default candidate profiles

P3 provider catalog SHALL provide default profiles for SEC EDGAR, FRED, Alpha Vantage, Nasdaq Data Link, Stooq, and Yahoo Finance unofficial paths with dispositions matching P2.

#### Scenario: Default catalog is loaded
- **GIVEN** the default provider catalog
- **WHEN** profiles are listed
- **THEN** SEC EDGAR and FRED are preferred, Alpha Vantage and Nasdaq Data Link are conditional, Stooq is research-only, and Yahoo Finance unofficial paths are excluded.

### Requirement: Implementation readiness classification

P3 provider catalog SHALL classify preferred candidates as ready for adapter-contract planning, conditional candidates as needing evidence, and research-only or excluded providers as blocked from default automated implementation.

#### Scenario: Excluded provider is classified
- **GIVEN** an excluded provider profile
- **WHEN** implementation readiness is evaluated
- **THEN** OSCA returns a blocked readiness decision with retained blocking constraint identifiers.

### Requirement: No provider runtime boundary

P3 provider catalog SHALL NOT implement provider adapters, invoke provider APIs, materialize credentials, alter runtime routing, or promote providers as part of P3.

#### Scenario: P3 profile exists
- **GIVEN** a provider appears in the P3 profile catalog
- **WHEN** runtime provider behavior is evaluated
- **THEN** the provider remains unavailable for live calls, routing, and promotion until later governed milestones accept that scope.
