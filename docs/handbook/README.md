# OSCA Architecture Handbook

- **Milestone:** M0.5
- **Status:** Planned
- **Purpose:** Teach contributors and AI agents how to apply the accepted architecture consistently.

## Handbook structure

1. Architecture overview and compass
2. Architectural principles and invariants
3. Capability and module authoring
4. Command, query, event, and workflow selection
5. Persistence ownership and projections
6. Extension development and trust tiers
7. Security and secure communication
8. Observability, audit, and health
9. Testing, quality gates, and architecture fitness
10. Specification and traceability authoring
11. Architecture review playbook
12. Common patterns and anti-patterns
13. Reference capability
14. Glossary and decision matrix

## Required companion artifacts

- `engineering/constitution.md`
- `engineering/decision-matrix.md`
- `engineering/ai-contributor-contract.md`
- `engineering/architecture-evolution-policy.md`
- `engineering/architecture-registry.yaml`

## Reference capability

The handbook will include one technology-neutral vertical slice demonstrating intent, requirements, ownership, public contracts, queries, commands, domain and integration events, durable workflow coordination, persistence, extension interaction, security, observability, recovery, tests, and retained evidence.

The example teaches existing decisions; it must not introduce new product scope or bypass unresolved implementation choices.

## Completion criteria

M0.5 is complete when a contributor unfamiliar with the project can use the handbook to classify an interaction, identify ownership, author a compliant specification, select required evidence, and review a vertical slice without relying on undocumented conventions.
