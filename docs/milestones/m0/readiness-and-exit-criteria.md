# M0 Readiness and Exit Criteria

- **Status:** Draft
- **Milestone:** M0 — Intent and architecture foundation

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

Before declaring M0 complete, reviewers must confirm:

1. Every accepted ADR is indexed and reflected in downstream documents.
2. Every M0 document has status, scope, owner or governing role, and authoritative references.
3. Candidate capabilities have clear conceptual ownership and no known contradictory ownership.
4. Public seams define ownership, input/output obligations, failure semantics, provenance, security, compatibility, and conformance expectations.
5. Security trust boundaries and privileged operations are identifiable.
6. Durable state classes and recovery obligations are identifiable.
7. Quality gates map to change risk and cannot be bypassed without an expiring exception.
8. Known unresolved choices are explicitly deferred with a trigger and decision authority.
9. No technology has been selected without evidence against requirements and ADR fitness obligations.
10. M1 can define executable walking-skeleton acceptance tests from the retained specifications.

## Non-exit conditions

M0 is not complete if:

- a material product requirement is only represented in conversation history;
- a consequential choice lacks an ADR;
- a public or durable contract lacks an owner and compatibility policy;
- a security or recovery obligation depends on an unspecified permissive default;
- a known architecture conflict is hidden in an open-ended TODO;
- implementation is required merely to discover what the intended behavior is;
- deferred decisions lack timing, evidence needs, or decision ownership.

## M1 entry criteria

M1 may begin when:

- M0 review findings are resolved or accepted as owned risks;
- the first implementation slice and its acceptance scenarios are selected;
- technology candidates are evaluated against architecture fitness obligations;
- initial module boundaries and public contracts needed by the slice are specified;
- CI can enforce the baseline gates or has a time-bounded bootstrap plan;
- security, persistence, and recovery impact of the slice are classified.

## M0 evidence package

The retained milestone package should include:

- approved intent and scope;
- architecture document index;
- accepted ADR set;
- traceability snapshot;
- open risks and exceptions;
- deferred-decision register;
- review record;
- M1 readiness assessment.

## Approval

M0 completion requires explicit architecture-authority approval after review of the evidence package. Approval confirms readiness to proceed; it does not resolve choices intentionally deferred to later ADRs.
