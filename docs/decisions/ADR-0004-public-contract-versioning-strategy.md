# ADR-0004 — Public Contract Versioning Strategy

- **Status:** Baseline
- **Date:** 2026-07-17
- **Decision owners:** Architecture authority and product authority
- **Related:** ADR-0001, ADR-0002, ADR-0003, public seam specifications

## Context

OSCA must evolve durable and independently consumed contracts without silently changing the meaning of retained research, datasets, events, workflows, models, extensions, reports, or paper-trading history.

A single universal version number is insufficient because API requests, durable artifacts, events, extension contracts, and persisted definitions have different reader, writer, replay, migration, and reproducibility requirements.

## Considered alternatives

### A — Universal semantic versioning

Familiar and easy to communicate, but too weak to express reader/writer compatibility, replay guarantees, behavioral compatibility, and reproducibility equivalence across different contract families.

### B — Contract-family versioning with compatibility profiles

Each durable contract has an independent family identity, compatibility version, exact revision, supported producer and consumer ranges, and a profile appropriate to its semantics.

### C — Product-release or date versioning

Operationally simple, but couples independent contract evolution to product releases and does not state compatibility directly.

## Decision

OSCA adopts **contract-family versioning with explicit compatibility profiles**.

Every durable or independently consumed contract must declare, as applicable:

- globally unique contract-family identity;
- major compatibility version;
- exact compatible revision;
- producer and consumer support ranges;
- structural compatibility rules;
- behavioral compatibility rules;
- migration and downgrade policy;
- retention and replay obligations;
- deprecation and removal policy;
- conformance fixtures and validation evidence.

A major version represents a compatibility boundary rather than a product or marketing release. Compatible revisions may add or correct behavior only within the family’s declared rules.

Internal implementation interfaces that are neither durable nor independently consumed do not require long-lived compatibility versions.

## Compatibility profiles

### API and request-response profile

Used by external application APIs, automation payloads, CLI machine interfaces, and LLM tools.

It requires additive evolution within a compatibility version, structured-error stability, explicit deprecation, and capability negotiation where needed.

### Durable data and artifact profile

Used by dataset schemas, analytical results, model manifests, backtests, reports, paper records, and reproducibility manifests.

It requires exact revision retention, explicit reader compatibility, migration provenance, and no silent reinterpretation. A migrated artifact must expose whether exact, equivalent, degraded, or unavailable reproduction remains possible.

### Event profile

Used by retained domain and integration events.

It requires producer, consumer, retention, ordering, idempotency, and replay compatibility. Event meaning cannot be changed in place.

### Extension profile

Used by extension manifests and capability-specific extension contracts.

An extension declares supported OSCA product ranges, contract-family ranges, permission-model version, dependency locks, and conformance-suite version.

### Persisted-definition profile

Used by analyses, workflows, schedules, dashboards, policies, and other executable definitions.

It requires exact definition revision, referenced contract ranges, resolved dependency locks, upgrade preview, and either migration or continued execution under a compatible runtime.

## Mandatory rules

1. Every retained artifact pins the exact contract family, compatibility version, and revision used.
2. Schema-valid does not automatically mean behaviorally compatible.
3. Unknown incompatible major versions are rejected rather than guessed.
4. Unknown compatible fields are preserved or safely ignored only according to the family policy.
5. Migrations are explicit, versioned capabilities and record provenance.
6. Migrations do not silently overwrite the retained source representation when it is required for audit or reproduction.
7. Compatibility is proven through executable producer, consumer, migration, downgrade where supported, and replay fixtures.
8. Each OSCA product release publishes a manifest of supported contract families and version ranges.
9. Deprecation requires usage impact, migration availability, documentation, support duration, and an explicit removal condition.
10. Independently distributed extensions declare both product compatibility and contract-family compatibility.

## Consequences

### Positive

- Contract evolution is independent of application release cadence.
- Reproducibility and compatibility remain explicit and testable.
- Events, artifacts, APIs, extensions, and persisted definitions use semantics appropriate to their risks.
- Multiple compatible contract revisions can coexist during migration.

### Negative and tradeoffs

- A governed contract catalog and compatibility matrices are required.
- Migration and replay fixtures add engineering work.
- Contract-family boundaries require architectural discipline.
- Tooling must distinguish structural compatibility from behavioral equivalence.

## Follow-up obligations

M0 must define:

- the contract catalog record;
- compatibility-test expectations;
- migration evidence requirements;
- product compatibility manifest requirements;
- deprecation governance;
- how implementation technologies will enforce or validate these rules.
