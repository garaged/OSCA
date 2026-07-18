# ADR-0007: Event Reliability and Delivery Model

- **Status:** Frozen
- **Tier:** Foundational
- **Date:** 2026-07-17

## Context

Integration events must support recovery, replay, auditability, and possible future distributed execution without relying on infrastructure-specific exactly-once claims.

## Decision

Use at-least-once delivery with idempotent consumers.

Integration events are durably recorded before publication. Duplicate delivery is expected. Consumers affected by retries must be idempotent and must retain sufficient deduplication evidence for the contract's reliability window.

Ordering is guaranteed only within an explicitly declared scope, such as one aggregate, stream, or workflow. Global ordering must not be assumed.

Each integration event includes:

- unique event identifier;
- correlation and causation identifiers;
- producing capability and actor or service identity where applicable;
- occurrence and recording timestamps;
- contract family, compatibility version, and exact revision;
- provenance and replay metadata.

Retry, backoff, quarantine, and dead-letter handling are operational policies rather than domain behavior. Replay must preserve provenance, expose that execution is a replay, and use compatible contract revisions and migrations. Domain events remain private unless deliberately promoted to an integration contract.

## Consequences

The system gains practical reliability and recoverability across in-process and distributed deployments. Consumers bear explicit idempotency responsibilities, ordering assumptions must be modeled, and replay tooling becomes an operational capability.

## Rejected alternatives

- Best-effort delivery for governed integration events.
- Universal exactly-once delivery semantics.
