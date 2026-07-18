## Why

M1.1–M1.7 are implemented and evidenced, but milestone acceptance requires a governed M1.8 reconciliation of all acceptance criteria, performance observations, compatibility, residual risks, deferred work, traceability, and repository status. This change prepares that decision without granting acceptance itself.

## What Changes

- Build the M1-AC-001–M1-AC-020 exit matrix.
- Add bounded reference-environment performance observations for M1-AC-019.
- Reconcile contract lifecycle, compatibility, specification open questions, residual risks, and deferred work.
- Retain one integrated M1 exit evidence and review record.
- Update traceability, milestone navigation, architecture status, and registry only when supported.
- Validate, synchronize, and archive the change before the exit PR merges.

## Capabilities

### New Capabilities

- `m1-exit-review`: Governed reconciliation and evidence for the M1 acceptance decision.

### Modified Capabilities

None. This change does not add product behavior or redefine M1 contracts.

## Impact

- **Requirements:** REQ-0001–REQ-0020.
- **Acceptance criteria:** M1-AC-001–M1-AC-020.
- **Governing architecture:** ADR-0001–ADR-0016, with ADR-0005 controlling evidence sufficiency.
- **Risk class:** Governed high-risk milestone exit review.
- **Non-goals:** M2 implementation, architecture redesign, production certification, new compatibility promises, or OpenSpec-based acceptance.
