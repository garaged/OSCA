# M2 Entry Decision Package

- **Status:** Accepted decision criteria and persistence selection; provider selections pending licensing evidence
- **Governing role:** Architecture authority
- **Product, security, data, licensing, and quality approval:** Accepted for the criteria 2026-07-18
- **Authoritative sources:** M2 intent/scope; D-012–D-018; D-040; DD-003, DD-010
- **Last reviewed:** 2026-07-18

## Decisions triggered before implementation

1. Exact semantic/structural M2 public contracts and ownership.
2. Instrument/provider/market-data schema ownership and migration sequence.
3. Daily payload persistence and replaceable access boundary — decided by ADR-0017.
4. Reference stock and crypto providers and their permitted acquisition/retention/fixture use.
5. Quota, retry, endpoint, timeout, and credential-reference profiles.
6. Daily expected-date policy sufficient for M2 without claiming the M3 calendar engine.
7. Recovery inclusion/exclusion for registry, mappings, policies, catalog metadata, source evidence, and canonical payloads.
8. Bounded M2 performance observations; DD-010 production budgets remain deferred.

## Reference-provider selection criteria

A candidate is eligible only if:

- official documented access exists and automation is permitted;
- stock or spot-crypto daily OHLCV capability matches the slice;
- credentials can use named vault references;
- terms for local retention, transformation, tests, export, backup, and fixture redistribution are reviewed explicitly;
- quota and retry behavior are machine representable;
- timestamp, adjustment, completion, price, and volume semantics are documented;
- deterministic license-safe fixtures can be retained, or a synthetic conformance fixture can fully prove the adapter boundary;
- stable identifiers/discovery metadata support canonical mapping;
- failure modes can be reproduced without live-network CI;
- no mandatory paid cloud service is introduced.

Provider popularity alone is not evidence. No provider is selected by this proposal.

## Persistence selection criteria

The M2 choice must:

- preserve exact daily numeric and temporal meaning;
- support bounded range reads, uniqueness, revisions, integrity, gaps, and targeted repair;
- keep Instrument, Provider, Market Data, and Catalog ownership enforceable;
- separate bulk payload access from M1 metadata schemas;
- provide deterministic migrations/export and corruption detection;
- operate locally without a mandatory service;
- allow later evidence-driven replacement without changing public dataset identity;
- avoid preselecting M3 intraday/analytical behavior.

[ADR-0017](../../decisions/ADR-0017-m2-metadata-and-daily-payload-persistence.md) selects capability-owned SQLite metadata plus immutable, manifest-governed Parquet source/canonical payloads. M2.1 may implement the owned metadata schemas. M2.3 payload work remains subject to the ADR's schema, coordination, migration, and recovery fitness obligations.

## Decision gate

M2.1 is authorized against ADR-0017 and the accepted requirements/contracts/risks. Production-visible M2.7 adapters remain gated until provider-specific licensing and policy approval; deterministic fixture adapters may be built earlier against the accepted contract.
