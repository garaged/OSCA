| ID | Requirement | Criterion | Evidence |
|---|---|---|---|
| M12-AC-001 | REQ-0145, REQ-0146 | Backup manifests preserve encrypted profile, integrity, recovery classes, off-device intent, and secret exclusion. | Contract and service tests |
| M12-AC-002 | REQ-0147, REQ-0148 | Restore verification and DR exercises preserve isolated validation evidence and fail closed when integrity, compatibility, or reconciliation fails. | Contract and service tests |
| M12-AC-003 | REQ-0149, REQ-0150 | Health findings and alert policies preserve impact, remediation, correlation, dedupe, escalation, and local-only delivery metadata. | Contract and service tests |
| M12-AC-004 | REQ-0151 | Durable workflow run records preserve trigger, idempotency, missed-run policy, approval requirement, status, and diagnostics. | Contract tests |
| M12-AC-005 | REQ-0152 | Financially meaningful missed runs require approval and cannot auto-replay through bounded catch-up. | Contract tests |
| M12-AC-006 | REQ-0153 | Deterministic risk decisions reject breached strict controls and require override authority for modified outcomes. | Contract and service tests |
| M12-AC-007 | REQ-0154 | SQLite persistence round trips and queries M12 metadata by component, workflow, and policy. | Persistence tests |
| M12-AC-008 | REQ-0155, REQ-0156 | Manual testing, traceability, OpenSpec, ADR, status, and exit evidence are retained. | Inspection and hosted Quality |
