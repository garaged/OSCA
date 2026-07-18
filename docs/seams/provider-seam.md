# Provider Seam

- **Status:** Draft
- **Owner:** Provider and acquisition capability
- **Purpose:** Integrate replaceable market, reference, news, macroeconomic, and related data sources without leaking vendor-specific behavior into product rules.

## Contract groups

1. **Capability declaration:** supported asset classes, venues, categories, intervals, history, freshness, adjustment semantics, quotas, licensing, persistence restrictions, authentication, health, and known limitations.
2. **Discovery and mapping:** provider search, remote metadata, canonical-identity candidates, time-aware mappings, verification state, and ambiguity diagnostics.
3. **Acquisition:** canonical request identity, routing context, completion and freshness policy, pagination or streaming continuation, checksums, source metadata, and structured status.
4. **Health and quota:** availability, latency, authentication, rate-limit state, remaining budget, reset semantics, and degradation guidance.

## Mandatory behavior

- Provider symbols never become canonical instrument identity.
- Fallback and provider transitions are recorded in provenance.
- Adapters cannot silently merge, overwrite, average, or reinterpret conflicting observations.
- Source timestamps, retrieval time, provisional state, adjustment semantics, and licensing restrictions remain explicit.
- Credentials are referenced by approved capability, never returned through the seam.
- Equivalent requests support idempotent or duplicate-aware retrieval behavior.
- Errors distinguish unsupported capability, ambiguous identity, authentication, quota, transport, provider failure, invalid payload, partial completion, and policy rejection.

## Conformance evidence

Fixtures must cover capability declaration, mapping ambiguity, pagination or continuation, quota exhaustion, partial data, malformed payloads, timestamp normalization, fallback provenance, cancellation, retry classification, and credential redaction.