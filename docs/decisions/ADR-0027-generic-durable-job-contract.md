# ADR-0027 — Generic Durable Job Contract

- **Status:** Accepted
- **Date:** 2026-07-18
- **Decision owners:** Product, architecture, Workflow, and Market Data authorities
- **Scope:** M2 retrieval/repair work and future durable capability jobs
- **Related requirements:** REQ-0036, REQ-0037, REQ-0040
- **Related decisions:** ADR-0004, ADR-0006, ADR-0007, ADR-0009, ADR-0013
- **Supersedes:** None
- **Superseded by:** None

## Context

ADR-0013 established an embedded durable executor, but M1 published only the diagnostic-specific `osca.workflow.diagnostic-run` contract and persistence. M2 retrieval and repair require the same identity, idempotency, lease, cancellation, retry, restart, and result-reference behavior without pretending that market-data work is a diagnostic probe.

## Decision

Workflow publishes `osca.workflow.job-run` 1.0.0 alongside the existing diagnostic contract. The new contract carries a typed job kind, versioned input family, canonical input digest, durable lifecycle, lease/checkpoint metadata, safe error, and durable result reference.

The diagnostic contract remains supported and unchanged. Generic jobs use a separate retained Workflow-owned table so compatibility does not depend on rewriting released diagnostic rows. The embedded executor retains at-least-once semantics; handlers remain capability-owned, idempotent or duplicate-aware, and reachable only through published application contracts.

Market Data uses `market-data.retrieve` and `market-data.repair` kinds. Equivalent actor/kind/idempotency submissions resolve the same durable job only when their versioned input digest is equivalent; conflicting reuse fails.

## Consequences and fitness

OSCA gains one reusable durable-work seam without duplicating workflow state in Market Data. It adds a public contract and migration that require schema, transition, concurrency, restart, cancellation, compatibility, and migration evidence. Tests retain diagnostic behavior, prove generic idempotency and atomic claim, and reject successful terminal state without a durable result reference.

## Revisit triggers

Distributed execution, cross-node leases, substantially different scheduling classes, or evidence that one generic envelope cannot preserve capability-specific semantics.
