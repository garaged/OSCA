# ADR-0003 — Module-Boundary Enforcement Model

- **Status:** Baseline
- **Date:** 2026-07-17
- **Decision owners:** Architecture authority and quality authority
- **Scope:** Repository structure, build graph, module visibility, architecture tests, CI evidence, and public/private contracts
- **Related requirements:** To be assigned during requirements-catalog population
- **Related product decisions:** D-006, D-007, D-008, D-021, D-044, D-046, D-047
- **Supersedes:** None
- **Superseded by:** None

## Context

ADR-0002 establishes capability-oriented modules, explicit ownership, acyclic dependencies, and narrow published contracts. Documentation and review conventions alone cannot reliably prevent private imports, shared persistence, hidden cycles, or erosion of extension boundaries. Independently versioning every internal module would add distribution and release complexity that the initial modular monolith does not need.

## Decision drivers

- Make logical boundaries mechanically verifiable.
- Preserve one repository, product version, and default deployable boundary.
- Keep internal refactoring practical.
- Support independent module tests and architecture evidence.
- Distinguish internal contracts from durable public contracts.
- Avoid premature package-distribution and microservice complexity.

## Considered alternatives

### Alternative A — Convention and review

Low setup cost, but weak evidence and easy boundary erosion.

### Alternative B — Build-enforced modules with fitness checks

Physical build units expose deliberate contracts, hide implementation by default, and are checked for cycles and prohibited dependencies while shipping together.

### Alternative C — Independently versioned internal packages

Strong isolation, but excessive compatibility, publishing, and release overhead for modules that always ship as one product.

## Decision

OSCA will use **build-enforced capability modules with automated architecture fitness checks**.

Internal modules:

- live in one repository;
- normally share one OSCA release version;
- form one default modular-monolith deployable;
- expose explicit contract surfaces;
- keep domain implementation, persistence, adapters, migrations, and test internals private by default;
- declare an acyclic build dependency graph;
- support module-focused build and test execution;
- are verified by automated architecture checks in CI.

Only independently consumed and durable surfaces—such as external application APIs, event schemas, artifact schemas, extension contracts, and persisted workflow definitions—receive separately governed compatibility versions when required.

The exact language, build system, package manager, repository layout syntax, and architecture-test tool remain later technology decisions. Candidate technologies must demonstrate that they can satisfy this ADR.

## Required fitness evidence

CI must eventually detect or prove, as applicable:

- module dependency cycles;
- imports of private module implementation;
- direct access to another module's persistence;
- extension dependencies on internal packages;
- unapproved shared-kernel growth;
- undeclared module dependencies;
- public-contract compatibility failures;
- expired architecture exceptions;
- ability to build and test modules without unrelated runtime dependencies.

## Consequences

### Positive

- Architecture rules become enforceable rather than aspirational.
- One product release remains easy to refactor and operate.
- Public seams have clear owners and visibility.
- Module and contract tests can provide focused evidence.
- Future extraction decisions can use real dependency data.

### Negative and tradeoffs

- Build configuration and architecture tests add initial work.
- Some language ecosystems may require additional tooling.
- Excessively fine module decomposition could harm build speed and developer experience.
- Contract discipline remains necessary even with physical enforcement.

### Required follow-up

- Finalize the module catalog and dependency graph.
- Define a technology-neutral repository structure specification.
- Specify public seams and compatibility obligations.
- Include enforcement capability in language and build-system evaluation criteria.
- Define architecture-exception records and CI quality gates.

## Migration and compatibility

No runtime migration is required. Early scaffolding must follow the selected physical module model. A future move to independent package releases or service extraction requires a new ADR and migration plan.

## Revisit triggers

Reconsider if the chosen ecosystem cannot provide meaningful module visibility and dependency checks, if build performance becomes unacceptable, or if independently deployed capabilities become operationally justified.