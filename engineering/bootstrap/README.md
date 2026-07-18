# Engineering System Bootstrap

- **Status:** Accepted
- **Milestone:** M0.8
- **Governing role:** Architecture authority
- **Approval roles:** Quality authority and repository maintainers
- **Purpose:** Make the accepted engineering system repeatable for the first M1 vertical slice.
- **Authoritative sources:** Engineering constitution; governed workflow; ADR-0001 through ADR-0010
- **Review trigger:** M1 entry, stack selection, or quality-gate change
- **Last reviewed:** 2026-07-18

## Initiating M1 work

1. Complete the [M1 initiation checklist](m1-initiation-checklist.md).
2. Create milestone intent from the governed template.
3. Link approved requirements and resolve triggered deferred decisions.
4. Specify one thin end-to-end slice.
5. Classify risk and select gates under ADR-0005.
6. Implement only after required decisions and acceptance criteria are reviewable.
7. Retain results using the [evidence template](../../docs/templates/evidence-record-template.md).
8. Complete PR evidence and update traceability/navigation in the same change.

## Bootstrap assets

- [M1 initiation checklist](m1-initiation-checklist.md)
- [Review checklist](review-checklist.md)
- [Automation backlog](automation-backlog.md)
- [AI contributor contract](../ai-contributor-contract.md)
- [Decision matrix](../decision-matrix.md)
- [Metrics framework](../metrics-framework.md)

## Core chain and expanded loop

The mandatory governance chain is:

`Intent → Requirements → Architecture → Specification → Validation → Evidence`

Implementation occurs between specification and validation. Operational review and lessons learned follow evidence. The expanded constitution loop and the core chain describe the same system at different levels of detail.

## Technology boundary

M0.8 defines controls that are independent of language and tooling. M1 must resolve triggered technology choices before adding stack-specific enforcement. Prototype convenience cannot resolve a deferred decision implicitly.
