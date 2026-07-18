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
| REQ-0001–REQ-0010, REQ-0016–REQ-0020 | Cited PRD sections and D-records in requirements catalog | [M1 intent](../milestones/m1/intent.md) | [Secure walking skeleton](../specifications/m1-secure-walking-skeleton.md) | M1-AC-001–M1-AC-010, M1-AC-016–M1-AC-020 | [M1 exit evidence](../../evidence/m1/m1-exit-evidence.md) | [M1 exit review](../milestones/m1/exit-review.md) | ADR-0001–ADR-0016 | Verified |
| REQ-0011–REQ-0015 | Cited PRD sections and D-records in requirements catalog | [M1 intent](../milestones/m1/intent.md) | [Secure walking skeleton](../specifications/m1-secure-walking-skeleton.md) | M1-AC-011–M1-AC-015 | [M1.4 evidence](../../evidence/m1/m1-4-durable-diagnostic-jobs.md) | [Diagnostic jobs usage](../milestones/m1/diagnostic-jobs.md) | ADR-0003, ADR-0004, ADR-0005, ADR-0006, ADR-0007, ADR-0009, ADR-0010, ADR-0012, ADR-0013, ADR-0014 | Verified |
| REQ-0010, REQ-0013, REQ-0017, REQ-0018 | Cited PRD sections and D-records in requirements catalog | [M1 intent](../milestones/m1/intent.md) | [Secure walking skeleton](../specifications/m1-secure-walking-skeleton.md) | M1-AC-013–M1-AC-016 | [M1.5–M1.6 evidence](../../evidence/m1/m1-5-6-recovery-skeleton.md) | [Recovery guidance](../milestones/m1/recovery.md) | ADR-0009, ADR-0012, ADR-0014, ADR-0015, ADR-0016 | Verified |
| REQ-0019, REQ-0020 | Cited PRD sections and D-records in requirements catalog | [M1 intent](../milestones/m1/intent.md) | [Secure walking skeleton](../specifications/m1-secure-walking-skeleton.md) | M1-AC-001, M1-AC-003, M1-AC-018, M1-AC-020 | [M1.7 evidence](../../evidence/m1/m1-7-documentation-operational-evidence.md) | [Run and operate M1](../milestones/m1/operations-guide.md) | ADR-0001, ADR-0004, ADR-0005, ADR-0009, ADR-0010 | Verified |

Implementation, test-result, documentation, and risk-disposition links are added incrementally. “Planned” does not claim verification completion.


## M2 allocation

| Requirements | Authority | Intent | Specification | Acceptance criteria | Evidence plan | Documentation | ADRs/decisions | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-0021–REQ-0040 | PRD sections 8, 10–14, 37–39; D-012–D-018, D-040 | [M2 intent](../milestones/m2/intent.md) | [M2 governed daily market data](../specifications/m2-governed-daily-market-data.md) | M2-AC-001–M2-AC-020 | [M2 evidence plan](../milestones/m2/evidence-plan.md) | [M2 index](../milestones/m2/README.md) | ADR-0001–ADR-0016 plus triggered M2 decisions pending | Accepted planning; implementation gated |

No M2 verification is claimed. Implementation remains gated by the accepted entry package, including provider licensing and persistence decisions.
