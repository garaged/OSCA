# M12 Release Readiness and Operational Resilience Specification

- **Status:** Accepted
- **Milestone:** M12
- **Requirements:** REQ-0145 through REQ-0156
- **ADR:** ADR-0038
- **Last updated:** 2026-07-25

## Intent

M12 establishes the governed release-readiness and operational-resilience foundation for OSCA. It defines metadata contracts, deterministic validation gates, and SQLite persistence for backup profiles, restore verification, disaster-recovery exercises, health findings, alert policies, durable workflow runs, and deterministic risk-policy decisions.

## Scope

M12 includes metadata and evidence contracts for policy-aware backup manifests, recovery objectives, isolated restore verification, DR exercises, health and alert records, workflow run records, missed-run safeguards, risk-policy decisions, and operations metadata persistence.

M12 does not implement real off-device transfer, active restore execution, external notification delivery, runtime scheduler execution, personal-server transport hardening, broker or exchange execution, real-capital orders, or provider production promotion.

## Acceptance Criteria

| ID | Requirement | Criterion | Evidence |
|---|---|---|---|
| M12-AC-001 | REQ-0145, REQ-0146 | Backup manifests preserve encrypted profile, integrity, recovery class, off-device intent, and secret exclusion. | Contract and service tests |
| M12-AC-002 | REQ-0147, REQ-0148 | Restore verification and DR exercises fail closed when integrity, compatibility, reconciliation, or isolation evidence is missing. | Contract and service tests |
| M12-AC-003 | REQ-0149, REQ-0150 | Health findings and alert policies preserve impact, remediation, correlation, dedupe, escalation, and local-only delivery metadata. | Contract and service tests |
| M12-AC-004 | REQ-0151, REQ-0152 | Workflow run records preserve trigger, idempotency, missed-run policy, approval, status, and safe replay behavior. | Contract tests |
| M12-AC-005 | REQ-0153 | Risk-policy decisions fail closed for breached strict controls and require explicit authority for modified outcomes. | Contract and service tests |
| M12-AC-006 | REQ-0154 | SQLite persistence round trips and queries M12 metadata by component, workflow, and policy. | Persistence tests |
| M12-AC-007 | REQ-0155, REQ-0156 | Manual testing, traceability, OpenSpec, ADR, status, and exit evidence are retained. | Inspection and hosted Quality |

## Deferred Scope

- Real off-device backup transport or cloud storage integration.
- Active restore execution.
- External alert delivery.
- Runtime scheduler execution.
- Personal-server TLS/session implementation beyond prior skeleton boundaries.
- Broker or exchange execution.
- Real-capital orders.
- Provider production promotion.
