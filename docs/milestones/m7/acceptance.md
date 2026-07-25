# M7 Acceptance Criteria

| ID | Requirement | Acceptance criterion | Verification |
|---|---|---|---|
| M7-AC-001 | REQ-0093 | Event contracts preserve typed identity and timezone-aware effective time. | Contract tests |
| M7-AC-002 | REQ-0094 | Order lifecycle events retain order-intent links and reject invalid lifecycle regressions. | Service tests |
| M7-AC-003 | REQ-0095 | Simulated fills retain model, observation, price, quantity, fee, spread, slippage, latency, liquidity, and partial-fill metadata. | Contract tests |
| M7-AC-004 | REQ-0096 | Risk outcomes represent approve, modify, reject, and pause decisions with policy version and rationale. | Contract tests |
| M7-AC-005 | REQ-0097 | Journal transactions fail closed unless line amounts balance by currency. | Contract and service tests |
| M7-AC-006 | REQ-0098 | Valuation snapshots retain base currency, price source, FX source when needed, effective time, and valuation version. | Contract tests |
| M7-AC-007 | REQ-0099 | Portfolio projections identify journal and valuation evidence as rebuild inputs. | Contract tests |
| M7-AC-008 | REQ-0100 | Promotion gates disclose blocking findings and cannot approve F3 activation. | Service tests |
| M7-AC-009 | REQ-0101 | M7 completion is evidenced through tests, OpenSpec validation, traceability, docs, and hosted Quality. | Exit review |
