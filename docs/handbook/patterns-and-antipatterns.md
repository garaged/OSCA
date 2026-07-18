# OSCA Architecture Patterns and Anti-patterns

- **Status:** Accepted guidance
- **Governing role:** Architecture authority
- **Authoritative sources:** ADR-0002 through ADR-0010; dependency rules
- **Review trigger:** ADR supersession or repeated architecture finding
- **Last reviewed:** 2026-07-18

| Concern | Preferred pattern | Anti-pattern | Authority |
|---|---|---|---|
| Ownership | One capability owns mutable state and invariants | Shared mutable domain model | ADR-0002, ADR-0009 |
| Dependency | Depend on a published application contract | Import another module's internals | ADR-0003 |
| Read access | Public query or governed projection | Cross-module table access | ADR-0009 |
| Mutation | Command to the owning capability | Event used as a disguised command | ADR-0006 |
| Facts | Idempotent integration event after commit | Assume exactly-once delivery | ADR-0007 |
| Long work | Durable checkpointed workflow | In-memory orchestration with implicit recovery | ADR-0006 |
| Compatibility | Owned versioned contract family with fixtures | Structurally change a durable payload in place | ADR-0004 |
| Extension | Explicit seam, grants, and trust-tier isolation | Internal imports or ambient credentials | ADR-0008 |
| Observability | Contracted signals with correlation and redaction | Logs added after failure | ADR-0010 |
| Quality | Risk-selected evidence and expiring exceptions | Lower a test threshold to pass current code | ADR-0005 |

## Review use

Treat this table as a diagnostic aid. When it identifies a concern, review and cite the governing ADR; do not approve or reject a design from the shorthand alone.
