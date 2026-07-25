# M12 Risk Register

| Risk | Treatment | Status |
|---|---|---|
| M12-R-001 Backup package leaks secrets | Require encrypted manifests and secret-reference-only backups. | Treated |
| M12-R-002 Restore corrupts active state | Require isolated restore verification and reject active-environment mutation. | Treated |
| M12-R-003 Disaster recovery is unverified | Preserve DR exercise records linked to restore verification and objectives. | Treated |
| M12-R-004 Health failures remain silent | Preserve health findings with impact, remediation, correlation identity, and alert policy metadata. | Treated |
| M12-R-005 Missed workflows replay unsafe work | Require approval for financially meaningful missed runs. | Treated |
| M12-R-006 Risk controls are bypassed | Reject breached strict controls and require override authority for modified outcomes. | Treated |
| M12-R-007 Persistence evidence is ambiguous | Store typed operations records with component, workflow, and policy scoped indexes. | Treated |
