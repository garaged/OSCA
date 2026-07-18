# Specification — M2 Governed Daily Market Data

- **Status:** Proposed
- **Governing role:** Architecture authority
- **Approval roles:** Product, security, data, licensing, and quality authorities
- **Governing intent:** [M2 intent](../milestones/m2/intent.md)
- **Requirements:** REQ-0021–REQ-0040
- **Related decisions:** D-012–D-018, D-040; ADR-0001–ADR-0016
- **Risk class:** Governed high-risk data-integrity, licensing, and external-adapter change
- **Last reviewed:** 2026-07-18

## Public contract candidates

- `osca.instrument.reference` 1.0.0;
- `osca.provider.capability` 1.0.0;
- `osca.market-data.daily-bar` 1.0.0;
- `osca.market-data.retrieval-request` 1.0.0;
- `osca.market-data.resolution` 1.0.0;
- `osca.data-quality.finding` 1.0.0;
- `osca.cache.cleanup-plan` 1.0.0.

Exact semantic and structural schemas must be accepted before implementation. Unknown major versions fail closed.

## Behavioral specification

### Instrument registration

Canonical stock identity distinguishes listing/venue, currency, lifecycle, and stable external identity where available. Canonical crypto-pair identity distinguishes base asset, quote asset, venue/scope, currencies, and lifecycle. Registration detects duplicates and ambiguity. Provider mappings are time-aware, inspectable, correctable records; unverified ambiguous mappings cannot normalize observations.

### Provider capability and policy

Adapters expose capability, timestamp/adjustment, quota, authentication, licensing, retention/export, quality, and health metadata. Routing evaluates an explicit ordered policy. M2 normally selects one source. Fallback is observable and cannot silently merge series. Credentials are named references only.

Reference adapters must be replaceable, deterministic under recorded fixtures, bounded in time/size/retry, and incapable of choosing arbitrary caller-controlled destinations. Live network access is excluded from required CI evidence.

### Daily observations

A daily bar contains canonical instrument identity, `1d` interval, source timestamp/session label, normalized effective date, completion state, open/high/low/close, volume, currency/unit semantics, provider/source identity, retrieval identity, schema revision, and integrity identity. Numeric representation must not introduce silent binary-float ambiguity in retained canonical meaning.

M2 does not implement adjusted bars, corporate actions, intraday sessions, or cross-provider reconciliation.

### Source and canonical layers

Permitted source evidence is immutable and checksummed. When retention is prohibited, metadata records intentional non-retention and policy. Normalization is deterministic and versioned. Corrections create new canonical revisions. Provider symbols never replace canonical identity. Catalog metadata survives payload cleanup.

### Retrieval and freshness

Requests declare canonical instrument, daily interval, inclusive/exclusive range semantics, freshness, completeness, provider constraints, and idempotency context. Resolution returns a typed dataset revision or a structured state: fresh, stale, partial, invalid, corrupt, unavailable, refreshing, quota-blocked, or policy-blocked.

Equivalent work deduplicates through durable workflow semantics. Provider latency and quota are visible. Retry is bounded and only for declared categories. Cancellation and restart never publish a partial result as complete.

### Gaps, repair, and quality

The M2 daily reference policy declares expected dates without claiming the complete M3 calendar engine. Missing expected dates produce gaps; non-trading/date uncertainty produces an explicit unresolved finding rather than fabricated data. Repair requests only missing/invalid ranges and produces a new dataset revision with lineage.

Initial rules reject or find: non-finite numbers, negative price/volume, high below open/close/low, low above open/close/high, duplicate identity/date, identity mismatch, invalid completion/time semantics, and declared range gaps. Findings never silently mutate observations.

### Inspection and cleanup

Inspection reports usage by layer/provider/instrument and links dataset identity, availability, policy, pinning, and lineage. Cleanup is preview-first, scoped, and explicit. M2 may evict permitted reconstructable source payloads under policy but cannot silently delete accepted canonical history, catalog metadata, pinned material, or required reproducibility inputs. Automatic reclamation remains later scope.

## Security and failure behavior

Treat provider metadata and payloads as untrusted structured input. Enforce scheme/host policy, timeouts, response and decompression limits, schema bounds, safe parsing, log injection resistance, and redaction. Distinguish authentication, authorization/policy, quota, transport, schema, quality, mapping, storage, and compatibility failures. Configuration and licensing uncertainty fail closed.

## Persistence, migration, and recovery

Instrument, Provider, and Market Data each own schemas. Catalog receives typed public metadata only. Payload storage is physically replaceable and cannot reuse another capability's private tables. Migrations retain every released revision and prove upgrade/downgrade policy. M2 recovery protects registry/mapping/policy/catalog metadata; bulk source/canonical payload backup is deferred pending an explicit profile, with availability/reconstruction implications documented.

## Acceptance criteria

| ID | Criterion | Requirements |
|---|---|---|
| M2-AC-001 | Register stock and crypto-pair canonical identities without provider-key identity. | REQ-0021–REQ-0024 |
| M2-AC-002 | Ambiguous/duplicate/unverified mappings fail before canonical writes. | REQ-0023, REQ-0024 |
| M2-AC-003 | Both reference adapters pass one provider contract and deterministic fixtures. | REQ-0025, REQ-0029 |
| M2-AC-004 | Routing respects capability, quota, licensing, and explicit provider policy. | REQ-0026–REQ-0029 |
| M2-AC-005 | Fallback/provider transition is visible and no silent merge occurs. | REQ-0027 |
| M2-AC-006 | Retention/export/backup restrictions fail closed and are cataloged. | REQ-0028, REQ-0031 |
| M2-AC-007 | Daily-bar schema and normalization fixtures are deterministic. | REQ-0030–REQ-0033 |
| M2-AC-008 | Corrections create revisions; accepted history is not silently rewritten. | REQ-0031, REQ-0032 |
| M2-AC-009 | Requests have canonical identity and explicit freshness/completeness semantics. | REQ-0034 |
| M2-AC-010 | Resolution states and safe remediation are semantically equivalent across interfaces. | REQ-0035 |
| M2-AC-011 | Equivalent concurrent requests deduplicate durably and survive restart/cancellation. | REQ-0036 |
| M2-AC-012 | Declared daily gaps are detected and targeted repair preserves unaffected lineage. | REQ-0037 |
| M2-AC-013 | Initial quality properties reject/find all specified invalid observations. | REQ-0038 |
| M2-AC-014 | Inspection reports governed usage/provenance/availability. | REQ-0033, REQ-0039 |
| M2-AC-015 | Cleanup preview protects canonical, pinned, and required material. | REQ-0039 |
| M2-AC-016 | Untrusted payload, SSRF, size, timeout, quota, and secret negatives fail safely. | REQ-0025, REQ-0028, REQ-0029 |
| M2-AC-017 | Owned migrations and recovery metadata policy pass upgrade/rollback/reconciliation. | REQ-0031–REQ-0033, REQ-0039 |
| M2-AC-018 | Cached/indexed operations meet stated M2 reference observations or disposition. | REQ-0034–REQ-0039 |
| M2-AC-019 | Installation, provider policy, registration, retrieval, repair, inspection, cleanup, and troubleshooting examples are validated. | REQ-0040 |
| M2-AC-020 | Final evidence has no missing authority, risk, licensing, contract, test, documentation, or residual-risk link. | REQ-0040 |

## Entry blockers

Reference provider selection, payload persistence, exact schemas, threat/risk approval, licensing policy, deterministic fixtures, performance observations, and migration/recovery profile must be accepted before implementation.
