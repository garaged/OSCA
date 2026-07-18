# OSCA Module Dependency Rules

- **Status:** Draft
- **Governing role:** Architecture authority
- **Approval roles:** Quality authority and security authority where applicable
- **Purpose:** Define technology-neutral dependency, ownership, communication, consistency, and verification constraints for OSCA capability modules.
- **Authoritative sources:** ADR-0002; architecture principles; modular-monolith boundaries; system context; conceptual domain model; PRD engineering-quality direction
- **Downstream consumers:** Final module graph, repository structure, public seams, specifications, code reviews, tests, CI gates, and architecture exceptions
- **Review triggers:** Module-map change, new dependency type, cross-module transaction, public seam change, enforcement-tool decision, or architecture exception

## Rule notation

- **Must** indicates a mandatory architecture constraint.
- **Should** indicates the expected default; deviation requires documented rationale.
- **May** indicates an allowed option whose detailed semantics must still be specified.

These rules govern logical dependencies regardless of programming language, build tool, package manager, process layout, or physical database.

## DR-01 — Dependencies follow published contracts

A module must depend only on another module’s explicitly published application contract, immutable contract types, versioned event schema, or approved public extension seam.

A module must not depend on another module’s private domain types, internal services, adapter implementations, persistence entities, migration code, test internals, or generated framework artifacts.

## DR-02 — Module-level dependencies are explicit and acyclic

The accepted module graph must be reviewable and acyclic at build-time dependency level.

A conceptual business cycle must be resolved through ownership, application orchestration, events, queries, replicated read models, or extraction of a genuinely shared invariant. It must not be hidden through runtime service lookup, dependency injection containers, reflection, string-based imports, or a shared database.

## DR-03 — One authoritative owner per mutable concept

Every mutable domain concept and invariant must have one owning module.

Non-owning modules may hold:

- stable identifiers;
- immutable value snapshots;
- explicit cached query results;
- replicated read models with owner and freshness metadata;
- event-derived projections.

They must not write or correct the owner’s state directly.

## DR-04 — Shared mutable domain models are prohibited

A shared package must not contain aggregates, mutable entities, repositories, application services, or product rules belonging to several modules.

Cross-module contract types should be minimal, immutable, versioned where externally durable, and free of private persistence or framework concerns.

## DR-05 — Shared kernel requires explicit approval

A shared kernel may contain only genuinely universal, stable, dependency-light semantics whose duplication would create greater correctness risk than coupling.

Candidates may include carefully governed identity, time, money, quantity, version, or error-envelope primitives, but inclusion is not automatic.

Every shared-kernel addition must document:

- why ownership by one module is incorrect;
- why translation or duplication is unsafe;
- stability and compatibility expectations;
- dependency and migration impact;
- tests proving universal semantics.

A growing shared kernel triggers architecture review and may require an ADR.

## DR-06 — Infrastructure depends inward on owned ports

External adapters implement ports or contracts owned by the capability requiring them.

Product rules must not depend directly on:

- provider SDKs;
- database drivers or persistence models;
- web frameworks;
- model-vendor clients;
- rendering libraries;
- secret-store implementations;
- notification SDKs;
- filesystem layout;
- deployment orchestrators.

Adapter-specific failures are translated into stable structured capability errors without erasing diagnostic detail.

## DR-07 — Clients depend on application capabilities

Web, CLI, API, notebooks, external automation, LLM tools, and background workers must invoke shared application capabilities.

Clients must not:

- duplicate authoritative validation or financial rules;
- query private persistence;
- construct private domain entities;
- bypass permission, provenance, audit, quality, or risk enforcement;
- infer success from transport completion alone.

Interface-specific presentation and interaction logic remains outside domain authority.

## DR-08 — Workers are execution adapters, not a business layer

A worker may schedule, invoke, resume, cancel, and observe application capabilities. It must not contain product rules unavailable to interactive or externally invoked application behavior.

Worker-specific checkpointing or batching may exist, but its semantics belong to the workflow or owning module specification.

## DR-09 — Commands target one owning module

A state-changing command must have one primary owning module responsible for validation, authorization, invariant enforcement, persistence, audit, and result semantics.

An application workflow may invoke several commands, but each state transition retains clear ownership. A broad command that mutates private state across modules is prohibited unless a documented cross-module invariant requires coordinated atomicity.

## DR-10 — Queries preserve ownership and policy

A query may return owned results, immutable references, or governed projections. It must preserve applicable authorization, privacy, licensing, quality, provenance, freshness, approximation, and availability semantics.

Queries must not expose arbitrary internal tables or implementation-shaped object graphs.

## DR-11 — Events describe completed facts

A domain or integration event must represent a completed owned fact, not a command disguised as an event.

Durable events must define:

- stable event identity;
- owner and schema version;
- effective and recorded times;
- correlation and causation identities;
- ordering scope if any;
- idempotency and duplicate behavior;
- replay and retention policy;
- privacy, licensing, and audit classification;
- compatibility rules.

An event consumer cannot assume delivery exactly once unless a later implementation decision and specification prove that guarantee. Business behavior must be idempotent or duplicate-aware where required.

## DR-12 — Orchestration owns process, not domain state

A coordinated workflow may manage sequence, progress, checkpointing, retry, timeout, compensation, and human approval across module capabilities.

It must not become the owner of domain rules or duplicate module state. Workflow state describes process progress and references module-owned results.

## DR-13 — Read models declare consistency

A replicated or composed read model must identify:

- authoritative sources;
- update mechanism;
- schema and version;
- freshness or lag expectation;
- rebuild procedure;
- invalidation behavior;
- behavior when a source is partial, unavailable, revised, or incompatible;
- security and licensing constraints.

A read model cannot be used as write authority merely because it is convenient or fast.

## DR-14 — Cross-module transactions are exceptional

A module owns atomic consistency for its own invariants. A cross-module transaction requires a documented business invariant, alternatives analysis, failure model, recovery plan, and architecture review.

Sharing one database transaction manager does not by itself justify cross-module atomic writes.

Where atomicity is not mandatory, designs should use explicit workflows, checkpoints, events, idempotency, compensation, or safe degraded states.

## DR-15 — Error contracts are structured and stable

Cross-module errors must preserve category, retryability, user impact, affected identity, diagnostic correlation, and safe remediation guidance as applicable.

Modules must not depend on another module’s exception class hierarchy or leak secrets, provider payloads, licensed data, or internal stack traces through public contracts.

## DR-16 — Temporal semantics are explicit

Contracts involving market data, models, strategies, paper actions, schedules, or recovery must distinguish relevant times, including:

- effective time;
- observed or provider time;
- retrieval time;
- recorded time;
- information-availability time;
- interval completion state;
- timezone and market calendar;
- revision or supersession time.

A generic timestamp without declared semantics is insufficient for financially or analytically material behavior.

## DR-17 — Data references are typed and revision-aware

Cross-module data access should pass stable dataset or artifact references with type, schema, revision, availability, integrity, lineage, and policy context rather than raw storage locations.

Paths, table names, mutable aliases, provider symbols, or URLs must not serve as authoritative cross-module identity.

## DR-18 — Security and permissions are enforced at every boundary

A caller’s owner status does not allow clients, extensions, LLM tools, or workers to bypass capability authorization.

Contracts must state required capability, scope, project or account context, credential references, audit behavior, and sensitive-output classification as applicable.

A module must not trust upstream validation as the sole protection for its owned invariants.

## DR-19 — Extensions depend only on public extension contracts

Extension code must not import internal module packages, access private persistence, rely on undocumented process state, or receive unrestricted credentials.

Public extension contracts must include:

- input, output, and parameter schemas;
- compatibility and versioning;
- provenance requirements;
- deterministic or seed behavior;
- resource and permission declarations;
- failure and diagnostics;
- data quality and provisional-input behavior;
- conformance fixtures.

## DR-20 — Public contracts evolve compatibly

A durable or independently consumed contract must declare a compatibility policy.

Breaking changes require:

- a new contract version or explicitly governed migration;
- impact analysis;
- coexistence or upgrade policy;
- retained-artifact and reproducibility treatment;
- tests for supported versions;
- documentation in the same change.

Internal contracts may evolve more rapidly but cannot silently break persisted workflows, artifacts, or extension references.

## DR-21 — Tests respect module ownership

A module’s unit and component tests should run without booting unrelated modules or external systems.

Cross-module tests use published contracts, controlled fixtures, and explicit fakes or test adapters. They must not depend on private persistence or internal test builders from another module unless the builder is a governed contract-test fixture.

End-to-end tests complement rather than replace module, contract, property, migration, security, and failure tests.

## DR-22 — Migrations preserve module ownership

Schema and data migrations are owned by the module that owns the affected state.

A migration crossing module state requires coordinated specifications, compatibility order, rollback or forward-recovery treatment, backup implications, and architecture review.

One module must not modify another module’s storage schema through its ordinary migration path.

## DR-23 — Observability crosses boundaries through correlation, not shared internals

Modules emit structured health, metrics, traces, job events, and audit records through governed telemetry contracts.

Correlation identity may connect activity across modules, but telemetry consumers must not become authoritative owners of domain state.

Sensitive or licensed content follows redaction and retention policy at emission time and at export.

## DR-24 — Recovery coordination does not erase ownership

Backup and recovery coordination may request consistent snapshots, checkpoints, export manifests, migrations, reconciliation, and validation from modules.

Each module retains responsibility for the meaning, integrity, compatibility, and validation of its owned state. The recovery capability coordinates recovery points and activation rather than interpreting every module’s domain records directly.

## DR-25 — Dependency exceptions are governed and temporary where possible

An exception must record:

- violated rule;
- necessity and alternatives;
- affected modules and requirements;
- security, consistency, migration, test, and recovery impact;
- owner and approver;
- removal plan or revisit trigger;
- automated detection where feasible.

An undocumented dependency is a defect, not an exception.

## Required dependency evidence

Before M0 exit, the architecture package must define how the selected repository and build structure will provide evidence for:

- prohibited dependency detection;
- module-cycle detection;
- public versus private contract visibility;
- shared-kernel growth;
- direct persistence access;
- internal-package imports by extensions;
- contract compatibility;
- module-specific tests;
- architecture exceptions and expiration.

The enforcement mechanism is intentionally deferred to a dedicated architecture decision because it will materially constrain repository structure, build behavior, and developer workflow.
