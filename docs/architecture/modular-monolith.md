# OSCA Modular-Monolith Boundaries

- **Status:** Draft
- **Governing role:** Architecture authority
- **Approval roles:** Product authority, security authority, and quality authority where applicable
- **Purpose:** Define how capability modules are identified, owned, reviewed, and evolved within the initial single-user modular monolith.
- **Authoritative sources:** PRD sections 4, 6, 15–16, 18–30, 36, 38–40; decisions D-006–D-008, D-016–D-021, D-023–D-037, D-044, D-046–D-047; ADR-0002; system context; conceptual domain model; architecture principles
- **Downstream consumers:** Final module catalog, dependency graph, repository structure, public seams, specifications, tests, CI architecture gates, and service-extraction reviews
- **Review triggers:** Module creation, split, merge, ownership change, cross-module transaction, public seam change, architecture exception, or extraction proposal

## Boundary objective

The modular monolith must provide meaningful capability isolation without imposing distributed-system operation. Boundaries exist to protect language, invariants, state, security, failure behavior, changeability, verification, and future compatibility.

A folder name alone is not a module boundary. A valid module has all of the following:

- a named product or operational capability;
- a concise purpose and explicit non-responsibilities;
- governed vocabulary and semantic ownership;
- owned invariants and mutable state;
- published commands, queries, events, or public extension contracts;
- declared dependencies and consumers;
- explicit consistency and failure semantics;
- security, permission, provenance, and audit obligations;
- independent verification and fixtures;
- usage and operational documentation appropriate to risk.

## Boundary discovery criteria

A candidate capability should become a module when several of these signals align:

| Signal | Boundary implication |
|---|---|
| Distinct language and invariants | Strong evidence for separate ownership or a bounded context. |
| Independent lifecycle or revision policy | Separate module likely prevents inappropriate shared state. |
| Distinct security or permission boundary | Separate ownership and narrower contracts are required. |
| Different failure or recovery semantics | Module boundary supports containment and targeted recovery. |
| Coherent change pattern | Changes normally affect the capability without requiring unrelated internals. |
| Independent performance or workload profile | Separate internal execution policy may be justified without separate deployment. |
| Public extension seam | Stable explicit owner is required. |
| Distinct regulatory, licensing, or retention concerns | Separate policy enforcement and evidence may be required. |
| Independent testing and fixtures | Capability can demonstrate behavior without booting the entire system. |
| Plausible evidence-based extraction | Useful supporting signal, but never the primary reason to create a module. |

A candidate should not become a module solely because it has its own screen, table, framework component, external library, development team, or possible future microservice.

## Module categories

### Core domain modules

Capabilities whose rules directly protect financial, temporal, research, analytical, identity, or lifecycle correctness. They normally use explicit domain models and strong invariant tests.

Examples may include market identity, governed data revisions, analytical result lifecycle, strategy evaluation, deterministic risk, paper orders, and accounting.

### Supporting domain modules

Capabilities with meaningful product behavior that support core domains but may require less domain ceremony. Examples may include visualization composition, notification policy, or project export.

### Platform capability modules

Capabilities necessary across the product but still governed as products rather than generic utility libraries, such as durable workflows, extension governance, identity and permissions, observability, and recovery coordination.

Platform capability does not mean unrestricted dependency direction. A platform module publishes narrow services and cannot become a shared dumping ground.

### Adapters

Adapters translate owned ports to external technologies or providers. They do not own product rules. A provider SDK, database driver, model runtime, renderer, secret store, or notification mechanism is an adapter concern until product semantics require a governed capability around it.

## Candidate capability landscape

The following is a boundary hypothesis derived from the current context and domain model. It is not yet the accepted final module catalog.

| Candidate capability | Candidate ownership | Explicit exclusions or collaboration needs |
|---|---|---|
| **Market reference** | Canonical instruments, assets, listings, pairs, venues, provider mappings, calendars, lifecycle events, universes | Does not retrieve provider payloads or own project watchlists. |
| **Provider and acquisition** | Provider definitions, capabilities, routes, quotas, retrieval jobs, fallback, source capture | Does not define canonical market truth or analysis methodology. |
| **Data governance and lineage** | Dataset identity, revisions, canonical normalization governance, quality, repair, lineage, availability, retention impact | Physical payload storage may be adapter-owned; project ownership remains separate. |
| **Research projects** | Project intent, hypotheses, decisions, dependency locks, timelines, manifests, ad hoc promotion | Does not own global instruments, extensions, models, or paper-account history. |
| **Analytical composition** | Capability registry for analysis use, analysis definitions and graphs, runs, structured results, outcome evaluation | Does not own visualization rendering or authoritative paper execution. |
| **Visualization and reporting** | Visualization grammar, dashboards, report definitions, rendering, export, approximation disclosure, accessibility | Consumes governed results; cannot query private module storage. |
| **Strategy evaluation** | Strategy definitions, F0–F2 evaluation semantics, assumptions, comparisons, promotion evidence | Shares approved event, order-intent, and risk concepts with paper operation through explicit contracts. |
| **Deterministic risk** | Policy definitions, hierarchy, decisions, overrides, pause conditions, stress scenarios | Cannot depend on models or strategies for exception authority. |
| **Paper accounts and accounting** | Accounts, paper orders, immutable events, fills, journal, valuation, projections, reconciliation, automation pause | Independent of project ownership; consumes promoted candidates and market evidence. |
| **ML lifecycle** | Experiment definitions and runs, feature/label contracts, model registry, evaluations, deployments, drift | Training implementations may be extensions; deterministic risk remains external authority. |
| **LLM gateway** | Provider-neutral routing, prompts, tools, context policy, runs, structured validation, budgets, evaluations | Cannot own deterministic facts, direct database access, or live-order capability. |
| **Extension governance** | Package identity, manifests, installation, trust, permissions, activation, compatibility, conformance, impact | Extension execution isolation mechanism remains a later technical decision. |
| **Durable workflows** | Workflow definitions, schedules, runs, concurrency, checkpoints, missed-run and retry semantics | Invokes application capabilities; does not duplicate capability business rules. |
| **Identity and security** | Local and remote identity, sessions, scoped credentials, capability authorization, secret references, trust configuration, security audit | Secret values remain in a vault adapter; future multi-user identity requires redesign. |
| **Operations and recovery** | Health model, telemetry correlation, alerts and delivery coordination, storage pressure, backup profiles, recovery points, restore and exercises | Coordinates module-owned health and consistent recovery; does not silently assume ownership of all state. |

## Boundary questions before final approval

The final module catalog must explicitly resolve:

- whether market calendars and lifecycle events stay inside market reference or become separate capabilities;
- whether data governance owns normalization execution or only its policies, identity, quality, and lineage;
- whether analytical capability registration belongs to analysis or extension governance;
- how strategy evaluation and paper accounts share order, fill, accounting, and risk semantics without cyclic ownership;
- whether deterministic risk is an independent module or a subdomain exposed through one execution owner;
- whether alerts belong to analytical result lifecycle, operations, or a dedicated notification capability;
- how global catalog concepts are represented without becoming one shared-state module;
- how recovery coordinates consistent snapshots across module-owned state;
- whether any value types justify a minimal shared kernel.

These questions require detailed specifications and may produce additional ADRs. They do not justify choosing a language, framework, database, or deployment topology now.

## Module ownership record

The accepted module catalog will require one record per module containing:

- module ID and name;
- purpose and non-responsibilities;
- governing vocabulary;
- owned concepts, invariants, and state;
- application commands and queries;
- emitted and consumed events;
- public extension contracts, if any;
- upstream and downstream dependencies;
- consistency and transaction boundaries;
- idempotency, retry, and replay behavior;
- security, permission, privacy, and audit obligations;
- provenance and lineage obligations;
- failure and degraded states;
- observability and health semantics;
- backup, restore, migration, and compatibility responsibilities;
- test fixtures and fitness checks;
- related requirements, ADRs, risks, and milestones.

## Internal organization

A module may internally separate domain, application, ports, adapters, and presentation-supporting concerns where useful. This internal layering is subordinate to the capability boundary.

The following are prohibited:

- a global domain layer containing mutable concepts from many capabilities;
- a global service layer that bypasses module application contracts;
- a persistence layer shared as an unrestricted integration mechanism;
- generic `common`, `shared`, or `utils` areas with product rules or mutable state;
- framework annotations or generated models serving as the only domain contract;
- worker-specific business logic unavailable through the owning application capability.

## State ownership

- Each mutable record has one authoritative owning module.
- A module may expose stable immutable data references, snapshots, or queries.
- Consumer-specific read models are owned by their consumer or by an explicitly identified projection capability.
- Replicated data states its owner, source contract, version, freshness, rebuild behavior, and failure semantics.
- Physical co-location in one database does not imply shared ownership.
- Cross-module writes through another module’s persistence are prohibited.

## Collaboration forms

Permitted collaboration forms are:

1. **Application command:** asks the owning module to perform validated state-changing behavior.
2. **Application query:** requests an owned result or immutable reference without private-store access.
3. **Domain or integration event:** reports a completed fact for asynchronous reaction, with version, idempotency, and replay semantics.
4. **Coordinated workflow:** a durable application-level process invoking multiple module capabilities with checkpoints and compensation or recovery rules.
5. **Replicated read model:** explicit consumer projection derived from a published contract or event.
6. **Public extension contract:** separately versioned, permissioned, and conformance-tested seam.

Shared mutable objects and direct foreign persistence access are not collaboration mechanisms.

## Consistency boundaries

A module owns atomic consistency for its invariants. A requirement for atomicity across modules must document:

- the business invariant that would otherwise be violated;
- failure consequences and recovery behavior;
- alternatives considered;
- ownership of coordination;
- interruption and replay semantics;
- migration and operational impact.

Cross-module atomic transactions are permitted only when the documented invariant outweighs coupling cost. Transactional convenience is insufficient.

Backup and restore may require a consistent logical recovery point across modules. That coordination does not transfer semantic ownership to the recovery capability.

## Module evolution

A module may be split when its language, invariants, security, lifecycle, workload, or change patterns are no longer cohesive. Modules may be merged when boundaries create translation cost without protecting meaningful ownership or isolation.

Every split or merge requires:

- requirement and decision impact analysis;
- data and identity migration plan;
- contract and compatibility plan;
- test and observability changes;
- recovery and rollback treatment;
- an ADR when consequences are material.

## Service extraction threshold

Module extraction into a separately deployed service is not an M0 or default objective. It requires measured evidence such as:

- independently dominant scale or resource profile;
- security or fault-isolation need not achievable in-process;
- deployment cadence or availability requirement that materially differs;
- external organizational ownership with explicit operational capacity;
- technology constraint impossible to satisfy safely inside the product boundary.

The extraction ADR must include network failure, consistency, deployment, observability, security, backup, compatibility, local-mode, and operational-cost consequences.

## Pending architecture decision

The logical boundary rules are defined independently of implementation technology. M0 still requires a consequential decision on how these boundaries will be physically and automatically enforced in the repository and build system.
