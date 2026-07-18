# ADR-0009: Persistence Ownership Model

- **Status:** Accepted
- **Tier:** Foundational
- **Date:** 2026-07-17

## Context

A modular codebase loses its boundaries when capabilities depend on one another's storage structures. Physical database sharing must not become shared domain ownership.

## Decision

Each capability exclusively owns its persistent state.

Ownership includes schema evolution, migrations, validation, retention, backup compatibility, recovery procedures, and persistence-specific performance decisions.

A capability must not read or write another capability's persistence directly and must not depend on another capability's schema. Cross-capability information and state transitions use public queries, commands, integration events, or explicitly governed projections and composed read models.

Persistence is an implementation detail and public contracts must not expose storage entities, table layouts, ORM objects, or provider-specific persistence types. A shared physical database does not imply shared logical ownership. A capability may replace its storage technology or schema while preserving public contract and compatibility obligations.

Cross-capability reporting and analytics use owned projections rather than direct joins across capability-owned schemas. Projection provenance, freshness, rebuild behavior, and compatibility are explicit.

## Consequences

Capabilities can evolve and be tested independently, and future extraction remains feasible. Reporting may duplicate data and requires deliberate projection design. Migration and recovery ownership become clearer.

## Rejected alternatives

- Unrestricted shared persistence.
- Governed exceptions permitting direct cross-capability reads.
