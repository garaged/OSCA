# Architecture Decision Records

- **Status:** Active
- **Governing role:** Architecture authority
- **Purpose:** Index consequential technical decisions and their lifecycle.
- **Authoritative sources:** baseline product requirements and active architecture decisions
- **Downstream consumers:** Architecture, specifications, implementation, reviews, migrations, risks, and documentation

## Scope

An ADR records a consequential technical or engineering-governance choice that constrains multiple components, is expensive to reverse, establishes a compatibility or operational contract, resolves a material tradeoff, or creates an architecture fitness obligation.

ADRs cannot change product scope or weaken a baseline product requirement.

## Lifecycle

ADR lifecycle and freeze rules are defined in `engineering/architecture-evolution-policy.md`. Baseline ADRs remain authoritative within their scope until explicitly superseded.

## Index

| ADR | Title | Status |
|---|---|---|
| [ADR-0001](ADR-0001-requirements-authority-and-traceability-model.md) | Requirements authority and traceability model | Frozen |
| [ADR-0002](ADR-0002-modular-monolith-decomposition-model.md) | Modular-monolith decomposition model | Frozen |
| [ADR-0003](ADR-0003-module-boundary-enforcement-model.md) | Module-boundary enforcement model | Frozen |
| [ADR-0004](ADR-0004-public-contract-versioning-strategy.md) | Public contract versioning strategy | Frozen |
| [ADR-0005](ADR-0005-risk-tiered-quality-gate-enforcement.md) | Risk-tiered quality gate enforcement | Frozen |
| [ADR-0006](ADR-0006-inter-module-communication-model.md) | Inter-module communication model | Frozen |
| [ADR-0007](ADR-0007-event-reliability-and-delivery-model.md) | Event reliability and delivery model | Frozen |
| [ADR-0008](ADR-0008-tiered-extension-isolation-model.md) | Tiered extension isolation model | Frozen |
| [ADR-0009](ADR-0009-persistence-ownership-model.md) | Persistence ownership model | Frozen |
| [ADR-0010](ADR-0010-unified-observability-architecture.md) | Unified observability architecture | Frozen |
| [ADR-0011](ADR-0011-python-runtime-build-and-repository-model.md) | Python runtime, build, and repository model | Accepted |
| [ADR-0012](ADR-0012-m1-metadata-persistence-and-migration.md) | M1 metadata persistence and migration | Accepted |
| [ADR-0013](ADR-0013-embedded-durable-job-executor.md) | Embedded durable job executor | Accepted |
| [ADR-0014](ADR-0014-m1-contract-and-interface-representation.md) | M1 contract and interface representation | Accepted |
| [ADR-0015](ADR-0015-local-security-secrets-and-telemetry-profile.md) | Local security, secrets, and telemetry profile | Accepted |

## Baseline status

ADR-0001 through ADR-0010 are the validated and Frozen M0 Baseline. Changes require superseding ADRs. ADR-0011 through ADR-0015 are accepted M1 decisions and remain governed by the architecture evolution policy.

## Template

Use [adr-template.md](adr-template.md) for new decisions.
