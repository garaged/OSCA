# Reference Capability — Governed Market Snapshot

- **Status:** Accepted reference guidance
- **Governing role:** Architecture authority
- **Purpose:** Demonstrate the accepted intent-to-evidence chain without defining new product scope or selecting deferred technology.
- **Authoritative sources:** Existing market-data requirements; ADR-0001 through ADR-0010; provider and workflow seams
- **Downstream consumers:** M1 intent and specification authors
- **Review trigger:** First M1 vertical-slice selection or governing ADR supersession
- **Last reviewed:** 2026-07-18

## Teaching scenario

An authorized user requests a reproducible market snapshot for an already supported instrument and interval. OSCA resolves provider identity, retrieves data through the provider seam, records lineage and quality, exposes status through a query, and retains evidence sufficient to explain or reproduce the result.

This is an architecture walkthrough, not an approved M1 scope commitment.

## Traceability chain

| Stage | Reference content |
|---|---|
| Intent | Provide a diagnosable, reproducible slice of governed market intelligence. |
| Requirements | Cite existing approved requirement IDs in the milestone specification; do not invent IDs here. |
| Architecture | Market Data owns dataset state; Workflow owns process progress; Identity owns canonical instrument identity. |
| Specification | Define request, status, result, failure, security, time, lineage, compatibility, and recovery semantics. |
| Validation | Contract, component, property, security-negative, resume, migration, and end-to-end evidence. |
| Evidence | Source revision, fixture/provider revision, results, telemetry assertions, recovery result, and trace links. |

## Interactions

1. A command requests snapshot acquisition from the owning Market Data application contract.
2. Market Data queries Identity through a published contract when canonical mapping is required.
3. A durable workflow coordinates retry, timeout, cancellation, and checkpointing without owning market data.
4. After durable commit, Market Data may publish a versioned integration event describing snapshot availability.
5. A query returns status and a typed dataset reference; it does not expose private persistence.

## Ownership

| Concept | Owner | Allowed external representation |
|---|---|---|
| Canonical instrument identity | Identity | Stable identity contract |
| Provider mapping | Provider/Identity boundary as specified | Versioned mapping result |
| Snapshot dataset, lineage, and quality | Market Data | Typed dataset reference and quality summary |
| Process progress and checkpoint | Workflow | Workflow status contract |
| Audit record | Governing security/audit capability when defined | Authorized audit query |

M1 must resolve any ownership detail that its selected slice needs through a specification or ADR; this example does not override the domain model.

## Public contracts

Candidate contract families include snapshot request/status, dataset reference, provider result, and snapshot-available event. Each independently consumed or durable family requires an owner, version, compatibility profile, error semantics, security classification, and conformance evidence under ADR-0004.

## Failure and recovery

The specification must distinguish invalid identity, denied permission, unavailable provider, incomplete interval, rate limiting, corrupt payload, quality rejection, cancellation, retry exhaustion, and incompatible checkpoint. Resume must be idempotent, and a committed dataset must never be inferred solely from workflow transport success.

## Security and observability

Authorization is enforced at the owning boundary. Credentials are referenced, scoped, and never embedded in contracts or telemetry. Protected network transfer is authenticated and secure. Traces correlate command, provider attempt, workflow, dataset, event, and audit outcome. Logs and metrics are diagnostic; audit evidence remains distinct.

## Minimum verification

- deterministic component tests with controlled clock, calendar, provider response, and identity mapping;
- provider and public-contract conformance fixtures;
- denial and credential-scope tests;
- duplicate command/event and workflow-resume tests;
- lineage, quality, time-semantics, and integrity assertions;
- interrupted checkpoint and recovery test;
- a thin end-to-end demonstration through public contracts;
- link validation and a completed evidence record.

## Review questions

Does every mutable concept have one owner? Are all cross-capability interactions classified? Are durable surfaces cataloged? Can failures be diagnosed and resumed safely? Is protected data minimized? Can the result be explained from retained evidence? Are any deferred-decision triggers now true?
