# P17 Real-Money Controlled Pilot Specification

## Purpose

If and only if P16 approves, implement a tiny controlled live-order pilot with hard limits, manual approval, reconciliation, and rollback.

## Phase

Real-money/order-execution readiness

## User-visible value

OSCA can test live execution mechanics under strict safety controls.

## Requirements

- REQ-0275-REQ-0281: OSCA must implement the P17 scope described by this specification before P17 is marked complete.
- REQ-0275-REQ-0281: P17 must preserve explicit non-scope boundaries and fail closed when a caller attempts deferred behavior.
- REQ-0275-REQ-0281: P17 completion requires updated requirements, traceability, milestone status, manual-testing review, OpenSpec evidence, automated validation, and hosted Quality evidence.

## Implementation scope

- Implement one approved broker/exchange adapter in manual-approval mode.
- Enforce hard spend, position, frequency, and symbol limits.
- Record pre-trade, order, fill, reconciliation, and rollback evidence.
- Add emergency stop and post-trade audit.

## Explicit non-scope

- Autonomous capital control, broad broker coverage, leveraged/derivative trading by default.

## Acceptance criteria

- The milestone objective is demonstrable from supported CLI, API, UI, or documented operator workflow surfaces, as applicable.
- Automated tests cover new code paths and negative/deferred-boundary behavior.
- Documentation and traceability identify implemented, specified-only, fixture-backed, and deferred behavior.
- The milestone exit review records validation evidence and remaining deferrals.

## Dependencies

P16 approval ADR, P14 production operations.

## Risks and decisions

High financial and compliance risk; P17 must not start without explicit approval.
