# M0.x Architecture Operationalization Roadmap

- **Status:** Complete
- **Governing role:** Architecture authority
- **Index:** [M0.x work products](m0x/README.md)
- **Last reviewed:** 2026-07-18

## M0 — Architecture Foundation

Defines the authoritative requirements model, foundational ADRs, capability boundaries, public seams, compatibility, security, recovery, quality, and operational architecture.

**State:** Accepted, merged, and validated.

## M0.5 — Architecture Handbook

Turns the baseline into practical authoring and review guidance without duplicating normative authority.

**State:** Complete.  
**Evidence:** [Handbook](../handbook/README.md), [patterns](../handbook/patterns-and-antipatterns.md), and [reference capability](../handbook/reference-capability.md).

## M0.6 — Architecture Validation

Runs repeatable traceability, ADR consistency, boundary, contract, security, recovery, fitness, reference-walkthrough, and deferred-decision checks.

**State:** Complete.  
**Evidence:** [Procedure](../validation/README.md), [manifest](../validation/checks.yaml), and [execution record](../validation/m0x-validation-record.md).

## M0.7 — Governance Baseline

Harmonizes lifecycle, review authority, registry validation, and governed exception mechanics.

**State:** Complete.  
**Evidence:** [Document control](../governance/document-control.md), [registry](../../engineering/architecture-registry.yaml), and [exception register](../governance/architecture-exceptions.md).

## M0.8 — Engineering System Bootstrap

Provides repeatable M1 initiation, review, evidence, and executable-architecture controls.

**State:** Complete.  
**Evidence:** [Bootstrap index](../../engineering/bootstrap/README.md) and [automation backlog](../../engineering/bootstrap/automation-backlog.md).

## Freeze point

Foundational ADRs are Baseline after M0.6 and become Frozen when M1 implementation begins. Later changes use superseding ADRs rather than silent edits.

## M1 planning rule

M1 is one thin end-to-end vertical slice, not horizontal technology layers. Before implementation, it must select exact requirement IDs, resolve triggered deferred decisions, approve its specification, select risk-tiered gates, and complete the M1 initiation checklist.
