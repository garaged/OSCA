# p2-no-cost-provider-discovery Specification

## Purpose

Index the verified P2 no-cost provider discovery and selection semantics under REQ-0168-REQ-0176 and ADR-0040.

## Requirements

### Requirement: No-cost provider discovery catalog

P2 provider discovery SHALL retain a governed catalog of no-cost provider candidates and exclusions before implementing additional provider adapters.

#### Scenario: Candidate is classified
- **GIVEN** a no-cost provider candidate
- **WHEN** it is added to the catalog
- **THEN** OSCA records cost model, account/key requirement, capability fit, source evidence, constraints, and disposition.

### Requirement: Discovery evidence and uncertainty

P2 provider discovery SHALL record official-source evidence where available and SHALL fail closed when licensing, redistribution, automation, quota, or account-plan evidence is unclear.

#### Scenario: Unclear automation evidence
- **GIVEN** a provider candidate without clear automation or redistribution evidence
- **WHEN** it is classified
- **THEN** the provider is marked conditional, research-only, or excluded.

### Requirement: Discovery does not imply promotion

P2 provider discovery SHALL NOT treat a catalog entry as adapter implementation, runtime routing, or production promotion.

#### Scenario: Catalog entry exists
- **GIVEN** a provider appears in the P2 catalog
- **WHEN** production routing is evaluated
- **THEN** the provider remains disabled until later implementation and P1 promotion evidence are accepted.
