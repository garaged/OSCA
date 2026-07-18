# OSCA Architecture Foundation

- **Status:** Draft
- **Governing role:** Architecture authority
- **Approval roles:** Product authority, security authority, and quality authority where applicable
- **Purpose:** Index the technology-neutral architecture artifacts that govern OSCA before production implementation.
- **Authoritative sources:** Product requirements; decisions D-001 through D-047; accepted ADRs
- **Downstream consumers:** Milestone specifications, module contracts, implementation structure, tests, threat model, CI gates, and operational documentation
- **Review triggers:** Architecture decision, requirement change, module-boundary change, milestone entry or exit, or contradicting implementation evidence

## Foundation artifacts

- [System context](system-context.md)
- [Domain model](domain-model.md)
- Architecture principles — pending
- Modular-monolith boundaries — pending
- Dependency rules — pending
- Proposed repository structure — pending

## Draft public seams

The provider, analysis, visualization, model, and extension seams will be specified after the context, domain language, architecture principles, and dependency rules are stable enough to establish ownership and invariants.

## Decision records

Accepted architecture decisions are indexed in [the ADR directory](../decisions/README.md).

## Model status

Architecture diagrams and domain relationships in M0 are conceptual governance models. They are not database schemas, network-deployment diagrams, framework component diagrams, or implementation class models.
