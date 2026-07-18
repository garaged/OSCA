# ADR-0028 — M2 Market Data Authorization Capabilities

- **Status:** Accepted
- **Date:** 2026-07-18
- **Decision owners:** Product, security, architecture, and Market Data authorities
- **Scope:** M2 retrieval, repair, inspection, cleanup preview, and cleanup execution
- **Related requirements:** REQ-0028, REQ-0029, REQ-0034–REQ-0039
- **Related decisions:** ADR-0004, ADR-0006, ADR-0015, ADR-0026
- **Supersedes:** None
- **Superseded by:** None

## Decision

M2 introduces explicit least-privilege capabilities for Market Data read, retrieval, repair, cleanup preview, and cleanup execution. Generic durable-job submit/read/cancel permissions are separate from domain permission: submitting retrieval or repair requires both the applicable Market Data capability and the generic Workflow capability.

Cleanup preview never grants execution authority. Cleanup execution requires its dedicated capability, the exact previewed actions, current policy-derived eligibility, and race-safe revalidation of protection and manifest state. Accepted canonical history remains non-selectable regardless of caller permissions.

## Consequences and fitness

Adapters cannot treat local ownership as implicit authority for destructive or provider-visible operations. Tests cover missing domain permission, missing Workflow permission, preview/execute separation, changed-plan rejection, canonical protection, and safe failure. Additional future operations require explicit capability review rather than reusing broad cleanup or Workflow authority.
