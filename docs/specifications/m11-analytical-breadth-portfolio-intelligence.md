# M11 Analytical Breadth and Portfolio Intelligence Specification

- **Status:** Accepted
- **Milestone:** M11
- **Requirements:** REQ-0134 through REQ-0144
- **ADR:** ADR-0037
- **Last updated:** 2026-07-25

## Intent

M11 establishes the governed analytical-breadth foundation for OSCA's broad intelligence platform. It defines metadata contracts and deterministic gates for analysis packs, evidence bundles, cross-family synthesis, method comparison, outcome calibration, portfolio scenario evidence, visualization pack metadata, and SQLite lifecycle persistence.

## Scope

M11 includes metadata and evidence contracts for fundamental and valuation, macro and cross-market, events and catalysts, news and sentiment, crypto market structure and on-chain, portfolio scenario, specialized ML, visualization, and cross-family synthesis pack families.

M11 does not implement external data retrieval, news scraping, on-chain adapters, chart rendering, LLM narrative generation, recommendation execution, live trading, or provider production promotion.

## Acceptance Criteria

| ID | Requirement | Criterion | Evidence |
|---|---|---|---|
| M11-AC-001 | REQ-0134, REQ-0135 | Analysis pack manifests preserve methodology, data requirements, assumptions, limitations, and fail-closed validation decisions. | Contract tests |
| M11-AC-002 | REQ-0136, REQ-0137 | Result bundles and synthesis reports preserve supporting and contradicting evidence references. | Contract tests |
| M11-AC-003 | REQ-0138 | Method comparison blocks preferred results that were not compared. | Service tests |
| M11-AC-004 | REQ-0139 | Outcome calibration records degraded outcomes when error metrics exceed threshold. | Service tests |
| M11-AC-005 | REQ-0140 | Portfolio scenario reports retain paper-account and stress-assumption evidence without order authority. | Contract tests |
| M11-AC-006 | REQ-0141 | Visualization pack specs require accessibility summaries and export metadata. | Contract tests |
| M11-AC-007 | REQ-0142 | SQLite persistence round trips and queries M11 metadata by project and paper account. | Persistence tests |
| M11-AC-008 | REQ-0143, REQ-0144 | Manual testing, traceability, OpenSpec, ADR, status, and exit evidence are retained. | Inspection and hosted Quality |

## Deferred Scope

- Runtime fundamental, macro, event, news, sentiment, on-chain, or portfolio analytics engines.
- External provider calls and production provider promotion.
- Visualization rendering and dashboard UI.
- LLM-generated synthesis.
- Live trading, real-capital orders, and recommendation execution.
