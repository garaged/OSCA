# M2 Initiation Gap Analysis

- **Status:** Complete analysis; M2 initiation pending
- **Governing role:** Product authority, with architecture, security, data, licensing, and quality review
- **Authoritative outcome:** PRD M2 — Instruments, Providers, and Cache Vertical Slice
- **Source baseline:** `979ae16a4271a8e8a5cbb29313b8ee9b1ca9b7af`
- **Reviewed:** 2026-07-18

## Scope and method

This analysis compares the accepted PRD M2 outcome and active decisions with the accepted M1 baseline, requirements catalog, ADRs, specifications, contracts, validation, and repository organization. It does not create requirements, choose providers, or begin implementation.

## Completed foundation available to M2

| Area | Reusable M1/M0 result |
|---|---|
| Architecture | Frozen modular-monolith boundaries, public seams, owned persistence, contract compatibility, quality, security, recovery, and observability rules |
| Runtime and engineering | Locked CPython 3.13/uv environment, CI, strict typing/linting, migrations, architecture checks, OpenSpec controls, and contributor routing |
| Application surfaces | Shared CLI, API, and web adapter patterns |
| Durable work | Typed idempotent jobs, lifecycle, leases, checkpointing, cancellation, retry, result metadata, telemetry, and audit |
| Catalog | Typed stable metadata identity, lineage, integrity, availability, and retention foundations |
| Configuration/security | Validated profiles, trusted authorization, vault references, safe errors, and redaction |
| Recovery | Protected metadata backup, compatibility verification, preview, and isolated restore |
| Documentation/evidence | Version-matched operational guidance and governed evidence workflow |

## Authoritative M2 outcome

The PRD requires a vertical slice in which users can register stock and crypto instruments and retrieve governed daily data, including:

- canonical instrument registry;
- provider mappings and discovery;
- one stock and one crypto provider adapter against the draft provider-extension contract;
- capability routing and quotas;
- source and canonical layers;
- daily OHLCV ingestion;
- policy-driven freshness;
- gap detection and incremental repair;
- basic storage inspection and cleanup;
- initial quality rules and provenance.

Active decisions directly governing this scope include D-012 (canonical instrument identity), D-016 (multi-provider routing and no silent merging), D-018 (policy-driven freshness and targeted repair), plus product licensing/acquisition, deterministic-computation, cache-budget, quality, provenance, and local-first decisions.

## Missing entry deliverables

| Deliverable | Current state | Required before implementation |
|---|---|---|
| M2 intent and scope | Absent | Select one demonstrable thin outcome and explicit non-goals from the PRD without importing M3 behavior |
| Stable requirements | No M2 `REQ-NNNN` allocation exists | Extract atomic requirements from exact PRD sections and active D-records |
| Traceability | No M2 row exists | Link authority → intent → requirement → specification → acceptance criterion → planned evidence |
| Capability ownership | Logical M2 owners are not allocated | Define Instrument, Provider, Data/Cache, Catalog, Workflow, Operations, and interface responsibilities and state |
| Provider contract | Only a product-level draft seam is referenced | Specify capability metadata, discovery/mapping, request/result, error, quota, licensing, and conformance behavior |
| Provider selection | No adapters selected | Establish evidence-based stock and crypto reference-adapter criteria; selection requires licensing and test-fixture viability |
| Canonical data contract | Absent | Specify daily OHLCV time/price/volume semantics, source versus canonical identity, revisions, quality, and provenance |
| Persistence | M1 SQLite is metadata-only | Decide M2 metadata and daily-payload storage without implicitly choosing the M3 analytical engine |
| Freshness/repair | Product decision only | Specify requirements, resolution status, gap semantics, idempotency, concurrent request behavior, and repair revisions |
| Quality | No M2 rule catalog | Define initial deterministic validation, quarantine/failure behavior, and no-silent-mutation invariant |
| Licensing/policy | Product principles exist but no M2 enforcement spec | Define provider rights, retention/export constraints, fixture provenance, and failure behavior |
| Security/threat delta | Absent | Cover provider credentials, untrusted payloads, quota abuse, SSRF/URL control, decompression/size limits, and diagnostic disclosure |
| Migration/recovery | Absent | Specify schema ownership, migration, cache reconstructability, protected metadata, cleanup, and backup inclusion/exclusion |
| Evidence plan | Absent | Select contract, adapter, property, quality, repair, quota, licensing, security, migration, performance, E2E, and documentation gates |
| Risk register | No M2 risk treatment record | Assign stable risks/owners for symbol ambiguity, licensing, provider change, canonical corruption, stale/partial data, quota exhaustion, and storage pressure |

## Boundaries requiring explicit protection

- M2 daily bars must not silently establish M3 intraday, calendar/session, corporate-action, reconciliation, derived-layer, or analytical-storage behavior.
- Provider symbols are aliases, never canonical primary identity.
- Provider transitions and disagreements remain visible; no silent cross-provider merging.
- Cache availability/freshness does not imply data correctness.
- Repairs create governed revisions and lineage; they do not rewrite accepted history invisibly.
- Market payload storage must remain separate from M1 metadata ownership.
- A concrete provider SDK/package boundary is exercised internally in M2 but independent external packaging remains M5.
- M2 must not add analysis, visualization, strategy, paper trading, ML, LLM, or live-order behavior.

## Inconsistencies and stale references

- The requirements catalog population text and traceability register remain M1-oriented and need an M2 allocation rather than reuse of M1 identifiers.
- The architecture registry is correctly `m1-complete` but has no M2 initiation record or M2 artifact links.
- The contract catalog contains only M1 families; no provider, instrument, retrieval, dataset, or quality-finding family is registered.
- DD-003 explicitly limits SQLite to M1 metadata, so M2 payload persistence cannot be inferred from existing code.
- DD-010 retains numeric production budgets as deferred; M2 must define bounded slice observations without inventing product-wide targets.

## Recommended initiation order

1. **Intent:** approve the smallest M2 user-visible daily-data outcome and non-goals.
2. **Requirements:** extract exact M2 `REQ-NNNN` entries and trace them to PRD/D-record authority.
3. **Architecture:** allocate capability/state ownership and identify triggered ADRs/deferred decisions.
4. **Specification:** define instrument, provider, daily-bar, retrieval/freshness, quality, licensing, migration, cleanup, and failure contracts.
5. **Validation:** approve risk class, provider conformance fixtures, security-negative tests, and evidence plan.
6. **Decisions:** select reference providers and persistence only after licensing, reproducibility, offline-fixture, and operational evidence exists.
7. **Implementation:** proceed as thin increments that each leave a user/operator-visible path and retained evidence.

## Blocking assessment

M2 implementation is blocked, by design, until intent, stable requirements, ownership, public contracts, triggered technology/licensing decisions, threat delta, acceptance criteria, and evidence plan are accepted. No M0/M1 defect blocks M2 initiation.
