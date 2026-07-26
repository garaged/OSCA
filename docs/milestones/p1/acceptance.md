| ID | Requirement | Criterion | Evidence |
|---|---|---|---|
| P1-AC-001 | REQ-0157, REQ-0158 | Provider production evidence preserves provider identity, capability scope, supported asset classes, intervals, and capability declarations for Twelve Data and Kraken. | Contract tests |
| P1-AC-002 | REQ-0159 | Licensing/account-plan evidence records retrieval, retention, transformation, export, backup, and redistribution permissions; missing required permissions fail closed. | Contract and service tests |
| P1-AC-003 | REQ-0160 | Credential evidence uses named secret references, verifies configured credentials, and rejects secret-looking values. | Contract tests |
| P1-AC-004 | REQ-0161 | Quota evidence records policy, limits, reset time, observed time, and required headroom; insufficient headroom blocks promotion. | Contract and service tests |
| P1-AC-005 | REQ-0162, REQ-0163 | Deterministic provider promotion decisions approve only complete evidence, defer warning findings, and block errors. | Service tests |
| P1-AC-006 | REQ-0164 | SQLite persistence round trips provider evidence and promotion decisions by provider. | Persistence tests |
| P1-AC-007 | REQ-0165, REQ-0166 | Manual testing, traceability, OpenSpec, ADR, status, and exit evidence are retained. | Inspection and hosted Quality |

- No-cost/free-tier account-plan evidence is represented explicitly, and complete no-cost provider evidence remains eligible for the baseline operating path without requiring user payment.
