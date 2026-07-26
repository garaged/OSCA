# P16 Live-Order Readiness Study Specification

## Purpose

Decide whether OSCA should support real-money order execution by producing threat models, controls, and a go/no-go ADR.

## Phase

Real-money/order-execution readiness

## User-visible value

The project avoids drifting into capital execution without explicit product, legal, and security acceptance.

## Requirements

- REQ-0268-REQ-0274: OSCA must implement the P16 scope described by this specification before P16 is marked complete.
- REQ-0268-REQ-0274: P16 must preserve explicit non-scope boundaries and fail closed when a caller attempts deferred behavior.
- REQ-0268-REQ-0274: P16 completion requires updated requirements, traceability, milestone status, manual-testing review, OpenSpec evidence, automated validation, and hosted Quality evidence.

## Implementation scope

- Document broker/exchange execution risks.
- Define kill switches, reconciliation, limits, audit, manual approval, and incident controls.
- Assess regulatory, tax, custody, and liability boundaries.
- Produce a go/no-go ADR and implementation preconditions.

## Explicit non-scope

- Placing real orders, broker/exchange adapter implementation.

## Acceptance criteria

- The milestone objective is demonstrable from supported CLI, API, UI, or documented operator workflow surfaces, as applicable.
- Automated tests cover new code paths and negative/deferred-boundary behavior.
- Documentation and traceability identify implemented, specified-only, fixture-backed, and deferred behavior.
- The milestone exit review records validation evidence and remaining deferrals.

## Dependencies

P13-P14.

## Risks and decisions

The responsible outcome may be no-go or permanently manual-only.
