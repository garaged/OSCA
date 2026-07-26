# ADR-0041: No-Cost Provider Profile Catalog Authority

- **Status:** Accepted
- **Date:** 2026-07-25
- **Deciders:** Product, architecture, data, licensing, operations, and quality authorities
- **Supersedes:** None
- **Superseded by:** None

## Context

P2 records additional no-cost provider candidates in documentation. Future implementation work needs an executable authority so preferred, conditional, research-only, and excluded sources cannot drift from the governed catalog.

## Decision

OSCA will represent no-cost provider candidates in deterministic provider profile contracts before adapter implementation.

The profile catalog is authoritative for implementation-readiness planning. Preferred candidates can proceed to adapter-contract planning. Conditional candidates require additional evidence. Research-only and excluded providers are blocked from default automated implementation.

## Consequences

- Provider selection becomes testable before any network adapter exists.
- Excluded unofficial paths remain blocked by code and policy.
- Provider profiles remain separate from P1 production-promotion evidence.
- P3 does not authorize provider calls, credentials, routing, or production promotion.
