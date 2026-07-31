# P16 - Live-Order Readiness Study

- **Status:** Study candidate
- **Governing role:** Product, architecture, and security authorities
- **Phase:** Real-money/order-execution readiness
- **Authoritative outcome:** Decide whether OSCA should support real-money order execution without implementing an order path.
- **Baseline:** P15 merge commit `5d3e7966a53668c9f38a3ad9feaf0a953afe8e14`
- **Last reviewed:** 2026-07-31
- **Decision:** NO-GO

## Objective

Evaluate capital-execution risks, mandatory controls, legal/accountability boundaries, and explicit reconsideration preconditions.

## Delivered artifacts

- [Threat model](threat-model.md)
- [Mandatory control matrix](control-matrix.md)
- [Legal and accountability review](legal-accountability-review.md)
- [Exit review](exit-review.md)
- [ADR-0044](../../decisions/ADR-0044-live-order-execution-readiness-decision.md)
- [Specification](../../specifications/p16-live-order-readiness-study.md)
- [OpenSpec](../../../openspec/specs/p16-live-order-readiness-study/spec.md)
- [P15-P16 reconciliation](../../governance/p15-p16-reconciliation.md)

## Outcome

OSCA is not ready for real-money order execution. Current architecture lacks independent per-order authorization, externally enforced limits, venue-specific order state and reconciliation, independently operable kill switches, hardened trading credential custody, completed legal/account review, and operational coverage.

## Explicit non-scope

- Broker or exchange adapters.
- Trading credentials.
- Order intent, approval, submission, cancellation, or reconciliation code.
- Sandbox or production orders.
- Autonomous execution or real-capital pilots.

## Reconsideration

A future proposal requires every blocker in the control matrix to be closed and an accepted ADR superseding ADR-0044. P17 remains unauthorized.

## Validation gates

- Documentation and link validation.
- Requirements and architecture traceability.
- OpenSpec doctor and strict validation.
- Secret scanning.
- Hosted Quality before completion is marked.
