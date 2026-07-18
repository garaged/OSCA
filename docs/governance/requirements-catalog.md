# Requirements Catalog

- **Status:** Active baseline catalog
- **Governing role:** Product authority
- **Purpose:** Assign stable identifiers and engineering metadata to testable requirements derived without semantic change from the approved PRD and active decisions.
- **Authoritative sources:** [Product requirements](../product-requirements.md), [decision log](../decision-log.md), [ADR-0001](../decisions/ADR-0001-requirements-authority-and-traceability-model.md)
- **Downstream consumers:** Milestone intents, specifications, acceptance criteria, tests, documentation, risk treatments, and automated traceability checks

## Authority

This catalog is an index and decomposition of authoritative requirements. It does not replace the PRD or active accepted decisions and cannot change their meaning.

If a catalog entry conflicts with its cited source, the cited source governs and the catalog entry must be corrected. A proposed correction that changes product meaning requires product decision governance.

## Identifier policy

Requirements receive immutable identifiers in the form `REQ-NNNN`.

The numeric identifier carries no domain or milestone meaning. Classification and allocation are stored as metadata so a requirement can move between modules or milestones without changing identity.

Identifiers are never reused. A retired or superseded requirement remains in the catalog with its history and replacement reference.

## Required fields

Each catalog entry must contain:

| Field | Meaning |
|---|---|
| ID | Stable `REQ-NNNN` identifier |
| Title | Short unique description |
| Normative statement | Atomic, testable requirement using defined requirement language |
| Authority | Exact PRD section and applicable decision IDs |
| Classification | Product behavior, architecture constraint, quality attribute, security, process, documentation, or governance |
| Scope | Affected capability or cross-cutting concern |
| Planned milestones | Milestones expected to specify or satisfy the requirement |
| Verification class | Test, analysis, inspection, demonstration, or mixed |
| Risk links | Related risk identifiers |
| Status | Active, superseded, retired, or deferred |
| Supersedes / superseded by | Requirement-history links |
| Notes | Non-normative clarification only |

## Decomposition rules

- Each normative statement expresses one independently verifiable obligation where practical.
- Decomposition may make implicit subjects or conditions explicit but cannot add behavior.
- Requirement language follows the approved PRD definitions.
- A requirement may cite multiple PRD passages and decisions.
- A PRD passage may produce multiple catalog requirements when it contains separable obligations.
- Duplicate requirements are consolidated while preserving all authority links.
- Implementation details are excluded unless already mandated by an authoritative source.
- Unresolved design questions are not converted into requirements.

## Population status

The catalog policy is accepted. Exact numbered requirements are extracted and reviewed when a milestone selects their scope, keeping decomposition small and reviewable. ADR-0001 requires the selected entries and machine-validatable links before implementation depends on them.

## Catalog entries

No numbered entries are allocated before the first M1 vertical slice is selected. This is an explicit M1 entry gate, not permission to reference only broad prose during implementation.
