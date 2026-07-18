# OSCA Governed Engineering Workflow

- **Status:** Draft
- **Purpose:** Define the mandatory intent, specification, implementation, verification, review, and evidence flow for all OSCA milestones.
- **Applies to:** Product behavior, architecture, contracts, migrations, security changes, operational changes, documentation, and implementation.

## Governing principle

OSCA uses intent-driven, specification-driven, and test-driven development as one connected control system.

No implementation change is complete merely because code compiles or a local test passes. The change must preserve traceability from approved intent through specification, implementation, verification, documentation, and review evidence.

## Change lifecycle

### 1. Intent

A change begins with an approved intent that states:

- problem or opportunity;
- desired outcome;
- scope and exclusions;
- affected users and capabilities;
- constraints and assumptions;
- success evidence;
- consequential decisions still unresolved.

An intent defines why and what outcome is required. It must not prematurely dictate implementation unless a prior accepted decision already constrains it.

### 2. Requirement refinement

The change identifies existing `REQ-NNNN` requirements and creates new requirements only through the governed requirements catalog.

Each requirement must be:

- uniquely identified;
- testable or otherwise verifiable;
- assigned an authority and lifecycle state;
- linked to source decisions;
- scoped to one or more milestones;
- explicit about mandatory versus optional behavior.

### 3. Decision review

The team identifies choices that are consequential, costly to reverse, security-sensitive, compatibility-forming, or cross-cutting.

Such choices require an ADR before implementation proceeds. Routine local design choices remain in the specification or code review and do not require ADR inflation.

### 4. Specification

A specification defines observable behavior and evidence before implementation.

It includes, as applicable:

- owned capability and boundaries;
- commands, queries, events, and contracts;
- state transitions and invariants;
- temporal and identity semantics;
- quality, provenance, and audit obligations;
- security and permission behavior;
- failure, retry, idempotency, and recovery behavior;
- migration and compatibility behavior;
- acceptance criteria;
- test strategy;
- documentation impact;
- observability and operational evidence.

Specifications must use governed terminology and reference requirements and ADRs.

### 5. Test design

Tests are designed before or alongside implementation, beginning with the highest-risk invariants and failure modes.

The test plan selects appropriate evidence from:

- unit tests;
- property-based tests;
- component tests;
- contract tests;
- migration tests;
- replay tests;
- security tests;
- performance and resource tests;
- accessibility tests;
- operational recovery tests;
- end-to-end tests.

A large end-to-end suite cannot substitute for missing module-level and contract-level evidence.

### 6. Implementation

Implementation follows the accepted module boundaries and public seams.

Changes should be delivered in small, reviewable slices that preserve a buildable state. Each slice must avoid unrelated refactoring unless explicitly included in scope.

Implementation may reveal specification defects. In that case the specification is corrected and reviewed rather than allowing code to silently become the authority.

### 7. Verification

Automated and manual verification proves the acceptance criteria and relevant quality attributes.

Failures are classified as:

- implementation defect;
- specification defect;
- requirement ambiguity;
- environment or fixture defect;
- accepted limitation requiring explicit evidence.

A test is not weakened merely to permit the current implementation unless the governing requirement or specification is legitimately changed.

### 8. Review

Reviews examine:

- requirement and intent alignment;
- architecture and dependency compliance;
- invariant and failure correctness;
- security and privacy impact;
- compatibility and migration impact;
- reproducibility and provenance;
- operational behavior;
- test sufficiency;
- documentation completeness;
- unnecessary complexity.

Review findings that identify a reusable rule should update the appropriate governance, architecture, or specification artifact.

### 9. Evidence and closure

A change closes only when the traceability register links:

- intent;
- requirements;
- decisions;
- specifications;
- implementation changes;
- tests and results;
- documentation;
- residual risks or limitations.

## Change classes

### Routine change

Local, reversible, and contained within an accepted specification and module boundary.

### Governed design change

Changes a public seam, persisted state, migration, security behavior, module ownership, operational contract, or quality threshold. Requires explicit architecture or authority review.

### Consequential decision

Meets ADR criteria and cannot proceed until the decision is accepted.

### Emergency correction

May use an expedited review path when active integrity, security, or availability is at risk. It still requires retrospective specification, test, documentation, and decision reconciliation before normal work resumes.

## Required pull-request evidence

Each implementation pull request must state, as applicable:

- intent and requirement identifiers;
- specification and ADR links;
- modules and contracts affected;
- migration and compatibility impact;
- security and threat impact;
- tests added or changed;
- performance or resource impact;
- documentation changes;
- rollback or forward-recovery behavior;
- residual risks and deferred work.

## Governance exceptions

An exception records the rule, necessity, alternatives, owner, approver, risk, expiration or removal trigger, and automated detection where practical.

Undocumented deviation is a defect rather than an exception.
