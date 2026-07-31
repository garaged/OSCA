# P17 Real-Money Controlled Pilot Specification

## Purpose

Record that P17 is blocked because P16 produced a binding NO-GO decision for real-money order execution.

## Decision

ADR-0044 is authoritative. P17 SHALL NOT implement broker connectivity, trading credentials, order APIs, sandbox orders, production orders, or any real-capital pilot.

## Requirements

- REQ-0275: P17 remains blocked unless ADR-0044 is explicitly superseded.
- REQ-0276: No broker or exchange adapter may be added under P17.
- REQ-0277: No trading credential material may be stored, requested, or consumed.
- REQ-0278: No order intent, approval, submission, cancellation, or reconciliation path may be introduced.
- REQ-0279: Existing research, paper, model, scheduler, and extension surfaces must remain unable to place orders.
- REQ-0280: Reconsideration requires closure of every P16 control-matrix blocker and a superseding ADR.
- REQ-0281: Documentation, OpenSpec, architecture status, roadmap, and hosted Quality must record the blocked disposition.

## Explicit non-scope

All live-order implementation work.

## Acceptance criteria

- P17 is visibly marked blocked and unauthorized.
- No executable order path is added.
- P16 NO-GO boundaries remain authoritative.
- The roadmap redirects to usability and release hardening of the non-trading product.

## Dependencies

ADR-0044 and the P16 exit review.
