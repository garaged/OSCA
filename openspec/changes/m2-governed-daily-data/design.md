## Context

The accepted M2 specification, REQ-0030–REQ-0040, and ADR-0017–ADR-0026 govern this change. OpenSpec tracks execution and cannot approve provider rights or replace those authorities.

## Decisions

- Market Data remains a capability boundary and depends only on published Instrument, Provider, Workflow, Catalog, and Operations contracts.
- SQLite stores owned manifest metadata; immutable Parquet objects store bounded source or canonical payloads under staged publication.
- Accepted canonical revisions are immutable and protected throughout M2. Exact pins never substitute another revision.
- Completed UTC dates are expected for crypto. Stock weekdays remain unresolved until confirmed as sessions; only confirmed gaps are repair-eligible.
- Cleanup is preview-first and requires explicit policy-derived eligibility. It cannot select canonical, pinned, or otherwise protected material.
- M2 includes free public-access reference implementations with injected I/O; paid/authenticated providers are deferred to post-M2 with explicit licensing evidence.

## Failure and recovery

Publication fails closed before a manifest becomes ready. Corrupt or partial revisions remain explicit and cannot resolve as fresh. Restarted equivalent work uses durable Workflow identity. Recovery protects metadata and every accepted canonical payload; policy controls whether retained source payloads are backed up.

## Observability

Retrieval, repair, publication, provider transitions, quality findings, and cleanup execution must use stable operation/correlation identities and emit safe telemetry plus distinct audit records for governed state changes.

## Rollout and forward recovery

Retained migrations are additive. Failed staged payloads are reconciled or quarantined. Published canonical history is never rolled back by deletion; corrections create a new revision and lineage.

## Provider integration strategy

Free, public-access providers are included as reference implementations in M2 to demonstrate the provider-neutral contract and adapter pattern. Paid services, authentication-required APIs, and quota-managed providers are deferred to a separate change with explicit licensing, credential rotation, quota enforcement, and integration tests before any production promotion.

## Architecture fitness

Boundary tests, migration tests, deterministic contract fixtures, strict typing, OpenSpec validation, link checks, and secret scanning protect dependency direction and governed semantics.