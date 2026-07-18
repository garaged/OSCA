# M1 Execution Plan

- **Status:** Proposed
- **Governing role:** Architecture authority
- **Product approval:** Product authority
- **Authoritative sources:** M1 intent and scope; ADR-0001 through ADR-0010
- **Last reviewed:** 2026-07-18

## Increment sequence

1. **M1.0 — Entry decisions:** approve requirements, technology ADRs, specifications, and evidence profile.
2. **M1.1 — Repository skeleton:** establish modules, build, configuration, structural fitness checks, and one executable entrypoint.
3. **M1.2 — Readiness contract:** implement shared capability plus API, CLI, and web adapters.
4. **M1.3 — Security and secrets:** enforce deployment profiles, secret references, audit, and negative tests.
5. **M1.4 — Durable diagnostic job:** implement persistent lifecycle, restart/resume, cancellation, and telemetry.
6. **M1.5 — Metadata catalog foundation:** retain typed job and backup metadata with lineage and availability.
7. **M1.6 — Recovery skeleton:** create, verify, preview, and isolate minimal restore.
8. **M1.7 — Documentation and operational evidence:** execute examples, validate references, and close findings.
9. **M1.8 — Exit review:** reconcile traceability, risks, gates, compatibility, and deferred work.

## Increment rule

Each increment must leave the repository buildable, testable, and diagnosable. Infrastructure without a user-visible or operator-visible path is incomplete. Later increments may strengthen an earlier contract but cannot bypass its compatibility policy.
