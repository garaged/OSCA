# M8 Acceptance Criteria

| ID | Requirement | Acceptance criterion |
|---|---|---|
| M8-AC-001 | REQ-0102 | Paper accounts preserve independent identity, base currency, status, and lifecycle timestamps. |
| M8-AC-002 | REQ-0103 | Paper evaluation accepts only candidates linked to an approved M7 promotion gate. |
| M8-AC-003 | REQ-0104 | Paper run requests declare paper account, approved candidate, data requirements, schedule identity when present, and request time. |
| M8-AC-004 | REQ-0105 | Data and operational health gates block paper processing when error findings or blocked states exist. |
| M8-AC-005 | REQ-0106 | Account pause and system kill-switch controls are explicit deterministic state. |
| M8-AC-006 | REQ-0107 | Paper evaluation state cannot imply live execution or real-capital order placement. |
| M8-AC-007 | REQ-0108 | Backtest-versus-forward comparison preserves F2/F3 identities, metric methodology, and findings. |
| M8-AC-008 | REQ-0109 | Durable automation, notification delivery, and recovery behavior fail closed until specified in later M8 slices. |
| M8-AC-009 | REQ-0110 | M8 documentation and evidence identify deferred live execution, ML, LLM, and provider promotion scope. |
| M8-AC-010 | REQ-0111 | M8 closes only with retained evidence, accepted spec, archived OpenSpec change, and hosted Quality pass. |
| M8-AC-011 | REQ-0112 | M8 creates the first manual testing and usage baseline and requires later milestone specs to update it or document why no change is needed. |
