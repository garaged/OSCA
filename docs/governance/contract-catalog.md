# OSCA Contract Catalog

- **Status:** Accepted
- **Purpose:** Define the authoritative record for durable and independently consumed contract families.
- **Decision basis:** ADR-0004

## Scope

The contract catalog covers external application APIs, durable event schemas, dataset and artifact schemas, extension contracts, persisted definitions, machine-readable CLI interfaces, LLM tool schemas, and other surfaces whose compatibility must outlive an internal implementation refactor.

Private, non-durable implementation interfaces do not require catalog entries.

## Contract-family record

Each catalog entry must contain:

- globally unique family identity;
- human-readable title and purpose;
- owning module and accountable owner;
- compatibility profile;
- current major version and exact revision;
- supported producer versions;
- supported consumer versions;
- serialization-independent semantic definition;
- structural schema references;
- behavioral invariants;
- error and failure semantics;
- security, privacy, licensing, and audit classification;
- retention, replay, and reproduction obligations;
- migration and downgrade capabilities;
- deprecation and removal state;
- conformance fixtures and compatibility evidence;
- affected requirements, ADRs, specifications, and documentation.

## Lifecycle

Contract revisions move through:

1. Draft
2. Proposed
3. Accepted
4. Supported
5. Deprecated
6. Retired

A contract may remain readable or replayable after retirement when retained artifacts or audit obligations require it.

## Change classification

### Compatible revision

A change remains within the current major compatibility version only when executable evidence shows that supported producers and consumers remain safe under the family profile.

Examples may include:

- optional fields with defined absence behavior;
- new enum values only when unknown-value behavior is already specified;
- stricter diagnostics that do not change successful meaning;
- corrected documentation matching existing behavior;
- additive capabilities negotiated explicitly.

### Breaking revision

A new major version is required when a supported consumer cannot safely interpret the change, a producer obligation changes incompatibly, or the semantic meaning of an existing value changes.

Examples include:

- removing or renaming required fields;
- changing units, currencies, time semantics, identity semantics, or default behavior;
- changing event meaning or ordering assumptions;
- changing permission requirements incompatibly;
- changing a persisted definition so prior execution meaning is lost;
- changing analytical interpretation while retaining the same structural shape.

## Compatibility evidence

Each accepted revision must provide, as applicable:

- old-producer/new-consumer tests;
- new-producer/old-consumer tests;
- exact-revision round trips;
- migration tests;
- replay tests;
- downgrade tests where supported;
- unknown-field and unknown-enum behavior;
- semantic golden fixtures;
- security and authorization tests;
- reproducibility impact assessment.

## Product compatibility manifest

Every OSCA release publishes a machine-readable manifest listing:

- product version and build identity;
- supported contract families and version ranges;
- default produced revisions;
- readable historical revisions;
- available migrations;
- deprecated and removed families;
- required extension and permission-model versions;
- known degraded compatibility conditions.

## Deprecation

Deprecation requires:

- reason and replacement;
- affected consumers and retained artifacts;
- migration path;
- support window or objective removal condition;
- telemetry or catalog evidence of remaining use where available;
- user and developer documentation;
- rollback or recovery implications.

Removal is prohibited while protected artifacts, active extensions, workflows, or recovery packages require the contract unless a supported preservation or migration path exists.

## Ownership rules

The owning module controls semantics and publishes the contract. Consumers may propose changes but cannot redefine owner meaning locally.

Cross-module contract families must still have one authoritative owner. A neutral namespace does not imply shared mutable ownership.


## M1 contract families

| Family | Owner | Purpose | Compatibility | Current version | Status | Specification |
|---|---|---|---|---|---|---|
| `osca.readiness.snapshot` | Operations | Cross-interface immutable readiness result | Additive-minor with explicit unknown-field behavior | 1.0.0 | Accepted | [M1 specification](../specifications/m1-secure-walking-skeleton.md) |
| `osca.error.envelope` | Platform | Stable structured public failure semantics | Additive-minor; codes are never repurposed | 1.0.0 | Accepted | [M1 specification](../specifications/m1-secure-walking-skeleton.md) |
| `osca.workflow.diagnostic-run` | Workflow | Diagnostic submission, lifecycle, checkpoint, and result | Additive-minor; transitions are semantic invariants | 1.0.0 | Accepted | [M1 specification](../specifications/m1-secure-walking-skeleton.md) |
| `osca.catalog.metadata-reference` | Catalog | Typed stable identity, revision, lineage, and availability | Additive-minor; identity/time meaning cannot change | 1.0.0 | Accepted | [M1 specification](../specifications/m1-secure-walking-skeleton.md) |
| `osca.recovery.backup-manifest` | Recovery | Backup contents, exclusions, integrity, and compatibility | Read-compatible within major; exact revision retained | 1.0.0 | Accepted | [M1 specification](../specifications/m1-secure-walking-skeleton.md) |
| `osca.recovery.restore-plan` | Recovery | Previewed isolated restore actions and conflicts | Additive-minor; execution requires exact accepted plan revision | 1.0.0 | Accepted | [M1 specification](../specifications/m1-secure-walking-skeleton.md) |

Conformance fixtures, structural schemas, security classifications, supported producer/consumer revisions, and exact error-code catalogs must be delivered with the first implementation of each family.
