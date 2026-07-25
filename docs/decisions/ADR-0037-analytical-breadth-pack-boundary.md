# ADR-0037: Analytical Breadth Pack Boundary

- **Status:** Accepted
- **Date:** 2026-07-25
- **Deciders:** Product authority, architecture authority, quality authority
- **Technical Story:** M11 analytical breadth and portfolio intelligence

## Context

M11 expands OSCA from governed foundations into a broader intelligence platform. The PRD names fundamental and valuation, macro and cross-market, events, news and sentiment, crypto market structure and on-chain, portfolio and scenario analysis, specialized ML, visualization packs, cross-family evidence synthesis, method comparison, and outcome calibration.

Implementing all runtime engines at once would mix provider policy, data licensing, visualization rendering, ML, LLM, and portfolio-risk concerns in one milestone.

## Decision

M11 establishes analysis-pack and intelligence-evidence contracts before runtime engines. Built-in and future extension packs must declare family, version, supported asset classes, output kinds, data requirements, methodology, assumptions, limitations, and documentation.

M11 result evidence is retained as typed metadata: result bundles, method comparisons, outcome calibration, portfolio scenario reports, cross-family synthesis reports, and visualization pack specs. Validation fails closed when required methodology or synthesis metadata is absent.

SQLite persistence stores metadata only and supports project, pack, and paper-account scoped queries.

## Consequences

- Analytical breadth can grow through governed packs without privileged database access.
- Cross-family synthesis preserves supporting and contradicting evidence rather than producing opaque scores.
- Portfolio scenario evidence is not order authority and cannot imply live execution.
- Runtime analytical engines, provider adapters, chart rendering, LLM narrative generation, and production provider promotion remain deferred.
