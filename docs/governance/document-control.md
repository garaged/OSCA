# Document Control

- **Status:** Draft
- **Governing role:** Product authority
- **Purpose:** Define authority, lifecycle, ownership, review, and change rules for governed OSCA documentation.
- **Authoritative sources:** PRD sections 1 and 40; decisions D-022, D-045–D-047
- **Downstream consumers:** All governed project artifacts

## Authority hierarchy

When artifacts differ, authority is resolved in this order:

1. active accepted product decisions;
2. approved product requirements;
3. accepted ADRs within their stated scope;
4. approved milestone intents and specifications;
5. acceptance criteria and test plans;
6. implementation and generated references;
7. explanatory documentation.

A lower-level artifact cannot weaken or expand a higher-level authority. Conflicts must be made explicit and resolved through the applicable governance process.

## Governing roles

- **Product authority:** approves product requirements, product-boundary changes, milestone intent, and product decision records.
- **Architecture authority:** governs architecture principles, module boundaries, dependency rules, technical ADRs, and architecture fitness evidence.
- **Security authority:** governs threat-model adequacy, security requirements, control evidence, and security-risk disposition.
- **Quality authority:** governs test strategy, benchmark methodology, quality gates, evidence sufficiency, and release-quality criteria.
- **Repository maintainers:** enforce repository policy, review requirements, contribution rules, and automated checks.

A role may be held by the same person during early development, but reviews and records must identify which authority is being exercised.

## Required document metadata

Every governed artifact must identify:

- status;
- governing role;
- approval role when different;
- purpose;
- authoritative sources;
- downstream consumers;
- traceability references where applicable;
- review frequency or review trigger; and
- last review date after approval.

## Lifecycle states

Governed documents use these states:

- **Draft:** under development and not authoritative.
- **Proposed:** complete enough for formal review.
- **Accepted:** authoritative within its declared scope.
- **Superseded:** replaced by an identified artifact or decision.
- **Retired:** no longer applicable and not replaced.

Approved product requirements and accepted product decisions retain their existing status terminology.

## Change classification

- **Editorial:** improves clarity without changing meaning. Requires normal review.
- **Derived clarification:** makes an accepted requirement testable without changing its authority or scope. Requires traceability review.
- **Architecture decision:** selects a consequential technical approach. Requires an ADR.
- **Product change:** changes scope, mandatory behavior, authority, success criteria, milestone commitment, or accepted product constraint. Requires product decision governance and impact analysis.

## Review triggers

An artifact must be reviewed when:

- an authoritative upstream source changes;
- a related ADR is accepted or superseded;
- a risk is realized or materially re-rated;
- implementation evidence contradicts an assumption;
- a milestone begins or exits;
- compatibility or migration impact is introduced; or
- its stated periodic review date is reached.

## Documentation completeness

Documentation is product material. Behavior, operational requirements, limitations, security consequences, migration effects, and recovery procedures must be updated in the same change as the affected implementation or decision.
