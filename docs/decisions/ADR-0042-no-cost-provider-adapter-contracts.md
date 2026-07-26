# ADR-0042: No-Cost Provider Adapter Contracts

- **Status:** Accepted
- **Date:** 2026-07-26
- **Decision drivers:** REQ-0167, P2 discovery catalog, P3 provider profile catalog, licensing safety, no-cost usability

## Context

P3 selected SEC EDGAR and FRED as preferred no-cost provider profiles ready for adapter-contract planning. The next step needs executable contract shape without accidentally enabling live provider access.

## Decision

OSCA will define fixture-backed adapter contracts for SEC EDGAR and FRED before implementing live clients. These contracts will preserve provider-specific endpoint scope, credential requirements, fair-access or quota constraints, request identity, fixture validation, and a disabled-network boundary.

## Consequences

- SEC EDGAR and FRED become adapter-contract ready.
- Non-preferred providers remain blocked from default adapter contracts.
- Live provider calls, runtime routing, credential materialization, production promotion, and ingestion remain deferred.
