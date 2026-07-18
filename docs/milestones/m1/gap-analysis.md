# M1 Repository Gap Analysis

- **Status:** Completed
- **Governing role:** Architecture authority
- **Purpose:** Identify the delta from the merged M0.x baseline to an implementation-ready M1 secure walking skeleton.
- **Baseline:** `b4bc6d06bdc9ddb220fbddb7a5d1a8032092dd9f`
- **Last reviewed:** 2026-07-18

## Already complete

M0/M0.x provides authoritative capability boundaries, dependency rules, contract/versioning policy, security and recovery baselines, workflow/event semantics, observability architecture, verification strategy, fitness obligations, handbook guidance, exception mechanics, and M1 initiation controls.

## Missing before implementation

- approved M1 intent and bounded vertical-slice scope;
- exact requirement IDs derived from the approved PRD;
- accepted runtime/build/repository-layout decisions;
- persistence and durable-job technology decision for the M1 workload;
- concrete secret-store and local/personal-server security profile;
- versioned readiness API/CLI/web contract specification;
- minimal metadata, backup, and restore contract specifications;
- implementation repository and executable quality gates;
- M1 evidence plan and Tier-1 ADR freeze transition.

## Triggered deferred decisions

| Decision | Why triggered |
|---|---|
| DD-001 | M1 produces the first runnable product. |
| DD-002 | ADR-0003 and ADR-0005 require physical boundary and gate enforcement. |
| DD-003 | Durable jobs, metadata, configuration, and recovery introduce persistent state. |
| DD-009 | M1 requires an embedded durable job framework. |
| DD-011 | M1 introduces the first versioned API and retained contracts. |
| DD-012 | M1 introduces local-owner security, vault abstraction, and remote-profile skeleton. |
| DD-010 | Only M1 responsiveness targets supported by the PRD should be asserted; unsupported availability/recovery claims remain deferred. |

DD-007 is only triggered if the web shell needs a framework choice that cannot remain an adapter-local reversible decision.

## Recommended order

1. Approve M1 intent, scope, and requirement extraction.
2. Accept a coherent technology decision set for runtime, build, layout, persistence, workflow, contracts, and secrets.
3. Specify readiness behavior and public contracts.
4. Define structural, security, recovery, and documentation evidence.
5. Freeze Tier-1 ADRs and implement the smallest end-to-end scenario.
6. Expand through diagnostic-job and backup/restore scenarios while remaining deployable.
