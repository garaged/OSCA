# M2 Intent — Governed Daily Market Data

- **Status:** Accepted
- **Governing role:** Product authority
- **Architecture, security, data, licensing, and quality approval:** Accepted 2026-07-18
- **Purpose:** Deliver the smallest user-visible path from canonical instrument registration to governed daily OHLCV retrieval.
- **Authoritative sources:** PRD sections 4, 5, 8, 10–14, 35–39; D-012–D-018; D-040
- **Baseline:** Accepted M1 secure walking skeleton
- **Review trigger:** Scope, provider, licensing, canonical-data, persistence, or compatibility change
- **Last reviewed:** 2026-07-18

## Intent statement

Enable a local owner to register one US-listed stock and one spot-cryptocurrency pair under provider-neutral identities, resolve explicit provider mappings, retrieve a bounded daily OHLCV range through governed adapters, inspect source/canonical provenance and quality, repair a declared missing range incrementally, and inspect or safely preview cleanup through shared CLI/API behavior.

## User outcome

A user can discover or manually register an instrument, see whether each reference provider supports daily bars, request a date range with explicit freshness/completeness needs, receive a typed dataset revision or structured partial/failure status, inspect exactly which provider observations and normalization rules produced it, and repair gaps without silently replacing accepted history.

## Requirements allocation

New immutable M2 requirements begin at REQ-0021. Exact entries must be accepted before implementation. M1 requirements remain active where their shared security, workflow, metadata, telemetry, recovery, documentation, and evidence obligations apply.

## In scope

- stock and spot-crypto-pair canonical identities;
- explicit time-aware provider mappings and ambiguity handling;
- one reference stock adapter and one reference crypto adapter;
- machine-readable daily-bar capabilities, quota, policy, and health;
- daily OHLCV only, with explicit UTC/source timestamp semantics and completed bars;
- immutable permitted source records or explicit non-retention evidence;
- versioned canonical daily-bar dataset revisions;
- request identity, freshness/completeness policy, structured resolution status, idempotent retrieval, gap detection, and targeted repair;
- deterministic initial quality rules and visible findings;
- basic usage inspection, pin/protection metadata, and dry-run/scoped cleanup;
- shared CLI and versioned API paths;
- correlated telemetry, audit where security/policy sensitive, documentation, migrations, and retained evidence.

## Non-goals

- intraday intervals, full exchange calendars, provisional bars, corporate actions, adjusted views, derived/artifact layers, provider reconciliation/merging, analytical queries, visualization, external extension packaging, distributed workers, scheduling, market payload backup, or M3+ scale claims;
- public-internet provider proxying or multi-user quota sharing;
- commercial redistribution or any provider use not supported by reviewed policy metadata.

## Success measures

- canonical registration rejects ambiguous or duplicate economic identity safely;
- provider symbols never become canonical primary keys;
- equivalent requests share durable work and return the same governed revision;
- a bounded daily range is retrieved, normalized, quality checked, and exposed with complete provenance;
- missing ranges are detected and repaired without refetching unaffected accepted history;
- provider, quota, license, stale, partial, invalid, corrupt, and unavailable states are distinguishable;
- cleanup preview protects pinned/catalog-required material and never silently deletes accepted canonical history;
- no secret, untrusted payload, or licensing restriction is disclosed or bypassed;
- all examples and evidence are reproducible from deterministic fixtures without requiring live-network CI.

## Exit evidence

The retained record must link source revision, exact requirements, ADRs, provider-policy decisions, contracts, schemas, migrations, adapter conformance, deterministic fixtures, ambiguity and licensing negatives, freshness/repair properties, quality findings, cleanup safety, interface semantics, telemetry, documentation, performance observations, residual risks, and immutable CI identity.
