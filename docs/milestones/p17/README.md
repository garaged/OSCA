# P17 - Real-Money Controlled Pilot

- **Status:** Blocked and not authorized
- **Governing role:** Product authority
- **Phase:** Real-money/order-execution readiness
- **Authoritative outcome:** Preserve the P16 NO-GO decision and prevent implementation of a live-order pilot unless ADR-0044 is superseded.
- **Baseline:** P16 merge commit `81297ed1f6c781bd1256304e4b94667dde55f8f8`
- **Last reviewed:** 2026-07-31
- **Validation:** Documentation-only disposition pending hosted Quality

## Disposition

P17 cannot start because its mandatory prerequisite was not satisfied. P16 concluded with ADR-0044: NO-GO for real-money order execution.

## Prohibited work

- Broker or exchange adapters.
- Trading credential storage or retrieval.
- Order intent, approval, submission, cancellation, or reconciliation APIs.
- Sandbox or production orders.
- Autonomous or manually approved real-capital pilots.

## Reconsideration rule

P17 may be reconsidered only after every blocker in the P16 control matrix is closed and a new ADR explicitly supersedes ADR-0044. Repository code, documentation, examples, and extensions must continue to fail closed until then.

## Safe roadmap direction

The next product work should improve the already usable research product: onboarding, integrated manual workflows, release packaging, usability validation, diagnostics, and evidence export. It must not create an execution path.

## Completion meaning

P17 is not implemented and is not marked complete as a pilot. This disposition closes the planned sequence by recording that the prerequisite failed and the capability remains unauthorized.
