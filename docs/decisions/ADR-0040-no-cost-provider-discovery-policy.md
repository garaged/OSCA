# ADR-0040: No-Cost Provider Discovery and Selection Policy

- **Status:** Accepted
- **Date:** 2026-07-25
- **Deciders:** Product, architecture, data, licensing, and quality authorities
- **Supersedes:** None
- **Superseded by:** None

## Context

P1 added provider production promotion evidence gates and an explicit no-cost provider baseline. OSCA now needs a conservative way to discover additional no-cost sources without confusing discovery with implementation or production approval.

Free provider claims are not enough. Some sources are official but quota-limited, some are dataset-specific, some are useful only for macro/fundamental enrichment, and some popular sources rely on unofficial endpoints or scraping.

## Decision

OSCA will maintain a governed no-cost provider discovery catalog before implementing additional provider adapters.

The catalog must classify each source by cost model, payment requirement, account/key requirement, capability fit, source evidence, operational constraints, and disposition. Licensing, redistribution, automation, or quota uncertainty fails closed into conditional, research-only, or excluded status.

Official APIs and clearly documented public data access are preferred. Unofficial or undocumented market-data endpoints are excluded until a compliant official path is evidenced.

## Consequences

- Future provider implementation work starts from a reviewed catalog instead of ad hoc popularity.
- A provider can be attractive and still not be implementation-ready.
- Macro/fundamental/event sources can strengthen OSCA without pretending to be OHLCV substitutes.
- P2 does not production-enable any provider; P1 gates still govern promotion.
