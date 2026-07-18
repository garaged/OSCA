# M1 Initiation Record

- **Status:** Accepted for M1.1 implementation
- **Governing role:** Architecture authority
- **Product approval:** Product authority
- **Baseline:** `b4bc6d06bdc9ddb220fbddb7a5d1a8032092dd9f`
- **Last reviewed:** 2026-07-18

## Intent and scope

- [x] Thin end-to-end outcome proposed.
- [x] In-scope and out-of-scope behavior explicit.
- [x] Approved PRD sections and product decisions linked.
- [x] Objective success measures and exit evidence proposed.

## Architecture and decisions

- [x] Logical owners and mutable state identified.
- [x] Commands, queries, job interactions, and retained artifacts classified.
- [x] Public/durable contract candidates identified.
- [x] Tier-1 ADRs and quality attributes identified.
- [x] Triggered decisions required for M1.1–M1.5 accepted; backup encryption remains gated before M1.6.
- [x] Consequential decisions recorded in ADR-0011 through ADR-0015.

## Specification

- [x] Readiness capability and public contracts specified.
- [x] Security profile and threat delta specified.
- [x] Telemetry, audit, health, and redaction specified.
- [x] Persistence, migration, compatibility, and recovery behavior specified; encryption container remains an M1.6 entry decision.
- [x] Acceptance criteria approved and mapped to requirements.

## Validation and evidence

- [x] ADR-0005 high-risk foundation classification accepted.
- [x] Deterministic fixtures and environment controls planned.
- [x] Structural, contract, security-negative, restart, recovery, and end-to-end evidence selected.
- [x] Evidence location and owners assigned.
- [x] Documentation and traceability changes planned.

## Entry decision

M1.1 implementation may begin. Work must proceed incrementally; M1.6 recovery implementation remains blocked until an interoperable reviewed backup-encryption format is accepted. Tier-1 ADRs move to Frozen with the first implementation commit.
