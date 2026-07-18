# M0.x Architecture Operationalization Roadmap

## M0 — Architecture Foundation

Defines the authoritative requirements model, foundational ADRs, capability boundaries, public seams, compatibility, security, recovery, quality, and operational architecture.

**State:** Architecturally accepted; repository validation pending.

## M0.5 — Architecture Handbook

Turns the baseline into practical authoring and review guidance. Produces the handbook, decision matrix, reference capability, AI contributor guidance, patterns, anti-patterns, and review playbooks.

**Exit evidence:** A new contributor can design and review a compliant vertical slice using repository guidance alone.

## M0.6 — Architecture Validation

Performs an architecture acceptance test:

- traceability audit;
- ADR consistency review;
- capability and dependency review;
- public contract ownership and compatibility review;
- security and recovery completeness review;
- fitness-rule dry run;
- reference-capability walkthrough;
- deferred-decision trigger review.

**Exit evidence:** Findings are closed, explicitly accepted as debt, or assigned to an owner with a trigger and deadline. The accepted M0 ADR set may then enter Baseline state.

## M0.7 — Governance Baseline

Finalizes lifecycle states, architecture freeze and supersession policy, registry identifiers, knowledge-graph relationships, maturity reporting, review authority, and governed exceptions.

**Exit evidence:** Every governed artifact type has an owner, identifier, lifecycle, review authority, and validation rule.

## M0.8 — Engineering System Bootstrap

Separates reusable engineering governance from product-specific architecture. Establishes constitution, architecture compass, engineering loop, AI contributor contract, review checklists, automation roadmap, metrics framework, and executable-architecture backlog.

**Exit evidence:** M1 work can be initiated through a repeatable vertical-slice workflow with required inputs, outputs, gates, and evidence.

## Freeze point

Foundational ADRs become Frozen when M1 begins. Subsequent changes use superseding ADRs rather than silent edits.

## M1 planning rule

M1 is organized as a thin end-to-end vertical slice, not as horizontal technology layers. It must exercise intent, requirements, specification, ownership, contracts, persistence, communication, security, observability, recovery, verification, and documentation while leaving the system deployable and diagnosable.
