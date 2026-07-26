# P16 - Live-Order Readiness Study

- **Status:** Planned
- **Governing role:** Product authority
- **Phase:** Real-money/order-execution readiness
- **Authoritative outcome:** Decide whether OSCA should support real-money order execution by producing threat models, controls, and a go/no-go ADR.
- **Baseline:** Completed M0-M12 roadmap and P1-P4 provider governance
- **Last reviewed:** 2026-07-26
- **Validation:** Planned

## Current artifacts

- [Milestone plan](README.md)
- [Specification](../../specifications/p16-live-order-readiness-study.md)
- [Accepted OpenSpec specification](../../../openspec/specs/p16-live-order-readiness-study/spec.md)

## Objective

Decide whether OSCA should support real-money order execution by producing threat models, controls, and a go/no-go ADR.

## User-visible value

The project avoids drifting into capital execution without explicit product, legal, and security acceptance.

## Implementation scope

- Document broker/exchange execution risks.
- Define kill switches, reconciliation, limits, audit, manual approval, and incident controls.
- Assess regulatory, tax, custody, and liability boundaries.
- Produce a go/no-go ADR and implementation preconditions.

## Explicit non-scope

- Placing real orders, broker/exchange adapter implementation.

## Acceptance criteria

- REQ-0268-REQ-0274 are allocated before implementation begins.
- The implementation proves the stated scope with automated tests where code changes are made.
- Manual testing and usage is updated when operator-visible behavior changes.
- Deferred provider, credential, production-ingestion, and real-capital boundaries remain visible and fail closed unless this milestone explicitly owns them.
- Hosted Quality passes before completion is marked.

## Validation gates

- Ruff, mypy, pytest, architecture validation, OpenSpec validation, and secret scanning.
- Documentation, traceability, and manual-testing review.
- Exit review recording final evidence.

## Dependencies

P13-P14.

## Risks and decisions

The responsible outcome may be no-go or permanently manual-only.
