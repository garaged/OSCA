# M0.x Repository Gap Analysis

- **Status:** Completed
- **Governing role:** Architecture authority
- **Approval roles:** Quality authority and repository maintainers
- **Purpose:** Establish the repository-backed delta between the merged M0 foundation and the work required to begin M1 safely.
- **Authoritative sources:** M0 merge commit `30746da69162777000fec6e686dcee29df6345b2`; accepted ADR-0001 through ADR-0010; M0 architecture review record; M0.x roadmap
- **Downstream consumers:** M0.5–M0.8 implementation, M1 readiness review, architecture validation evidence
- **Review trigger:** Any change to the M0.x scope or discovery of contradictory implementation evidence
- **Last reviewed:** 2026-07-18

## Audit boundary and method

The audit reviewed the repository at `main` commit `30746da69162777000fec6e686dcee29df6345b2`, including the root navigation, M0 status and roadmap, architecture and seam indexes, Tier-1 ADRs, governance artifacts, quality policies, handbook placeholder, and engineering-system artifacts.

The audit classifies an artifact as:

- **complete** when it already defines authoritative M0 behavior and needs no M0.x redesign;
- **partial** when sound content exists but lifecycle, packaging, validation evidence, or actionable mechanics are missing;
- **remaining** when the roadmap requires a deliverable that does not yet exist.

## Completed work

The following M0 outcomes are complete and authoritative:

- approved product requirements and decision baseline;
- M0 intent, scope, execution plan, readiness criteria, and architecture review;
- system context, domain model, architecture principles, modular-monolith model, and dependency rules;
- ADR-0001 through ADR-0010;
- provider, analysis, model, LLM, workflow, visualization, and extension seam specifications;
- security architecture and resilience/recovery baseline;
- verification strategy and architecture-fitness program content;
- requirements, traceability, contract, and deferred-decision governance concepts;
- engineering constitution, decision matrix, AI contributor contract, evolution policy, architecture registry seed, knowledge-graph model, and metrics framework.

These artifacts are inputs to M0.x. They must be referenced and operationalized, not recreated.

## Partially completed work

### M0.5 — Architecture Handbook

The handbook index and its intended chapter structure exist, while most chapters are not authored. Companion artifacts already cover the architecture compass, interaction decision matrix, AI contribution rules, evolution policy, and metrics. A technology-neutral reference capability is promised but absent.

### M0.6 — Architecture Validation

The verification strategy and fitness-program categories are comprehensive, but there is no repeatable validation procedure, check inventory, execution record, findings register, or retained evidence proving the merged baseline satisfies those checks.

### M0.7 — Governance Baseline

Document control, architecture evolution, deferred decisions, contract governance, traceability, registry, and knowledge-graph concepts exist. Lifecycle vocabularies are inconsistent across them; governed artifact ownership and review authority are not represented comprehensively in the registry; and there is no exception register or validation-ready governance catalog.

### M0.8 — Engineering System Bootstrap

The constitution, workflow, contributor contract, decision matrix, and metrics framework exist. Missing pieces are an M1 initiation checklist, pull-request/review checklist, evidence-record template, automation backlog, and an explicit split between immediately executable repository checks and technology-dependent checks deferred until M1 selects the stack.

## Remaining deliverables

1. A concise handbook that routes readers to authoritative detail and adds application guidance without copying governing rules.
2. A reference vertical slice demonstrating the complete intent-to-evidence chain without adding product scope.
3. A repeatable architecture-validation plan, machine-readable check manifest, executed validation record, and findings disposition.
4. Harmonized lifecycle vocabulary and metadata expectations across document control, evolution policy, contract catalog, and registry.
5. Expanded registry coverage for governed artifact types, ownership, review authority, and validation rules.
6. An architecture-exception process, template, and active register.
7. M1 initiation, design-review, PR-evidence, and milestone-evidence checklists/templates.
8. An automation roadmap separating stack-independent bootstrap checks from stack-dependent architecture enforcement.
9. Updated repository navigation and status pages that accurately represent M0.x completion and M1 readiness.

## Inconsistencies

| Area | Evidence | Required correction |
|---|---|---|
| Architecture lifecycle | Root status says M0 is complete and approved; `docs/architecture/README.md` says Draft and claims repository structure, enforcement, and public seams are pending. | Mark the index as accepted baseline and link existing boundary, seam, fitness, and deferred-decision artifacts. |
| Quality lifecycle | M0 review says verification and fitness baselines are complete; both quality documents remain Draft. | Move normative policies to Accepted; keep execution evidence separately lifecycle-controlled. |
| Governance lifecycle | M0 completion asserts traceability and workflow baselines, while document control, workflow, traceability model/register, and contract catalog remain Draft. | Accept the governing policies where M0 approval already covered them; describe genuinely unpopulated registers as active baseline registers rather than draft policy. |
| Traceability register | It states that no requirements are approved, contradicting the approved requirements catalog and M0 completion evidence. | Replace the stale statement with current baseline coverage and reserve implementation/specification links for M1. |
| Deferred decisions | DD-004, DD-005, and DD-006 describe communication, event, and extension models as unresolved even though ADR-0006, ADR-0007, and ADR-0008 selected those architecture models. | Mark those entries resolved by the ADRs, while retaining technology selections as separately deferred concerns. |
| Baseline status | The registry says `accepted-pending-validation`, which is correct before M0.6, while other pages loosely use “baseline” for accepted M0 content. | Distinguish “authoritative accepted M0 foundation” from lifecycle state `baseline`; promote ADRs only after recorded M0.6 validation. |
| Engineering loop terminology | The constitution includes Implementation and Operational review; the requested core workflow emphasizes Intent → Requirements → Architecture → Specification → Validation → Evidence. | Document the core governance chain and its implementation/operation expansion without treating them as competing workflows. |

## Duplicate guidance

Duplication is concentrated in the engineering workflow, constitution, AI contributor contract, decision matrix, verification strategy, and planned handbook. The content is compatible, but the handbook must avoid restating full rules.

Use this authority split:

- constitution: stable invariants and authority compass;
- governance workflow: normative lifecycle and required evidence;
- ADRs: consequential architecture decisions;
- quality policies: normative verification obligations;
- decision matrix: quick classification aid;
- AI contributor contract: contributor-specific obligations;
- handbook: explanatory navigation, worked examples, patterns, and review playbooks.

Where a handbook chapter needs a rule, it should summarize it briefly and link to the governing source.

## Stale references

- `docs/architecture/README.md` contains the largest stale block: draft status, pending repository structure, absent seam specifications, and an unresolved enforcement decision.
- `ARCHITECTURE_STATUS.md` still says “Ready for pull request” after PR #2 was merged.
- `README.md` says M0 is “approved for merge” rather than merged.
- The M0.x roadmap says M0 repository validation is pending, but does not link to the future validation evidence location.
- The traceability register claims no approved requirements.
- Deferred decisions DD-004 through DD-006 overlap decisions already settled by accepted ADRs.

## Navigation improvements

- Add a single M0.x index joining roadmap, gap analysis, handbook, validation, governance, bootstrap, and readiness evidence.
- Make the root README and architecture status point to that index.
- Make the architecture index route to public seams, fitness, security, recovery, governance, and the registry.
- Give each new M0.x area a local README so readers can distinguish policy, procedure, template, register, and evidence.
- Add reciprocal links between the handbook, ADR index, decision matrix, and reference capability.

## Recommended implementation order

1. **Correct authoritative navigation and stale status** so later work links to accurate sources.
2. **Complete M0.5** with a non-duplicative handbook, patterns/anti-patterns, review playbook, and reference capability.
3. **Complete M0.7 governance mechanics needed by validation**: harmonize lifecycle language, expand the registry, and add exception controls.
4. **Execute M0.6 validation** using the corrected repository and governance model; record every finding and disposition; promote eligible ADRs to Baseline.
5. **Complete M0.8 bootstrap** with M1 initiation/review/evidence templates and the executable-architecture backlog.
6. **Run final M1-readiness validation**, update indexes/status, and freeze Tier-1 ADRs only when M1 actually begins.

The ordering places governance mechanics before the final validation execution because M0.6 must validate the lifecycle and registry rules that M0.7 makes concrete. This is a sequencing refinement, not an architecture change.

## Initial risk assessment

- The largest immediate risk is false confidence from “complete” status pages coexisting with draft and stale authoritative indexes.
- The largest M1-entry risk is selecting implementation technology before DD-001, DD-002, and related stack-dependent enforcement triggers are deliberately resolved.
- The largest maintainability risk is copying normative rules into the handbook, creating multiple sources of truth.
- The largest validation risk is declaring M0.6 complete from document inspection alone without a retained check inventory and findings record.

## Implementation authorization boundary

This analysis authorizes maintenance and operationalization of accepted M0 intent. A discovered contradiction that changes a Tier-1 decision, product requirement, security outcome, or capability boundary requires authority review and, where consequential, a new or superseding ADR.
