# M0 — Product and Engineering Foundation

- **Status:** In progress
- **Governing role:** Architecture authority
- **Approval role:** Product authority
- **Authoritative sources:** [Product requirements](../../product-requirements.md), [decision log](../../decision-log.md)
- **Purpose:** Index the governed artifacts and evidence required to make OSCA implementation-ready without beginning production feature implementation.
- **Downstream consumers:** M1–M12 milestone intents, specifications, architecture decisions, implementation plans, tests, reviews, and release evidence

## Outcome

M0 establishes an implementation-ready governance and architecture foundation for OSCA while preserving the approved local-first, single-user modular-monolith boundary.

M0 does not select an implementation language, database, frontend framework, ML framework, or deployment stack before requirements and decision criteria for those choices are defined.

## Control artifacts

- [Intent](intent.md)
- [Scope](scope.md)
- [Execution plan](execution-plan.md)
- Completion checklist — pending
- Exit evidence — pending

## Governance foundation

- [Document control](../../governance/document-control.md)
- [Requirements catalog](../../governance/requirements-catalog.md)
- [Traceability model](../../governance/traceability-model.md)
- [Traceability register](../../governance/traceability-register.md)
- [Glossary and ubiquitous language](../../glossary.md)

## Architecture foundation

- [Architecture index](../../architecture/README.md)
- [System context](../../architecture/system-context.md)
- [Conceptual domain model](../../architecture/domain-model.md)
- [Architecture principles](../../architecture/principles.md)
- [Modular-monolith boundaries](../../architecture/modular-monolith.md)
- [Dependency rules](../../architecture/dependency-rules.md)
- Draft public seams — pending
- Proposed repository structure — pending

## Decision records

- [ADR index](../../decisions/README.md)
- [ADR-0001 — Requirements authority and traceability model](../../decisions/ADR-0001-requirements-authority-and-traceability-model.md)
- [ADR-0002 — Modular-monolith decomposition model](../../decisions/ADR-0002-modular-monolith-decomposition-model.md)

## Increment status

- **Increment 1 — Governance control plane:** Published for M0 review.
- **Increment 2 — Ubiquitous language and system understanding:** Draft artifacts published for M0 review.
- **Increment 3 — Architecture foundation:** Logical principles and dependency rules published; boundary-enforcement decision pending.

All M0 artifacts remain subject to complete-package approval. Publication on `agent/m0-foundation` does not merge or approve the M0 package.
