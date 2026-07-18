# Applying the OSCA Architecture

- **Status:** Accepted guidance
- **Governing role:** Architecture authority
- **Purpose:** Guide a contributor from accepted intent to a reviewable OSCA vertical slice.
- **Authoritative sources:** Engineering constitution; ADR-0001 through ADR-0010; governed engineering workflow
- **Review trigger:** Foundational ADR supersession or recurring review failure
- **Last reviewed:** 2026-07-18

## Start with authority

Use the [engineering constitution](../../engineering/constitution.md) to resolve authority and the [governed workflow](../governance/engineering-workflow.md) for normative delivery steps. This handbook explains application; it does not restate those rules as a second authority.

## Design sequence

1. Identify approved intent and requirement IDs.
2. Name the owning capability and the mutable state it alone owns.
3. Classify each interaction using the [decision matrix](../../engineering/decision-matrix.md).
4. Identify applicable ADRs, seams, quality attributes, and deferred-decision triggers.
5. Write the specification and acceptance criteria before implementation commits to a shape.
6. Classify change risk under ADR-0005 and select verification evidence.
7. Define security, observability, compatibility, migration, and recovery behavior.
8. Implement through published contracts and retain evidence.
9. Update traceability, indexes, usage guidance, and operational material in the same change.

## Capability authoring

A capability specification must make ownership visible: purpose, commands, queries, events, workflows, state, published contracts, dependencies, failure semantics, permissions, telemetry, recovery, and tests. Follow ADR-0002, ADR-0003, and the [dependency rules](../architecture/dependency-rules.md).

## Interaction selection

- Use a **query** to obtain information without requesting mutation.
- Use a **command** to ask the owning capability to change state.
- Use an **integration event** to publish an already committed fact.
- Use a **private domain event** only inside its owning capability.
- Use a **durable workflow** for long-running, retryable, scheduled, checkpointed, or compensating coordination.

ADR-0006 governs classification; ADR-0007 governs reliable events.

## State and persistence

One capability owns each mutable concept. Other capabilities use identifiers, immutable snapshots, public queries, or governed projections. Direct access to another capability's schema is prohibited by ADR-0009.

## Public contracts

Treat a surface as public when it is independently consumed, persisted, replayed, extended, automated, or expected to survive internal refactoring. Apply ADR-0004 and register the contract family before relying on compatibility.

## Cross-cutting completion

A feature is incomplete until its specification covers:

- deny-by-default authorization and secure authenticated transfer;
- telemetry, audit distinction, correlation, redaction, and health;
- failure, retry, idempotency, degradation, and recovery;
- migration and historical compatibility;
- deterministic or explicitly tolerant verification;
- user, developer, methodology, and operational documentation as applicable.

## Stop conditions

Stop and request a decision when work would silently resolve a triggered deferred decision, change product scope, cross a capability ownership boundary, weaken a Tier-1 ADR, create an ungoverned public contract, or accept security/recovery risk without authority.
