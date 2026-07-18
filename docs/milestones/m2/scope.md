# M2 Scope — Instruments, Providers, and Daily Cache

- **Status:** Proposed
- **Governing role:** Product authority
- **Architecture approval:** Required
- **Authoritative sources:** [M2 intent](intent.md); PRD M2; D-012–D-018; D-040
- **Last reviewed:** 2026-07-18

## Vertical-slice boundary

M2 is organized around one governed daily-data request, not separate registry, adapter, storage, or cache projects.

The slice begins with canonical instrument identity, resolves an explicit provider mapping and policy, creates durable retrieval work, retains permitted source evidence, normalizes a versioned canonical daily-bar revision, applies quality rules, and returns a typed resolution through shared interfaces. Inspection and targeted repair use the same identities and ownership boundaries.

## Capability allocation

| Capability | M2 responsibility | State owned |
|---|---|---|
| Instrument | Canonical stock/crypto identity, lifecycle, ambiguity, provider mappings | Instrument and mapping records |
| Provider | Adapter capability/policy/health, request execution, quota observations | Provider configuration and operational quota state |
| Market Data | Request identity, source observations, canonical daily bars, dataset revisions, gaps and repairs | Source/canonical market-data records |
| Catalog | Typed dataset metadata, lineage, integrity, availability, retention/pinning references | Catalog metadata only |
| Workflow | Durable retrieval/repair lifecycle through existing job semantics | Retrieval run state and checkpoints |
| Operations | Data/provider health, quality findings, telemetry, audit | Operational observations/findings |
| Recovery | M2 metadata inclusion/exclusion policy only | Existing recovery records; payload recovery is out of scope |
| Interface adapters | Register, retrieve, inspect, and cleanup-preview presentations | No authoritative state |

No capability may import another capability's private persistence. Provider adapters cannot write canonical data directly.

## Required end-to-end scenarios

1. Register one unambiguous stock and one spot-crypto pair with canonical identity and explicit mappings.
2. Reject ambiguous ticker/pair, duplicate identity, invalid venue/currency, and unverified mapping.
3. Resolve a daily-bar request through a provider capability/policy without exposing credentials.
4. Persist permitted immutable source evidence and a versioned canonical revision with lineage and quality.
5. Return structured fresh, stale, partial, invalid, unavailable, quota-blocked, and policy-blocked outcomes.
6. Detect a deterministic missing daily range and repair only that range through idempotent durable work.
7. Inspect usage/provenance and preview scoped cleanup while protecting pinned and required records.
8. Exercise the path through CLI and versioned API with equivalent semantics and retained evidence.

## M2/M3 boundary

M2 models daily bars sufficiently to avoid daily-only identity assumptions, but does not implement intraday calendars/sessions, provisional observations, resampling, corporate actions, provider reconciliation, derived layers, or representative product-scale benchmarks. Those remain M3 scope.

## Entry gates

Implementation cannot begin until:

- REQ-0021 onward are accepted and traced;
- provider/instrument/data contracts and acceptance criteria are accepted;
- persistence ownership and migration/recovery behavior are decided;
- provider selection has licensing, quota, fixture, and reproducibility evidence;
- threat delta and risk treatments are accepted;
- evidence plan and reference fixtures are approved.
