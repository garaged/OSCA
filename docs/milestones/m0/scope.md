# M0 Scope

- **Status:** Draft
- **Governing role:** Architecture authority
- **Approval role:** Product authority
- **Purpose:** Define the work included in M0, explicit exclusions, and the boundary between foundation design and implementation.
- **Authoritative sources:** PRD sections 38–40; decision D-046
- **Downstream consumers:** M0 execution planning, reviews, risk assessment, and exit approval

## In scope

M0 establishes:

- M0 intent, scope, execution sequence, completion checklist, and exit evidence;
- glossary and ubiquitous language;
- system context and domain model;
- architecture principles;
- modular-monolith capability boundaries and dependency rules;
- draft provider, analysis, visualization, model, and extension seams;
- initial ADRs and deferred-decision criteria;
- specification-driven, intent-driven, and test-driven development workflows;
- requirement, specification, acceptance-criterion, test, and documentation traceability;
- coding, testing, documentation, migration, and review standards;
- threat model and detailed initial risk register;
- CI and quality-gate design;
- reference dataset and benchmark methodology;
- milestone intent and specification templates;
- proposed repository structure and contribution guidance; and
- evidence demonstrating that M0 exit criteria are satisfied.

## Explicitly out of scope

M0 does not:

- implement production product features;
- select the implementation language, database, frontend framework, ML framework, or deployment stack before selection requirements and tradeoffs are documented;
- implement live brokerage or exchange execution;
- introduce multi-tenancy or cross-installation synchronization;
- design OSCA as microservices or require distributed deployment;
- finalize extension runtime isolation, package format, signing technology, or registry implementation without the required decision analysis;
- claim benchmark compliance before reproducible benchmark fixtures and environments exist; or
- merge M0 into `main` or open the final M0 pull request without explicit product-authority approval.

## Architectural spikes

A spike is allowed only when a documented uncertainty cannot be resolved credibly through analysis alone and materially blocks an M0 decision.

Every proposed spike must define:

- the uncertainty and why it matters;
- alternatives being evaluated;
- bounded scope and disposal expectations;
- measurable evidence to collect;
- security and data constraints;
- a time and resource budget;
- the decision it will inform; and
- whether any output may be retained as production code.

Spike output is evidence, not an implicit technology commitment.

## Change boundary

Safe documentation changes that express already accepted requirements may proceed incrementally. A change that alters product scope, authority, mandatory behavior, recovery objectives, security posture, or milestone commitments requires product decision governance. A consequential technical choice requires an ADR.
