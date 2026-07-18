# M0 Readiness and Exit Criteria

- **Status:** Approved
- **Milestone:** M0 — Intent and architecture foundation
- **Review record:** [Architecture review record](architecture-review-record.md)

## Purpose

M0 is complete when implementation can begin without relying on undocumented architectural assumptions, while deliberately deferred technology choices remain explicit and governed.

## Required accepted foundations

M0 exit requires:

- authoritative PRD and immutable requirement identifiers;
- traceability model and register;
- ubiquitous language glossary;
- system context and conceptual domain model;
- accepted architecture principles;
- capability-oriented modular-monolith model;
- enforced module-boundary policy;
- public seam specifications;
- public-contract versioning policy and catalog;
- engineering workflow;
- verification strategy and risk-tiered quality gates;
- security architecture baseline;
- resilience and recovery baseline;
- architecture fitness program;
- risk, open-question, and deferred-decision registers.

## Evidence checklist

The architecture authority confirmed:

1. [x] Every accepted ADR is indexed and reflected in downstream documents.
2. [x] Every M0 document has sufficient status, scope, governing role, and authoritative context for its purpose.
3. [x] Candidate capabilities have clear conceptual ownership and no known contradictory ownership.
4. [x] Public seams define the principal ownership, contract, provenance, security, compatibility, and conformance obligations required at this stage.
5. [x] Security trust boundaries and privileged operations are identifiable.
6. [x] Durable state classes and recovery obligations are identifiable.
7. [x] Quality gates map to change risk and cannot be bypassed without a governed, expiring exception.
8. [x] Known unresolved choices are explicitly deferred with a trigger and decision authority.
9. [x] No implementation technology has been selected without evidence against requirements and ADR fitness obligations.
10. [x] M1 can define executable vertical-slice acceptance tests from the retained specifications.

## Non-exit conditions

M0 would not be complete if:

- a material product requirement were only represented in conversation history;
- a consequential choice lacked an ADR;
- a public or durable contract lacked an owner and compatibility policy;
- a security or recovery obligation depended on an unspecified permissive default;
- a known architecture conflict were hidden in an open-ended TODO;
- implementation were required merely to discover intended behavior;
- deferred decisions lacked timing, evidence needs, or decision ownership.

The completed review found none of these conditions to be present as a merge blocker.

## M1 entry criteria

M1 may begin when:

- M0.5–M0.8 outputs required by the selected slice are complete or explicitly scheduled;
- the first vertical slice and its acceptance scenarios are selected;
- technology candidates are evaluated against architecture fitness obligations;
- initial module boundaries and public contracts needed by the slice are specified;
- CI can enforce the baseline gates or has a time-bounded bootstrap plan;
- security, persistence, observability, and recovery impact of the slice are classified.

## M0 evidence package

The retained milestone package includes:

- approved intent and scope;
- architecture document index;
- accepted ADR set;
- traceability snapshot;
- deferred-decision register;
- architecture review record;
- merge-readiness status.

## Approval

The architecture authority approved M0 on 2026-07-17. This approval confirms that the architecture-foundation branch is ready for pull-request creation and merge. It does not resolve choices intentionally deferred to later ADRs or milestone-specific specifications.
