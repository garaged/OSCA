# U10 Requirement Traceability

| Requirement | Implementation | Automated evidence | Manual evidence |
|---|---|---|---|
| Dedicated retained-evidence sections | `analyst_workspace/contracts.py`, `services.py` | `test_research_evidence_uses_dedicated_sections` | Workspace snapshot |
| Explicit artifact health | `analyst_workspace/evidence.py` reconciliation | `test_incomplete_incompatible_and_orphaned_are_derived`, corrupt-evidence test | Disposable malformed/incomplete/orphaned exercise |
| Navigable lineage | `WorkspaceEvidenceService.detail` and lineage links | `test_detail_lineage_filters_and_portable_export` | Experiment detail output |
| Date, symbol, timeframe, type, and status filters | `WorkspaceFilter`, API query parameters, CLI flags | API/CLI equivalence test | Filtered CLI/API comparison |
| Raw JSON download | `/api/evidence/{item_id}/raw` | API equivalence test | Local raw download inspection |
| Policy-governed portable export | `portable_export`, export manifest, CLI/API endpoints | ZIP manifest and exclusion assertions | Portable ZIP manifest inspection |
| CLI/API/export agreement | CLI evidence service, loopback API, shared contracts | `test_api_cli_and_export_use_equivalent_contracts` | Retained comparison output |
| Read-only safety boundaries | snapshot/detail contracts and loopback-only server | dedicated-section and API tests | Snapshot and health inspection |
| No duplicate generic reports | report exclusion rules | dedicated-section regression | Snapshot inspection |

U10 does not authorize recommendations, automatic promotion, live model serving, provider retrieval from the workspace, broker connectivity, autonomous execution, real-capital orders, remote writes, or public evidence sharing.
