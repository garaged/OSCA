# P17 - Real-Money Controlled Pilot

- **Status:** Planned
- **Governing role:** Product authority
- **Phase:** Real-money/order-execution readiness
- **Authoritative outcome:** If and only if P16 approves, implement a tiny controlled live-order pilot with hard limits, manual approval, reconciliation, and rollback.
- **Baseline:** Completed M0-M12 roadmap and P1-P4 provider governance
- **Last reviewed:** 2026-07-26
- **Validation:** Planned

## Current artifacts

- [Milestone plan](README.md)
- [Specification](../../specifications/p17-real-money-controlled-pilot.md)
- [Accepted OpenSpec specification](../../../openspec/specs/p17-real-money-controlled-pilot/spec.md)

## Objective

If and only if P16 approves, implement a tiny controlled live-order pilot with hard limits, manual approval, reconciliation, and rollback.

## User-visible value

OSCA can test live execution mechanics under strict safety controls.

## Implementation scope

- Implement one approved broker/exchange adapter in manual-approval mode.
- Enforce hard spend, position, frequency, and symbol limits.
- Record pre-trade, order, fill, reconciliation, and rollback evidence.
- Add emergency stop and post-trade audit.

## Explicit non-scope

- Autonomous capital control, broad broker coverage, leveraged/derivative trading by default.

## Acceptance criteria

- REQ-0275-REQ-0281 are allocated before implementation begins.
- The implementation proves the stated scope with automated tests where code changes are made.
- Manual testing and usage is updated when operator-visible behavior changes.
- Deferred provider, credential, production-ingestion, and real-capital boundaries remain visible and fail closed unless this milestone explicitly owns them.
- Hosted Quality passes before completion is marked.

## Validation gates

- Ruff, mypy, pytest, architecture validation, OpenSpec validation, and secret scanning.
- Documentation, traceability, and manual-testing review.
- Exit review recording final evidence.

## Dependencies

P16 approval ADR, P14 production operations.

## Risks and decisions

High financial and compliance risk; P17 must not start without explicit approval.
