# ADR-0006: Inter-Module Communication Model

- **Status:** Frozen
- **Tier:** Foundational
- **Date:** 2026-07-17

## Context

OSCA requires strong capability ownership without imposing distributed-system complexity on the initial modular monolith. A single communication mechanism would either create excessive temporal coupling or force asynchronous behavior where immediate consistency is required.

## Decision

Adopt a deliberate hybrid communication model.

- **Queries** retrieve information and do not mutate state.
- **Commands** request an owned state transition through the receiving capability's public application interface.
- **Domain events** describe facts inside the owning capability and are private unless deliberately promoted.
- **Integration events** communicate committed facts across capability boundaries without requiring an immediate result.
- **Durable workflows** coordinate long-running, retryable, scheduled, checkpointed, or compensating work.

Direct invocation is permitted only through public application interfaces. A capability must not access another capability's internal implementation or persistence. Workflow orchestration does not transfer domain ownership from participating capabilities.

Commands may execute synchronously in the initial modular monolith while retaining semantics that permit durable dispatch later. Integration events are published only after the owning transaction commits successfully.

## Consequences

The model preserves responsiveness and transactional clarity while supporting decoupling, fan-out, replay, and future extraction. Contributors must explicitly classify interactions and architecture fitness rules must detect misuse, including mutating queries, events used as disguised RPC, and cross-capability persistence access.

## Rejected alternatives

- Direct synchronous invocation for every interaction.
- Internal messaging for every interaction.
