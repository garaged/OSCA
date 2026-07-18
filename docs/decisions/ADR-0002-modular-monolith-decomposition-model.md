# ADR-0002 — Modular-Monolith Decomposition Model

- **Status:** Baseline
- **Date:** 2026-07-17
- **Decision owners:** Architecture authority
- **Scope:** Internal architecture, module ownership, dependency design, contracts, persistence ownership, testing boundaries, and future service extraction
- **Related requirements:** To be assigned during requirements-catalog population
- **Related product decisions:** D-006, D-007, D-008, D-019, D-021, D-044, D-046, D-047
- **Supersedes:** None
- **Superseded by:** None

## Context

OSCA is required to begin as a local-first, single-user modular monolith with background workers. It must support strong internal boundaries, independently testable capabilities, governed extension seams, and possible future service extraction without prematurely designing a distributed system.

The architecture therefore needs a consistent decomposition method before the system context, domain model, module catalog, dependency rules, repository structure, and draft extension seams can be finalized.

A purely horizontal architecture would make most product changes cross every layer and would encourage shared persistence and domain models. Applying full bounded-context isolation uniformly would provide strong separation but would impose translation and duplication costs even for supporting capabilities whose domain complexity does not justify them.

## Decision drivers

- Align module boundaries with accepted product capabilities and change patterns.
- Preserve the single-user modular-monolith boundary.
- Prevent a shared-model or shared-database monolith.
- Permit rigorous domain modeling where financial, analytical, temporal, security, or lifecycle complexity requires it.
- Keep supporting capabilities proportionate rather than forcing identical domain ceremony everywhere.
- Provide stable, testable contracts for interfaces, workers, extensions, and later milestones.
- Preserve future service extraction as an evidence-driven option rather than an initial design target.
- Avoid dependence on an implementation language, framework, database, or deployment stack.

## Considered alternatives

### Alternative A — Strict domain-driven bounded contexts everywhere

Every module would be treated as an independently modeled bounded context with explicit translations at every boundary.

**Benefits**

- Strong semantic isolation.
- Clear ownership of domain language and invariants.
- Strong protection against shared mutable models.
- Potentially clear service-extraction boundaries.

**Costs and risks**

- Imposes translation and duplication overhead on simple supporting capabilities.
- Encourages speculative bounded contexts before sufficient implementation evidence exists.
- Can increase cognitive load and slow delivery without improving correctness.
- Risks treating future distribution as an implicit objective.

### Alternative B — Capability-oriented modules informed by domain-driven design

Product capabilities are the primary decomposition unit. Bounded-context, aggregate, value-object, domain-event, and translation patterns are applied where domain complexity and semantic ownership justify them. Supporting capabilities remain explicit modules with governed contracts and ownership without mandatory full DDD ceremony.

**Benefits**

- Aligns directly with the PRD and risk-ordered milestones.
- Provides strong module boundaries while remaining proportionate.
- Supports independently testable capabilities and stable seams.
- Allows complex financial and research domains to use rigorous domain models.
- Keeps service extraction evidence-driven.

**Costs and risks**

- Requires disciplined rules so capability modules do not become arbitrary feature folders.
- Cross-cutting concepts require explicit ownership and translation decisions.
- Boundary quality depends on contract discipline and automated fitness checks.
- Some module boundaries will need refinement as domain knowledge improves.

### Alternative C — Traditional horizontal layers as the primary decomposition

The system would be organized principally into presentation, application, domain, persistence, infrastructure, and worker layers.

**Benefits**

- Familiar organization.
- Straightforward initial scaffolding in many frameworks.
- Centralized technical concerns can appear simple early in development.

**Costs and risks**

- Product changes tend to span every layer.
- Capability ownership is weak.
- Encourages shared persistence and domain models.
- Makes independent testing and extension contracts harder to govern.
- Creates poor evidence-based extraction boundaries.

## Decision

OSCA will use **capability-oriented modules informed by domain-driven design**.

A module is a cohesive product or operational capability with an explicit purpose, governing vocabulary, owned rules, owned state, published contracts, failure behavior, observability obligations, and verification boundary.

Domain-driven design patterns are required where they improve correctness or preserve semantic ownership, especially for instrument identity, governed datasets and lineage, analytical results, strategy validation, paper orders, accounting, risk, model lifecycle, extension governance, and recovery consistency. They are not mandatory ceremony for every supporting module.

The final M0 module catalog will be derived from the system context, domain model, accepted requirements, change patterns, security boundaries, consistency needs, and milestone dependencies. The preliminary capability list is a hypothesis to refine, not a frozen architecture.

Horizontal layers may exist **inside** a capability module as an implementation organization technique. They are not the primary system-level decomposition.

## Boundary rules established by this decision

- Every authoritative concept, invariant, and mutable record has one owning module.
- Other modules consume owned behavior or data only through published contracts or explicit replicated read models.
- A module cannot reach into another module's private persistence, internal types, or implementation services.
- Cross-module dependencies must be explicit, reviewable, and acyclic at the module level.
- Shared mutable domain models are prohibited.
- A shared kernel, if any, must remain minimal, stable, dependency-light, and limited to genuinely universal semantics.
- Infrastructure adapters implement ports owned by the capability that requires them; infrastructure does not own product rules.
- Background workers execute application capabilities and do not form an independent business-logic layer.
- Client interfaces use versioned application capabilities rather than duplicating module rules.
- Extension contracts are deliberate public seams and are narrower and more stable than ordinary internal module interfaces.
- Cross-module transactions must be justified by a documented consistency requirement. Transactional convenience alone cannot erase module ownership.
- Service extraction requires profiling, isolation, deployment, scaling, security, or organizational evidence and a new ADR.

## Rationale

Alternative B best satisfies the accepted modular-monolith direction. It aligns architecture with product capabilities and milestone outcomes while allowing rigorous bounded contexts where financial correctness, lineage, lifecycle, or security semantics demand them.

It avoids the weak ownership of horizontal layering and the speculative overhead of treating every capability as a fully isolated bounded context. It also preserves future compatibility without designing microservices, multi-tenancy, or distributed consistency into the initial product.

## Consequences

### Positive

- Module boundaries align with product behavior and change impact.
- Rich domains can protect invariants and language explicitly.
- Supporting capabilities can remain proportionate and understandable.
- Testing, observability, security review, and documentation can be organized by owned capability.
- Provider, analysis, visualization, model, and extension seams can be assigned to clear owners.
- Future extraction candidates can be evaluated from real dependency and operational evidence.

### Negative and tradeoffs

- Capability boundaries require continuous architecture review.
- Some concepts will need explicit translation between modules.
- Duplicate representations may be preferable to inappropriate shared ownership.
- Automated dependency and architecture checks will be necessary.
- Initial module hypotheses may change as requirements are decomposed and domain knowledge improves.

### Required follow-up

- Produce the system context and domain model before approving the concrete module catalog.
- Define architecture principles and detailed dependency rules.
- Assign ownership for cross-cutting concepts and identify any proposed shared kernel.
- Specify consistency, event, query, and failure semantics between modules.
- Define architecture fitness checks and repository enforcement before production implementation.
- Map each draft provider, analysis, visualization, model, and extension seam to an owning module.

## Fitness and verification

This decision remains effective when architecture evidence demonstrates that:

- every approved module has a unique purpose and owned capability;
- every mutable domain record and invariant has exactly one owning module;
- module dependencies are explicit and acyclic;
- no module accesses another module's private persistence or internal implementation types;
- cross-module interactions use documented contracts with defined failure behavior;
- architecture tests or equivalent automated checks detect forbidden dependencies;
- specifications, tests, observability, and documentation identify their owning module;
- changes to one capability do not require unrelated modules to change without a documented contract reason; and
- service extraction is not introduced without evidence and an accepted ADR.

## Migration and compatibility

No runtime migration is required because production implementation has not begun.

Future module refinements may move responsibilities while preserving requirement IDs, public contract compatibility, artifact lineage, and migration history. A change that alters an accepted public seam, persistence ownership, or cross-module consistency guarantee requires impact analysis and may require a superseding ADR.

## Risks

- **Arbitrary capability boundaries:** treat the module catalog as a reviewed architecture artifact derived from requirements, language, invariants, and change patterns.
- **Hidden coupling:** require explicit contracts, dependency visualization, architecture tests, and persistence-access controls.
- **Oversized modules:** review cohesion, change frequency, test scope, and internal subdomain boundaries.
- **Excessive fragmentation:** require each module to justify independent ownership and avoid one-concept modules.
- **Shared-kernel growth:** require architecture approval for additions and prefer module-owned representations with translation.
- **Premature extraction:** require evidence and a separate ADR.

## Revisit triggers

Reconsider this decision if:

- architecture fitness evidence shows persistent cyclic or high-change coupling;
- a capability cannot maintain clear ownership without excessive translation;
- operational evidence justifies process or service isolation;
- multi-tenancy or cross-installation synchronization becomes approved product scope;
- the extension model requires a materially different isolation boundary; or
- implementation experience demonstrates that the selected decomposition method prevents required correctness, performance, or maintainability outcomes.
