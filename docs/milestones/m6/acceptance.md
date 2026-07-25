# M6 Acceptance Criteria

| ID | Requirement | Acceptance criterion | Verification |
|---|---|---|---|
| M6-AC-001 | REQ-0085 | Backtest requests identify project, strategy, fidelity profile, execution mode, window, dataset revisions, data availability, assumptions, and optional seed. | Contract tests |
| M6-AC-002 | REQ-0086 | Fidelity profile and execution mode mismatches fail closed before execution. | Service tests |
| M6-AC-003 | REQ-0087 | Revised-after-fact data is rejected for backtest planning. | Service tests |
| M6-AC-004 | REQ-0088 | Event-driven and forward-paper profiles reject provisional data. | Service tests |
| M6-AC-005 | REQ-0089 | Strategy decisions and order intents retain evidence and decision linkage without live-execution behavior. | Contract tests |
| M6-AC-006 | REQ-0090 | Execution plans disclose required checks and cannot be executable when error findings exist. | Contract tests and service tests |
| M6-AC-007 | REQ-0091 | Completed backtest results require at least one metric and retain method metadata. | Contract tests |
| M6-AC-008 | REQ-0092 | M6 completion is evidenced through tests, OpenSpec validation, traceability, docs, and hosted Quality. | Exit review |
