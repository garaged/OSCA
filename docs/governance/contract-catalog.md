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
| `osca.readiness.snapshot` | Operations | Cross-interface immutable readiness result | Additive-minor with explicit unknown-field behavior | 1.0.0 | Supported | [M1 specification](../specifications/m1-secure-walking-skeleton.md) |
| `osca.error.envelope` | Platform | Stable structured public failure semantics | Additive-minor; codes are never repurposed | 1.0.0 | Supported | [M1 specification](../specifications/m1-secure-walking-skeleton.md) |
| `osca.workflow.diagnostic-run` | Workflow | Diagnostic submission, lifecycle, checkpoint, and result | Additive-minor; transitions are semantic invariants | 1.0.0 | Supported | [M1 specification](../specifications/m1-secure-walking-skeleton.md) and [evidence](../../evidence/m1/m1-4-durable-diagnostic-jobs.md) |
| `osca.catalog.metadata-reference` | Catalog | Typed stable identity, revision, lineage, and availability | Additive-minor; identity/time meaning cannot change | 1.0.0 | Supported | [M1 specification](../specifications/m1-secure-walking-skeleton.md) |
| `osca.catalog.recovery-reference` | Catalog | Typed backup and restore lineage, integrity, availability, and retention metadata | Additive-minor; identity, lineage, and integrity meaning cannot change | 1.0.0 | Supported | [M1 recovery guidance](../milestones/m1/recovery.md) |
| `osca.recovery.backup-manifest` | Recovery | Backup contents, exclusions, integrity, and compatibility | Read-compatible within major; exact revision retained | 1.0.0 | Supported | [M1 specification](../specifications/m1-secure-walking-skeleton.md) |
| `osca.recovery.restore-plan` | Recovery | Previewed isolated restore actions and conflicts | Additive-minor; execution requires exact accepted plan revision | 1.0.0 | Supported | [M1 specification](../specifications/m1-secure-walking-skeleton.md) |


## M2 instrument contract families

| Family | Owner | Purpose | Compatibility | Current version | Status | Structural schema |
|---|---|---|---|---|---|---|
| `osca.instrument.reference` | Instrument | Provider-neutral stock or spot-crypto-pair canonical identity | Additive-minor only; identity key, asset class, venue, currency, and lifecycle meaning cannot change | 1.0.0 | Supported | `osca.instrument.api.InstrumentReference` |
| `osca.instrument.provider-mapping` | Instrument | Time-aware, evidenced provider alias bound to one canonical identity | Additive-minor only; alias scope, validity, verification, and capability meaning cannot change | 1.0.0 | Supported | `osca.instrument.api.ProviderMapping` |

Instrument contracts are immutable Pydantic values. Unknown major versions fail validation. A stock identity key is asset class + listing venue + currency + stable external identity (or display symbol only when no stable external identity exists). A crypto-pair identity key is asset class + venue/scope + currency + base asset + quote asset. Provider identifiers and symbols are aliases and never enter either canonical primary key.

A mapping can become active only when verified, its canonical instrument exists, its validity interval is coherent, and no verified mapping for the same provider/symbol/scope/venue overlaps another canonical identity. Unverified or ambiguous mappings fail before canonical market-data writes. Conformance evidence includes exact-revision round trips, stock/pair validation, duplicate identity rejection, and time-overlap ambiguity rejection.


## M2 provider contract families

| Family | Owner | Purpose | Compatibility | Current version | Status | Structural schema |
|---|---|---|---|---|---|---|
| `osca.provider.capability` | Provider | Machine-readable asset, interval, history, timestamp, adjustment, authentication, quota, rights, endpoint, health, and quality limits | Additive-minor with explicit negotiation; existing semantic fields and failure codes are never repurposed | 1.0.0 | Supported | `osca.provider.api.ProviderCapability` |
| `osca.provider.daily-request` | Provider | Bounded mapped-symbol daily acquisition request | Additive-minor; range is start-inclusive/end-exclusive and interval meaning cannot change | 1.0.0 | Supported | `osca.provider.api.DailyProviderRequest` |
| `osca.provider.daily-result` | Provider | Deterministic observations or one typed safe failure | Additive-minor; success/failure exclusivity, decimal/time meaning, ordering, and codes cannot change | 1.0.0 | Supported | `osca.provider.api.ProviderResult` |

Provider results contain exactly one of ordered unique observations or a typed failure. Failures distinguish authentication, policy, quota, transport, schema, mapping, quality, and compatibility. Credentials are represented only by named references in capability metadata. Provider-specific behavior is capability/policy data and cannot redefine canonical Instrument or Market Data meaning.

Conformance fixtures, structural schemas, security classifications, supported producer/consumer revisions, and exact error-code catalogs must be delivered with the first implementation of each family.


## M2 Market Data contract families

| Family | Owner | Purpose | Compatibility | Current version | Status | Structural schema |
|---|---|---|---|---|---|---|
| `osca.market-data.daily-bar` | Market Data | Exact complete canonical daily OHLCV observation | Additive-minor; identity, decimal, time, units, completion, and provenance meaning cannot change | 1.0.0 | Supported | `osca.market_data.api.CanonicalDailyBar` |
| `osca.market-data.dataset-manifest` | Market Data | Immutable payload publication, revision, lineage, integrity, availability, retention, and protection metadata | Additive-minor; dataset/revision identity, range, digest, state, and protection meaning cannot change | 1.0.0 | Supported | `osca.market_data.api.DatasetManifest` |
| `osca.market-data.retrieval-request` | Market Data | Canonical bounded daily request with freshness, completeness, provider constraints, pinning, and idempotency | Additive-minor; ranges remain start-inclusive/end-exclusive and exact pins never substitute | 1.0.0 | Supported | `osca.market_data.api.RetrievalRequest` |
| `osca.market-data.repair-request` | Market Data | Explicit disjoint confirmed-gap ranges and idempotent repair identity | Additive-minor; ranges remain start-inclusive/end-exclusive and cannot overlap | 1.0.0 | Supported | `osca.market_data.api.RepairRequest` |
| `osca.market-data.resolution` | Market Data | Exact revision resolution with explicit freshness, completeness, integrity, availability, and remediation | Additive-minor; states and exact dataset/revision identity are semantic invariants | 1.0.0 | Supported | `osca.market_data.api.RetrievalResolution` |
| `osca.data-quality.finding` | Market Data | Visible deterministic date/quality classification and repair eligibility | Additive-minor; classifications and repair eligibility cannot be weakened | 1.0.0 | Supported | `osca.market_data.api.DateFinding` |
| `osca.cache.cleanup-plan` | Market Data | Preview-only scoped cleanup actions and protected/reclaimable accounting | Additive-minor; a plan never grants deletion authority and protected material cannot become selectable | 1.0.0 | Supported | `osca.market_data.application.CleanupPlan` |

Unknown major versions fail validation. Canonical daily bars reject binary floats, non-finite or out-of-range decimals, invalid OHLC relationships, negative values, non-UTC timestamps, and incomplete observations. Dataset manifests are immutable; accepted canonical manifests are protected throughout M2 under ADR-0026. Resolution returns the exact selected manifest identity, and an unavailable exact pin never falls back. Cleanup execution is outside the plan contract and requires separate authorization plus race-safe revalidation.


## Generic Workflow job contract

| Family | Owner | Purpose | Compatibility | Current version | Status | Structural schema |
|---|---|---|---|---|---|---|
| `osca.workflow.job-run` | Workflow | Capability-neutral durable identity, versioned input, idempotency, lifecycle, lease, checkpoint, error, and result reference | Additive-minor; state transitions, actor/kind/idempotency identity, input digest, and terminal-result rules cannot change | 1.0.0 | Supported | `osca.workflow.api.JobRun` |

The generic contract is additive and does not replace or reinterpret `osca.workflow.diagnostic-run`. Generic and diagnostic rows remain separately readable. At-least-once execution requires idempotent or duplicate-aware handlers. Unknown input or job contract major versions fail before handler execution.

## M9 contract families

| Family | Owner | Purpose | Compatibility | Current version | Status | Specification |
|---|---|---|---|---|---|---|
| `osca.ml.feature-definition` | ML lifecycle | Govern feature identity, lineage, type, and point-in-time safety | Additive-minor with explicit semantic review | 1.0.0 | Proposed | [M9 specification](../specifications/m9-governed-ml-lifecycle.md) |
| `osca.ml.label-definition` | ML lifecycle | Govern label identity, objective, horizon, and leakage checks | Additive-minor with explicit semantic review | 1.0.0 | Proposed | [M9 specification](../specifications/m9-governed-ml-lifecycle.md) |
| `osca.ml.training-workflow` | ML lifecycle | Govern training workflow identity and reproducibility metadata | Additive-minor with explicit semantic review | 1.0.0 | Proposed | [M9 specification](../specifications/m9-governed-ml-lifecycle.md) |
| `osca.ml.model-artifact` | ML lifecycle | Govern immutable model artifact identity and digest metadata | Additive-minor with explicit semantic review | 1.0.0 | Proposed | [M9 specification](../specifications/m9-governed-ml-lifecycle.md) |
| `osca.ml.evaluation-report` | ML lifecycle | Govern split-scoped metrics and calibration evidence | Additive-minor with explicit semantic review | 1.0.0 | Proposed | [M9 specification](../specifications/m9-governed-ml-lifecycle.md) |
| `osca.ml.promotion-decision` | ML lifecycle | Govern deterministic ML promotion outcomes | Additive-minor with explicit semantic review | 1.0.0 | Proposed | [M9 specification](../specifications/m9-governed-ml-lifecycle.md) |
