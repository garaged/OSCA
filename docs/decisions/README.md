# Architecture Decision Records

- **Status:** Active
- **Governing role:** Architecture authority
- **Purpose:** Index consequential technical decisions and their lifecycle.
- **Authoritative sources:** accepted product requirements and active architecture decisions
- **Downstream consumers:** Architecture, specifications, implementation, reviews, migrations, risks, and documentation

## Scope

An ADR records a consequential technical or engineering-governance choice that constrains multiple components, is expensive to reverse, establishes a compatibility or operational contract, resolves a material tradeoff, or creates an architecture fitness obligation.

ADRs cannot change product scope or weaken an accepted product requirement.

## Lifecycle

ADR lifecycle and freeze rules are defined in `engineering/architecture-evolution-policy.md`. Accepted ADRs remain authoritative within their scope until explicitly superseded.

## Index

| ADR | Title | Status |
|---|---|---|
| [ADR-0001](ADR-0001-requirements-authority-and-traceability-model.md) | Requirements authority and traceability model | Accepted |
| [ADR-0002](ADR-0002-modular-monolith-decomposition-model.md) | Modular-monolith decomposition model | Accepted |
| [ADR-0003](ADR-0003-module-boundary-enforcement-model.md) | Module-boundary enforcement model | Accepted |
| [ADR-0004](ADR-0004-public-contract-versioning-strategy.md) | Public contract versioning strategy | Accepted |
| [ADR-0005](ADR-0005-risk-tiered-quality-gate-enforcement.md) | Risk-tiered quality gate enforcement | Accepted |
| [ADR-0006](ADR-0006-inter-module-communication-model.md) | Inter-module communication model | Accepted |
| [ADR-0007](ADR-0007-event-reliability-and-delivery-model.md) | Event reliability and delivery model | Accepted |
| [ADR-0008](ADR-0008-tiered-extension-isolation-model.md) | Tiered extension isolation model | Accepted |
| [ADR-0009](ADR-0009-persistence-ownership-model.md) | Persistence ownership model | Accepted |
| [ADR-0010](ADR-0010-unified-observability-architecture.md) | Unified observability architecture | Accepted |

## Baseline status

The foundational ADR set is accepted and pending M0.6 validation. It enters Baseline after validation and becomes Frozen when M1 begins.

## Template

Use [adr-template.md](adr-template.md) for new decisions.
