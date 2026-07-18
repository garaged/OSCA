# OSCA Architecture Status

## Current state

- **Product baseline:** Approved
- **M0 intent and architecture foundation:** Complete
- **Tier-1 ADRs:** Accepted
- **Architecture review:** Approved by architecture authority
- **Merge readiness:** Ready for pull request
- **Next milestone:** M0.5 — Architecture Handbook
- **Freeze point:** Tier-1 ADRs become frozen when M1 begins

## Governing baseline

The accepted Tier-1 architecture consists of ADR-0001 through ADR-0010. These decisions remain authoritative until superseded according to the [architecture evolution policy](engineering/architecture-evolution-policy.md).

No architecture artifact is frozen yet. Until M1 starts, corrections that preserve accepted intent may be applied as maintenance. Consequential changes require a new or superseding ADR.

## M0 completion evidence

- [x] Authoritative product requirements and immutable requirement identifiers
- [x] Traceability model and register
- [x] Ubiquitous language glossary
- [x] System context and conceptual domain model
- [x] Architecture principles and modular-monolith model
- [x] Module-boundary enforcement policy
- [x] Public seam specifications
- [x] Public-contract versioning policy and catalog
- [x] Communication, event reliability, extension, persistence, and observability decisions
- [x] Engineering workflow and AI contributor contract
- [x] Verification strategy and risk-tiered quality gates
- [x] Security, resilience, and recovery baselines
- [x] Architecture fitness program
- [x] Deferred-decision governance
- [x] Architecture authority review completed

## Open work

Remaining work is intentionally post-M0 and does not block this merge:

1. Complete the M0.5 handbook chapters and reference capability.
2. Execute the repeatable M0.6 validation program.
3. Baseline lifecycle, registry, and governance mechanics in M0.7.
4. Complete engineering-system automation planning in M0.8.
5. Select and specify the first M1 vertical slice.

## Key navigation

- [Repository overview](README.md)
- [Architecture overview](docs/architecture/README.md)
- [Architecture decisions](docs/decisions/README.md)
- [Engineering constitution](engineering/constitution.md)
- [M0 readiness and exit criteria](docs/milestones/m0/readiness-and-exit-criteria.md)
- [M0.x roadmap](docs/milestones/m0x-roadmap.md)
- [Deferred decisions](docs/governance/deferred-decisions.md)
