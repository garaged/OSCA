# ADR-0044: Live-order execution readiness decision

- **Status:** Accepted
- **Date:** 2026-07-31
- **Owners:** Product authority, architecture authority, security authority
- **Decision type:** Safety, product scope, and operational risk

## Context

OSCA now supports deterministic research, backtesting, paper evidence, bounded production data ingestion, personal-server operations, and trusted-local extension packs. The roadmap requires an explicit decision before any broker or exchange order path is implemented.

Real-money submission introduces irreversible financial impact and new trust boundaries: credentials, account state, order authorization, venue ambiguity, partial fills, reconciliation, limits, emergency stopping, regulatory obligations, and operational coverage. Current OSCA capabilities do not close these risks.

## Decision

OSCA is **NO-GO for real-money order execution**.

The repository must not add broker/exchange trading credentials, live-order adapters, order-submission endpoints, unattended execution, or real-capital pilot behavior under the current architecture and governance baseline.

Research outputs, model previews, paper evaluation, schedules, and extension packs must remain incapable of directly creating or submitting a real order.

## Rationale

- There is no independent per-order authorization mechanism bound to an immutable order digest.
- There are no externally enforced pre-trade limits or independently operable kill switches.
- There is no durable venue-specific order state machine or continuous account reconciliation.
- Credential custody, non-withdrawable scope, rotation, and emergency revocation are not implemented or tested.
- Legal, tax, account-contract, jurisdiction, and accountability reviews are unresolved.
- The trusted-local extension boundary is not a hostile-code sandbox and must never gain implicit order authority.
- Existing alert, backup, evidence, and paper controls are useful foundations but insufficient for capital execution.

## Consequences

### Required behavior

- All real-order requests remain absent or explicitly policy-blocked.
- Documentation must clearly distinguish research, paper evidence, and live execution.
- P17 remains unauthorized.
- Any future reconsideration requires every blocker in the P16 control matrix to be closed.

### Prohibited shortcuts

- Treating broker sandbox success as production authorization.
- Reusing provider or extension credentials for trading.
- Allowing a strategy, model, scheduler, or pack to approve its own order.
- Blind retries after an ambiguous venue response.
- Depending only on an in-process kill switch.
- Using disclaimer text as a substitute for technical and operational controls.

## Reconsideration rule

A future proposal must use a superseding ADR and include:

1. Written legal and account-contract review for the exact jurisdiction, venue, account, asset class, and user model.
2. Named accountable product, risk, security, operations, and incident owners.
3. Independent per-order human approval and immutable order-intent evidence.
4. External hard limits, venue reconciliation, idempotency, unknown-state handling, and independent kill switches.
5. Security review, signed release provenance, credential-custody design, and emergency drills.
6. Sandbox and paper observation evidence with zero unresolved reconciliation drift.
7. A separately approved tiny fixed-capital pilot proposal.

Until a superseding ADR is accepted, the decision remains NO-GO.

## References

- `docs/milestones/p16/threat-model.md`
- `docs/milestones/p16/control-matrix.md`
- `docs/milestones/p16/legal-accountability-review.md`
- `docs/specifications/p16-live-order-readiness-study.md`
