# Traceability Register

- **Status:** Active baseline register
- **Governing role:** Quality authority
- **Approval roles:** Product and architecture authorities
- **Purpose:** Index relationships among requirements, milestone artifacts, decisions, verification, documentation, and risks.
- **Authoritative sources:** [Requirements catalog](requirements-catalog.md), [traceability model](traceability-model.md), ADR-0001
- **Downstream consumers:** CI validation, milestone reviews, impact analysis, and exit evidence
- **Review trigger:** Requirement allocation, milestone specification, supersession, or evidence change
- **Last reviewed:** 2026-07-25

## Register policy

The approved PRD and decisions remain product authority. Numbered `REQ-NNNN` entries are allocated through governed extraction when a milestone intent selects the corresponding scope. Before implementation of a slice begins, every mandatory behavior in that slice must have an approved requirement entry and complete planned trace links.

From M8 onward, milestone specifications must review the manual testing and usage baseline. A milestone must update [Manual testing and usage](../testing/manual-testing.md) when it changes user-visible or operator-visible behavior, or explicitly record why no manual coverage change is required.

The register summarizes governed links and does not replace source metadata.

## Required columns

| Requirement | Decision / PRD authority | Milestone intent | Specification | Acceptance criteria | Verification evidence | Documentation | ADRs | Risks | Status |
|---|---|---|---|---|---|---|---|---|---|

## Baseline coverage

| Authority | Current realization | Next required link | Status |
|---|---|---|---|
| Approved PRD and D-001-D-047 | Requirements catalog policy and ADR-0001 | Extract exact `REQ-NNNN` entries selected by each governed milestone intent | Active authority |
| ADR-0001-ADR-0010 | M0 architecture, quality, governance, and validation evidence | Link applicable ADRs from each milestone specification | Baseline |

## M1 gate

The first M1 intent may be drafted while requirement extraction is reviewed. M1 implementation cannot begin until its selected requirements have immutable IDs and links to the approved intent, specification, and acceptance criteria.

## M1 allocation

| Requirements | Authority | Intent | Specification | Acceptance criteria | Evidence plan | Documentation | ADRs | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-0001-REQ-0010, REQ-0016-REQ-0020 | Cited PRD sections and D-records in requirements catalog | [M1 intent](../milestones/m1/intent.md) | [Secure walking skeleton](../specifications/m1-secure-walking-skeleton.md) | M1-AC-001-M1-AC-010, M1-AC-016-M1-AC-020 | [M1 exit evidence](../../evidence/m1/m1-exit-evidence.md) | [M1 exit review](../milestones/m1/exit-review.md) | ADR-0001-ADR-0016 | Verified |
| REQ-0011-REQ-0015 | Cited PRD sections and D-records in requirements catalog | [M1 intent](../milestones/m1/intent.md) | [Secure walking skeleton](../specifications/m1-secure-walking-skeleton.md) | M1-AC-011-M1-AC-015 | [M1.4 evidence](../../evidence/m1/m1-4-durable-diagnostic-jobs.md) | [Diagnostic jobs usage](../milestones/m1/diagnostic-jobs.md) | ADR-0003, ADR-0004, ADR-0005, ADR-0006, ADR-0007, ADR-0009, ADR-0010, ADR-0012, ADR-0013, ADR-0014 | Verified |
| REQ-0010, REQ-0013, REQ-0017, REQ-0018 | Cited PRD sections and D-records in requirements catalog | [M1 intent](../milestones/m1/intent.md) | [Secure walking skeleton](../specifications/m1-secure-walking-skeleton.md) | M1-AC-013-M1-AC-016 | [M1.5-M1.6 evidence](../../evidence/m1/m1-5-6-recovery-skeleton.md) | [Recovery guidance](../milestones/m1/recovery.md) | ADR-0009, ADR-0012, ADR-0014, ADR-0015, ADR-0016 | Verified |
| REQ-0019, REQ-0020 | Cited PRD sections and D-records in requirements catalog | [M1 intent](../milestones/m1/intent.md) | [Secure walking skeleton](../specifications/m1-secure-walking-skeleton.md) | M1-AC-001, M1-AC-003, M1-AC-018, M1-AC-020 | [M1.7 evidence](../../evidence/m1/m1-7-documentation-operational-evidence.md) | [Run and operate M1](../milestones/m1/operations-guide.md) | ADR-0001, ADR-0004, ADR-0005, ADR-0009, ADR-0010 | Verified |

Implementation, test-result, documentation, and risk-disposition links are added incrementally. "Planned" does not claim verification completion.

## M2 allocation

| Requirements | Authority | Intent | Specification | Acceptance criteria | Evidence plan | Documentation | ADRs/decisions | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-0021-REQ-0040 | PRD sections 8, 10-14, 37-39; D-012-D-018, D-040 | [M2 intent](../milestones/m2/intent.md) | [M2 governed daily market data](../specifications/m2-governed-daily-market-data.md) | M2-AC-001-M2-AC-020 | [M2 exit review](../../evidence/m2/m2-exit-review.md) | [M2 index](../milestones/m2/README.md) | ADR-0001-ADR-0028 | Verified |
| REQ-0021-REQ-0024 | D-012; accepted M2 intent | [M2 intent](../milestones/m2/intent.md) | [M2 governed daily market data](../specifications/m2-governed-daily-market-data.md) | M2-AC-001, M2-AC-002; partial M2-AC-017 | [M2.1 evidence](../../evidence/m2/m2-1-instrument-registry.md) | [Contract catalog](contract-catalog.md) | ADR-0003, ADR-0004, ADR-0005, ADR-0009, ADR-0012, ADR-0017 | Verified |
| REQ-0025-REQ-0029 | D-016, D-040; accepted provider strategy | [M2 intent](../milestones/m2/intent.md) | [M2 governed daily market data](../specifications/m2-governed-daily-market-data.md) | M2-AC-003, partial M2-AC-004, M2-AC-006, M2-AC-016 | [M2.2 evidence](../../evidence/m2/m2-2-provider-contract-fixtures.md) | [Provider strategy](../milestones/m2/provider-strategy.md) | ADR-0003-ADR-0005, ADR-0008, ADR-0014, ADR-0015 | Verified |
| REQ-0030-REQ-0040 | PRD sections 10-14, 37-39; D-013-D-018; accepted M2 decisions | [M2 intent](../milestones/m2/intent.md) | [M2 governed daily market data](../specifications/m2-governed-daily-market-data.md) | M2-AC-004-M2-AC-020 | [M2 exit review](../../evidence/m2/m2-exit-review.md) | [M2 operations guide](../milestones/m2/operations-guide.md) | ADR-0017-ADR-0028 | Verified |

M2 verification is complete for the governed daily-data scope. Production promotion for paid, authenticated, or license-sensitive provider use is deferred beyond M2 and remains policy-blocked until exact provider-specific licensing, account-plan, credential, quota, and retention/export evidence is accepted.

## M3 allocation

| Requirements | Authority | Intent | Specification | Acceptance criteria | Evidence plan | Documentation | ADRs/decisions | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-0041-REQ-0052 | PRD sections 8, 10-14, 37-39; D-004, D-012-D-018, D-040 | [M3 intent](../milestones/m3/intent.md) | [M3 temporal correctness](../specifications/m3-temporal-correctness.md) | M3-AC-001-M3-AC-012 | [M3 exit review](../../evidence/m3/m3-exit-review.md) | [M3 index](../milestones/m3/README.md) | ADR-0029 | Verified |

## M4 allocation

| Requirements | Authority | Intent | Specification | Acceptance criteria | Evidence plan | Documentation | ADRs/decisions | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-0053-REQ-0068 | PRD sections 11, 15, 18-21, 34-39; D-009, D-019, D-021-D-026, D-046 | [M4 intent](../milestones/m4/intent.md) | [M4 research projects, analytics, and visualization](../specifications/m4-research-projects-analytics.md) | M4-AC-001-M4-AC-012 | [M4 exit review](../../evidence/m4/m4-exit-review.md) | [M4 index](../milestones/m4/README.md) | ADR-0030 | Verified |


## M5 allocation

| Requirements | Authority | Intent | Specification | Acceptance criteria | Evidence plan | Documentation | ADRs/decisions | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-0069-REQ-0084 | PRD sections 11, 13, 15-17, 20-21, 26-27, 34, 37-39; D-014, D-019, D-020, D-022, D-026, D-040, D-046 | [M5 intent](../milestones/m5/intent.md) | [M5 independent extension packaging and activation](../specifications/m5-extension-packaging.md) | M5-AC-001-M5-AC-008 | [M5 exit review](../../evidence/m5/m5-exit-review.md) | [M5 index](../milestones/m5/README.md) | ADR-0031 | Verified |


## M6 allocation

| Requirements | Authority | Intent | Specification | Acceptance criteria | Evidence plan | Documentation | ADRs/decisions | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-0085-REQ-0092 | PRD sections 22, 29-30, 34, 37-39; D-001-D-002, D-004, D-009, D-027-D-028, D-036-D-037, D-041, D-046 | [M6 intent](../milestones/m6/intent.md) | [M6 backtesting foundation](../specifications/m6-backtesting-foundation.md) | M6-AC-001-M6-AC-008 | [M6 exit review](../../evidence/m6/m6-exit-review.md) | [M6 index](../milestones/m6/README.md) | ADR-0032 | Verified |


## M7 allocation

| Requirements | Authority | Intent | Specification | Acceptance criteria | Evidence plan | Documentation | ADRs/decisions | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-0093-REQ-0101 | PRD sections 22-23, 30-31, 34, 37-39; D-001-D-002, D-004, D-009, D-027-D-028, D-037-D-038, D-041, D-046 | [M7 intent](../milestones/m7/intent.md) | [M7 F2 event-driven validation](../specifications/m7-event-driven-validation.md) | M7-AC-001-M7-AC-009 | [M7 exit review](../../evidence/m7/m7-exit-review.md) | [M7 index](../milestones/m7/README.md) | ADR-0033 | Verified |


## M8 allocation

| Requirements | Authority | Intent | Specification | Acceptance criteria | Evidence plan | Documentation | ADRs/decisions | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-0102-REQ-0112 | PRD sections 22-23, 28-31, 34-39; D-001-D-002, D-004, D-009, D-027-D-028, D-035-D-037, D-041-D-043, D-046 | [M8 intent](../milestones/m8/intent.md) | [M8 paper evaluation](../specifications/m8-paper-evaluation.md) | M8-AC-001-M8-AC-011 | [M8.1 evidence](../../evidence/m8/m8-1-paper-evaluation-contracts.md) | [M8 index](../milestones/m8/README.md), [Manual testing and usage](../testing/manual-testing.md) | ADR-0034 | Verified |

## M9 allocation

| Requirements | Authority | Intent | Specification | Acceptance criteria | Evidence plan | Documentation | ADRs | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-0113-REQ-0124 | PRD M9; REQ-0112 | [M9 intent](../milestones/m9/intent.md) | [M9 governed ML lifecycle](../specifications/m9-governed-ml-lifecycle.md) | [M9 acceptance](../milestones/m9/acceptance.md) | [M9 evidence plan](../milestones/m9/evidence-plan.md) | [Manual testing and usage](../testing/manual-testing.md) | ADR-0035 | Verified |

## M10 allocation

| Requirements | Authority | Intent | Specification | Acceptance criteria | Evidence plan | Documentation | ADRs | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-0125-REQ-0133 | PRD section 25; REQ-0112 | [M10 intent](../milestones/m10/intent.md) | [M10 LLM lifecycle and gateway](../specifications/m10-llm-lifecycle-gateway.md) | [M10 acceptance](../milestones/m10/acceptance.md) | [M10 evidence plan](../milestones/m10/evidence-plan.md) | [Manual testing and usage](../testing/manual-testing.md) | ADR-0036 | Verified |


## M11 allocation

| Requirements | Authority | Intent | Specification | Acceptance criteria | Evidence plan | Documentation | ADRs | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-0134-REQ-0144 | PRD sections 20-21, 34-35, 37-39; REQ-0112 | [M11 intent](../milestones/m11/intent.md) | [M11 analytical breadth and portfolio intelligence](../specifications/m11-analytical-breadth-portfolio-intelligence.md) | [M11 acceptance](../milestones/m11/acceptance.md) | [M11 evidence plan](../milestones/m11/evidence-plan.md) | [Manual testing and usage](../testing/manual-testing.md) | ADR-0037 | Verified |


## M12 allocation

| Requirements | Authority | Intent | Specification | Acceptance criteria | Evidence plan | Documentation | ADRs | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-0145-REQ-0156 | PRD sections 26-30, 37-39; REQ-0112 | [M12 intent](../milestones/m12/intent.md) | [M12 release readiness and operational resilience](../specifications/m12-release-readiness-resilience.md) | [M12 acceptance](../milestones/m12/acceptance.md) | [M12 evidence plan](../milestones/m12/evidence-plan.md) | [Manual testing and usage](../testing/manual-testing.md) | ADR-0038 | Verified |


## P1 allocation

| Requirements | Authority | Intent | Specification | Acceptance criteria | Evidence plan | Documentation | ADRs | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-0157-REQ-0166 | PRD sections 11-14, 26-27, 37-39; D-004, D-016, D-040, D-046; REQ-0112 | [P1 intent](../milestones/p1/intent.md) | [P1 provider production promotion](../specifications/p1-provider-production-promotion.md) | [P1 acceptance](../milestones/p1/acceptance.md) | [P1 evidence plan](../milestones/p1/evidence-plan.md) | [Manual testing and usage](../testing/manual-testing.md) | ADR-0039 | In review |
