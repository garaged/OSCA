# Traceability Register

- **Status:** Active baseline register
- **Governing role:** Quality authority
- **Approval roles:** Product and architecture authorities
- **Purpose:** Index relationships among requirements, milestone artifacts, decisions, verification, documentation, and risks.
- **Authoritative sources:** [Requirements catalog](requirements-catalog.md), [traceability model](traceability-model.md), ADR-0001
- **Downstream consumers:** CI validation, milestone reviews, impact analysis, and exit evidence
- **Review trigger:** Requirement allocation, milestone specification, supersession, or evidence change
- **Last reviewed:** 2026-07-18

## Register policy

The approved PRD and decisions remain product authority. Numbered `REQ-NNNN` entries are allocated through governed extraction when a milestone intent selects the corresponding scope. Before implementation of a slice begins, every mandatory behavior in that slice must have an approved requirement entry and complete planned trace links.

The register summarizes governed links and does not replace source metadata.

## Required columns

| Requirement | Decision / PRD authority | Milestone intent | Specification | Acceptance criteria | Verification evidence | Documentation | ADRs | Risks | Status |
|---|---|---|---|---|---|---|---|---|---|

## Baseline coverage

| Authority | Current realization | Next required link | Status |
|---|---|---|---|
| Approved PRD and D-001–D-047 | Requirements catalog policy and ADR-0001 | Extract exact `REQ-NNNN` entries selected by M1 intent | Active authority |
| ADR-0001–ADR-0010 | M0 architecture, quality, governance, and validation evidence | Link applicable ADRs from M1 specifications | Baseline |

## M1 gate

The first M1 intent may be drafted while requirement extraction is reviewed. M1 implementation cannot begin until its selected requirements have immutable IDs and links to the approved intent, specification, and acceptance criteria.


## M1 allocation

| Requirements | Authority | Intent | Specification | Acceptance criteria | Evidence plan | Documentation | ADRs | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-0001–REQ-0020 | Cited PRD sections and D-records in requirements catalog | [M1 intent](../milestones/m1/intent.md) | [Secure walking skeleton](../specifications/m1-secure-walking-skeleton.md) | M1-AC-001–M1-AC-020 | [M1 evidence plan](../milestones/m1/evidence-plan.md) | Required by REQ-0019; implementation links pending | ADR-0001–ADR-0015 | Planned |

Implementation, test-result, documentation, and risk-disposition links are added incrementally. “Planned” does not claim verification completion.
