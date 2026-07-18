# Traceability Model

- **Status:** Accepted
- **Governing role:** Quality authority
- **Approval roles:** Product authority and architecture authority
- **Purpose:** Define how OSCA demonstrates that product authority flows into specifications, tests, documentation, risks, and implementation evidence.
- **Authoritative sources:** PRD sections 1, 38–40; decisions D-022, D-042, D-045–D-047; [ADR-0001](../decisions/ADR-0001-requirements-authority-and-traceability-model.md)
- **Downstream consumers:** Requirements catalog, milestone specifications, CI quality gates, reviews, and exit evidence

## Traceability chain

The minimum forward chain is:

```text
Product decision / PRD authority
  -> catalog requirement
  -> milestone intent
  -> specification
  -> acceptance criterion
  -> verification evidence
  -> usage or operational documentation
```

Depending on risk and scope, the chain also links:

- ADRs;
- architecture constraints and fitness checks;
- threat-model entries and security controls;
- risk-register entries and treatment evidence;
- schemas and migrations;
- observability and failure behavior;
- benchmark definitions and results; and
- implementation changes.

## Traceability directions

- **Forward traceability:** every active requirement identifies planned and completed realization evidence.
- **Backward traceability:** every material specification, acceptance criterion, test, implementation change, and user-facing behavior identifies its governing requirement or decision.
- **Change-impact traceability:** supersession or modification identifies affected downstream artifacts and migration or compatibility consequences.

## Link requirements

### Requirement to intent

A milestone intent identifies which requirements it advances, why they belong in the milestone, and which requirements remain deferred.

### Intent to specification

A specification identifies its governing intent and lists all requirements it realizes or constrains.

### Specification to acceptance criteria

Every mandatory specified behavior has at least one objective acceptance criterion or an explicit rationale for verification by analysis or inspection.

### Acceptance criteria to evidence

Evidence may include automated tests, property checks, contract suites, static analysis, benchmark results, security analysis, review records, demonstrations, or operational exercises. Evidence type must match risk.

### Behavior to documentation

User-visible and operator-relevant behavior links to version-matched usage, methodology, limitation, troubleshooting, migration, or runbook documentation as applicable.

## Coverage rules

A requirement is not complete merely because an implementation exists. Completion requires:

- an approved specification;
- satisfied acceptance criteria;
- appropriate verification evidence;
- required documentation;
- addressed observability and failure behavior;
- resolved or accepted linked risks; and
- compatibility and migration evidence when applicable.

## Orphan prevention

Automated quality gates should reject, as applicable:

- active requirements with no planned milestone;
- specifications with no governing requirement or approved intent;
- mandatory acceptance criteria with no evidence;
- product tests with no requirement or specification reference;
- user-facing behavior with missing documentation references;
- ADRs with no affected scope or consequences;
- migrations with no compatibility requirement and verification; and
- superseded authority with unresolved downstream references.

## Exceptions

An exception must be explicit, time-bounded where practical, owned, risk-assessed, and approved by the governing role. Exceptions cannot silently waive product authority or critical security and correctness requirements.
