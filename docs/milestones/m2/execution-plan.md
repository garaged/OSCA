# M2 Execution Plan

- **Status:** Proposed
- **Governing role:** Architecture authority
- **Product approval:** Required
- **Authoritative sources:** M2 intent/scope, REQ-0021–REQ-0040, accepted M2 specification and decisions
- **Last reviewed:** 2026-07-18

## Proposed increment sequence

1. **M2.0 — Entry decisions:** accept intent, requirements, contracts, risks, evidence plan, provider-selection criteria, persistence, and migration/recovery profile.
2. **M2.1 — Instrument registry:** canonical stock/crypto identity, mappings, ambiguity, persistence, and shared registration/query path.
3. **M2.2 — Provider contract and fixtures:** capability/policy schemas, conformance kit, deterministic stock and crypto fixture adapters.
4. **M2.3 — Governed daily ingestion:** request identity, source/canonical layers, normalization, revisions, lineage, and one interface path.
5. **M2.4 — Durable freshness and repair:** structured resolution, idempotent retrieval, gaps, targeted repair, restart, and cancellation.
6. **M2.5 — Quality and operations:** deterministic findings, provider/data health, telemetry, audit, and troubleshooting.
7. **M2.6 — Inspection and cleanup preview:** usage/provenance inspection, pin/protection behavior, and safe scoped plan.
8. **M2.7 — Reference adapters:** production adapters become visible only after licensing, credential, quota, failure, and conformance review.
9. **M2.8 — Documentation and integrated evidence:** executable examples, performance observations, traceability, risks, and limitations.
10. **M2.9 — Exit review:** reconcile all criteria, compatibility, licensing, recovery, deferred work, and authority acceptance.

## Increment rule

Each increment must be buildable, testable, diagnosable, and reachable through an operator/user path. Infrastructure-only completion, live-network-only evidence, silent provider mixing, or premature M3 behavior is prohibited.
