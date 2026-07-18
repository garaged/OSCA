# OSCA Verification Strategy

- **Status:** Accepted
- **Purpose:** Define the evidence model used to prove product, architecture, security, compatibility, reproducibility, and operational behavior.
- **Applies to:** All milestones, modules, public seams, migrations, extensions, workflows, and releases.

## Verification principles

1. Verification follows risk and invariants rather than maximizing raw test count.
2. Deterministic financial, temporal, identity, accounting, and risk behavior requires strong executable evidence.
3. Public contracts require producer, consumer, migration, and replay evidence appropriate to their compatibility profile.
4. Module-focused tests are primary evidence; end-to-end tests verify integration and user journeys but do not replace lower-level proof.
5. Tests must exercise failure, partial, stale, retry, cancellation, recovery, and degraded behavior where those states are valid.
6. Reproducibility claims require exact inputs, versions, parameters, environment, and expected outputs or tolerances.
7. Security controls require negative tests proving bypass is rejected.
8. Operational readiness requires restore, reconciliation, and failure-injection evidence rather than documentation alone.

## Evidence layers

### Static and structural evidence

Covers:

- formatting and linting;
- type and schema checks;
- forbidden dependency detection;
- module-cycle detection;
- public/private visibility;
- secret and dependency scanning;
- documentation links and generated-reference freshness;
- contract catalog consistency;
- traceability completeness.

### Unit and property evidence

Used for value semantics, transformations, calculations, state transitions, parsers, policies, and invariants.

Property-based tests are expected where a domain has broad input spaces or algebraic invariants, including money, quantities, time ranges, resampling, accounting balance, identifier mapping, order lifecycle, and migration round trips.

### Module component evidence

Each module proves its application behavior using owned ports and controlled adapters without booting unrelated modules or real external services.

Component tests cover authorization, persistence behavior, idempotency, concurrency, failure translation, provenance, and audit obligations.

### Contract evidence

Public seams and durable contracts use:

- provider and consumer fixtures;
- compatibility matrices;
- semantic golden examples;
- unknown-field and version rejection behavior;
- error compatibility;
- event replay;
- extension conformance;
- workflow resume and migration fixtures.

### Integration evidence

Validates selected adapters and cross-module workflows using realistic infrastructure or provider simulators.

Integration tests must make external dependencies explicit and distinguish unavailable infrastructure from product failure.

### End-to-end evidence

Covers a small number of critical user and operational journeys across supported deployment profiles.

Examples include:

- discover instrument through provider mapping and governed data retrieval;
- create project, run analysis, inspect provenance, and export a report;
- evaluate a candidate and promote it to paper operation;
- install and activate a permitted extension;
- interrupt and resume a durable workflow;
- create, verify, and restore a backup into isolated storage.

### Non-functional evidence

Covers:

- performance and capacity;
- resource budgets;
- concurrency and contention;
- accessibility;
- security and abuse resistance;
- resilience and recovery;
- reproducibility and numerical stability;
- observability and diagnostic usefulness.

## Test determinism

Tests must control clocks, random seeds, market calendars, time zones, provider responses, model versions, prompt versions, and network behavior where material.

A nondeterministic test is treated as a defect. Quarantine may be temporary only with an owner, issue, expiration, and preserved blocking visibility.

## Fixtures and reference data

Fixtures must declare:

- provenance and license;
- schema and revision;
- time and market assumptions;
- expected quality state;
- whether values are synthetic, anonymized, or retained provider data;
- integrity digest;
- update policy.

Synthetic fixtures are preferred for invariant and failure testing. Retained real-world reference datasets may be used for realism only when licensing and privacy permit.

## Numerical evidence

Numerical tests specify exact expectations when deterministic arithmetic permits it and explicit tolerances when floating-point, statistical, or model behavior requires them.

Tolerance changes require rationale and must not hide material financial or analytical error.

## Migration and recovery evidence

Every state or contract migration must test:

- clean upgrade;
- representative historical states;
- interrupted migration;
- retry or forward recovery;
- rollback where supported;
- backup compatibility;
- reconciliation and integrity;
- retained provenance;
- degraded outcomes when exact migration is impossible.

Recovery evidence includes isolated restore tests and post-restore smoke, integrity, and reconciliation checks.

## Security evidence

Security verification includes, as applicable:

- authentication and authorization denial paths;
- credential-scope enforcement;
- secret redaction;
- transport and certificate failure behavior;
- input and schema validation;
- extension and LLM permission isolation;
- prompt-injection resistance;
- dependency and supply-chain checks;
- audit generation and tamper evidence;
- backup confidentiality and authenticity.

## Evidence retention

Milestone and release evidence records:

- source revision;
- build identity;
- tool and environment versions;
- selected test and fixture versions;
- results and failures;
- waivers or exceptions;
- performance and security reports;
- generated artifacts and integrity digests.

Retained evidence must be sufficient to explain why a milestone or release was accepted at that time.
