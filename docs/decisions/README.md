# Architecture Decision Records

- **Status:** Active
- **Governing role:** Architecture authority
- **Purpose:** Index consequential technical decisions and their lifecycle.
- **Authoritative sources:** baseline product requirements and active architecture decisions
- **Downstream consumers:** Architecture, specifications, implementation, reviews, migrations, risks, and documentation

## Scope

An ADR records a consequential technical or engineering-governance choice that constrains multiple components, is expensive to reverse, establishes a compatibility or operational contract, resolves a material tradeoff, or creates an architecture fitness obligation.

ADRs cannot change product scope or weaken an baseline product requirement.

## Lifecycle

ADR lifecycle and freeze rules are defined in `engineering/architecture-evolution-policy.md`. Baseline ADRs remain authoritative within their scope until explicitly superseded.

## Index

| ADR | Title | Status |
|---|---|---|
| [ADR-0001](ADR-0001-requirements-authority-and-traceability-model.md) | Requirements authority and traceability model | Baseline |
| [ADR-0002](ADR-0002-modular-monolith-decomposition-model.md) | Modular-monolith decomposition model | Baseline |
| [ADR-0003](ADR-0003-module-boundary-enforcement-model.md) | Module-boundary enforcement model | Baseline |
| [ADR-0004](ADR-0004-public-contract-versioning-strategy.md) | Public contract versioning strategy | Baseline |
| [ADR-0005](ADR-0005-risk-tiered-quality-gate-enforcement.md) | Risk-tiered quality gate enforcement | Baseline |
| [ADR-0006](ADR-0006-inter-module-communication-model.md) | Inter-module communication model | Baseline |
| [ADR-0007](ADR-0007-event-reliability-and-delivery-model.md) | Event reliability and delivery model | Baseline |
| [ADR-0008](ADR-0008-tiered-extension-isolation-model.md) | Tiered extension isolation model | Baseline |
| [ADR-0009](ADR-0009-persistence-ownership-model.md) | Persistence ownership model | Baseline |
| [ADR-0010](ADR-0010-unified-observability-architecture.md) | Unified observability architecture | Baseline |

## Baseline status

The foundational ADR set is baseline and pending M0.6 validation. It enters Baseline after validation and becomes Frozen when M1 begins.

## Template

Use [adr-template.md](adr-template.md) for new decisions.
