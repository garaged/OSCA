# P2 No-Cost Provider Discovery OpenSpec

## ADDED Requirements

### Requirement: No-cost provider discovery catalog

OSCA SHALL retain a governed catalog of no-cost provider candidates and exclusions before implementing additional provider adapters.

#### Scenario: Candidate is classified
- **GIVEN** a no-cost provider candidate
- **WHEN** it is added to the catalog
- **THEN** OSCA records cost model, account/key requirement, capability fit, source evidence, constraints, and disposition

### Requirement: Discovery does not imply promotion

OSCA SHALL NOT treat provider discovery as adapter implementation, runtime routing, or production promotion.

#### Scenario: Catalog entry exists
- **GIVEN** a provider appears in the P2 catalog
- **WHEN** production routing is evaluated
- **THEN** the provider remains disabled until later implementation and P1 promotion evidence are accepted
