# OSCA Architecture Foundation

- **Status:** Accepted baseline
- **Governing role:** Architecture authority
- **Approval roles:** Product, security, and quality authorities where applicable
- **Purpose:** Index the technology-neutral M0 architecture that governs OSCA implementation.
- **Authoritative sources:** Product requirements; decisions D-001 through D-047; ADR-0001 through ADR-0010
- **Downstream consumers:** Milestone specifications, module contracts, implementation, tests, CI gates, and operations
- **Review trigger:** Superseding ADR, requirement change, module-boundary change, or contradicting evidence
- **Last reviewed:** 2026-07-18

## Foundation

- [System context](system-context.md)
- [Domain model](domain-model.md)
- [Architecture principles](principles.md)
- [Modular-monolith boundaries](modular-monolith.md)
- [Dependency rules](dependency-rules.md)
- [Why OSCA is built this way](why-osca-is-built-this-way.md)

Physical repository syntax remains intentionally deferred by DD-001 and DD-002. ADR-0003 and the dependency rules already define the required enforcement outcomes.

## Public seams

Provider, analysis, model, LLM, workflow, visualization, and extension seams are indexed in the [public seams catalog](../seams/README.md). ADR-0004 governs durable contract evolution.

## Cross-cutting architecture

- [Security architecture](../security/security-architecture.md)
- [Resilience and recovery](../operations/resilience-and-recovery.md)
- [Verification strategy](../quality/verification-strategy.md)
- [Architecture fitness program](../quality/architecture-fitness-program.md)
- [Contract catalog](../governance/contract-catalog.md)
- [Architecture registry](../../engineering/architecture-registry.yaml)

## Application and validation

- [Architecture handbook](../handbook/README.md)
- [Decision matrix](../../engineering/decision-matrix.md)
- [Reference capability](../handbook/reference-capability.md)
- [Architecture validation](../validation/README.md)
- [Tier-1 ADR index](../decisions/README.md)

Architecture diagrams and domain relationships are conceptual governance models, not database schemas, deployment diagrams, framework components, or implementation classes.
