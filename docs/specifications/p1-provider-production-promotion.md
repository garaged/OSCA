# P1 Provider Production Promotion Specification

- **Status:** Accepted
- **Milestone:** P1
- **Requirements:** REQ-0157 through REQ-0166
- **ADR:** ADR-0039
- **Last updated:** 2026-07-25

## Intent

P1 establishes governed provider production promotion evidence for paid, authenticated, or license-sensitive market-data providers. It defines provider evidence bundles, deterministic approval gates, and SQLite metadata persistence for Twelve Data and Kraken promotion decisions.

## Scope

P1 includes provider capability scope, licensing/account-plan permissions, named credential-reference verification, quota headroom evidence, deterministic promotion decisions, and metadata persistence.

P1 does not implement real provider calls, credential materialization, production ingestion jobs, external redistribution/export behavior, runtime provider scheduling, live execution, or real-capital orders.

## Acceptance Criteria

| ID | Requirement | Criterion | Evidence |
|---|---|---|---|
| P1-AC-001 | REQ-0157, REQ-0158 | Provider production evidence preserves provider identity, capability scope, supported asset classes, intervals, and capability declarations for Twelve Data and Kraken. | Contract tests |
| P1-AC-002 | REQ-0159 | Licensing/account-plan evidence records retrieval, retention, transformation, export, backup, and redistribution permissions; missing required permissions fail closed. | Contract and service tests |
| P1-AC-003 | REQ-0160 | Credential evidence uses named secret references, verifies configured credentials, and rejects secret-looking values. | Contract tests |
| P1-AC-004 | REQ-0161 | Quota evidence records policy, limits, reset time, observed time, and required headroom; insufficient headroom blocks promotion. | Contract and service tests |
| P1-AC-005 | REQ-0162, REQ-0163 | Deterministic provider promotion decisions approve only complete evidence, defer warning findings, and block errors. | Service tests |
| P1-AC-006 | REQ-0164 | SQLite persistence round trips provider evidence and promotion decisions by provider. | Persistence tests |
| P1-AC-007 | REQ-0165, REQ-0166 | Manual testing, traceability, OpenSpec, ADR, status, and exit evidence are retained. | Inspection and hosted Quality |


## Deferred Scope

- Real Twelve Data or Kraken API calls.
- Credential value access or secret materialization.
- Production ingestion jobs.
- External redistribution/export implementation.
- Runtime provider scheduling.
- Broker or exchange execution.
- Real-capital orders.
