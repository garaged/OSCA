# ADR-0036: LLM Lifecycle and Gateway Boundary

- **Status:** Accepted
- **Date:** 2026-07-25
- **Deciders:** Product authority, architecture authority, security authority
- **Milestone:** M10
- **Requirements:** REQ-0125-REQ-0132

## Context

The approved PRD requires LLM support through a governed provider-neutral gateway, bounded application tools, versioned prompts, explicit context selection, privacy controls, resource budgets, and evaluation evidence.

M9 established the governed ML lifecycle, but LLM behavior remains deferred. M10 needs a boundary that allows lifecycle contracts and deterministic gateway decisions to be implemented before any actual model-provider invocation or generated-output behavior.

## Decision

M10 will model LLM lifecycle and gateway behavior as immutable contracts and deterministic service decisions first.

The M10 foundation includes provider/model capability declarations, prompt templates, tool definitions, context policies, request envelopes, route decisions, structured-output contracts, and evaluation reports. Provider calls, prompt execution, retrieval materialization, generated recommendations, state-changing tool orchestration, and LLM-initiated paper actions remain deferred until later accepted slices define exact execution, persistence, and safety evidence.

## Consequences

- Exact provider and model versions are retained as evidence and cannot be silently substituted.
- State-changing tools require explicit approval and live-order capabilities remain prohibited.
- Privacy, untrusted-content, cost, latency, and tool-call budgets are evaluated before any provider execution exists.
- M10 can add deterministic tests and documentation without creating a dependency on external LLM providers.
