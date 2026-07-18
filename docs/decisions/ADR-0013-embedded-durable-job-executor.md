# ADR-0013 — Embedded Durable Job Executor

- **Status:** Accepted
- **Date:** 2026-07-18
- **Decision owners:** Workflow capability owner and architecture authority
- **Scope:** M1 durable diagnostic-job execution
- **Related requirements:** REQ-0011, REQ-0012, REQ-0014, REQ-0015
- **Related product decisions:** D-007, D-021, D-035, D-036, D-044
- **Supersedes:** DD-009 for M1
- **Superseded by:** None

## Context

M1 must prove stable job identity, status, progress, retry, cancellation, safe shutdown, and restart/resume on a workstation without requiring a broker or external orchestration service.

## Decision

OSCA will implement an embedded, database-backed, single-node executor behind the accepted workflow seam.

The executor owns process state only. Job handlers invoke public application contracts and cannot become a business-rule layer.

M1 semantics include:

- typed workflow and run identities;
- versioned input and result references;
- explicit pending, running, blocked, succeeded, failed, cancelling, cancelled, and interrupted states;
- atomic claim with lease/heartbeat metadata;
- idempotency key and duplicate behavior;
- bounded retry by structured error category;
- checkpoint and resume contract;
- cooperative cancellation;
- safe shutdown that marks or recovers abandoned leases;
- concurrency policy and resource budget;
- correlated telemetry and retained diagnostics.

Delivery and restart semantics are at-least-once. Handlers must be idempotent or duplicate-aware. No exactly-once claim is made.

## Consequences

OSCA avoids Redis, a broker, or an external workflow control plane in M1. It must implement and test lease, recovery, and concurrency behavior carefully. The public workflow seam allows a later executor adapter without changing business contracts.

## Fitness

- duplicate submission follows declared idempotency behavior;
- process termination and lease expiry recover deterministically;
- cancellation and retry preserve valid state transitions;
- no job handler imports another capability's private implementation;
- four independent M1 jobs can be represented without ambiguous latest-run state;
- failures become visible health findings and cannot remain silent.

## Revisit triggers

Distributed workers, sustained parallelism beyond the single-node envelope, isolation requirements, or operational evidence favoring an external engine.
