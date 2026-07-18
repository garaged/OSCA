# M1 Initiation Checklist

- **Status:** Accepted control
- **Governing role:** Architecture authority
- **Authority:** Engineering constitution; ADR-0001 through ADR-0010
- **Last reviewed:** 2026-07-18

## Intent and scope

- [ ] One thin, demonstrable end-to-end outcome is named.
- [ ] In-scope and out-of-scope behavior is explicit.
- [ ] Approved requirement IDs and product decisions are linked.
- [ ] Success measures and exit evidence are objective.

## Architecture and decisions

- [ ] Owning capabilities and mutable state are identified.
- [ ] Commands, queries, events, and workflows are classified.
- [ ] Public/durable contract candidates and owners are identified.
- [ ] Applicable Tier-1 ADRs and quality attributes are linked.
- [ ] Triggered deferred decisions are resolved before implementation depends on them.
- [ ] Any consequential new choice has an accepted ADR.

## Specification

- [ ] Invariants, time/identity semantics, and failure states are specified.
- [ ] Security, permissions, secure transfer, and threat deltas are specified.
- [ ] Observability, audit, health, diagnostics, and redaction are specified.
- [ ] Persistence, migration, compatibility, recovery, and degraded behavior are specified.
- [ ] Acceptance criteria map to requirements.

## Validation and evidence

- [ ] Risk class and ADR-0005 gate profile are recorded.
- [ ] Deterministic fixtures, clocks, calendars, seeds, and versions are planned.
- [ ] Contract, security-negative, recovery, migration, and end-to-end evidence is selected as applicable.
- [ ] Evidence retention location and owners are named.
- [ ] Documentation and traceability updates are planned.

## Entry decision

M1 implementation may begin only when unchecked items are either non-applicable with rationale or covered by an approved, expiring exception. At that point Tier-1 ADRs move from Baseline to Frozen.
